#!/usr/bin/env python3
"""R309 source-controlled: NASA photo context index, no-JS and real Chromium QA.
Run: python experience2/apollo-r309/qa/source_controlled_gate.py
Requires PHP, Python playwright, system Chromium. NOT WordPress/axe-core/field CWV.
"""
from pathlib import Path
import subprocess,re,json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
php=root/'apollo-r281/apollo-source-experience.php'
fixture=root/'apollo-r301/qa/local_http_fixture.php'
css=(root/'apollo-r281/assets/apollo-source-experience.css').read_text()
urls=[
'https://www.nasa.gov/image-detail/amf-s67-15717/',
'https://www.nasa.gov/image-detail/amf-s66-58038/',
'https://www.nasa.gov/image-detail/amf-s67-21294/',
'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/']
subprocess.run(['php','-l',str(php)],check=True,capture_output=True)
raw=subprocess.check_output(['php','-r','$_SERVER["QUERY_STRING"]="instances=2";parse_str($_SERVER["QUERY_STRING"],$_GET);include $argv[1];',str(fixture)],text=True)
raw=re.sub(r'<link\b[^>]+rel="stylesheet"[^>]*>','',raw)
html=raw.replace('</head>','<style>'+css+'</style></head>')
contexts=0; toggles=0; links=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (320,360,390,768,1440,1920):
  for js in (False,True):
   page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=width<800,reduced_motion='reduce')
   calls=[];page.on('request',lambda r:calls.append(r.url))
   page.set_content(html)
   assert not calls, calls
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
   ids=page.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)')
   assert len(ids)==len(set(ids))
   assert page.locator('section.fv-r281').count()==2
   labels=[]
   for region in page.locator('section.fv-r281').all():
    assert region.locator('.fv-r281__source-list>li[data-fv-evidence-role="documented-textual-claim"]').count()==3
    assert region.locator('[data-fv-cta]').count()==1
    box=region.locator('details.fv-r309__media-index')
    assert box.count()==1 and box.get_attribute('open') is None
    labels.append(box.locator('summary').inner_text())
    assert box.locator('li[data-fv-evidence-role="contextual-media-only"]').count()==4
    assert box.locator('img,iframe,video').count()==0
    for index,link in enumerate(box.locator('a').all()):
     assert link.get_attribute('href')==urls[index]
     assert link.get_attribute('data-fv-conversion-kind')=='noncommercial-media-reference'
     links+=1
    box.locator('summary').focus();page.keyboard.press('Enter')
    assert box.get_attribute('open') is not None
    box.locator('summary').focus();page.keyboard.press('Space')
    assert box.get_attribute('open') is None
    toggles+=2
   assert labels[0]!=labels[1]
   if width==390 and not js:
    plain=re.sub(r'<style>.*?</style>','',html,flags=re.S)
    page.set_content(plain)
    for box in page.locator('details.fv-r309__media-index').all():
     box.locator('summary').click();assert box.locator('a').count()==4
   contexts+=1;page.close()
 browser.close()
print(json.dumps({'offline_chromium_contexts':contexts,'media_links_checked':links,
                  'native_keyboard_toggles':toggles,'image_requests':0,
                  'genuine_axe':'NOT_RUN','installed_wordpress':'NOT_RUN','field_CWV':'NOT_MEASURED'}))
