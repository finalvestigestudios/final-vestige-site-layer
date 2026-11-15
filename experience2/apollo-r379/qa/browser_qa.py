#!/usr/bin/env python3
"""R379 local PHP WP-API stub + real Chromium fixture suite; no installed WordPress claim."""
import hashlib, json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
CSS=ROOT.parent/'apollo-r377/assets/source-role.css'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FLAM='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SCENARIOS=['part','nested','reusable','duplicate','cycle','foreign_theme','bad_slug','wrong_identity','draft','hidden_in_attrs','code_sample','missing_part','wrong_template_type','oversize','foreign_owner','production','wronghost','disabled','no_id']
MODES=[('320-mobile',320,False,False,False,False,False),('390-mobile',390,False,False,False,False,False),('768-tablet',768,False,False,False,False,False),('1440-desktop',1440,False,False,False,False,False),('1920-wide',1920,False,False,False,False,False),('320-nojs',320,True,False,False,False,False),('320-root4x',320,False,True,False,False,False),('390-reduced',390,False,False,True,False,False),('320-forced-colors',320,False,False,False,True,False),('390-touch',390,False,False,False,False,True)]
OBS="""window.__fvR379Vitals={lcp:null,cls:0};
try{new PerformanceObserver(l=>{for(const x of l.getEntries())window.__fvR379Vitals.lcp=x.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>{for(const x of l.getEntries())if(!x.hadRecentInput)window.__fvR379Vitals.cls+=x.value}).observe({type:'layout-shift',buffered:true})}catch(e){}
"""
def php(*args):
 p=subprocess.run(['php',str(ROOT/'qa/wp_stub.php'),*args],text=True,capture_output=True)
 if p.returncode: raise AssertionError(f'PHP {args}: {p.stdout[-700:]} {p.stderr[-700:]}')
 return p.stdout.strip().removesuffix('\\n')
