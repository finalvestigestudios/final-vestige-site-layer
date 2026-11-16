#!/usr/bin/env python3
"""R398 exact-custody/local-prepaint Chromium QA. Not installed WP or HTTP acceptance."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'apollo-r398'; QA=HERE/'QA'; QA.mkdir(exist_ok=True)
BASE=ROOT/'apollo-r384/assets/gallery.css'; FIT=ROOT/'apollo-r395/assets/mobile-fit.css'
FIXTURE=ROOT/'apollo-r393/QA/local-php-fixture.html'
REVIEWED={BASE:'4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9',
 FIT:'93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756',
 FIXTURE:'5242da6c49b64d7f37484b6f5924042a69872073e4fd15d9a0ed694920bb11eb',
 ROOT/'apollo-r377/custody.json':'60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f'}
for path,expected in REVIEWED.items():
 if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
  raise SystemExit(f'HOLD: reviewed input altered: {path}')
sys.path[:0]=[str(ROOT/'apollo-r394/qa'),str(ROOT/'apollo-r393/qa'),str(ROOT/'apollo-r392/qa')]
from visibility_custody import verify_page as verify_visibility
from topology import verify_page as verify_topology
fixture=FIXTURE.read_text(); fit=FIT.read_text()
# The R393 fixture already includes exact R384 CSS in <head>; add fit before any body.
# This is NOT a browser network or WordPress wp_head proof.
perf="""<script>window.__fv398={lcp:null,cls:0};try{
 new PerformanceObserver(l=>{for(let e of l.getEntries())if(!e.hadRecentInput)window.__fv398.cls+=e.value}).observe({type:'layout-shift',buffered:true});
 new PerformanceObserver(l=>{for(let e of l.getEntries())window.__fv398.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
}catch(e){window.__fv398.error=String(e)}</script>"""
def markup(root4=False):
 insert=("<style>html{font-size:400%!important}</style>" if root4 else '')
 insert+='<style id="r398-canonical-prepaint" media="screen">'+fit+'</style>'
 return fixture.replace('</head>',insert+'</head>',1).replace('<head>','<head>'+perf,1)
contexts=[('320',320,780,False,False,'no-preference','none',False),
 ('360',360,780,False,False,'no-preference','none',False),
 ('390',390,850,False,False,'no-preference','none',False),
 ('768',768,950,False,False,'no-preference','none',False),
 ('1024',1024,900,False,False,'no-preference','none',False),
 ('1440',1440,900,False,False,'no-preference','none',False),
 ('1920',1920,1080,False,False,'no-preference','none',False),
 ('320-nojs',320,800,False,True,'no-preference','none',False),
 ('390-touch',390,850,True,False,'no-preference','none',False),
 ('390-reduced',390,850,False,False,'reduce','none',False),
 ('320-forced',320,850,False,False,'no-preference','active',False),
 ('320-text4x',320,900,False,False,'no-preference','none',True),
 ('390-text4x',390,900,False,False,'no-preference','none',True)]
report={'scope':'OFFLINE_CHROMIUM_PAGE_SET_CONTENT_NOT_STAGING','status':'HOLD',
 'source_sha256':{str(path.relative_to(ROOT)):sha for path,sha in REVIEWED.items()},
 'contexts':[],'tests':0,'axe_core':'NOT_RUN_NO_PINNED_GENUINE_BUILD',
 'installed_wordpress':'NOT_RUN','browser_network':'NOT_RUN_BLOCKED_BY_ADMINISTRATOR',
 'native_400_percent_zoom':'NOT_RUN_ROOT_FONT_ONLY','release_allowed':False}
def ok(condition,reason):
 report['tests']+=1
 if not condition: raise AssertionError(reason)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 try:
  for name,w,h,touch,nojs,motion,colors,root4 in contexts:
   ctx=b.new_context(viewport={'width':w,'height':h},has_touch=touch,
      java_script_enabled=not nojs,reduced_motion=motion,forced_colors=colors)
   pg=ctx.new_page();pg.set_content(markup(root4),wait_until='load');pg.wait_for_timeout(160)
   a,err=verify_visibility(pg);ok(a,f'{name}: visibility/provenance: {err}')
   t,toperr=verify_topology(pg);ok(t,f'{name}: source and chronology: {toperr}')
   ok(pg.locator('.fv-r384__card').count()==6,f'{name}: six questions')
   ok(pg.locator('[data-fv-r384-publication]').count()==2,f'{name}: two publications')
   ok(pg.locator('.fv-r384__rail a').count()==3,f'{name}: three stages')
   ok(pg.locator('[data-fv-free-cta]').count()==1,f'{name}: single free CTA')
   ok(pg.locator('head #r398-canonical-prepaint').count()==1,f'{name}: pre-head CSS')
   overflow=pg.evaluate('document.documentElement.scrollWidth-innerWidth')
   ok(overflow<=1,f'{name}: overflow: {overflow}px')
   ok(pg.locator('details').count()==6,f'{name}: six native disclosures')
   first=pg.locator('details summary').first;first.focus();pg.keyboard.press('Enter')
   ok(pg.locator('details').first.get_attribute('open') is not None,f'{name}: keyboard open')
   pg.keyboard.press('Enter');ok(pg.locator('details').first.get_attribute('open') is None,f'{name}: keyboard close')
   if touch:
    first.tap();ok(pg.locator('details').first.get_attribute('open') is not None,f'{name}: touch')
   if root4:
    fs=float(pg.evaluate('getComputedStyle(document.documentElement).fontSize')[:-2])
    ok(fs>=60,f'{name}: must preserve enlarged text')
   # Navigate to in-page NASA record by HTML link rather than JavaScript.
   jump=pg.locator('.fv-r384__source-index a[href^="#"]').last
   target=jump.get_attribute('href');jump.click()
   ok(pg.evaluate('location.hash')==target,f'{name}: in-document source navigation')
   ok(pg.locator(target).count()==1,f'{name}: target present')
   if name in ('320','1440','320-nojs','320-text4x','390-touch'):
    pg.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
   perfdata=pg.evaluate('window.__fv398') if not nojs else None
   if perfdata:
    ok(perfdata['cls'] <= 0.1,f'{name}: lab CLS {perfdata["cls"]}')
   report['contexts'].append({'name':name,'width':w,'nojs':nojs,'text4x':root4,
      'overflow_px':max(overflow,0),'fixture_cls':None if nojs else perfdata['cls'],
      'fixture_lcp_ms':None if nojs else perfdata['lcp']})
   ctx.close()
  # A print-only semantic QA: all six custody mirror records visible, source
  # links remain present, closed/open drawers are suppressed, and screen-fit CSS
  # is not applicable to print. PDF engine/print rendering remains separate.
  ctx=b.new_context(viewport={'width':768,'height':1000});pg=ctx.new_page()
  pg.set_content(markup(),wait_until='load');pg.emulate_media(media='print')
  ok(pg.locator('.fv-r384__print-custody').count()==6,'print: mirrors six')
  for item in pg.locator('.fv-r384__print-custody').all():
   ok(item.is_visible(),'print: custody mirror visible')
  ok(not pg.locator('.fv-r384__drawer').first.is_visible(),'print: drawers suppressed')
  ok(pg.locator('[data-fv-r384-nasa]').count()==6,'print: six sources')
  ok(pg.locator('[data-fv-r384-publication]').count()==2,'print: two publisher links')
  ok(pg.locator('[data-fv-free-cta]').count()==1,'print: free CTA')
  ctx.close()
 finally:b.close()
report['status']='PASS_LOCAL_FIXTURE_ONLY'
(QA/'browser-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':report['status'],'assertions':report['tests'],
 'contexts':len(report['contexts']),
 'max_lab_cls':max((x['fixture_cls'] or 0) for x in report['contexts']),
 'observed_lcp_ms':[x['fixture_lcp_ms'] for x in report['contexts'] if x['fixture_lcp_ms'] is not None]}))
