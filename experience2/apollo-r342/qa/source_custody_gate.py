#!/usr/bin/env python3
"""R342 committed read-only QA: real PHP -> Playwright Chromium, source custody and no-JS.
Run at repo root: python experience2/apollo-r342/qa/source_custody_gate.py
Python playwright+Chromium and php-cli required; does NOT certify WordPress, axe or revenue.
"""
import json, os, subprocess
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r339/chronology-rail.php'
APP=ROOT/'apollo-r340/apollo-accession-gallery.php'
CSS=[ROOT/'apollo-r339/assets/chronology-rail.css',ROOT/'apollo-r340/assets/accession-gallery.css']
OUT=Path(os.getenv('FV_R342_OUT',str(ROOT/'apollo-r342/QA')))
OUT.mkdir(parents=True,exist_ok=True)

def run_php(expr):
    return subprocess.check_output(['php','-r',"define('ABSPATH',true); require '"+str(PHP)+"'; require '"+str(APP)+"'; "+expr],text=True)

records=json.loads(run_php('echo json_encode(fv_apollo_r339_chronology());'))
html=run_php('echo fv_apollo_r340_experience_shortcode();')
assert len(records)==6
assert [r['tier'] for r in records]==['board-analysis']*5+['later-history']
assert [r['time'] for r in records]==['23:31:04.7','About 23:31:12','23:31:16.8','About 23:31:19','23:31:22.4','Following the 1967 fire']
assert all(urlparse(r['source']).hostname=='www.nasa.gov' and r['source'].startswith('https://') and r['boundary'] and r['custody'] for r in records)
assert 'not become intense until about this time' in records[1]['description']
assert '23:31:21.8' in records[4]['description']
assert not any(k in r for r in records for k in ['map_pin','lat','lng','merchant_url','licensed_image'])
assert html.count('data-fv-r339-cta="editorial"')==1
assert html.count('data-fv-r340-role="contextual-photo-only"')==4
assert 'did not conclusively identify' in html
assert not any(s in html for s in ['data-geo-pin','data-geo-edge','data-affiliate','utm_content='])
styles='\n'.join(f.read_text() for f in CSS)
fixture='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+styles+'</style></head><body><main><h1 style="overflow-wrap:anywhere">Apollo 1 evidence</h1>'+html+'</main></body></html>'
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
    for width,js,root_px in [(320,True,16),(320,True,64),(390,False,16),(768,True,16),(1440,True,16),(1920,False,16)]:
        page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
        content=fixture if js else fixture.replace('</style>',f'html{{font-size:{root_px}px}}</style>',1)
        page.set_content(content,wait_until='load')
        if js:page.evaluate("px=>document.documentElement.style.fontSize=px+'px'",root_px)
        assert page.locator('[data-fv-r339-evidence]').count()==6
        assert page.locator('.fv-apollo-r340__card').count()==4
        summary=page.locator('.fv-apollo-r339__source summary').first
        summary.focus();page.keyboard.press('Enter')
        assert page.locator('.fv-apollo-r339__source').first.get_attribute('open') is not None
        assert page.locator('.fv-apollo-r339__source a').first.is_visible()
        assert page.locator('.fv-apollo-r339__nav a').count()==6
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        if js and width in (320,1440) and root_px==16:page.screenshot(path=str(OUT/f'r342-committed-{width}.png'),full_page=True)
        results.append({'viewport':width,'js':js,'root_px':root_px,'result':'PASS'})
        page.close()
    browser.close()
receipt={'r342_committed_gate':'PASS','contexts':results,'axe':'NOT_EXECUTED','installed_wp':'NOT_VERIFIED'}
(OUT/'r342-committed-gate.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
