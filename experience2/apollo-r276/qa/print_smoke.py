#!/usr/bin/env python3
"""R276 committed Chromium print/keyboard/no-JS regression against authentic PHP."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
CSS=(ROOT/'apollo-r273/assets/review-custody.css').read_text()
SOURCE='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/fv-apollo-r276');OUT.mkdir(parents=True,exist_ok=True)
HTML=subprocess.check_output(['php',str(ROOT/'apollo-r274/qa/multi-render.php')]).decode()
assert CSS in HTML
sha={};cases=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        for js in (True,False):
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,device_scale_factor=1,reduced_motion='reduce',has_touch=width<=390)
            page=context.new_page();requests=[];page.on('request',lambda r:requests.append(r.url))
            page.set_content(HTML)
            assert page.locator('aside.fv-r273').count()==3
            assert page.locator('details[open]').count()==0
            assert not page.locator('a[href="'+SOURCE+'"]').first.is_visible()
            assert page.locator('a[href="'+SOURCE+'"]').count()==6
            assert page.locator('a[href="'+ARTICLE+'"]').count()==3
            assert page.locator('[data-fv-review-ready="true"]').count()==0
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            if width in (390,1440) and js:
                path=OUT/f'{width}-screen.png';page.screenshot(path=str(path),full_page=True,animations='disabled');sha[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            page.emulate_media(media='print')
            assert page.locator('.fv-r273__shared-source').first.is_visible()
            link=page.locator('a[href="'+SOURCE+'"]').first
            assert link.is_visible()
            assert SOURCE in link.evaluate('(e)=>getComputedStyle(e,"::after").content')
            for cls in ('__status','__eyebrow','__boundary'):
                assert page.locator('.fv-r273'+cls).first.evaluate('(e)=>getComputedStyle(e).color')=='rgb(0, 0, 0)'
            assert not page.locator('.fv-r273__external').first.is_visible()
            assert page.locator('details[open]').count()==0
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            if width in (390,1440) and js:
                path=OUT/f'{width}-print.png';page.screenshot(path=str(path),full_page=True,animations='disabled');sha[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            page.emulate_media(media='screen')
            assert not link.is_visible()
            page.locator('summary').first.focus();page.keyboard.press('Enter')
            assert link.is_visible()
            assert requests==[]
            cases.append({'width':width,'js':js,'result':'PASS'})
            context.close()
    # Authentic R275 CSS hid NASA sources from paper; fail on removing print override.
    before=HTML.replace(CSS,CSS.split('/* R276: print')[0])
    page=browser.new_page();page.set_content(before);page.emulate_media(media='print')
    assert not page.locator('a[href="'+SOURCE+'"]').first.is_visible()
    page.close()
    browser.close()
receipt={'suite':'R276 source-matched Chromium print smoke','cases':cases,'screens_sha256':sha,'negative_R275_print_hidden':'REPRODUCED','axe':'NOT_EXECUTED','installed_WP':'NOT_TESTED','HTTP':'BLOCKED_BY_ADMINISTRATOR','field_CWV':'NOT_TESTED','release':'HARD_HOLD'}
(OUT/'smoke_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('R276 committed smoke',len(cases),'PASS; sha256',hashlib.sha256((OUT/'smoke_receipt.json').read_bytes()).hexdigest())
