#!/usr/bin/env python3
"""Chromium actual-PHP offline UI contract. Not HTTP, axe, WordPress or field CWV."""
import re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[2]
css=(BASE/'apollo-r281/assets/apollo-source-experience.css').read_text()
markup=subprocess.check_output(['php',str(BASE/'apollo-r294/qa/local_http_fixture.php')],text=True)
markup=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',markup)
markup=markup.replace('</head>','<style>'+css+'</style></head>')
count=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in [320,390,768,1440,1920]:
  for js in [False,True]:
   page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
   page.set_content(markup)
   assert page.get_by_text('Unresolved source distinction:',exact=False).is_visible()
   assert page.get_by_role('link',name='Read the free Apollo 1 investigation').count()==1
   comparison=page.locator('.fv-r296__date-disclosure')
   assert comparison.count()==1 and comparison.get_attribute('open') is None
   assert not comparison.locator('.fv-r281__reconciliation-list>li').first.is_visible()
   assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
   comparison.locator('summary').focus();page.keyboard.press('Enter')
   assert comparison.get_attribute('open') is not None
   assert comparison.locator('a[href="https://www.nasa.gov/history/Apollo204/15.html"]').is_visible()
   comparison.locator('summary').focus();page.keyboard.press('Space')
   assert comparison.get_attribute('open') is None
   page.close();count+=1
 browser.close()
print(f'PASS {count}/10 actual-PHP offline Chromium contexts; no axe, HTTP, installed WP or field CWV')
