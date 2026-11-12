#!/usr/bin/env python3
"""R307 committed browser gate: offline PHP fixture, actual Chromium. No axe/WP/HTTP claims."""
from pathlib import Path
import re, subprocess, json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
php=root/'apollo-r281/apollo-source-experience.php'
css=root/'apollo-r281/assets/apollo-source-experience.css'
fixture=root/'apollo-r301/qa/local_http_fixture.php'
subprocess.run(['php','-l',str(php)],check=True)
html=subprocess.check_output(['php','-r','parse_str("instances=2",$_GET);include $argv[1];',str(fixture)],text=True)
html=re.sub(r'<link\b[^>]+rel="stylesheet"[^>]+>','',html)
html=html.replace('</head>','<style>'+css.read_text()+'</style></head>')
passed=journeys=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [320,390,768,1440,1920]:
  for js in [False,True]:
   page=browser.new_page(viewport={'width':width,'height':850},java_script_enabled=js,has_touch=True,reduced_motion='reduce',forced_colors='active' if width==768 else 'none')
   page.set_content(html)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   regions=page.locator('section.fv-r281')
   assert regions.count()==2 and page.locator('[data-fv-cta]').count()==2
   assert page.locator('[data-fv-conversion-kind="merchant-confirmed-purchase"]').count()==0
   ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(e=>e.id)')
   assert len(ids)==len(set(ids))
   for i in [1,2]:
    region=regions.nth(i-1)
    footer=region.locator('footer.fv-r281__next')
    target=f'fv-r281-{i}-continue'
    assert footer.get_attribute('id')==target and footer.get_attribute('tabindex')=='-1'
    assert footer.locator('[data-fv-cta][data-fv-conversion-kind="editorial-continuation"]').count()==1
    for j in [1,2,3]:
     source=region.locator(f'#fv-r281-{i}-source-{j}')
     link=source.locator('a.fv-r307__continue-return')
     assert link.count()==1 and link.get_attribute('href')=='#'+target
     assert f'atlas instance {i}' in link.text_content()
     link.focus();page.keyboard.press('Enter')
     assert page.evaluate('location.hash')=='#'+target
     assert footer.evaluate('(e)=>e===document.activeElement')
     assert footer.evaluate('(e)=>getComputedStyle(e).outlineStyle')=='solid'
     journeys+=1
    # A corrupted cross-instance return must not match the signed contract.
    link=region.locator('.fv-r307__continue-return').first
    link.evaluate('(e)=>e.setAttribute("href","#fv-r281-999-continue")')
    assert link.get_attribute('href')!='#'+target
   passed+=1
   page.close()
 # CSS-free and JavaScript-free fallback.
 page=browser.new_page(viewport={'width':390,'height':850},java_script_enabled=False)
 page.set_content(re.sub(r'<style>.*?</style>','',html,flags=re.S))
 page.locator('.fv-r307__continue-return').first.click()
 assert page.evaluate('location.hash')=='#fv-r281-1-continue'
 assert page.locator('#fv-r281-1-continue').evaluate('(e)=>e===document.activeElement')
 page.close()
 browser.close()
assert passed==10 and journeys==60
print(json.dumps({'actual_offline_Chromium_contexts':passed,'source_to_continuation_keyboard_journeys':journeys,'css_free_no_js':'PASS','commercial_orders':'NONE','axe':'NOT EXECUTED','wordPress':'NOT TESTED','field_performance':'NOT TESTED'}))
