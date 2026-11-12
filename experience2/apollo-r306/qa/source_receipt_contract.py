#!/usr/bin/env python3
"""Source-controlled R306 in-memory Chromium contract. No HTTP/WP/axe/field claims."""
import subprocess, re, json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
php=root/'apollo-r281/apollo-source-experience.php'
css=root/'apollo-r281/assets/apollo-source-experience.css'
fixture=root/'apollo-r301/qa/local_http_fixture.php'
subprocess.run(['php','-l',str(php)],check=True)
html=subprocess.check_output(['php','-r','parse_str("instances=2",$_GET);include $argv[1];',str(fixture)],text=True)
html=re.sub(r'<link\b[^>]+rel="stylesheet"[^>]+>', '',html)
html=html.replace('</head>','<style>'+css.read_text()+'</style></head>')
count=0
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        for js in (False,True):
            page=browser.new_page(viewport={'width':width,'height':850},java_script_enabled=js,has_touch=True,reduced_motion='reduce')
            page.set_content(html)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            assert page.locator('[data-fv-cta]').count()==2
            assert page.locator('[data-fv-conversion-kind="merchant-confirmed-purchase"]').count()==0
            sections=page.locator('section.fv-r281')
            assert sections.count()==2
            for i in range(2):
                scope=sections.nth(i)
                details=scope.locator('details[data-fv-custody-trail]')
                assert details.count()==1 and details.locator('li').count()==3
                assert details.get_attribute('open') is None
                for j in range(3):
                    row=details.locator('li').nth(j)
                    target=scope.locator('.fv-r281__source-list li').nth(j)
                    assert row.get_attribute('data-fv-custody-source-id')==target.get_attribute('data-fv-source-id')
                    assert row.get_attribute('data-fv-cites-claim')==target.get_attribute('data-fv-cites-claim')
                details.locator('summary').focus();page.keyboard.press('Enter')
                assert details.get_attribute('open') is not None
                details.locator('li a').first.click()
                assert page.evaluate('location.hash')=='#fv-r281-'+str(i+1)+'-source-1'
                assert scope.locator('.fv-r281__source-list li').first.evaluate('(e)=>e===document.activeElement')
                details.locator('summary').focus();page.keyboard.press('Space')
                assert details.get_attribute('open') is None
            count+=1;page.close()
    browser.close()
assert count==10
print(json.dumps({'source_controlled_chromium_contexts':count,'source_custody_rows_checked':count*6,'keyboard_operations':count*4,'css':'in-memory original','axe':'not run','http_and_field':'not verified'}))
