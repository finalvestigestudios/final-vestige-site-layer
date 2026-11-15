#!/usr/bin/env python3
"""R394 real Playwright Chromium fixture acceptance; NEVER installed staging proof."""
import hashlib
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from visibility_custody import verify_page, VISIBILITY_JS, evaluate_visibility, REQUIRED_KEYS
from topology import verify_page as inherited_verify

HERE=Path(__file__).resolve().parents[1]
FIXTURE=HERE.parents[0]/'apollo-r393'/'QA'/'local-php-fixture.html'
# Path.parents[0] is experience2 when HERE is experience2/apollo-r394.
QA=HERE/'QA'; QA.mkdir(parents=True,exist_ok=True)
if not FIXTURE.is_file(): raise SystemExit('HARD HOLD: real reviewed R393 PHP fixture not found')
html=FIXTURE.read_text(encoding='utf-8')
report={'kind':'ACTUAL_CHROMIUM_LOCAL_PHP_FIXTURE_NOT_INSTALLED_STAGING',
 'fixture_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
 'assertions':0,'contexts':[],'tamper_proofs':[],
 'network_browser':'PAGE_SET_CONTENT_ONLY: actual local HTTP browser navigation blocked by runtime',
 'axe_core':'NOT_RUN: genuine reviewed build unavailable', 'release_allowed':False}

def check(condition,why):
    report['assertions']+=1
    if not condition:raise AssertionError(why)

contexts=[('320-mobile',320,780,True,False,'no-preference','none',False),
 ('390-mobile',390,850,True,False,'no-preference','none',False),
 ('768-tablet',768,900,False,False,'no-preference','none',False),
 ('1440-desktop',1440,900,False,False,'no-preference','none',False),
 ('1920-wide',1920,1080,False,False,'no-preference','none',False),
 ('320-nojs',320,800,True,True,'no-preference','none',False),
 ('390-touch',390,850,True,False,'no-preference','none',True),
 ('390-reduced',390,850,True,False,'reduce','none',False),
 ('320-forced',320,850,True,False,'no-preference','active',False),
 ('320-root4x',320,900,True,False,'no-preference','none',False)]

attacks=[
 ('gallery_fully_transparent',"document.querySelector('.fv-r384').style.opacity='0'",'gallery_visually_unavailable'),
 ('source_index_transparent',"document.querySelector('.fv-r384__source-index').style.opacity='0'",'source_index_visually_unavailable'),
 ('publisher_a_transparent',"document.querySelector('[data-fv-r384-publication=A]').style.opacity='0'",'publisher_1_visually_unavailable'),
 ('source_6_transparent',"document.querySelectorAll('[data-fv-r384-nasa]')[5].style.opacity='0'",'nasa_6_visually_unavailable'),
 ('cta_transparent',"document.querySelector('[data-fv-free-cta]').style.opacity='0'",'free_cta_visually_unavailable'),
 ('source_pointer_blocked',"document.querySelector('[data-fv-r384-nasa]').style.pointerEvents='none'",'nasa_1_inoperable'),
 ('publisher_keyboard_blocked',"document.querySelector('[data-fv-r384-publication]').tabIndex=-1",'publisher_1_inoperable'),
 ('cta_keyboard_blocked',"document.querySelector('[data-fv-free-cta]').tabIndex=-1",'free_cta_inoperable'),
 ('cta_aria_disabled',"document.querySelector('[data-fv-free-cta]').setAttribute('aria-disabled','true')",'free_cta_inoperable'),
 ('cta_clipped',"document.querySelector('[data-fv-free-cta]').style.clipPath='inset(100%)'",'free_cta_visually_unavailable'),
 ('source_index_offscreen',"document.querySelector('.fv-r384__source-index').style.transform='translateX(-100000px)'",'source_index_visually_unavailable'),
 ('hidden_link_text',"document.querySelector('.fv-r384__source-index ol a').style.fontSize='0'",'index_link_1_visually_unavailable'),
]

with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 try:
  for name,w,h,touch,nojs,motion,forced,phone in contexts:
   ctx=b.new_context(viewport={'width':w,'height':h},has_touch=touch or phone,
       is_mobile=phone,java_script_enabled=not nojs,reduced_motion=motion,forced_colors=forced)
   page=ctx.new_page();page.set_content(html,wait_until='load')
   if name=='320-root4x':
    page.add_style_tag(content='html{font-size:400%!important}')
    report['root4x_overflow_before_px']=page.evaluate('document.documentElement.scrollWidth-innerWidth')
    check(report['root4x_overflow_before_px']>0,'must reproduce previously missed 400%-font overflow')
    page.screenshot(path=str(QA/'320-root4x-before.png'),full_page=True,animations='disabled')
    page.add_style_tag(path=str(HERE/'assets'/'root4x-overflow-candidate.css'))
    report['root4x_overflow_after_px']=page.evaluate('document.documentElement.scrollWidth-innerWidth')
   page.evaluate("""() => {window.__fvR394={lcp:null,cls:0}; try {
     new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvR394.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
     new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvR394.cls+=e.value}).observe({type:'layout-shift',buffered:true});
     } catch(e){window.__fvR394.error=String(e)} }""")
   page.wait_for_timeout(80)
   vitals=page.evaluate('window.__fvR394')
   inherited_ok,inherited_codes=inherited_verify(page)
   ok,codes=verify_page(page)
   check(ok and inherited_ok,name+': sealed NASA semantic+visibility gate '+str(codes+inherited_codes))
   checks=page.evaluate(VISIBILITY_JS)['checks']
   check([c['key'] for c in checks]==list(REQUIRED_KEYS),name+': source/link inventory')
   check(all(c['present'] and c['visible'] and c['clickable'] for c in checks),name+': perceived accessible controls')
   check(not page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'),name+': horizontal overflow')
   check(page.locator('details').count()==6,name+': native no-JS drawers')
   check(page.locator('[data-fv-free-cta]').count()==1,name+': one free CTA')
   if name in ('320-mobile','1440-desktop','320-nojs','320-root4x'):
    page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
   report['contexts'].append({'name':name,'width':w,'nojs':nojs,'semantic_pass':inherited_ok,
      'visibility_pass':ok,'control_count':len(checks),'horizontal_overflow':False,'fixture_lcp_ms':vitals.get('lcp'),'fixture_cls':vitals.get('cls')})
   ctx.close()
  # Every case must demonstrate an actual inherited acceptance bypass, then a new rejection.
  ctx=b.new_context(viewport={'width':390,'height':850})
  page=ctx.new_page()
  for name,script,expected in attacks:
   page.set_content(html,wait_until='load');page.evaluate(script)
   old_ok,old_codes=inherited_verify(page)
   new_ok,new_codes=verify_page(page)
   check(old_ok,name+': should reproduce R393 bypass '+str(old_codes))
   check(not new_ok and expected in new_codes,name+': should be R394 BLOCK '+str(new_codes))
   report['tamper_proofs'].append({'name':name,'R393_accepted':old_ok,'R394_rejected':not new_ok,'reason':expected})
  ctx.close()
 finally:b.close()
report['status']='LOCAL_QA_PASSED_NOT_STAGING';
(QA/'visibility-results.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':report['status'],'assertions':report['assertions'],
 'contexts':len(report['contexts']),'R393_bypasses_blocked':len(report['tamper_proofs'])},indent=2))
