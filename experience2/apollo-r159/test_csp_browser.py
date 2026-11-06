#!/usr/bin/env python3
"""Offline CSP/SRI browser acceptance for the exact PHP-generated R159 staging candidate.

No actual WordPress, site network, or server. Chromium HTTP/file navigation is
blocked by the runtime; only asset transport URLs are substituted with byte-
identical data: URLs. Thus this does NOT test WordPress same-origin CSP policy.
"""
import argparse
import base64
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HOST='https://fv-apollo-staging.invalid'
PREFIX='/wp-content/plugins/fv-apollo-r159/'
WIDTHS=(320,360,390,768,1440,1920)
HARNESS=r'''<?php
define('ABSPATH', __DIR__);
function esc_url($x) { return htmlspecialchars($x, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function esc_attr($x) { return htmlspecialchars($x, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function plugins_url($path, $file) { return 'https://fv-apollo-staging.invalid/wp-content/plugins/fv-apollo-r159/'.ltrim($path,'/'); }
function add_shortcode($name,$callback) { $GLOBALS['shortcodes'][$name]=$callback; }
require __DIR__.'/fv-apollo-r159/fv-apollo-research-desk.php';
$markup=fv_apollo_r159_shortcode();
$again=getenv('R159_TWICE') ? fv_apollo_r159_shortcode() : '';
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo review</title></head><body><a id="outside" href="#fv-ex2-ledger-apollo1-record-05">Jump to fire evidence</a><main>'.$markup.$again.'</main></body></html>';
'''

def sha(x): return hashlib.sha256(x).hexdigest()

