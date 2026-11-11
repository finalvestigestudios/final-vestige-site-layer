#!/usr/bin/env python3
"""Offline actual-PHP+Chromium staging QA. Not installed WordPress or axe."""
import os,re,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
php=root/'apollo-r281/apollo-source-experience.php'
css=root/'apollo-r281/assets/apollo-source-experience.css'
html=subprocess.check_output(['php',str(root/'apollo-r294/qa/local_http_fixture.php')],text=True)
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',html)
html=html.replace('</head>','<style>'+css.read_text()+'</style></head>')
count=0
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('APOLLO_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 for width in (320,390,768,1440,1920):
  for js in (False,True):
   page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
   page.set_content(html)
   assert page.locator('.fv-r281__reconciliation-list>li').count()==3
   assert page.locator('a[href="https://www.nasa.gov/history/Apollo204/15.html"]').count()==1
   assert page.locator('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==1
   assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
   summary=page.locator('.fv-r291__authority-disclosure>summary')
   summary.focus();page.keyboard.press('Enter')
   assert page.locator('.fv-r291__authority-disclosure').get_attribute('open') is not None
   if not js and width in (390,1440): page.screenshot(path=str(root/'QA'/f'r295-{width}-nojs.png'),full_page=True,animations='disabled')
   if not js and width==390:
    page.emulate_media(media='print')
    page.pdf(path=str(root/'QA'/'r295-390-print.pdf'),print_background=True)
   page.close();count+=1
 browser.close()
assert count==10
print(f'PASS {count}/10 local Chromium contexts; genuine axe, browser HTTP, installed WP and field CWV UNVERIFIED')
