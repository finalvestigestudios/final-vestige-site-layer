#!/usr/bin/env python3
"""R228 exact generated source / touch target / no-JS / custody acceptance.

Uses the R227 PHP lifecycle test shim in the parent branch (not real WordPress).
Uses Playwright/Chromium set_content because local navigation is policy-blocked.
No external browser requests, paid dependencies, site writes or pretend axe results.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,390,768,1440,1920)
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def digest(b): return hashlib.sha256(b).hexdigest()
def dump(obj):return (json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def require(cond,msg):
    if not cond:raise AssertionError(msg)

def load_parent_gate(path):
    spec=importlib.util.spec_from_file_location('fv_parent_gate',path)
    require(spec is not None and spec.loader is not None,'Missing parent QA runner')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def run(dist,out,parent_gate):
    parent=load_parent_gate(parent_gate)
    receipt=json.loads((dist/'r228-build-receipt.json').read_text())
    manifest=json.loads((dist/'manifest.json').read_text())
    require(digest((dist/'manifest.json').read_bytes())==receipt['new_manifest_sha256'],'R228 manifest drift')
    for name,expected in manifest['files'].items():
        p=dist/name
        require(p.is_file() and digest(p.read_bytes())==expected,'Generated file differs: '+name)
    require(manifest['files']['assets/atlas-scoped.css']==receipt['new_css_sha256'],'CSS not pinned')
    require(manifest['files']['fv-ex2-apollo-r224.php']==receipt['new_adapter_sha256'],'PHP not pinned')
    original=(dist/'templates/atlas-fragment.html').read_text()
    php_html,php=parent.run_php(parent_gate.with_name('wp_lifecycle_shim.php'),dist)
    require(php_html==original,'PHP output changed from immutable NASA evidence HTML')
    require(php['mutation_css-bytes']['detected'] and php['mutation_crosswalk']['detected'],'Fail-open corruption gate not passed')
    css=(dist/'assets/atlas-scoped.css').read_text()
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        version=browser.version
        try:
            for width in WIDTHS:
                for js in (False,True):
                    mode='js' if js else 'nojs'
                    context=browser.new_context(viewport={'width':width,'height':840},
                        device_scale_factor=1,java_script_enabled=js,
                        has_touch=width<=390,is_mobile=width<=390,
                        reduced_motion='reduce' if width==320 else 'no-preference',
                        forced_colors='active' if width==768 else 'none')
                    page=context.new_page();outbound=[]
                    page.on('request',lambda r: outbound.append(r.url))
                    document=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                              '<meta name="viewport" content="width=device-width,initial-scale=1">'
                              '<style>'+css+'</style></head><body>'+php_html+'</body></html>')
                    page.set_content(document,wait_until='load')
                    require(not outbound,'Unexpected outbound browser request')
                    require(page.locator('.fv-apollo-atlas').count()==1,'Atlas missing')
                    require(page.locator(f'a[href="{FREE}"]').count()==1,'Free investigation CTA duplicated')
                    selectors=('.fv-apollo-trace-grid li p > a[href^="#"],'
                               '.fv-apollo-custody-list li > p > a')
                    cards=page.locator(selectors)
                    require(cards.count()>=10,'Expected at least ten source-navigation links')
                    rectangles=[]
                    for i in range(cards.count()):
                        link=cards.nth(i);box=link.bounding_box()
                        require(box and box['height']>=43.9 and box['width']>=24,
                            f'{width}/{mode} source navigation target {i}: {box}')
                        rectangles.append(round(box['height'],2))
                    require(page.locator('details > summary').count()>=4,'Native source details missing')
                    # Capture the pristine rendered state BEFORE input/focus; touch focus painting
                    # can vary with host compositor and must not pollute deterministic screenshots.
                    shot=out/f'{width}-{mode}.png'
                    page.screenshot(path=str(shot),animations='disabled',full_page=True)
                    first=page.locator('details > summary').first
                    first.focus()
                    if width<=390 and not js:first.tap()
                    else:page.keyboard.press('Enter')
                    require(first.evaluate('(e)=>e.parentElement.open'),'Native disclosure input failed')
                    require(page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')<=1,
                            f'{width} horizontal overflow')
                    ax=page.locator(f'a[href="{FREE}"]').aria_snapshot()
                    require('link' in ax.lower(),'Free CTA lost native link role')
                    require(page.locator('script').count()==0,'Unexpected script in page')
                    # Displayed photo records and technical source crosswalk still derive from unchanged HTML.
                    require(page.locator('a[data-authority="nasa-apollo-204-board"]').count()==4,
                            'Technical NASA source binding drift')
                    results.append({'width':width,'javascript':js,'touch':width<=390,
                        'native_keyboard':True,'source_links':cards.count(),
                        'min_source_nav_height_css_px':min(rectangles),
                        'screenshot_sha256':digest(shot.read_bytes()),
                        'remote_requests':len(outbound),'forced_colors':width==768})
                    context.close()
        finally:browser.close()
    result={'status':'PASS','source':'R228 exact generated PHP/CSS','chromium_version':version,
        'input_manifest_sha256':receipt['new_manifest_sha256'],
        'browser':results,'php_lifecycle_cases':9,'php_corruption_cases':5,
        'source_text_unchanged':True,'genuine_axe_core':'NOT_EXECUTED: package unavailable offline',
        'field_lcp_cls':'NOT_MEASURED: no installed host/production navigation',
        'actual_browser_zoom':'NOT_TESTED',
        'limits':['Playwright page.set_content; no real HTTP/WordPress host',
                  'PHP function shim, not installed Assembler/WordPress',
                  'No real payment, product checkout, creator ID or revenue evidence',
                  'R198 inherited ancestry unresolved; CI/independent QA/founder release pending']}
    (out/'receipt.json').write_bytes(dump(result))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dist',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--parent-gate',type=Path,default=Path(__file__).resolve().parents[2]/'apollo-r227/qa/wp_lifecycle_browser_gate.py')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    result=run(a.dist.resolve(),a.out.resolve(),a.parent_gate.resolve())
    print('PASS:',len(result['browser']),'Chromium contexts, 9 PHP scenarios, 5 tamper tests')
    print('SHA256:',digest((a.out/'receipt.json').read_bytes()))
