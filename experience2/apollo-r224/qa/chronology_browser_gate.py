#!/usr/bin/env python3
"""R224 exact-source ChronologyRail acceptance; offline Chromium fixture, NOT WordPress or axe-core."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
DATES=['1966-10-18','1967-01-03','1967-01-27','1967-01-28','1967-04']
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
PIN='28a393405a86742b190cd7af83518d9d1eac9b3b68882176cc5e7726a5064693'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p,m):
 if not p:raise AssertionError(m)
def run(parent,builder,out):
 out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('r224_build',builder);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 d=out/'dist';check(mod.create(parent,d)==PIN,'R224 exact build digest drift')
 m=json.loads((d/'manifest.json').read_text())
 for name,h in m['files'].items():check(sha(d/name)==h,'Artifact digest: '+name)
 php=d/'fv-ex2-apollo-r224.php';shim=d/'wp-render-shim-r224.php'
 check('No syntax errors' in subprocess.check_output(['php','-l',str(php)],text=True),'PHP syntax')
 def render(mode):return json.loads(subprocess.check_output(['php',str(shim),str(php),mode],text=True))
 normal=render('normal');check(not normal['fallback'] and render('late')['fallback'],'Fallback/normal regression')
 for name in ['chronology-report-custody.json','source-url-crosswalk.json','templates/atlas-fragment.html']:
  f=d/name;b=f.read_bytes()
  try:f.write_bytes(b+b' ');check(render('normal')['fallback'] and FREE in render('normal')['html'],'Fail-open regression '+name)
  finally:f.write_bytes(b)
 html=normal['html'];css=(d/'assets/atlas-scoped.css').read_text()
 doc='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
 shots=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [320,360,390,768,1024,1440,1920]:
   for js in (False,True):
    ctx=browser.new_context(viewport={'width':width,'height':844},is_mobile=width<=390,has_touch=width<=390,java_script_enabled=js,reduced_motion='reduce')
    page=ctx.new_page();page.set_content(doc)
    a=page.evaluate('''() => {let r=document.querySelector('.fv-apollo-atlas');let li=r.querySelector('li[data-evidence-kind="retrospective-report"]');let ids=[...r.querySelectorAll('[id]')].map(x=>x.id);let report=li.querySelector('.fv-apollo-rail-report-link');return {dates:[...r.querySelectorAll('ol.rail>li>time')].map(t=>t.dateTime),source:report.href,sourceHeight:report.getBoundingClientRect().height,idsOkay:ids.length===new Set(ids).size,limits:li.textContent.includes('no single ignition source was conclusively identified'),ctas:[...r.querySelectorAll('a.cta')].map(x=>x.href),overflow:document.documentElement.scrollWidth>innerWidth+2,active:r.querySelectorAll('script,form,iframe').length,geo:r.querySelectorAll('[data-lat],[data-lon],.map-pin').length}}''')
    check(a['dates']==DATES and a['source']==NASA and a['sourceHeight']>=44 and a['limits'],'Historical source and dates')
    check(a['idsOkay'] and a['ctas']==[FREE] and not a['overflow'] and not a['active'] and not a['geo'],'Integrity and conversion')
    summary=page.locator('#fv-apollo-source-drawer summary');summary.scroll_into_view_if_needed()
    if width<=390:
     b=summary.bounding_box();page.touchscreen.tap(b['x']+20,b['y']+b['height']/2)
    else:summary.focus();page.keyboard.press('Enter')
    check(page.locator('#fv-apollo-source-drawer').evaluate('x=>x.open'),'Native summary fails')
    link=page.locator('li[data-evidence-kind="retrospective-report"] a[href="#fv-apollo-source-drawer"]');link.click()
    check(page.evaluate('location.hash')=='#fv-apollo-source-drawer','Context navigation')
    page.evaluate('document.querySelector(".fv-apollo-atlas").style.zoom="2"')
    check(not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),'2x CSS zoom overflow')
    page.evaluate('document.querySelector(".fv-apollo-atlas").style.zoom="1"')
    page.emulate_media(media='print');check(page.locator('li[data-evidence-kind="retrospective-report"]').is_visible(),'Print missing report')
    page.emulate_media(media='screen');page.locator('li[data-evidence-kind="retrospective-report"]').scroll_into_view_if_needed()
    path=out/f'{width}-{int(js)}.png';page.screenshot(path=str(path),animations='disabled')
    shots.append({'width':width,'js':js,'sha256':sha(path)});ctx.close()
  browser.close()
 (out/'receipt.json').write_text(json.dumps({'status':'LOCAL_PASS_STAGING_HOLD','manifest_sha256':PIN,'browser_contexts':len(shots),'screenshots':shots,'axe':'NOT_EXECUTED','wordpress':'NOT_TESTED','live':'NO','commercial':'HOLD'},indent=2,sort_keys=True)+'\n')
 print('R224 PASS',len(shots),'real Chromium contexts',PIN)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--builder',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
 q=ap.parse_args();run(q.parent,q.builder,q.out)
