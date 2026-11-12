#!/usr/bin/env python3
"""Chromium actual-PHP offline UI contract. Not HTTP, axe, WordPress or field CWV."""
import re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[2]
css=(BASE/'apollo-r281/assets/apollo-source-experience.css').read_text()
markup=subprocess.check_output(['php','-r','parse_str("instances=2", $_GET); include $argv[1];',str(BASE/'apollo-r294/qa/local_http_fixture.php')],text=True)
markup=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',markup)
markup=markup.replace('</head>','<style>'+css+'</style></head>')
count=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in [320,390,768,1440,1920]:
  for js in [False,True]:
   page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
   page.set_content(markup)
   # R297: names of repeated shortcode landmarks must be unique *in the
   # real Chromium accessibility tree*, not only in the HTML source.
   assert page.locator('.fv-r281').count()==2
   ids=page.locator('[id]').evaluate_all('(nodes)=>nodes.map(x=>x.id)')
   assert len(ids)==len(set(ids)), 'duplicate fragment targets'
   names=page.locator('nav.fv-r281__rail').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("aria-label"))')
   assert names==['Apollo 1 chronology — atlas instance 1','Apollo 1 chronology — atlas instance 2'],names
   regions=page.locator('aside.fv-r281__reconciliation,aside.fv-r281__gallery').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("aria-label"))')
   assert len(regions)==4 and len(regions)==len(set(regions)), regions
   cdp=page.context.new_cdp_session(page)
   ax=cdp.send('Accessibility.getFullAXTree')['nodes']
   roles={(n.get('role',{}).get('value'),n.get('name',{}).get('value')) for n in ax}
   assert all(('navigation',n) in roles for n in names)
   assert all(('complementary',n) in roles for n in regions)
   assert page.get_by_text('Unresolved source distinction:',exact=False).first.is_visible()
   assert page.get_by_role('link',name='Read the free Apollo 1 investigation').count()==2
   comparison=page.locator('.fv-r296__date-disclosure').first
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
print(f'PASS {count}/10 two-instance actual-PHP Chromium contexts; AX landmarks distinct; axe/HTTP/WP/field CWV NOT verified')
