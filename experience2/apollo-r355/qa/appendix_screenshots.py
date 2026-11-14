#!/usr/bin/env python3
"""Produce reproducible R355 source-annotation screenshots (pure PHP render, Chromium)."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];OUT=R/'QA';OUT.mkdir(exist_ok=True)
php='define("ABSPATH",true);require '+json.dumps(str(R/'postfire-ledger.php'))+';echo fv_apollo_r355_postfire_shortcode();'
body=subprocess.check_output(['php','-r',php],text=True)
css=(R/'postfire-ledger.css').read_text()
doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+css+'</style></head><body>'+body+'</body></html>'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in (390,1440):
  page=browser.new_page(viewport={'width':width,'height':900})
  page.set_content(doc)
  page.locator('.fv-apollo-r355__source summary').click()
  assert page.locator('[data-fv-r355-reviewed-source]:visible').count()==1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=str(OUT/f'r355-source-annotation-{width}.png'),full_page=True)
  page.close()
 browser.close()
print('R355 annotation screenshots: 390 and 1440, Chromium, native disclosure open, PASS')