def main():
 QA.mkdir(parents=True,exist_ok=True)
 for f in [ROOT/'prehead-template-parts.php',ROOT/'qa/wp_stub.php']:
  check=subprocess.run(['php','-l',str(f)],capture_output=True,text=True)
  assert check.returncode==0,check.stderr
 apis=[json.loads(php(s)) for s in SCENARIOS]
 assert all(not t['failed'] for t in apis)
 html=php('part','--html').replace('</head>','<style>'+CSS.read_text()+'</style></head>')
 assert html.startswith('<!doctype html>')
 result=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,width,nojs,root4x,reduced,forced,touch in MODES:
   print("START",name,flush=True)
   ctx=browser.new_context(viewport={'width':width,'height':800},has_touch=touch,
       java_script_enabled=not nojs,reduced_motion='reduce' if reduced else 'no-preference',
       forced_colors='active' if forced else 'none')
   if not nojs:ctx.add_init_script(OBS)
   page=ctx.new_page();requests=[]
   page.on('request', lambda r: requests.append(r.url))
   page.set_content(html,wait_until='load')
   if root4x:page.evaluate("document.documentElement.style.fontSize='64px'")
   page.wait_for_timeout(140)
   dom=page.evaluate('''() => {
    const r=document.querySelector('[data-fv-r377]');
    const rows=[...r.querySelectorAll('[data-fv-r377-record]')];
    return {records:rows.length,links:rows.map(x=>x.querySelector('[data-fv-r377-evidence]').href),
     drawers:r.querySelectorAll('[data-fv-r377-source]').length,
     oneCTA:[...r.querySelectorAll('[data-fv-free-cta]')].map(x=>x.href),
     hasPhotoMisattribution:r.textContent.includes('NOT an instrument chronology'),
     hasAfterFire:r.textContent.includes('not 102 ignitions during the January 1967 accident'),
     css:getComputedStyle(r).getPropertyValue('--rv-bg').trim(),
     overflowing:document.documentElement.scrollWidth>innerWidth+1,
     idList:[...document.querySelectorAll('[id]')].map(x=>x.id),
     rootFont:getComputedStyle(document.documentElement).fontSize,
     vitals:window.__fvR379Vitals||null};}''')
   checks={
      'six_records':dom['records']==6,'six_native_source_drawers':dom['drawers']==6,
      'primary_board_custody':dom['links'][:5]==[BOARD]*5,
      'later_testing_custody':dom['links'][5]==FLAM,
      'photo_not_telemetry':dom['hasPhotoMisattribution'],
      'later_tests_distinguished':dom['hasAfterFire'],
      'exactly_one_free_CTA':dom['oneCTA']==[FREE],
      'no_image_embed_or_paid_links':page.locator('img,iframe,video,[href*="checkout"],[href*="payhip"]').count()==0,
      'stylesheet_applied_in_fixture':dom['css']=='#0d1011',
      'no_horizontal_scroll':not dom['overflowing'],
      'unique_IDs':len(dom['idList'])==len(set(dom['idList'])),
      'no_network_requests_from_fixture':not requests,
   }
   first=page.locator('[data-fv-r377-source]').first
   first.locator('summary').focus()
   checks['keyboard_focus_visible']=first.locator('summary').evaluate('(e)=>getComputedStyle(e).outlineStyle')!='none'
   page.keyboard.press('Enter')
   checks['keyboard_open']=first.evaluate('(e)=>e.open')
   page.keyboard.press('Enter')
   checks['keyboard_close']=not first.evaluate('(e)=>e.open')
   first.locator('summary').click()
   checks['touch_or_pointer_open']=first.evaluate('(e)=>e.open')
   checks['touch_or_pointer_close']=not first.locator('summary').click() and not first.evaluate('(e)=>e.open')
   if root4x:checks['font_4x_confirmed']=dom['rootFont']=='64px'
   if forced:checks['forced_colors_active']=page.evaluate("matchMedia('(forced-colors: active)').matches")
   if reduced:checks['reduced_motion_active']=page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
   if nojs:checks['javascript_disabled']=True
   path=QA/(name+'.png');page.screenshot(path=str(path),full_page=not root4x,animations='disabled',timeout=12000)
   if name=='1440-desktop':
    page.emulate_media(media='print')
    checks['print_sources_visible']=page.locator('.fv-r377__print a:visible').count()==6
    checks['print_details_hidden']=page.locator('details:visible').count()==0
   result.append({'name':name,'viewport_width':width,'checks':checks,'pass':all(checks.values()),
                  'vitals_local_fixture_only':dom['vitals'],'screenshot':str(path.relative_to(ROOT))})
   ctx.close()
   print("FINISH",name,flush=True)
  browser.close()
 status='LOCAL_API_STUB_AND_REAL_CHROMIUM_FIXTURE_PASS_NOT_INSTALLED_STAGING' if all(t['pass'] for t in result) else 'FAIL'
 report={'status':status,'php_scenarios':SCENARIOS,'php_assertions':sum(x['passed'] for x in apis),
    'browser_contexts':len(result),'browser_assertions':sum(sum(x['checks'].values()) for x in result),
    'browser_possible_assertions':sum(len(x['checks']) for x in result),
    'browser':result,'CSS_sha256':hashlib.sha256(CSS.read_bytes()).hexdigest(),
    'boundary':'Chromium set_content PHP API-stub; no installed WordPress/Assembler, HTTP waterfall, real CSP, production CWV',
    'genuine_axe_core':'NOT_EXECUTED_PACKAGE_NOT_AVAILABLE',
    'screen_reader_and_native_zoom':'NOT_EXECUTED',
    'staging_HTTP_CSP_CI':'NOT_EXECUTED',
    'verified_sales_or_leads':'NOT_OBSERVABLE'}
 (QA/'results.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print(status,'PHP',report['php_assertions'],'Chromium',report['browser_assertions'],'/',report['browser_possible_assertions'],'contexts',len(result))
 return 0 if status.startswith('LOCAL_') else 1
if __name__=='__main__':sys.exit(main())
