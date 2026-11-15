#!/usr/bin/env python3
"""R377 real Chromium set_content QA, not an installed WordPress or production run."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'QA'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
TESTS=[('mobile-320',320,False,False,False,False,False),('mobile-390',390,False,False,False,False,False),
('tablet-768',768,False,False,False,False,False),('desktop-1440',1440,False,False,False,False,False),
('wide-1920',1920,False,False,False,False,False),('nojs-320',320,True,False,False,False,False),
('root4x-320',320,False,True,False,False,False),('reduced-390',390,False,False,True,False,False),
('forced-320',320,False,False,False,True,False),('touch-390',390,False,False,False,False,True)]
JS_OBSERVERS="""window.__lab={LCP:null,CLS:0};
try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__lab.LCP=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__lab.CLS+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}"""

def shell(cmd):return subprocess.run(cmd,capture_output=True,text=True)
def run():
    OUT.mkdir(exist_ok=True)
    lint=shell(['php','-l',str(ROOT/'source-role-desk.php')])
    assert lint.returncode==0,lint.stderr
    php=[]
    for scenario in ['enabled','disabled','production','wronghost','preowned','tamper']:
        cp=shell(['php',str(ROOT/'qa/fixture.php'),scenario]); assert cp.returncode==0,(scenario,cp.stdout,cp.stderr)
        row=json.loads(cp.stdout);assert row['failed']==0,row
        php.append({'scenario':scenario,'passed':row['passed'],'failed':row['failed']})
    html=shell(['php',str(ROOT/'qa/fixture.php'),'enabled','--html'])
    assert html.returncode==0,html.stderr
    fixture=ROOT/'qa/r377_local_fixture.html';fixture.write_text(html.stdout,encoding='utf-8')
    fixture_html=html.stdout.replace('<link rel="stylesheet" href="../assets/source-role.css">','<style>'+ (ROOT/'assets/source-role.css').read_text() +'</style>')
    results=[];screens=[]
    with sync_playwright() as p:
      browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
      for name,width,nojs,root4,reduced,forced,touch in TESTS:
        ctx=browser.new_context(viewport={'width':width,'height':860},java_script_enabled=not nojs,
           reduced_motion='reduce' if reduced else 'no-preference',
           forced_colors='active' if forced else 'none',has_touch=touch)
        if not nojs:ctx.add_init_script(JS_OBSERVERS)
        page=ctx.new_page();requests=[]
        page.on('request',lambda r: requests.append(r.url))
        page.set_content(fixture_html,wait_until='load')  # Browser navigation prohibited; this is fixture injection, never HTTP QA
        if root4:page.add_style_tag(content='html{font-size:64px!important}')
        page.wait_for_timeout(220)
        dom=page.evaluate("""() => {
          const r=document.querySelector('[data-fv-r377]'), cards=[...r.querySelectorAll('[data-fv-r377-record]')];
          return {cards:cards.length,drawers:r.querySelectorAll('[data-fv-r377-source]').length,
            evidence:[...r.querySelectorAll('[data-fv-r377-evidence]')].map(a=>a.href),
            context:[...r.querySelectorAll('[data-fv-r377-context]')].map(a=>a.href),
            cta:[...r.querySelectorAll('[data-fv-free-cta]')].map(a=>a.href),
            titles:cards.map(c=>c.querySelector('h3').textContent.trim()),
            content:r.textContent,overflow:document.documentElement.scrollWidth>innerWidth+1,
            ids:[...document.querySelectorAll('[id]')].map(x=>x.id),
            css:getComputedStyle(r).backgroundColor, css_variable:getComputedStyle(r).getPropertyValue('--rv-bg').trim(),
            lab:window.__lab||null,
            rootFont:getComputedStyle(document.documentElement).fontSize,
            paragraphWidth:cards[0].querySelector('p:not(.fv-r377__number)').getBoundingClientRect().width,
            sources:cards.map(c=>c.querySelector('[data-fv-r377-evidence]').href)};
        }""")
        checks={'six_cards':dom['cards']==6,'six_native_drawers':dom['drawers']==6,
          'primary_source_roles':dom['evidence'][:5]==[BOARD]*5,
          'flammability_source_role':dom['evidence'][5]=='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
          '2022_context_distinct':dom['context'][0]=='https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
          'image_not_telemetry': 'NOT an instrument chronology' in dom['content'],
          '102_after_fire_not_1967_accident':'not 102 ignitions during the January 1967 accident' in dom['content'],
          'single_free_CTA':dom['cta']==[FREE],
          'no_horiz_scroll':not dom['overflow'],
          'unique_IDs':len(dom['ids'])==len(set(dom['ids'])),
          'stylesheet_applied':dom['css_variable']=='#0d1011',
          'no_external_network':not any(x.startswith('http://') or x.startswith('https://') for x in requests)}
        summary=page.locator('[data-fv-r377-source] > summary').first
        summary.focus();page.keyboard.press('Enter')
        checks['keyboard_toggle_open']=page.locator('[data-fv-r377-source]').first.evaluate('(d)=>d.open')
        page.keyboard.press('Enter')
        checks['keyboard_toggle_close']=not page.locator('[data-fv-r377-source]').first.evaluate('(d)=>d.open')
        summary.click();checks['touch_pointer_open']=page.locator('[data-fv-r377-source]').first.evaluate('(d)=>d.open')
        summary.click()
        if root4:
          checks['enlarged_root_font']=dom['rootFont']=='64px'
          checks['reflow_preserves_readable_width']=dom['paragraphWidth']>=200
        path=OUT/f'{name}.png';page.screenshot(path=str(path),full_page=True,animations='disabled')
        screens.append(path)
        if name=='desktop-1440':
            page.emulate_media(media='print')
            page.pdf(path=str(OUT/'R377_Source_Role_Dossier.pdf'),format='A4',print_background=True)
        results.append({'name':name,'width':width,'checks':checks,'all_pass':all(checks.values()),
          'lab_timings_NOT_field':dom['lab'], 'mode':'SET_CONTENT_LOCAL_FIXTURE_NOT_INSTALLED_WP'})
        ctx.close()
      browser.close()
    reader=PdfReader(str(OUT/'R377_Source_Role_Dossier.pdf'))
    urls=[]
    for pg in reader.pages:
        for a in pg.get('/Annots',[]):
            d=a.get_object().get('/A')
            if d and d.get('/URI'):urls.append(str(d['/URI']))
    pdffile={'pages':len(reader.pages),'links':sorted(set(urls)),
            'pass':BOARD in urls and 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/' in urls and FREE in urls}
    result={'status':'LOCAL_QA_PASS_NOT_STAGING' if all(r['all_pass'] for r in results) and pdffile['pass'] else 'FAIL',
      'php':php,'browser':results,'pdf':pdffile,
      'browser_boundary':'real Chromium set_content fixture, not HTTP navigation or WordPress/Assembler',
      'axe_core':'NOT_EXECUTED - genuine distribution unavailable offline',
      'native_zoom_screen_readers':'NOT_EXECUTED',
      'http_csp_hosted_ci_installed_wordpress':'NOT_EXECUTED',
      'production_cwv_net_revenue':'NOT_MEASURED',
      'source_custody_sha256':hashlib.sha256((ROOT/'custody.json').read_bytes()).hexdigest()}
    (OUT/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'], 'PHP',sum(r['passed'] for r in php),'/',sum(r['passed']+r['failed'] for r in php),
          'Chromium',sum(sum(row['checks'].values()) for row in results),'/',sum(len(row['checks']) for row in results),
          'contexts',len(results),'PDF',pdffile)
    return 0 if result['status']=='LOCAL_QA_PASS_NOT_STAGING' else 1
if __name__=='__main__':sys.exit(run())