def run(args):
    out=Path(args.out)
    if out.exists(): raise RuntimeError('Output directory exists; cannot overwrite test evidence')
    out.mkdir(parents=True)
    source=out/'php-source'
    with zipfile.ZipFile(args.package) as z:
        for item in z.infolist():
            target=source/item.filename
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(item.filename))
    php_file=source/'fv-apollo-r159/fv-apollo-research-desk.php'
    (source/'index.php').write_text(HARNESS)
    syntax=subprocess.run(['php','-l',str(php_file)],capture_output=True,text=True)
    assert syntax.returncode==0,syntax.stdout+syntax.stderr
    def render(twice=False):
        env={**os.environ,'R159_TWICE':'1' if twice else ''}
        x=subprocess.run(['php','-f',str(source/'index.php')],capture_output=True,text=True,env=env)
        assert x.returncode==0,x.stdout+x.stderr
        return x.stdout
    html=render()
    twice=render(True)
    css=(source/'fv-apollo-r159/assets/research-desk.css').read_bytes()
    js=(source/'fv-apollo-r159/assets/research-desk.js').read_bytes()
    receipt=[];errors=[];screens=[];labs=[]
    def check(width,name,val): receipt.append({'width':width,'check':name,'pass':bool(val)})
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
        def context(width,nojs=False,touch=False):
            return browser.new_context(viewport={'width':width,'height':850},java_script_enabled=not nojs,reduced_motion='reduce',has_touch=touch)
        def offline_html(rendered, mutate_js=False):
            # Chromium cannot navigate HTTP/file in this sandbox. Preserve PHP
            # output but replace asset URL transport with SRI-protected data URLs.
            js_bytes=js+b'\n//unexpected mutation' if mutate_js else js
            css_url='data:text/css;base64,'+base64.b64encode(css).decode()
            js_url='data:text/javascript;base64,'+base64.b64encode(js_bytes).decode()
            return (rendered.replace(HOST+PREFIX+'assets/research-desk.css',css_url)
                    .replace(HOST+PREFIX+'assets/research-desk.js',js_url)
                    .replace('<head>','<head><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; script-src data:; style-src data:; img-src data:; connect-src &#39;none&#39;; object-src &#39;none&#39;">',1))
        for width in WIDTHS:
            c=context(width,nojs=True)
            page=c.new_page();page.set_content(offline_html(html),wait_until='load')
            check(width,'nojs_six_visible',page.locator('[data-fvx-record]:visible').count()==6)
            check(width,'nojs_native_chronology',page.locator('.fv-ex2-ledger__rail-list a').count()==4)
            check(width,'nojs_source_drawer_present',page.locator('[data-fvx-source-drawer]').count()==1)
            check(width,'nojs_evidence_cta_present',page.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count()==1)
            check(width,'nojs_no_horizontal_scroll',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
            c.close()
            c=context(width,touch=(width==390));page=c.new_page()
            page.on('pageerror',lambda e,w=width: errors.append({'width':w,'type':'runtime','message':str(e)}))
            page.on('console',lambda m,w=width: errors.append({'width':w,'type':'console','message':m.text}) if m.type=='error' else None)
            # set_content doesn't run add_init_script on about:blank. Observe
            # the original document before injecting source, no network timing.
            page.evaluate("""()=>{window.__qa={lcp:[],cls:[]};try{new PerformanceObserver(list=>{for(const x of list.getEntries())window.__qa.lcp.push(x.startTime)}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(list=>{for(const x of list.getEntries())if(!x.hadRecentInput)window.__qa.cls.push(x.value)}).observe({type:'layout-shift',buffered:true});}catch(e){window.__qa.failure=String(e)}}""")
            page.set_content(offline_html(html),wait_until='load')
            check(width,'external_css_link_single',page.locator('link#fv-apollo-r159-css[href^="data:text/css;base64,"]').count()==1)
            check(width,'external_js_script_single',page.locator('script#fv-apollo-r159-js[src^="data:text/javascript;base64,"]').count()==1)
            check(width,'no_inline_style_script',page.locator('style#fv-apollo-r158-css,script#fv-apollo-r158-js').count()==0)
            check(width,'csp_data_transport_js_runs',page.locator('[data-fvx-initialized="yes"]').count()==1)
            check(width,'csp_css_computed',page.evaluate("getComputedStyle(document.querySelector('[data-fvx-tools]')).display")!='none')
            check(width,'six_records',page.locator('[data-fvx-record]').count()==6)
            check(width,'nasa_links_preserved',page.locator('a[href*="nasa.gov"]').count()>=6)
            check(width,'one_read_investigation_link',page.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count()==1)
            check(width,'no_checkout_offers',page.locator('a[href*="awin"],a[href*="payhip"],a[href*="checkout"]').count()==0)
            search=page.locator('input[data-fvx-search]');search.fill('S66-58038')
            check(width,'search_filters',0<page.locator('[data-fvx-record]:visible').count()<6)
            page.locator('#outside').click();page.wait_for_timeout(60)
            check(width,'external_fragment_reveals',page.locator('#fv-ex2-ledger-apollo1-record-05').is_visible())
            check(width,'external_fragment_focus',page.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-05')
            drawer=page.locator('[data-fvx-source-drawer]');drawer.locator('summary').focus();page.keyboard.press('Enter')
            check(width,'native_keyboard_drawer',drawer.get_attribute('open') is not None)
            check(width,'no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
            check(width,'reduced_motion',page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
            check(width,'no_browser_console_errors',not any(e['width']==width for e in errors))
            page.set_content(offline_html(html),wait_until='load')
            page.screenshot(path=str(out/f'r159-{width}.png'),full_page=True,animations='disabled')
            screens.append({'width':width,'sha256':sha((out/f'r159-{width}.png').read_bytes())})
            labs.append({'width':width,**page.evaluate('window.__qa || {}')})
            c.close()
        c=context(390);page=c.new_page();violations=[]
        page.on('console',lambda m: violations.append(m.text) if m.type=='error' else None)
        page.set_content(offline_html(html,mutate_js=True),wait_until='load')
        check(390,'tampered_script_browser_sri_blocked',page.locator('[data-fvx-initialized="yes"]').count()==0)
        check(390,'tampered_script_nojs_evidence_remains',page.locator('[data-fvx-record]:visible').count()==6)
        check(390,'tampered_script_integrity_error_reported',any('integrity' in m.lower() or 'digest' in m.lower() for m in violations))
        c.close()
        c=context(390);page=c.new_page();page.set_content(offline_html(twice),wait_until='load')
        check(390,'duplicate_has_one_js_asset',page.locator('script#fv-apollo-r159-js').count()==1)
        check(390,'duplicate_shortcodes_one_ledger',page.locator('[data-fvx-ledger]').count()==1)
        check(390,'duplicate_has_return_link',page.locator('a[href="#fv-apollo-r159-root"]').count()==1)
        c.close()
        bad=source/'fv-apollo-r159/assets/research-desk.js';bad.write_bytes(js+b'\n// mutation')
        fail=render()
        check('server','mutated_source_returns_fallback','Research Desk preview unavailable' in fail)
        check('server','mutated_source_omits_scripts','fv-apollo-r159-js' not in fail)
        check('server','mutated_source_original_link','the-hatch-opened-inward-apollo-1' in fail)
        bad.write_bytes(js)
        browser.close()
    with zipfile.ZipFile(args.package) as z:
        check('source','zip_php_source_preserved',php_file.read_bytes()==z.read('fv-apollo-r159/fv-apollo-research-desk.php'))
    check('source','js_unchanged_after_mutation',bad.read_bytes()==js)
    check('source','all_six_screenshots',len(screens)==len(WIDTHS))
    passed=sum(v['pass'] for v in receipt)
    data={'status':'PASS' if passed==len(receipt) else 'FAIL','checks':receipt,'passed':passed,'total':len(receipt),'screenshots':screens,'performance_lab_not_wp':labs,'browser_errors':errors,'csp_test_policy':'data: URLs (same-origin HTTP blocked by runtime); script-src data:; style-src data:','axe':'NOT_EXECUTED','wordpress':'PHP_EMULATION_ONLY','source_package_sha256':sha(Path(args.package).read_bytes())}
    (out/'receipt.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(f"{i['sha256']}  r159-{i['width']}.png\n" for i in screens))
    print(json.dumps({'passed':passed,'total':len(receipt),'status':data['status'],'browser_errors':len(errors),'screenshots':len(screens),'sri_blocked':any('digest' in v.lower() for v in violations)}))
    if passed!=len(receipt):
        print(json.dumps([c for c in receipt if not c['pass']],indent=2))
        raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--package',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--chromium',default='/usr/bin/chromium')
    run(p.parse_args())
