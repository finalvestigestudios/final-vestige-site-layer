#!/usr/bin/env python3
"""R277 authentic R273/R276 HTML/CSS through R277 adapter, real Chromium.
Local inline-document testing != WordPress, actual HTTP/CSP, axe-core or field CWV.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/fv-r277-qa')
OUT.mkdir(parents=True,exist_ok=True)
HTML=subprocess.check_output(['php',str(ROOT/'qa/render_browser.php')],text=True)
NASA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
assert 'malicious.invalid' not in HTML
assert '<script' not in HTML
assert HTML.count('data-fv-review-ready="false"')==2
assert HTML.count(NASA)==4 and HTML.count(FREE)==2
checks=[]; screenshots={};perf=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        for javascript in (True,False):
            c=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=javascript,
              reduced_motion='reduce',has_touch=width<400,device_scale_factor=1)
            page=c.new_page();requests=[];page.on('request',lambda r:requests.append(r.url))
            page.add_init_script('''window.__shifts=[];window.__lcp=[];try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__shifts.push(e.value)}).observe({type:'layout-shift',buffered:true}); new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}''')
            page.set_content(HTML)
            assert page.locator('aside.fv-r273').count()==2
            assert page.locator('a[href="'+NASA+'"]').count()==4
            assert page.locator('a[href="'+FREE+'"]').count()==2
            assert page.get_by_role('heading',name='Editorial review remains open').count()==2
            assert len(set(page.locator('aside.fv-r273 h2').evaluate_all('(x)=>x.map(e=>e.id)')))==2
            assert page.locator('details[open]').count()==0
            assert page.locator('a[href="'+NASA+'"]').first.is_visible() is False
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            if width in (390,1440) and javascript:
                f=OUT/f'{width}-screen.png';page.screenshot(path=str(f),animations='disabled',full_page=True);screenshots[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
            # Real native keyboard disclosure, regardless of JS availability.
            page.locator('summary').first.focus();page.keyboard.press('Enter')
            assert page.locator('a[href="'+NASA+'"]').first.is_visible()
            page.keyboard.press('Enter')
            assert page.locator('details[open]').count()==0
            page.emulate_media(media='print')
            assert page.locator('a[href="'+NASA+'"]').first.is_visible()
            assert NASA in page.locator('a[href="'+NASA+'"]').first.evaluate('(x)=>getComputedStyle(x,"::after").content')
            assert page.locator('.fv-r273__shared-source').first.is_visible()
            assert page.locator('details[open]').count()==0
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            if width in (390,1440) and javascript:
                f=OUT/f'{width}-print.png';page.screenshot(path=str(f),animations='disabled',full_page=True);screenshots[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
            assert requests==[], requests
            perf.append({'width':width,'js':javascript,'lcp_ms':page.evaluate('window.__lcp||[]'),'layout_shift_entries':page.evaluate('window.__shifts||[]')})
            checks.append({'width':width,'javascript':javascript,'status':'PASS'})
            c.close()
    # Browser CSS at 200% and 400% root text stress.
    for width in (320,390):
        for scale in (2,4):
            page=browser.new_page(viewport={'width':width,'height':850});page.set_content(HTML)
            page.add_style_tag(content=f'html{{font-size:{100*scale}%!important}}')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert page.locator('a[href="'+FREE+'"]').first.is_visible()
            checks.append({'width':width,'font_scale':scale,'status':'PASS'})
            page.close()
    browser.close()
receipt={'suite':'R277 R276-original-component WordPress-adapter browser simulation','passed':len(checks),'cases':checks,
         'screenshots_sha256':screenshots,'axe_core':'NOT_EXECUTED_NO_PINNED_BUNDLE',
         'installed_wordpress':'NOT_TESTED','http_csp':'NOT_TESTED','browser_ui_zoom':'NOT_TESTED',
         'merchant_acceptance':'UNVERIFIED','production_release':'HARD_HOLD'}
(OUT/'lab_metrics.json').write_text(json.dumps({'note':'local Chromium observations; not field CWV', 'observations':perf},sort_keys=True,indent=2)+'\n')
(OUT/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(f'R277 Chromium {len(checks)}/{len(checks)} PASS; receipt sha256 {hashlib.sha256((OUT/"receipt.json").read_bytes()).hexdigest()}')
