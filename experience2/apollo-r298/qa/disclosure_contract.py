#!/usr/bin/env python3
"""R298: actual PHP + Chromium accessibility-tree disclosure names, offline only.
Requires installed PHP, Playwright Python and Chromium; does not claim axe/HTTP/WP QA.
"""
import json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
html=subprocess.check_output(['php','-r','parse_str("instances=2", $_GET); include $argv[1];',str(ROOT/'apollo-r294/qa/local_http_fixture.php')],text=True)
css=(ROOT/'apollo-r281/assets/apollo-source-experience.css').read_text()
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',html).replace('</head>','<style>'+css+'</style></head>')
checks=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [320,390,768,1440,1920]:
  for js in [False,True]:
   pg=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=True)
   pg.set_content(html,wait_until='load')
   assert pg.locator('section.fv-r281').count()==2
   assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
   summaries=pg.locator('section.fv-r281 details > summary')
   assert summaries.count()==10
   snapshots=[s.aria_snapshot() for s in summaries.all()]
   assert len(set(snapshots))==10,('duplicate accessible disclosure names',width,js,snapshots)
   for snapshot in snapshots:
    assert 'atlas instance ' in snapshot,snapshot
   for i in [1,2]:
    assert sum('atlas instance '+str(i) in s for s in snapshots)==5
   # Native Enter/Space works when JS is disabled, and record text remains intact.
   d=pg.locator('.fv-r281__drawer').first
   d.locator('summary').focus();pg.keyboard.press('Enter');assert d.get_attribute('open') is not None
   pg.keyboard.press('Space');assert d.get_attribute('open') is None
   date=pg.locator('.fv-r296__date-disclosure').first
   date.locator('summary').click();assert date.get_attribute('open') is not None
   assert date.locator('a[href^="https://www.nasa.gov/"]').count()>=2
   assert pg.locator('footer.fv-r281__next a[href^="https://finalvestige.com/"]').count()==2
   assert pg.locator('script,iframe,form').count()==0
   checks+=1;pg.close()
 browser.close()
print(json.dumps({'result':'PASS OFFLINE FIXTURE','chromium_contexts':checks,'unique_ax_disclosure_names':10,'screen_widths':[320,390,768,1440,1920], 'javascript_modes':[False,True], 'real_axe':'NOT TESTED','installed_wordpress':'NOT TESTED','browser_http_csp':'NOT TESTED'},sort_keys=True))
