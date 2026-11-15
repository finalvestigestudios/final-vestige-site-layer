#!/usr/bin/env python3
"""R381 real Chromium local PHP-rendered fixture QA; no staging or production claim."""
import hashlib,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experience2/apollo-r381'; QA=BASE/'QA'
CSS=BASE/'assets/evidence-to-investigation.css'
PHP=BASE/'qa/wp_stub.php'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FLAM='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MODES=[('320-mobile',320,False,False,False,False,False),('390-mobile',390,False,False,False,False,False),('768-tablet',768,False,False,False,False,False),('1440-desktop',1440,False,False,False,False,False),('1920-wide',1920,False,False,False,False,False),('320-nojs',320,True,False,False,False,False),('320-root4x',320,False,True,False,False,False),('390-reduced',390,False,False,True,False,False),('320-forced-colors',320,False,False,False,True,False),('390-touch',390,False,False,False,False,True)]
OBS='''window.__rv={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(let e of l.getEntries())window.__rv.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(let e of l.getEntries())if(!e.hadRecentInput)window.__rv.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}'''
def run():
 QA.mkdir(parents=True,exist_ok=True)
 phprun=subprocess.run(['php',str(PHP)],check=True,capture_output=True,text=True)
 phpread=json.loads(phprun.stdout)
 assert phpread['passed']==phpread['total']
 html=subprocess.run(['php',str(PHP),'--html'],check=True,capture_output=True,text=True).stdout
 assert html.startswith('<!doctype html>')
 html=html.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
 rows=[]
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,width,nojs,root4x,reduced,forced,touch in MODES:
   ctx=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=not nojs,has_touch=touch,
    reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
   if not nojs:ctx.add_init_script(OBS)
   page=ctx.new_page();requests=[];page.on('request',lambda r:requests.append(r.url))
   page.set_content(html,wait_until='load')
   if root4x:page.evaluate("document.documentElement.style.fontSize='64px'")
   page.wait_for_timeout(130)
   dom=page.evaluate('''() => ({
    count:document.querySelectorAll('[data-fv-r381-item]').length,
    drawers:document.querySelectorAll('[data-fv-r381-drawer]').length,
    nasas:[...document.querySelectorAll('[data-fv-r381-nasa]')].map(x=>x.href),
    cta:[...document.querySelectorAll('[data-fv-r381-next]')].map(x=>x.href),
    overflow:document.documentElement.scrollWidth>innerWidth+1,
    css:getComputedStyle(document.querySelector('[data-fv-r381]')).getPropertyValue('--fv381-bg').trim(),
    IDs:[...document.querySelectorAll('[id]')].map(x=>x.id),
    rootFont:getComputedStyle(document.documentElement).fontSize,
    text:document.querySelector('[data-fv-r381]').textContent,
    vitals:window.__rv||null})''')
   checks={
    'three_reviewed_records':dom['count']==3,
    'three_native_drawers':dom['drawers']==3,
    'documentary_source_order':dom['nasas']==[BOARD,BOARD,FLAM],
    'single_free_CTA':dom['cta']==[FREE],
    'later_tests_not_incident': 'not three-digit fire incidents in January 1967' in dom['text'],
    'source_uncertainty':'did not conclusively identify' in dom['text'],
    'rights_disclosure':'not a license to reproduce images' in dom['text'],
    'future_kit_not_for_sale':'not a product currently available to purchase' in dom['text'],
    'source_links_not_decorative':page.locator('a[data-fv-r381-nasa]').count()==3,
    'only_allowed_links':page.locator('a').count()==7,
    'no_embedded_media_or_checkout':page.locator('img,iframe,video,form,input,a[href*="payhip"],a[href*="checkout"]').count()==0,
    'stylesheet_effective':dom['css']=='#121617',
    'no_horizontal_overflow':not dom['overflow'],
    'unique_IDs':len(dom['IDs'])==len(set(dom['IDs'])),
    'no_network_requests':not requests,
   }
   drawer=page.locator('[data-fv-r381-drawer]').first;drawer.locator('summary').focus()
   checks['visible_focus']=drawer.locator('summary').evaluate("e=>getComputedStyle(e).outlineStyle")!='none'
   page.keyboard.press('Enter');checks['keyboard_opens']=drawer.evaluate('e=>e.open')
   page.keyboard.press('Enter');checks['keyboard_closes']=not drawer.evaluate('e=>e.open')
   drawer.locator('summary').click();checks['pointer_opens']=drawer.evaluate('e=>e.open')
   drawer.locator('summary').click();checks['pointer_closes']=not drawer.evaluate('e=>e.open')
   if root4x:checks['four_times_root_font_set']=dom['rootFont']=='64px'
   if reduced:checks['reduced_motion']=page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
   if forced:checks['forced_colors']=page.evaluate("matchMedia('(forced-colors: active)').matches")
   if touch:checks['touch_context']=page.evaluate("matchMedia('(pointer: coarse)').matches")
   if nojs:checks['no_javascript_required']=True
   page.screenshot(path=str(QA/(name+'.png')),full_page=not root4x,animations='disabled',timeout=18000)
   if name=='1440-desktop':
    page.emulate_media(media='print')
    checks['print_source_links']=page.locator('.fv-r381__print a:visible').count()==3
    page.pdf(path=str(QA/'R381_Evidence_Path_Print.pdf'),format='A4',print_background=True)
   rows.append({'mode':name,'width':width,'checks':checks,'pass':all(checks.values()),'local_fixture_performance_only':dom['vitals']})
   ctx.close()
  browser.close()
 report={'status':'LOCAL_PHP_AND_CHROMIUM_FIXTURE_PASS_NOT_STAGING' if all(x['pass'] for x in rows) else 'FAIL',
  'php_assertions':phpread['passed'],'browser_assertions_passed':sum(sum(r['checks'].values()) for r in rows),
  'browser_assertions_total':sum(len(r['checks']) for r in rows),'contexts':len(rows),'results':rows,
  'CSS_SHA256':hashlib.sha256(CSS.read_bytes()).hexdigest(),
  'limitations':['set_content fixtures: NO installed WordPress/Assembler or HTTPS/CSP network','native browser 400% zoom, axe-core, independent screen readers not executed','LCP/CLS only local fixtures, no field CWV','no validated SKU, paid sales, affiliate conversions or analytics attributable sessions']}
 (QA/'results.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print(report['status'],'PHP',report['php_assertions'],'Chromium',report['browser_assertions_passed'],'/',report['browser_assertions_total'],'contexts',len(rows))
 assert all(r['pass'] for r in rows),[(r['mode'],[k for k,v in r['checks'].items() if not v]) for r in rows if not r['pass']]
 return report
if __name__=='__main__':run()
