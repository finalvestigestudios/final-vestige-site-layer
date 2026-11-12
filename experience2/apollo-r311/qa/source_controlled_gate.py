#!/usr/bin/env python3
"""R311 cache-stable Apollo continuation: source-controlled PHP/Chromium gate.
No claim of actual WordPress, CDN, native HTTP/CSP, axe-core, or field CWV.
"""
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import hashlib, subprocess, re
ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
FIX=ROOT/'apollo-r301/qa/local_http_fixture.php'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
Q=[
 '',
 'utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_lf_001',
 'utm_source=tiktok&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=visitor_b',
 'utm_source=youtube&utm_source=tiktok&utm_content=duplicate',
 'utm_content=buyer%40example.test&gclid=private'
]
def render(q):
 raw='instances=2&queue=0'+('&'+q if q else '')
 return subprocess.check_output(['php','-r','$_SERVER["QUERY_STRING"]=$argv[2];parse_str($argv[2],$_GET);include $argv[1];',str(FIX),raw],text=True)
def contract(h):
 soup=BeautifulSoup(h,'lxml')
 regions=soup.select('section.fv-r281')
 assert len(regions)==2
 for region in regions:
  assert region.get('data-fv-attribution-policy')=='cache-stable-no-query-forwarding'
  sources=region.select_one('ul.fv-r281__source-list')
  media=region.select_one('details.fv-r309__media-index')
  assert sources and media and sources.parent==media.parent
  assert len(sources.find_all(recursive=False))==3
  assert len(media.select('ul.fv-r309__media-list > li'))==4
  cta=region.select('a[data-fv-cta="apollo-read-free-investigation"]')
  assert len(cta)==1 and cta[0].get('href')==FREE
  assert cta[0].get('data-fv-conversion-kind')=='editorial-continuation'
  assert not region.select('img,iframe,script,[data-fv-conversion-kind="merchant-confirmed-purchase"]')
  for source in region.select('a[data-fv-link-purpose="official-evidence-source"]'):
   host=urlparse(source.get('href','')).hostname or ''
   assert host=='nasa.gov' or host.endswith('.nasa.gov')
 ids=[x['id'] for x in soup.select('[id]')]
 assert len(ids)==len(set(ids))
subprocess.run(['php','-l',str(PHP)],check=True)
baseline=render('')
contract(baseline)
for q in Q:
 h=render(q)
 contract(h)
 assert h==baseline, 'request-dependent body: unsafe for shared query-agnostic cache'
bad=baseline.replace(FREE,FREE+'?utm_content=wrong_visitor',1)
assert bad!=baseline and 'wrong_visitor' not in baseline
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',baseline).replace('</head>','<style>'+CSS.read_text()+'</style></head>')
contexts=keyboard=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [320,360,390,768,1440,1920]:
  for js in [False,True]:
   page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=width<800,reduced_motion='reduce',forced_colors='active' if width==768 else 'none')
   page.set_content(html)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   assert page.locator('ul.fv-r281__source-list > li').count()==6
   assert page.locator('ul.fv-r309__media-list > li').count()==8
   for i in [1,2]:
    region=page.locator('section.fv-r281').nth(i-1)
    assert region.locator('[data-fv-cta]').get_attribute('href')==FREE
    summary=region.locator('details.fv-r306__source-receipt summary')
    summary.focus();page.keyboard.press('Enter')
    assert region.locator('details.fv-r306__source-receipt').get_attribute('open') is not None
    jump=region.locator('.fv-r281__source-jump a').first
    jump.focus();page.keyboard.press('Enter')
    assert page.evaluate('document.activeElement.id')==f'fv-r281-{i}-source-1'
    keyboard+=2
   contexts+=1
   page.close()
 browser.close()
print(f'PASS R311: {len(Q)} request variants with identical PHP HTML, 1 cache-poisoning negative control, {contexts} real offline Chromium contexts, {keyboard} keyboard operations; not deployed.')
