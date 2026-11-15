#!/usr/bin/env python3
"""True local Chromium Playwright fixture QA; NOT installed WP/HTTP/axe/field CWV."""
from pathlib import Path
import subprocess, json, sys, re
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'QA'; ART.mkdir(exist_ok=True)
html=subprocess.check_output(['php',str(ROOT/'qa/fixture.php')],text=True)
cases=[
 ('mobile-320',320,16,False,False,False,False),
 ('mobile-390',390,16,False,False,False,False),
 ('tablet-768',768,16,False,False,False,False),
 ('desktop-1440',1440,16,False,False,False,False),
 ('wide-1920',1920,16,False,False,False,False),
 ('mobile-nojs-320',320,16,True,False,False,False),
 ('mobile-root4x-320',320,64,False,False,False,False),
 ('reduced-390',390,16,False,True,False,False),
 ('forced-320',320,16,False,False,True,False),
 ('touch-390',390,16,False,False,False,True),
]
result={'runner':'local php-rendered HTML in real Chromium Playwright page.set_content; browser HTTP/file navigation blocked','limitations':['not installed WordPress/Assembler','not axe-core','not HTTP response or CSP','not p75 field LCP/CLS/INP','not native zoom/screen-reader'], 'cases':[]}
counts=0
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for name,width,root,nojs,reduced,forced,touch in cases:
        ctx=browser.new_context(viewport={'width':width,'height':850},device_scale_factor=1,java_script_enabled=not nojs,
                                reduced_motion='reduce' if reduced else 'no-preference', forced_colors='active' if forced else 'none',has_touch=touch)
        page=ctx.new_page()
        page.set_content(html,wait_until='load')
        if root!=16: page.add_style_tag(content=f'html{{font-size:{root}px!important}}')
        page.wait_for_timeout(120)
        baseline=page.evaluate('''() => ({
           stages:document.querySelectorAll('[data-fv-evidence-stage]').length,
           drawers:document.querySelectorAll('[data-fv-source-drawer]').length,
           nasa:document.querySelectorAll('[data-fv-nasa-source]').length,
           context:document.querySelectorAll('[data-fv-nasa-context]').length,
           free:document.querySelectorAll('[data-fv-free-cta]').length,
           scripts:document.scripts.length, images:document.images.length,
           ids:[...document.querySelectorAll('[id]')].map(e=>e.id),
           jumpOk:[...document.querySelectorAll('.fv-apollo-r372__jump a')].every(a=>document.getElementById(a.getAttribute('href').slice(1))),
           overflow:document.documentElement.scrollWidth>innerWidth+1,
           cardWidth:Math.round(document.querySelector('[data-fv-evidence-stage]').getBoundingClientRect().width),
           bodyBackground:getComputedStyle(document.querySelector('[data-fv-apollo-path]')).backgroundColor,
           cssToken:getComputedStyle(document.querySelector('[data-fv-apollo-path]')).getPropertyValue('--ar-bg').trim(),
           allCitationsHttps:[...document.querySelectorAll('[data-fv-nasa-source],[data-fv-nasa-context]')].every(a=>a.href.startsWith('https://www.nasa.gov/')),
           anchorCt:[...document.querySelectorAll('a')].length,
           lcp:performance.getEntriesByType('largest-contentful-paint').map(x=>Math.round(x.startTime)).at(-1)??null,
           navigation:performance.getEntriesByType('navigation').length
        })''')
        paint=({'lcp_ms':None,'observed_cls':None} if nojs else page.evaluate('''() => new Promise(resolve=>{
          const lcp=[], shifts=[]; let a,b;
          try{a=new PerformanceObserver(list=>{for(const x of list.getEntries())lcp.push(Math.round(x.startTime))});a.observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
          try{b=new PerformanceObserver(list=>{for(const x of list.getEntries())if(!x.hadRecentInput)shifts.push(x.value)});b.observe({type:'layout-shift',buffered:true});}catch(e){}
          setTimeout(()=>{a?.disconnect();b?.disconnect();resolve({lcp_ms:lcp.at(-1)??null,observed_cls:shifts.reduce((u,v)=>u+v,0)})},120)
        })'''))
        checks={
         'four_stages':baseline['stages']==4,
         'four_drawers':baseline['drawers']==4,
         'source_links':baseline['nasa']==4,
         'retrospective_context':baseline['context']==1,
         'single_editorial_cta':baseline['free']==1,
         'no_scripts':baseline['scripts']==0,
         'no_images':baseline['images']==0,
         'unique_ids':len(baseline['ids'])==len(set(baseline['ids'])),
         'functional_jump_anchors':baseline['jumpOk'],
         'no_horizontal_overflow':not baseline['overflow'],
         'all_nasa_citations_https':baseline['allCitationsHttps'],
         'css_applied':baseline['cssToken']=='#0d1011',
         'source_closed_initially':not page.locator('[data-fv-source-drawer]').first.get_attribute('open'),
        }
        # Native keyboard disclosure with no JS, then reopen using pointer/touch.
        summary=page.locator('[data-fv-source-drawer] summary').first
        summary.focus();page.keyboard.press('Enter')
        checks['keyboard_open']=page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
        checks['keyboard_link_visible']=page.locator('[data-fv-nasa-source]').first.is_visible()
        page.keyboard.press('Enter')
        checks['keyboard_close']=not page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
        summary.click()
        checks['pointer_or_touch_open']=page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
        # Native Chromium Accessibility Tree, not axe-core / manual screen reader.
        try:
            session=ctx.new_cdp_session(page)
            nodes=session.send('Accessibility.getFullAXTree').get('nodes',[])
            names=[(n.get('role') or {}).get('value','')+':'+(n.get('name') or {}).get('value','') for n in nodes]
            checks['cdp_named_editorial_link']=any('link:Read the full free Apollo 1 investigation' in x for x in names)
            checks['cdp_named_source_summary']=any('Inspect document, date and rights for stage 1' in x for x in names)
        except Exception:
            checks['cdp_named_editorial_link']=False;checks['cdp_named_source_summary']=False
        # Restore to reproducible collapsed state for screenshot.
        summary.click()
        page.screenshot(path=str(ART/(name+'.png')),full_page=True,animations='disabled')
        if not all(checks.values()):
            print('FAIL '+name+' '+json.dumps({k:v for k,v in checks.items() if not v}));sys.exit(1)
        counts+=len(checks)
        result['cases'].append({'name':name,'width_css_px':width,'root_font_px':root,'java_script':not nojs,'touch':touch,'checks':checks,'card_width_px':baseline['cardWidth'],'local_lcp_entry_ms':paint['lcp_ms'],'local_observed_cls':paint['observed_cls']})
        if name=='desktop-1440':
            # Print without opening disclosures. All citations must still appear.
            page.emulate_media(media='print')
            page.pdf(path=str(ART/'apollo-evidence-path-print.pdf'),format='A4',print_background=True,prefer_css_page_size=False,
                     margin={'top':'10mm','bottom':'10mm','left':'10mm','right':'10mm'})
        ctx.close()
    browser.close()
pdf=PdfReader(str(ART/'apollo-evidence-path-print.pdf'))
links=[]
for page in pdf.pages:
 for a in page.get('/Annots',[]):
  obj=a.get_object();target=obj.get('/A')
  if target and target.get('/URI'):links.append(str(target['/URI']))
expected={
 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
 'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
 'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
}
if not expected.issubset(set(links)) or not any('finalvestige.com/2026/08/20' in x for x in links):
 print('FAIL print source links '+json.dumps(links));sys.exit(1)
result['print']={'pages':len(pdf.pages),'nasa_unique':len(set(links)&expected),'fv_links':sum('finalvestige.com' in x for x in links),'destinations':sorted(set(links))}
result['summary']={'contexts_passed':len(cases),'checks_passed':counts,'checks_failed':0,'no_synthetic_cwv_claim':True}
(ART/'browser-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('R372 real local Chromium PASS',len(cases),'contexts',counts,'checks; print',len(pdf.pages),'pages',len(set(links)&expected),'NASA URL destinations')
