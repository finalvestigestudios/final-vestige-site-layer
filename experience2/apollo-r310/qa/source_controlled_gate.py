#!/usr/bin/env python3
"""R310 source-controlled acceptance: PHP fixture + real offline Chromium.
No axe-core, installed WordPress, HTTP/CSP, or production CWV claims.
"""
from pathlib import Path
import subprocess,re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
F=R/'apollo-r301/qa/local_http_fixture.php'
q='instances=2&queue=0&utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_lf_001'
subprocess.run(['php','-l',str(P)],check=True)
def render():
 return subprocess.check_output(['php','-r','$_SERVER["QUERY_STRING"]=$argv[2];parse_str($argv[2],$_GET);include $argv[1];',str(F),q],text=True)
def contract(h):
 d=BeautifulSoup(h,'lxml');regions=d.select('section.fv-r281')
 if len(regions)!=2:return False
 for region in regions:
  src=region.select_one('ul.fv-r281__source-list')
  media=region.select_one('details.fv-r309__media-index')
  if not src or not media or src.parent is not media.parent or src.parent.name!='aside':return False
  items=src.find_all(recursive=False)
  if len(items)!=3 or any(x.name!='li' or x.get('data-fv-evidence-role')!='documented-textual-claim' for x in items):return False
  if media.find_parent('ul') is not None:return False
  mlist=media.select_one('ul.fv-r309__media-list')
  if not mlist or len(mlist.find_all(recursive=False))!=4:return False
  for item in mlist.find_all(recursive=False):
   if item.name!='li' or item.get('data-fv-claim-proof')!='no' or item.get('data-fv-image-rights')!='not-cleared-for-reuse':return False
   a=item.select_one('a')
   if not a or not a.get('href','').startswith('https://www.nasa.gov/image-detail/') or a.get('data-fv-conversion-kind')!='noncommercial-media-reference':return False
  if region.select('img,iframe,video,script,[data-fv-conversion-kind="merchant-confirmed-purchase"]'):return False
  links=region.select('a[data-fv-cta="apollo-read-free-investigation"]')
  if len(links)!=1 or links[0].get('data-fv-conversion-kind')!='editorial-continuation':return False
 return True
h=render()
assert contract(h)
bad=h.replace('</ul><details class="fv-r281__drawer fv-r309__media-index"','<details class="fv-r281__drawer fv-r309__media-index"',1)
bad=bad.replace('</details><p>No archive image, geolocation, ownership','</details></ul><p>No archive image, geolocation, ownership',1)
assert not contract(bad),'R309 list misnesting negative control must fail'
assert not contract(h.replace('data-fv-claim-proof="no"','data-fv-claim-proof="yes"',1))
assert not contract(h.replace('data-fv-conversion-kind="editorial-continuation"','data-fv-conversion-kind="merchant-confirmed-purchase"',1))
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',h)
html=html.replace('</head>','<style>'+C.read_text()+'</style></head>')
contexts=focus=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in [320,360,390,768,1440,1920]:
  for js in [False,True]:
   page=b.new_page(viewport={'width':w,'height':900},java_script_enabled=js,has_touch=w<800,reduced_motion='reduce',forced_colors='active' if w==768 else 'none')
   page.set_content(html)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   assert page.locator('ul.fv-r281__source-list > li').count()==6
   assert page.locator('ul.fv-r281__source-list > details').count()==0
   assert page.locator('ul.fv-r309__media-list > li').count()==8
   for i in [1,2]:
    s=page.locator('section.fv-r281').nth(i-1)
    d=s.locator('details.fv-r309__media-index')
    assert d.evaluate('(e)=>e.parentElement===e.previousElementSibling.parentElement && e.previousElementSibling.tagName==="UL"')
    if w<800:d.locator('summary').tap()
    else:d.locator('summary').focus();page.keyboard.press('Enter')
    assert d.get_attribute('open') is not None
    jump=s.locator('.fv-r281__source-jump a').first
    jump.focus();page.keyboard.press('Enter')
    assert page.evaluate('location.hash')==f'#fv-r281-{i}-source-1'
    assert page.evaluate('document.activeElement.id')==f'fv-r281-{i}-source-1'
    focus+=1
   contexts+=1;page.close()
 b.close()
print(f'PASS R310: {contexts} real offline Chromium contexts; {focus} source-focus returns; 3 source records + 4 separate unlicensed media records per instance; 3 adversarial controls rejected.')
