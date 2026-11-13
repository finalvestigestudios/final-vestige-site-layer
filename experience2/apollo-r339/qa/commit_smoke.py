#!/usr/bin/env python3
"""Short exact-HEAD replay: genuine PHP render + Chromium no-JS/keyboard/source/CTA gate."""
import json
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
module = ROOT / 'chronology-rail.php'
css = ROOT / 'assets/chronology-rail.css'
php = "<?php define('ABSPATH',__DIR__); function add_shortcode($a,$b){}; require " + json.dumps(str(module)) + "; echo fv_apollo_r339_shortcode(); echo fv_apollo_r339_shortcode(); ?>"
body = subprocess.run(['php'],input=php,text=True,capture_output=True,check=True).stdout
html = '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css.read_text()+'</style><body style="margin:0">'+body+'</body></html>'
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
    for w,js in [(320,False),(320,True),(390,True),(1440,True),(1920,True)]:
        page=browser.new_page(viewport={'width':w,'height':800},java_script_enabled=js)
        page.set_content(html)
        roots=page.locator('section[data-fv-r339]')
        assert roots.count()==2
        assert all(roots.nth(i).locator('li.fv-apollo-r339__event').count()==6 for i in range(2))
        assert all(roots.nth(i).locator('a[data-fv-r339-source]').count()==6 for i in range(2))
        assert all(roots.nth(i).locator('a[data-fv-r339-cta=editorial]').count()==1 for i in range(2))
        assert page.evaluate('document.documentElement.scrollWidth - innerWidth')<=1
        assert page.evaluate("(()=>{const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size})()")
        first=roots.first.locator('details').first
        first.locator('summary').focus();page.keyboard.press('Enter')
        assert first.evaluate('(e)=>e.open')
        page.close()
        print('PASS exact-head smoke',w,'js='+str(js))
    browser.close()
print('PASS 5/5 Chromium contexts; not installed WordPress or axe-core')
