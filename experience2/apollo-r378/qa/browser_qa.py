#!/usr/bin/env python3
"""Actual Chromium fixture QA for R378's guarded reusable-block CSS enqueue.
This is explicitly NOT installed WordPress/Assembler nor HTTP/CSP acceptance.
No network calls, no vendor dependencies. Real axe-core is unavailable offline.
"""
import hashlib, json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'QA'
REPO=ROOT.parent
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FLAM='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CONTEXTS=[('320-mobile',320,False,False,False,False,False),('390-mobile',390,False,False,False,False,False),('768-tablet',768,False,False,False,False,False),('1440-desktop',1440,False,False,False,False,False),('1920-wide',1920,False,False,False,False,False),('320-no-js',320,True,False,False,False,False),('320-root4x',320,False,True,False,False,False),('390-reduced-motion',390,False,False,True,False,False),('320-forced-colors',320,False,False,False,True,False),('390-touch',390,False,False,False,False,True)]
OBSERVER="""window.__lab={lcp:null,cls:0};
try{new PerformanceObserver(x=>{for(const e of x.getEntries())window.__lab.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window.__lab.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}
"""
def php(*args):
    r=subprocess.run(['php',str(HERE/'wp_stub.php'),*args],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(f'PHP {args}: {r.stdout[-500:]} {r.stderr[-500:]}')
    return r.stdout

def main():
    OUT.mkdir(exist_ok=True)
    php_lint=subprocess.run(['php','-l',str(ROOT/'guarded-reusable-assets.php')],capture_output=True,text=True)
    if php_lint.returncode: raise RuntimeError(php_lint.stderr)
    scenarios=['direct','reusable','nested','duplicate','cycle','wrong_type','draft','unrelated','production','wronghost','disabled','preowned','oversize','tamper','symlink']
    api=[]
    for s in scenarios:
        data=json.loads(php(s));assert not data['failed'],data
        api.append({'scenario':s,'passed':data['passed']})
    fixture=php('reusable','--html')
    result=[]
    with sync_playwright() as p:
      b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
      for name,width,nojs,zoom,reduced,forced,touch in CONTEXTS:
        ctx=b.new_context(viewport={'width':width,'height':840},java_script_enabled=not nojs,
            reduced_motion='reduce' if reduced else 'no-preference',
            forced_colors='active' if forced else 'none',has_touch=touch)
        if not nojs: ctx.add_init_script(OBSERVER)
        page=ctx.new_page();outbound=[]
        page.on('request',lambda request:outbound.append(request.url))
        page.set_content(fixture,wait_until='load')
        if zoom: page.add_style_tag(content='html{font-size:64px!important}')
        page.wait_for_timeout(220)
        dom=page.evaluate('''() => {
          const r=document.querySelector('[data-fv-r377]');const records=[...r.querySelectorAll('[data-fv-r377-record]')];
          const styles=getComputedStyle(r);
          return {records:records.length,drawers:r.querySelectorAll('[data-fv-r377-source]').length,
            links:records.map(x=>x.querySelector('[data-fv-r377-evidence]').href),
            ctas:[...r.querySelectorAll('[data-fv-free-cta]')].map(x=>x.href),
            words:r.textContent,css:styles.getPropertyValue('--rv-bg').trim(),
            overflow:document.documentElement.scrollWidth>innerWidth+1,
            documentWidth:document.documentElement.scrollWidth,rootSize:getComputedStyle(document.documentElement).fontSize,
            textWidth:records[0].querySelector('p:not(.fv-r377__number)').getBoundingClientRect().width,
            ids:[...document.querySelectorAll('[id]')].map(x=>x.id), lab:window.__lab||null};
        }''')
        checks={
           'six_claims':dom['records']==6,
           'six_native_disclosures':dom['drawers']==6,
           'board_source_on_first_five':dom['links'][:5]==[BOARD]*5,
           'postfire_test_source_six':dom['links'][5]==FLAM,
           'no_photo_as_telemetry':'NOT an instrument chronology' in dom['words'],
           'one_editorial_link':dom['ctas']==[FREE],
           'no_merchant_or_unapproved_media':page.locator('img,video,iframe,[href*="payhip"],[href*="checkout"]').count()==0,
           'css_loaded':dom['css']=='#0d1011',
           'no_horizontal_overflow':not dom['overflow'],
           'unique_ids':len(dom['ids'])==len(set(dom['ids'])),
           'no_remote_requests':not any(x.startswith('http') for x in outbound),
        }
        first=page.locator('[data-fv-r377-source]').first
        first.locator('summary').focus()
        page.keyboard.press('Enter');checks['keyboard_open']=first.evaluate('(e)=>e.open')
        page.keyboard.press('Enter');checks['keyboard_close']=not first.evaluate('(e)=>e.open')
        first.locator('summary').click();checks['pointer_open']=first.evaluate('(e)=>e.open')
        if zoom:
          checks['4x_root_font']=dom['rootSize']=='64px'
          checks['4x_readable_width']=dom['textWidth']>=200
        path=OUT/f'{name}.png';page.screenshot(path=str(path),full_page=True,animations='disabled')
        if name=='1440-desktop':
          page.emulate_media(media='print')
          page.pdf(path=str(OUT/'Apollo_R378_Source_Role_Print.pdf'),format='A4',print_background=True)
        result.append({'context':name,'width':width,'checks':checks,'passed':sum(checks.values()),
            'all_pass':all(checks.values()),'lab_not_field_metrics':dom['lab'],
            'mode':'REAL_CHROMIUM_SET_CONTENT_LOCAL_PHP_STUB_NOT_INSTALLED_WORDPRESS'})
        ctx.close()
      b.close()
    pdf=PdfReader(str(OUT/'Apollo_R378_Source_Role_Print.pdf'))
    urls=[]
    for page in pdf.pages:
      for annot in page.get('/Annots',[]):
        a=annot.get_object().get('/A')
        if a and a.get('/URI'):urls.append(str(a['/URI']))
    pdfcheck={'page_count':len(pdf.pages),'unique_links':sorted(set(urls)),
        'pass':all(s in urls for s in (BOARD,FLAM,FREE))}
    status='LOCAL_PHP_STUB_AND_CHROMIUM_PASS_NOT_STAGING' if all(x['all_pass'] for x in result) and pdfcheck['pass'] else 'FAIL'
    report={'status':status,'php_api_stub_scenarios':api,'php_assertions':sum(x['passed'] for x in api),
            'chromium_checks':sum(x['passed'] for x in result),
            'chromium_possible_checks':sum(len(x['checks']) for x in result),
            'chromium':result,'pdf':pdfcheck,
            'source_css_sha256':hashlib.sha256((REPO/'apollo-r377/assets/source-role.css').read_bytes()).hexdigest(),
            'read_only_hosted_WordPress': 'NOT_EXECUTED_NO_APPROVED_INSTALLED_STAGING_URL',
            'axe_core': 'NOT_EXECUTED_DISTRIBUTION_UNAVAILABLE_OFFLINE',
            'screen_reader_native_zoom_http_CSP_hosted_CI':'NOT_EXECUTED',
            'attributed_paid_orders_net_revenue':'NOT_OBSERVABLE',
            'browser_boundary':'Chromium set_content of PHP WordPress API-stub output, no HTTP/CSP or installed WP' }
    (OUT/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(status,'php',report['php_assertions'],'chromium',report['chromium_checks'],'/',report['chromium_possible_checks'],'contexts',len(result),'print',len(pdf.pages),'pages',len(set(urls)),'links')
    return 0 if status.startswith('LOCAL_') else 1
if __name__=='__main__':sys.exit(main())
