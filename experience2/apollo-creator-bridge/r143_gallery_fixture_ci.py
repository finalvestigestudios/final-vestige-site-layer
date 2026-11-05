#!/usr/bin/env python3
"""Chromium offline gallery regression. Synthetic fixture, NOT live Apollo QA."""
import argparse, hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright
BAD="const photos = $(box, '[data-fvx-chrono-photo]');"
FIX="const photos = $$(box, '[data-fvx-chrono-photo]');"
JS="""const $=(r,s)=>r.querySelector(s);
const $$=(r,s)=>Array.from(r.querySelectorAll(s));
const box=document.querySelector('[data-fvx-chronology]');
const range=box.querySelector('input[type=range]');
const update=()=>{
const t=Number(range.value);
const photos = $(box, '[data-fvx-chrono-photo]');
if(photos.length===3){const i=t<6?0:t<11.3?1:2;
photos.forEach((p,j)=>{p.hidden=j!==i;});
box.querySelector('[data-fvx-chrono-position]').hidden=false;}}
range.addEventListener('input',update);update();
box.querySelector('[data-fvx-chrono-tool]').hidden=false;"""
HTML='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box}body{background:#10100f;color:#e9e0d1;font:18px system-ui;margin:0}
main{max-width:1000px;margin:auto;padding:24px}h1{font:clamp(32px,6vw,64px) Georgia;color:#c7a66c}
[hidden]{display:none!important}figure{border:1px solid #c7a66c;padding:16px;margin:8px 0}
input{width:100%;min-height:44px}a{color:#e6bf83}a:focus-visible,input:focus-visible{outline:3px solid #e6bf83}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}</style>
<main><h1>Apollo 1 — archival context</h1><section data-fvx-chronology>
<p>Photographs are historical context, not photos of events at each second.</p>
<div data-fvx-chrono-tool hidden><label>Documented seconds <input type="range" min="0" max="15" step="0.1" value="0"></label></div>
<div data-fvx-chrono-photo="0"><figure>NASA context photograph 1 — image intentionally omitted</figure></div>
<div data-fvx-chrono-photo="1"><figure>NASA context photograph 2 — image intentionally omitted</figure></div>
<div data-fvx-chrono-photo="2"><figure>NASA context photograph 3 — image intentionally omitted</figure></div>
<p data-fvx-chrono-position hidden>Archival context, not second-specific footage.</p></section>
<a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the full investigation</a></main></html>'''

def run(output):
    output.mkdir(parents=True,exist_ok=True)
    results=[];hashes={}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in (320,360,390,768,1440,1920):
                page=browser.new_page(viewport={'width':width,'height':850},reduced_motion='reduce')
                page.set_content(HTML)
                assert page.locator('[data-fvx-chrono-photo]:visible').count()==3  # no JS
                assert page.locator('[data-fvx-chrono-tool]:visible').count()==0
                page.evaluate(JS)
                assert page.locator('[data-fvx-chrono-photo]:visible').count()==3  # published defect
                page.set_content(HTML)
                page.evaluate(JS.replace(BAD,FIX))
                for value,expected in [('0','0'),('6','1'),('11.3','2'),('15','2')]:
                    page.locator('input[type=range]').fill(value)
                    assert page.locator('[data-fvx-chrono-photo]:visible').count()==1
                    assert page.locator('[data-fvx-chrono-photo]:visible').get_attribute('data-fvx-chrono-photo')==expected
                page.locator('input[type=range]').focus();page.keyboard.press('Home')
                assert page.locator('[data-fvx-chrono-photo]:visible').get_attribute('data-fvx-chrono-photo')=='0'
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                shot=output/f'r143_gallery_fixture_{width}.png';page.screenshot(path=str(shot),full_page=True)
                hashes[shot.name]=hashlib.sha256(shot.read_bytes()).hexdigest()
                results.append({'width':width,'no_js':'3 context cards','unpatched':'3 cards, no slider gallery response',
                                'patched':'one card, correct 4 marker transitions, Home keyboard PASS',
                                'overflow':False,'motion':'reduced','scope':'synthetic fixture'})
                page.close()
        finally:browser.close()
    receipt={'schema':'fv.apollo.r143.browser-fixture.v1','results':results,'sha256':hashes,
             'live_browser':'NOT_TESTED','axe':'NOT_TESTED','live_lcp_cls':'NOT_MEASURED','release':'STAGING_HOLD'}
    (output/'r143_fixture_receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    print(json.dumps({'checks':len(run(Path(args.output))['results']),'kind':'SYNTHETIC_ONLY'}))
