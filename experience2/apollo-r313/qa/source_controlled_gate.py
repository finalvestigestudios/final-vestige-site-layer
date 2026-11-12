#!/usr/bin/env python3
"""R313 real offline Chromium + PHP click-attribution contract (staging, not live)."""
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlsplit
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
JS=ROOT/'apollo-r281/assets/apollo-cache-continuation.js'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
FIX=ROOT/'apollo-r301/qa/local_http_fixture.php'
OUT=ROOT/'apollo-r313/QA';OUT.mkdir(parents=True,exist_ok=True)
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def render(query=''):
 q='instances=2&queue=0'+('&'+query if query else '')
 return subprocess.check_output(['php','-r','parse_str($argv[2],$_GET);include $argv[1];',str(FIX),q],text=True)
subprocess.run(['php','-l',str(PHP)],check=True)
subprocess.run(['node','--check',str(JS)],check=True)
valid='utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo1_pilot_2026_11&utm_content=apollo1_yt_alpha001'
invalid=[valid+'&utm_source=tiktok',valid.replace('youtube','tiktok'),valid.replace('alpha001','visitor%40example.com'),valid.replace('organic_social','paid_social'),valid.replace('2026_11','2026_13')]
base=render()
for query in [valid,*invalid,'utm_content=private']:assert render(query)==base
soup=BeautifulSoup(base,'lxml')
assert len(soup.select('section.fv-r281[data-fv-client-campaign="staging-click-only"]'))==2
assert len(soup.select('li[data-fv-evidence-role="documented-textual-claim"]'))==6
assert len(soup.select('li[data-fv-evidence-role="contextual-media-only"]'))==8
assert all(a.get('href')==FREE for a in soup.select('a[data-fv-cta]'))
assert not soup.select('img,script,iframe')
js=JS.read_text();css=CSS.read_text()
for token in ['fetch(','sendBeacon','localStorage','sessionStorage','document.cookie','XMLHttpRequest']:
 assert token not in js
contexts=0; keyboard=0; tagged=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [320,360,390,768,1440,1920]:
  for enabled in [False,True]:
   ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,has_touch=width<=390,reduced_motion='reduce',forced_colors='active' if width==768 else 'none')
   page=ctx.new_page();page.set_default_timeout(10000)
   page.goto('about:blank?'+valid)
   page.set_content(base.replace('</head>','<style>'+css+'</style></head>'))
   if enabled:
    page.add_script_tag(content=js)
    page.evaluate('''() => document.addEventListener('click',e=>{if(e.target.closest('a[data-fv-cta]'))e.preventDefault()})''')
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
   links=page.locator('section.fv-r281 a[data-fv-cta]');assert links.count()==2
   if enabled:
    if width<=390:links.first.tap()
    else:links.first.focus();page.keyboard.press('Enter');keyboard+=1
    actual=dict(parse_qsl(urlsplit(links.first.get_attribute('href')).query))
    assert actual==dict(parse_qsl(valid));tagged+=1
    assert links.nth(1).get_attribute('href')==FREE
   else:assert all(x==FREE for x in [links.nth(i).get_attribute('href') for i in [0,1]])
   if width in [390,1440] and not enabled:page.screenshot(path=str(OUT/f'r313-{width}-nojs.png'),full_page=True,animations='disabled')
   contexts+=1;ctx.close()
 # Reuse identical PHP body for two visitors, but stamp labels on user activation only.
 for name,query in [('A',valid),('B','utm_source=tiktok&utm_medium=organic_social&utm_campaign=apollo1_pilot_2026_11&utm_content=apollo1_tt_short001')]:
  page=browser.new_page();page.goto('about:blank?'+query);page.set_content(base)
  page.add_script_tag(content=js)
  page.evaluate('''() => document.addEventListener('click',e=>{if(e.target.closest('a[data-fv-cta]'))e.preventDefault()})''')
  a=page.locator('section.fv-r281 a[data-fv-cta]').first;a.focus();page.keyboard.press('Enter')
  assert dict(parse_qsl(urlsplit(a.get_attribute('href')).query))['utm_content']==dict(parse_qsl(query))['utm_content']
  page.close()
 # Duplicate, mismatched and PII-like tags must not be forwarded.
 for query in invalid:
  page=browser.new_page();page.goto('about:blank?'+query);page.set_content(base);page.add_script_tag(content=js)
  page.evaluate('''() => document.addEventListener('click',e=>{if(e.target.closest('a[data-fv-cta]'))e.preventDefault()})''')
  a=page.locator('section.fv-r281 a[data-fv-cta]').first;a.focus();page.keyboard.press('Enter')
  assert a.get_attribute('href')==FREE;page.close()
 browser.close()
receipt={'php_sha256':hashlib.sha256(PHP.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(JS.read_bytes()).hexdigest(),'chromium_offline_contexts':contexts,'tagged_valid_clicks':tagged,'keyboard_activation':keyboard,'invalid_rejected':len(invalid),'cache_shared_body_isolation':'PASS','source_and_media_custody':'PASS','not_verified':['genuine axe-core','HTTP/CSP (browser navigation policy-blocked)','installed WordPress/CDN','field CWV','approved merchant and paid order'],'release':'HARD HOLD'}
(OUT/'r313-source-controlled-qa.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(f'PASS R313: {contexts} Chromium contexts, {tagged} valid clicks, {len(invalid)} invalid rejections; HTTP/CSP and axe not verified')
