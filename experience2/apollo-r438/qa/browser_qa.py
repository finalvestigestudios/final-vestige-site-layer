"""Playwright Chromium testing PHP-generated component offline, with honest lab-metric limitations."""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1];QA=HERE/'QA';SHOTS=QA/'screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php',str(HERE/'qa/fixture.php')]).decode('utf-8')
checks=0;failed=[];widths=[320,360,390,768,1024,1440,1920]
def ok(v,lab):
 global checks
 checks+=1
 if not v:failed.append(lab)
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in widths:
  context=browser.new_context(viewport={'width':width,'height':900})
  page=context.new_page();page.set_content(html,wait_until='load');page.wait_for_timeout(75)
  roots=page.locator('[data-r438-atlas-root]');ok(roots.count()==2,f'two atlas instances {width}')
  ok(page.locator('[data-r438-card]').count()==10,f'ten source records {width}')
  ok(page.locator('.fv-r429__cta').count()==2,f'one free CTA per instance {width}')
  ok(page.locator('[data-r438-card] a[href^="https://www.nasa.gov/"]').count()==10,f'NASA origin link per record {width}')
  ok(page.locator('[data-r438-pick]').count()==10,f'ten compare buttons {width}')
  ok(page.locator('[data-r438-card]:visible').count()==10,f'visible records {width}')
  ids=page.evaluate('[...document.querySelectorAll("[id]")].map(e=>e.id)');ok(len(ids)==len(set(ids)),f'no repeated IDs {width}')
  ok(not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),f'no overflow {width}')
  page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True,animations='disabled')
  one=roots.first;two=roots.nth(1)
  one.locator('[data-r438-pick="review-1967"]').click()
  ok('Choose 1 more' in one.locator('[role="status"]').inner_text(),f'1st select status {width}')
  one.locator('[data-r438-pick="training-1966"]').focus();page.keyboard.press('Enter')
  ok(one.locator('[data-r438-comparison]:visible').count()==1,f'keyboard comparison visible {width}')
  ok(one.locator('[data-r438-comparison] article').count()==2,f'two comparison columns {width}')
  ok('cannot prove' in one.locator('[data-r438-comparison]').inner_text().lower(),f'comparison limitations {width}')
  ok(two.locator('[data-r438-comparison]:visible').count()==0,f'other instance independent {width}')
  one.locator('[data-r438-comparison] button').click()
  ok(one.locator('[data-r438-comparison]:visible').count()==0,f'clear comparison {width}')
  context.close()
 context=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
 page=context.new_page();page.set_content(html,wait_until='load')
 ok(page.locator('[data-r438-card]:visible').count()==10,'no JS: full source inventory')
 ok(page.locator('[data-r438-pick]').count()==0,'no JS: no nonworking controls')
 ok(page.locator('[data-r438-card] summary').count()==10,'no JS: native source-rights disclosure')
 ok(page.locator('.fv-r429__cta').count()==2,'no JS: CTA survives')
 page.screenshot(path=str(SHOTS/'nojs.png'),full_page=True);context.close()
 context=browser.new_context(viewport={'width':390,'height':900},has_touch=True,is_mobile=True)
 page=context.new_page();page.set_content(html,wait_until='load')
 first=page.locator('[data-r438-atlas-root]').first
 first.locator('[data-r438-pick="review-1967"]').tap();first.locator('[data-r438-pick="aftermath-1967"]').tap()
 ok(first.locator('[data-r438-comparison] article').count()==2,'touch comparison')
 page.screenshot(path=str(SHOTS/'touch.png'),full_page=True,animations='disabled');context.close()
 for name,args in [('reduced',{'reduced_motion':'reduce'}),('forced',{'forced_colors':'active'})]:
  context=browser.new_context(viewport={'width':390,'height':900},**args);page=context.new_page();page.set_content(html,wait_until='load')
  ok(page.locator('[data-r438-card]:visible').count()==10,f'{name}: records visible')
  page.screenshot(path=str(SHOTS/f'{name}.png'),full_page=True,animations='disabled');context.close()
 context=browser.new_context(viewport={'width':390,'height':900});page=context.new_page();page.set_content(html,wait_until='load')
 page.evaluate('document.documentElement.style.fontSize="200%"');ok(not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'200% text: no overflow')
 page.screenshot(path=str(SHOTS/'zoom200.png'),full_page=True,animations='disabled')
 page.emulate_media(media='print')
 ok(page.locator('.fv-r438__print-only:visible').count()==10,'print rights remain visible')
 ok(page.locator('[data-r438-card]:visible').count()==10,'print retains all evidence')
 page.screenshot(path=str(SHOTS/'print.png'),full_page=True,animations='disabled');context.close()
 browser.close()
report={'kind':'OFFLINE_ACTUAL_CHROMIUM_PHP_RENDERED_SET_CONTENT_NOT_NAVIGATED_STAGING','status':'PASS' if not failed else 'FAIL','checks':checks,'failed':failed,'viewports':widths,'screenshots':len(list(SHOTS.glob('*.png'))),'axe':'NOT RUN; authentic axe-core unavailable','lcp_ms':None,'cls':None,'navigation':'ERR_BLOCKED_BY_ADMINISTRATOR (environment browser restriction); no valid LCP/CLS or Core Web Vitals','wordpress_staging':'NOT ACCESSED','field_p75':'NOT MEASURED'}
QA.mkdir(exist_ok=True);(QA/'browser.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report))
if failed:raise SystemExit(1)
