#!/usr/bin/env python3
"""R459 independent print/source-hold regression (offline PHP-rendered markup only)."""
import json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SHOTS=ROOT/'QA'/'r459';SHOTS.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php','-r',f'require {json.dumps(str(ROOT/"apollo_rights_gallery.php"))}; echo fv457_render();'],text=True)
checks=[];fails=[]
def case(name,callback):
 try:callback();checks.append(name)
 except Exception as exc:fails.append({'name':name,'error':str(exc)[:550]})
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
 for w in (320,390,768,1440,1920):
  for js in (False,True):
   ctx=b.new_context(viewport={'width':w,'height':900},java_script_enabled=js)
   page=ctx.new_page();page.set_content(html,wait_until='load')
   def check():
    assert page.locator('.fv457__source-hold').count()==1
    assert page.locator('.fv457__source-hold').is_visible()
    assert page.locator('a[href*="the-hatch-opened-inward"]').count()==1
    assert page.locator('img,iframe,video').count()==0
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'overflow at {w}'
    assert page.locator('[data-fv457-controls]').is_visible()==js
    assert page.locator('a:has-text("CATALOGUE LINK UNVERIFIED")').count()==1
    assert page.locator('a:has-text("ID MAPPING UNVERIFIED")').count()==1
    assert page.locator('[data-fv457-card]').count()==6
    if w in (390,1440):page.screenshot(path=str(SHOTS/f'{w}-{ "js" if js else "nojs"}.png'),full_page=True,animations='disabled')
   case(f'{w}-{ "js" if js else "nojs"}-source-hold',check)
   if w==390 and js:
    def print_check():
     page.emulate_media(media='print')
     for selector in ('.fv457__card','.fv457__rights','.fv457__source-hold'):
      surface=page.locator(selector).first
      assert surface.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(255, 255, 255)',selector
      assert surface.evaluate('(e)=>getComputedStyle(e).color')=='rgb(0, 0, 0)',selector
     assert not page.locator('[data-fv457-controls]').is_visible()
     assert page.locator('.fv457__source-hold').is_visible()
     page.screenshot(path=str(SHOTS/'390-print.png'),full_page=True,animations='disabled')
     page.emulate_media(media='screen')
    case('print-white-cards-black-ink-and-visible-hold',print_check)
    def keyboard():
     button=page.get_by_role('button',name='Confirmed homepage (1)')
     button.focus();page.keyboard.press('Enter');assert button.get_attribute('aria-pressed')=='true'
     assert page.locator('[data-fv457-card]:visible').count()==1
     assert page.locator('.fv457__source-hold').is_visible()
    case('keyboard-filter-preserves-hold',keyboard)
   ctx.close()
 ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 page=ctx.new_page();page.set_content(html)
 def touch():
  page.get_by_role('button',name='Atlas chronology (3)').tap()
  assert page.locator('[data-fv457-card]:visible').count()==3
  assert page.locator('.fv457__source-hold').is_visible()
 case('touch-preserves-hold',touch);ctx.close()
 ctx=b.new_context(viewport={'width':390,'height':844},forced_colors='active',reduced_motion='reduce')
 page=ctx.new_page();page.set_content(html)
 case('forced-colors-reduced-motion-hold-visible',lambda: (page.locator('.fv457__source-hold').is_visible() or (_ for _ in ()).throw(AssertionError('hold missing'))));ctx.close()
 b.close()
report={'sprint':'R459','mode':'Chromium/PHP-rendered page.set_content; NOT navigated WordPress','passed':len(checks),'failed':fails,'cases':checks,'hosted_staging':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN','navigated_LCP_CLS':'HOLD_NOT_RUN','manual_AT':'HOLD_NOT_RUN','qualified_human_cohorts':'UNKNOWN','merchant_verified_sales':'UNKNOWN'}
(ROOT/'QA'/'R459_BROWSER_RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':len(checks),'failed':fails},indent=2))
if fails:raise SystemExit(1)
