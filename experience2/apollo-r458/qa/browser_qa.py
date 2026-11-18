#!/usr/bin/env python3
"""Actual local PHP render + Chromium interactions via set_content: NOT navigated WordPress or LCP/CLS."""
import json,os,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SHOTS=ROOT/'QA/screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
source=subprocess.check_output(['php','-r',f'require "{ROOT}/apollo_editorial_reconciliation.php"; echo fv458_render();'],text=True)
source2=subprocess.check_output(['php','-r',f'require "{ROOT}/apollo_editorial_reconciliation.php"; echo fv458_render(),fv458_render();'],text=True)
passed=[];failed=[]
def check(name,fn):
    try:fn();passed.append(name)
    except Exception as e:failed.append({'case':name,'error':str(e)[:400]})
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
 for w in [320,360,390,768,1024,1440,1920]:
  for js in [False,True]:
   ctx=b.new_context(viewport={'width':w,'height':850},java_script_enabled=js)
   pg=ctx.new_page();pg.set_default_timeout(4000);pg.set_content(source,wait_until='load')
   def one_case(pg=pg,w=w,js=js):
    assert pg.locator('[data-fv458-card]').count()==6
    assert pg.locator('.fv458__claim-grid article').count()==3
    assert pg.locator('a[href*="the-hatch-opened-inward"]').count()==1
    assert pg.locator('[data-fv458-tools]').is_visible()==js
    assert pg.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),f'overflow {w}'
    assert pg.locator('img').count()==0
    assert pg.get_by_text('Editorial mismatch / review required').count()==1
    if w in (320,390,768,1440,1920):pg.screenshot(path=str(SHOTS/f'{w}-{"js" if js else "nojs"}.png'),full_page=True,animations='disabled',timeout=10000)
   check(f'{w}-{"js" if js else "nojs"}-render-overflow',one_case)
   if w==390 and js:
    def filters():
     for label,n in [('Cross-page review',1),('Unverified catalogue',1),('Recorded context',4),('All six',6)]:
      x=pg.get_by_role('button',name=label);x.click();assert pg.locator('[data-fv458-card]:visible').count()==n;assert x.get_attribute('aria-pressed')=='true'
    check('all-4-source-filters',filters)
    def keyboard():
     x=pg.get_by_role('button',name='Cross-page review');x.focus();pg.keyboard.press('Enter');assert pg.locator('[data-fv458-card]:visible').count()==1
    check('keyboard-Enter',keyboard)
    def details():
     pg.get_by_role('button',name='All six').click();x=pg.locator('.fv458__card details').first;x.locator('summary').click();assert x.get_attribute('open') is not None
    check('native-disclosure',details)
    def checklist():
     x=pg.locator('.fv458__review input').first;x.check();assert x.is_checked() and pg.locator('.fv458__review input').count()==4
    check('local-checklist-no-submission',checklist)
   ctx.close()
 ctx=b.new_context(is_mobile=True,has_touch=True,viewport={'width':390,'height':844});pg=ctx.new_page();pg.set_content(source)
 check('touch-filter',lambda:(pg.get_by_role('button',name='Unverified catalogue').tap(),pg.locator('[data-fv458-card]:visible').count()==1 or (_ for _ in ()).throw(AssertionError('touch failed'))));ctx.close()
 for mode,settings in [('reduced-motion',{'reduced_motion':'reduce'}),('forced-colors',{'forced_colors':'active'}),('200%-zoom',{'device_scale_factor':2})]:
  ctx=b.new_context(viewport={'width':390,'height':844},**settings);pg=ctx.new_page();pg.set_content(source)
  check(mode,lambda pg=pg: (pg.locator('[data-fv458-card]').count()==6 and pg.evaluate('document.documentElement.scrollWidth <= innerWidth+1')) or (_ for _ in ()).throw(AssertionError('layout')))
  ctx.close()
 ctx=b.new_context(viewport={'width':768,'height':850});pg=ctx.new_page();pg.set_content(source2)
 def multi():
  assert pg.locator('[data-fv458-root]').count()==2
  ids=pg.locator('[data-fv458-root]').evaluate_all('(els)=>els.map(el=>el.id)')
  assert len(set(ids))==2
  pg.locator('[data-fv458-root]').nth(0).get_by_role('button',name='Cross-page review').click()
  assert pg.locator('[data-fv458-root]').nth(0).locator('[data-fv458-card]:visible').count()==1
  assert pg.locator('[data-fv458-root]').nth(1).locator('[data-fv458-card]:visible').count()==6
 check('multiple-instance-scoping',multi);ctx.close()
 b.close()
report={'sprint':'R458','render':'Actual PHP shortcode markup via page.set_content (not network navigation)','passed':len(passed),'failed':failed,'names':passed,'screenshot_files':sorted(x.name for x in SHOTS.glob('*.png')),'axe_core':'HOLD_NOT_RUN','navigated_LCP':'HOLD_NOT_RUN','navigated_CLS':'HOLD_NOT_RUN','WordPress_staging':'HOLD_NOT_RUN','field_CWV':'HOLD_NOT_RUN'}
(ROOT/'QA/BROWSER_RESULTS.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'passed':len(passed),'failed':failed},indent=2))
if failed:raise SystemExit(1)
