"""Actual Chromium rendering of the PHP-generated fixture offline. NOT network navigation, axe or CWV."""
from pathlib import Path
import json, subprocess
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1]
QA=HERE/'QA'; (QA/'screenshots').mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php',str(HERE/'qa/fixture.php')]); fixture=QA/'fixture.html';fixture.write_bytes(html)
checks=0

def ok(value,reason):
 global checks
 assert value,reason
 checks+=1

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path="/usr/bin/chromium",args=["--no-sandbox"])
 for width in (320,360,390,768,1024,1440,1920):
  page=browser.new_page(viewport={'width':width,'height':840},device_scale_factor=1)
  page.set_content(html.decode(),wait_until='load')
  ok(page.locator('[data-fv-r435]').count()==2,f'component loaded {width}')
  ok(page.locator('.fv-r429__cta').count()==2,'only two paid-free single CTAs')
  ok(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),f'no horizontal overflow {width}')
  ok(page.locator('img').count()==0,'no embedded NASA image')
  g=page.locator('[data-fv-r435-catalog]').first
  ok(not g.evaluate('(e)=>e.open'),'source gallery progressive disclosed')
  g.locator('summary').first.click()
  ok(g.evaluate('(e)=>e.open'),'click opens source catalog')
  ok(g.locator('.fv-r435__plate').count()==6,'six catalog records')
  ok(g.locator('.fv-r435__drawer').count()==6,'six native source drawers')
  ok(g.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6,'only verified catalog destinations')
  p=QA/'screenshots'/f'{width}.png';page.screenshot(path=str(p),full_page=True)
  page.close()
 # Keyboard native source disclosure
 page=browser.new_page(viewport={'width':390,'height':800})
 page.set_content(html.decode())
 summary=page.locator('[data-fv-r435-catalog] summary').first
 summary.focus();page.keyboard.press('Enter')
 ok(page.locator('[data-fv-r435-catalog]').first.evaluate('(e)=>e.open'),'keyboard enter opens')
 drawer=page.locator('.fv-r435__drawer').first;drawer.locator('summary').click()
 ok(drawer.evaluate('(e)=>e.open'),'nested source drawer')
 page.screenshot(path=str(QA/'screenshots/keyboard.png'),full_page=True);page.close()
 # Mobile touch
 page=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
 page.set_content(html.decode());page.locator('[data-fv-r435-catalog] summary').first.tap()
 ok(page.locator('[data-fv-r435-catalog]').first.evaluate('(e)=>e.open'),'touch opens catalog')
 page.screenshot(path=str(QA/'screenshots/touch.png'),full_page=True);page.close()
 # Disabled JS: all relevant content remains available through native details and links
 page=browser.new_page(viewport={'width':390,'height':844},java_script_enabled=False)
 page.set_content(html.decode());page.locator('[data-fv-r435-catalog] summary').first.click()
 ok(page.locator('.fv-r435__plate').count()==12,'no-JS source gallery')
 ok(page.locator('.fv-r429__cta').count()==2,'no-JS free article CTA')
 page.screenshot(path=str(QA/'screenshots/no-js.png'),full_page=True);page.close()
 # Reduced motion, forced colors, zoom
 for name,kwargs in [('reduced-motion',{'reduced_motion':'reduce'}),('forced-colors',{'forced_colors':'active'})]:
  page=browser.new_page(viewport={'width':390,'height':844},**kwargs)
  page.set_content(html.decode());page.locator('[data-fv-r435-catalog] summary').first.click()
  ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),name+' overflow')
  page.screenshot(path=str(QA/f'screenshots/{name}.png'),full_page=True);page.close()
 page=browser.new_page(viewport={'width':390,'height':844})
 page.set_content(html.decode());page.evaluate('document.documentElement.style.fontSize="32px"')
 page.locator('[data-fv-r435-catalog] summary').first.click()
 ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'200%-font no overflow')
 page.screenshot(path=str(QA/'screenshots/200-percent-text.png'),full_page=True);page.close()
 # Print media independent of JS
 page=browser.new_page(viewport={'width':768,'height':1000});page.set_content(html.decode())
 page.emulate_media(media='print');ok(page.locator('summary').count()>=12,'print-native source list retained')
 page.screenshot(path=str(QA/'screenshots/print.png'),full_page=True);page.close()
 # HTTP/file navigation is sandbox-blocked; neither LCP nor CLS can be reported from set_content.
 perf={'lcp':'NOT_MEASURED','cls':'NOT_MEASURED','reason':'Page.goto blocked by administrator; set_content is offline, no navigation'}
 browser.close()
report={'status':'PASS_OFFLINE_CHROMIUM','assertions':checks,'screenshots':len(list((QA/'screenshots').glob('*.png'))),'local_file_navigation_perf':perf,'real_wordpress_staging':'NOT_TESTED','axe_core':'NOT_TESTED','field_cwv':'NOT_COMPUTABLE'}
(QA/'browser.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print('PASS',checks,'offline Chromium assertions,',report['screenshots'],'screenshots; set_content offline only')
print('Local file laboratory LCP/CLS observer:',perf)
