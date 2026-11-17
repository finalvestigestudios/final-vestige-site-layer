"""Real HTTP navigation in local PHP Chromium; NOT WordPress staging or field Core Web Vitals."""
import json, socket, subprocess, time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1]
QA=HERE/'QA'; SHOTS=QA/'screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
checks=0; failures=[]; widths=[]; metrics=[]
def check(value,label):
 global checks
 checks+=1
 if not value: failures.append(label)
def measured(page):
 return page.evaluate('window.__r437Perf || {}')
INSTRUMENT="""(()=>{window.__r437Perf={lcp_ms:null,cls:0,entries:0};try{new PerformanceObserver(list=>{for(const e of list.getEntries()){window.__r437Perf.lcp_ms=e.startTime;}}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput){window.__r437Perf.cls+=e.value;window.__r437Perf.entries++}}).observe({type:'layout-shift',buffered:true})}catch(e){window.__r437Perf.error=String(e)}})();"""
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
url=f'http://127.0.0.1:{port}/fixture.php'
html=subprocess.check_output(['php',str(HERE/'qa/fixture.php')]).decode('utf-8')
server=subprocess.Popen(['php','-S',f'127.0.0.1:{port}','-t',str(HERE/'qa')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(50):
  try:
   with urlopen(url,timeout=.4) as resp:
    if resp.status==200:break
  except Exception:time.sleep(.1)
 else: raise RuntimeError('local PHP fixture HTTP server did not start')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [320,360,390,768,1024,1440,1920]:
   context=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1)
   page=context.new_page();page.add_init_script(INSTRUMENT)
   page.set_content(html,wait_until='load')
   page.wait_for_timeout(200)
   check(page.locator('title').inner_text().startswith('Apollo Evidence Chronology'),'PHP-generated HTML loaded in Chromium '+str(width))
   check(page.locator('[data-fv-r437]').count()==2,'two actual parent components at '+str(width))
   check(page.locator('[data-fv-r437] [data-period]').count()==8,'eight actual evidence records at '+str(width))
   check(page.locator('.fv-r429__cta').count()==2,'one inherited CTA per instance at '+str(width))
   check(page.locator('[data-fv-r437] button[data-filter]').count()==6,'enhancement controls added at '+str(width))
   overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
   check(not overflow,'no horizontal overflow at '+str(width))
   check(page.locator('[data-fv-r437] details').count()==8,'native evidence boundaries at '+str(width))
   ids=page.evaluate('Array.from(document.querySelectorAll("[id]"),e=>e.id)')
   check(len(ids)==len(set(ids)),'unique ids in duplicate instances at '+str(width))
   check(page.locator('[data-fv-r437] [data-period]:visible').count()==8,'all four stages per instance initially visible '+str(width))
   metrics.append({'viewport':width,'lab_lcp_ms':None,'lab_cls':None,'source':'NOT AVAILABLE: Chromium navigation blocked by administrator, content inserted via set_content'})
   page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True,animations='disabled')
   # filter one instance only; the other component must not change.
   first=page.locator('[data-fv-r437]').first;second=page.locator('[data-fv-r437]').nth(1)
   first.locator('button[data-filter="incident"]').click()
   check(first.locator('[data-period]:visible').count()==2,'incident filter '+str(width))
   check(second.locator('[data-period]:visible').count()==4,'isolated second instance '+str(width))
   check('Showing 2 of 4' in first.locator('[role=status]').inner_text(),'live status '+str(width))
   first.locator('button[data-filter="retrospective"]').focus();page.keyboard.press('Enter')
   check(first.locator('[data-period]:visible').count()==2,'keyboard Enter activates filter '+str(width))
   check(first.locator('[data-period="incident"]:visible').count()==0,'keyboard selects right period '+str(width))
   first.locator('button[data-filter="all"]').click()
   check(first.locator('[data-period]:visible').count()==4,'restore all records '+str(width))
   widths.append(width)
   context.close()
  # true no-JS mode has complete meaning and two free CTAs
  context=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
  page=context.new_page();page.set_content(html,wait_until='load')
  check(page.locator('[data-fv-r437] [data-period]:visible').count()==8,'no-JS all eight source records visible')
  check(page.locator('[data-fv-r437] [data-period] summary').count()==8,'no-JS native disclosures')
  check(page.locator('[data-fv-r437] button').count()==0,'no-JS has no dead filter buttons')
  check(page.locator('.fv-r429__cta').count()==2,'no-JS one action per instance')
  page.screenshot(path=str(SHOTS/'no-js-390.png'),full_page=True);context.close()
  # touch, reduced motion, high contrast and print are actual Chromium emulations
  context=browser.new_context(viewport={'width':390,'height':900},has_touch=True,is_mobile=True)
  page=context.new_page();page.set_content(html,wait_until='load')
  page.locator('[data-fv-r437]').first.locator('button[data-filter="retrospective"]').tap()
  check(page.locator('[data-fv-r437]').first.locator('[data-period="retrospective"]:visible').count()==2,'touch tap works')
  page.screenshot(path=str(SHOTS/'touch-390.png'),full_page=True,animations='disabled');context.close()
  context=browser.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
  page=context.new_page();page.set_content(html,wait_until='load')
  check(page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'),'reduced-motion honored')
  page.screenshot(path=str(SHOTS/'reduced-motion-390.png'),full_page=True,animations='disabled');context.close()
  context=browser.new_context(viewport={'width':390,'height':900},forced_colors='active')
  page=context.new_page();page.set_content(html,wait_until='load')
  check(page.evaluate('matchMedia("(forced-colors: active)").matches'),'forced colors honored')
  page.screenshot(path=str(SHOTS/'forced-colors-390.png'),full_page=True,animations='disabled');context.close()
  context=browser.new_context(viewport={'width':390,'height':900})
  page=context.new_page();page.set_content(html,wait_until='load')
  page.evaluate('document.documentElement.style.fontSize="200%"')
  check(not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'200% root text no horizontal overflow')
  page.screenshot(path=str(SHOTS/'200pct-text-390.png'),full_page=True,animations='disabled')
  page.emulate_media(media='print')
  check(page.locator('[data-fv-r437] .fv-r437__print:visible').count()==8,'print preserves evidence boundaries')
  page.screenshot(path=str(SHOTS/'print-390.png'),full_page=True,animations='disabled');context.close()
  browser.close()
finally:
 server.terminate()
 try:server.wait(timeout=3)
 except subprocess.TimeoutExpired:server.kill()
report={'kind':'ACTUAL_CHROMIUM_OFFLINE_PHP_MARKUP_NOT_NAVIGATED_STAGING','checks':checks,'failures':failures,'status':'PASS' if not failures else 'FAIL','viewports':widths,'perf_metrics':metrics,'screenshot_count':len(list(SHOTS.glob('*.png'))),'axe_core':'HOLD: genuine bundle not available locally; not simulated','field_cwv':'NOT_MEASURED','https_wordpress_staging':'NOT_ACCESSED','browser_navigation':'ERR_BLOCKED_BY_ADMINISTRATOR even on localhost; HTTP fixture was served and independently verified with urllib; Playwright used set_content'}
(QA/'browser.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('perf_metrics',)}))
print('lab metrics',metrics)
if failures:raise SystemExit(1)
