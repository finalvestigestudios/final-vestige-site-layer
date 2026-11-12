#!/usr/bin/env python3
"""R304 offline Chromium gate: PHP source custody, 320–1920, no JS, axe not implied."""
import re, subprocess, json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
subprocess.run(['php','-l',str(R/'apollo-r281/apollo-source-experience.php')],check=True)
html=subprocess.check_output(['php','-r','parse_str("instances=2",$_GET);include $argv[1];',str(R/'apollo-r301/qa/local_http_fixture.php')],text=True)
html=re.sub(r'<link\b[^>]+rel="stylesheet"[^>]+>','',html)
html=html.replace('</head>','<style>'+(R/'apollo-r281/assets/apollo-source-experience.css').read_text()+'</style></head>')
assert not re.search(r'<(script|iframe|img|form)\b',html,re.I)
contexts=triplets=mutations=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (320,390,768,1440,1920):
  for js in (False,True):
   page=b.new_page(viewport={'width':width,'height':850},java_script_enabled=js,reduced_motion='reduce',has_touch=True)
   page.set_content(html)
   assert page.locator('section.fv-r281').count()==2
   ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(e=>e.id)')
   assert len(ids)==len(set(ids))
   for section in page.locator('section.fv-r281').all():
    plates=section.locator('li.fv-r281__plate'); sources=section.locator('.fv-r281__source-list > li[data-fv-evidence-role=\"documented-textual-claim\"]')
    assert plates.count()==sources.count()==3
    for i in range(3):
     plate=plates.nth(i); source=sources.nth(i); drawer=plate.locator('details.fv-r281__drawer')
     claim=f'apollo-1-claim-{i+1}'; ref=plate.get_attribute('data-fv-source-id')
     assert ref in ('nasa_mission','nasa_proceedings','nasa_board')
     assert plate.get_attribute('data-fv-claim-key')==claim
     assert drawer.get_attribute('data-fv-claim-key')==claim and drawer.get_attribute('data-fv-source-id')==ref
     assert source.get_attribute('data-fv-cites-claim')==claim and source.get_attribute('data-fv-source-id')==ref
     assert plate.locator('.fv-r281__source-jump a').get_attribute('href')=='#'+source.get_attribute('id')
     assert source.locator('.fv-r281__source-return a').get_attribute('href')=='#'+plate.get_attribute('id')
     assert 'not a NASA catalogue number' in drawer.text_content()
     assert 'not a NASA archive number' in source.text_content()
     triplets+=1
    cta=section.locator('[data-fv-cta]')
    assert cta.count()==1 and cta.get_attribute('data-fv-conversion-kind')=='editorial-continuation'
    assert section.locator('[data-fv-link-purpose="official-evidence-source"]').count()==13
    for a in section.locator('[data-fv-link-purpose="official-evidence-source"]').all():
     assert a.get_attribute('data-fv-conversion-kind')=='noncommercial-source-reference'
     assert '.nasa.gov' in a.get_attribute('href')
    first=sources.first
    first.evaluate('(e)=>e.dataset.fvSourceId="injected"')
    assert first.get_attribute('data-fv-source-id')!=plates.first.get_attribute('data-fv-source-id')
    mutations+=1
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   if not js:
    output=R/'apollo-r304/QA'/f'r304-gate-{width}-nojs.png'
    output.parent.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(output),full_page=True,animations='disabled')
   contexts+=1
   page.close()
 b.close()
assert (contexts,triplets,mutations)==(10,60,20)
print(json.dumps({'contexts':contexts,'claim_drawer_catalogue_triplets':triplets,'negative_controls':mutations,'axe':'NOT EXECUTED','wordPress':'NOT VERIFIED','field_cwv':'NOT VERIFIED'}))
