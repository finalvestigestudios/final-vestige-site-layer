#!/usr/bin/env python3
"""Real navigated staging axe/LCP/CLS. Read-only. Fail closed on missing approved inputs.
Example (approved runner only): FV_APPROVED_STAGING_HOST=staging.example.com \
 python qa/hosted_acceptance.py https://staging.example.com/apollo-review/ /opt/approved/axe.min.js
"""
import hashlib,json,os,sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent.parent
report={'status':'HOLD_NOT_RUN','browser':'Chromium','navigation':'HOLD_NOT_RUN','axe':'HOLD_NOT_RUN','lcp_ms':'HOLD_NOT_RUN','cls':'HOLD_NOT_RUN'}
path=R/'QA'/'HOSTED_ACCEPTANCE.json'
url=sys.argv[1] if len(sys.argv)>1 else ''
axe=Path(sys.argv[2]) if len(sys.argv)>2 else None
approved=os.environ.get('FV_APPROVED_STAGING_HOST','')
try:
    target=urlsplit(url)
    if target.scheme!='https' or not approved or target.hostname!=approved or not target.path.startswith('/') or target.username or target.password or target.query or target.fragment:
        raise ValueError('Missing exact authorized staging host and clean HTTPS URL')
    if not axe or not axe.is_file():raise ValueError('Missing independently reviewed local axe-core bundle')
    sha=hashlib.sha256(axe.read_bytes()).hexdigest()
    expected=os.environ.get('FV_APPROVED_AXE_SHA256','')
    if len(expected)!=64 or sha!=expected:raise ValueError('axe-core bundle digest not approved')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        for width in [320,390,768,1440,1920]:
            ctx=browser.new_context(viewport={'width':width,'height':900})
            page=ctx.new_page()
            page.add_init_script('''window.__fvVitals={lcp:[],cls:0};
              new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fvVitals.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
              new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__fvVitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});''')
            response=page.goto(url,wait_until='networkidle',timeout=20000)
            if response is None or response.status>=400:raise RuntimeError('staging returned non-success')
            if page.locator('[data-fv456-root]').count()!=1:raise RuntimeError('staging shortcode absent')
            page.add_script_tag(path=str(axe))
            violations=page.evaluate('''async()=>{const v=await axe.run(document.querySelector('[data-fv456-root]'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return v.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length}))}''')
            metrics=page.evaluate('''()=>({lcp:window.__fvVitals.lcp.at(-1)??null,cls:window.__fvVitals.cls,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1})''')
            page.screenshot(path=str(R/'QA'/f'hosted-{width}.png'),full_page=True,animations='disabled')
            report.setdefault('widths',{})[str(width)]={'http_status':response.status,'violations':violations,'metrics':metrics}
            ctx.close()
        browser.close()
    if any(x['violations'] or x['metrics']['overflow'] or x['metrics']['lcp'] is None for x in report['widths'].values()):
        report['status']='FAIL_REVIEW_REQUIRED'
    else:
        report['status']='MEASURED_NEEDS_INDEPENDENT_ACCEPTANCE'
    report.update(navigation='RUN',axe='RUN',lcp_ms='MEASURED',cls='MEASURED',axe_sha256=sha)
except Exception as e:report['blocker']=str(e)
path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps(report,sort_keys=True))
if report['status']=='HOLD_NOT_RUN':raise SystemExit(2)
if report['status']=='FAIL_REVIEW_REQUIRED':raise SystemExit(1)
