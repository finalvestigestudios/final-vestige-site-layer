#!/usr/bin/env python3
"""R158: real PHP shortcode output served to Chromium, emulated WP APIs ONLY (not a WP install)."""
import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,768,1440,1920)
HARNESS=r'''<?php
define('ABSPATH', __DIR__);
function esc_url($value) { return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
$GLOBALS['shortcodes']=array();
function add_shortcode($name,$cb) { $GLOBALS['shortcodes'][$name]=$cb; }
require __DIR__.'/fv-apollo-r158/fv-apollo-research-desk.php';
$markup=fv_apollo_r158_shortcode();
$duplicate=getenv('R158_TWICE') ? fv_apollo_r158_shortcode() : '';
header('Content-Type: text/html; charset=UTF-8');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><a href="#fv-ex2-ledger-apollo1-record-05" id="outside">Jump to fire evidence</a><main>'.$markup.$duplicate.'</main></body></html>';
'''
def sha(x): return hashlib.sha256(x).hexdigest()

def main(args):
    out=Path(args.out)
    if out.exists(): raise RuntimeError('Will not overwrite evidence directory')
    out.mkdir(parents=True)
    server_dir=out/'harness'
    with zipfile.ZipFile(args.package) as z:
        for f in z.infolist():
            target=server_dir/f.filename
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(f.filename))
    (server_dir/'index.php').write_text(HARNESS)
    php=os.getenv('PHP','php')
    lint=subprocess.run([php,'-l',str(server_dir/'fv-apollo-r158/fv-apollo-research-desk.php')],capture_output=True,text=True)
    assert lint.returncode==0,lint.stdout+lint.stderr
    check=[]; screenshots=[]; errors=[]; lab=[]
    def ok(width,name,condition):check.append({'width':width,'check':name,'pass':bool(condition)})
    # Emulate nested/reusable shortcode rendering AFTER the document head in actual PHP.
    # Chromium network loopback is blocked in this runtime, so render PHP with CLI and
    # inject its exact output into Chromium. This is NOT actual WordPress staging.
    def php_render(twice=False):
        env={**os.environ, 'R158_TWICE':'1' if twice else ''}
        run=subprocess.run([php,'-f',str(server_dir/'index.php')],capture_output=True,text=True,env=env)
        assert run.returncode==0,run.stderr
        return run.stdout
    html=php_render()
    duplicate_html=php_render(True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
        for width in WIDTHS:
            nojs=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=False,reduced_motion='reduce')
            raw=nojs.new_page();raw.set_content(html,wait_until='load')
            ok(width,'no_js_all_six_records',raw.locator('[data-fvx-record]:visible').count()==6)
            ok(width,'no_js_chronology_and_source_drawer',raw.locator('.fv-ex2-ledger__rail-list a:visible').count()==4 and raw.locator('[data-fvx-source-drawer]').count()==1)
            ok(width,'no_js_search_hidden',not raw.locator('[data-fvx-tools]').is_visible())
            ok(width,'no_js_contextual_cta',raw.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count()==1)
            nojs.close()
            ctx=browser.new_context(viewport={'width':width,'height':850},reduced_motion='reduce',has_touch=(width==390))
            page=ctx.new_page()
            page.on('pageerror',lambda exc,w=width: errors.append({'width':w,'error':str(exc)}))
            perf_script='''<script>(()=>{window.__apolloPerf={lcp:[],cls:[]};new PerformanceObserver(x=>{for(const e of x.getEntries())window.__apolloPerf.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window.__apolloPerf.cls.push(e.value)}).observe({type:'layout-shift',buffered:true})})()</script>'''
            htmlperf=html.replace('<head>','<head>'+perf_script,1)
            page.set_content(htmlperf,wait_until='load')
            ok(width,'exact_six_records',page.locator('[data-fvx-record]').count()==6)
            ok(width,'js_search_activated',page.locator('[data-fvx-initialized="yes"]').count()==1 and page.locator('[data-fvx-tools]').is_visible())
            ok(width,'inline_single_css_js',page.locator('style#fv-apollo-r158-css').count()==1 and page.locator('script#fv-apollo-r158-js').count()==1)
            ok(width,'no_unrelated_commercial_links',page.locator('a[href*="payhip"],a[href*="awin"],a[href*="checkout"]').count()==0)
            inp=page.locator('input[data-fvx-search]');inp.fill('S66-58038')
            ok(width,'search_finds_context',0 < page.locator('[data-fvx-record]:visible').count() < 6)
            page.locator('#outside').click();page.wait_for_timeout(35)
            ok(width,'external_anchor_reveals_target',page.locator('#fv-ex2-ledger-apollo1-record-05').is_visible())
            ok(width,'external_anchor_restores_focus',page.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-05')
            ok(width,'native_location_hash',page.evaluate('location.hash')=='#fv-ex2-ledger-apollo1-record-05')
            drawer=page.locator('[data-fvx-source-drawer]')
            drawer.locator('summary').focus();page.keyboard.press('Enter')
            ok(width,'keyboard_source_drawer',drawer.get_attribute('open') is not None)
            drawer.locator('summary').click()
            ok(width,'responsive_no_overflow',page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
            ok(width,'reduced_motion',page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
            ok(width,'no_runtime_error',not any(e['width']==width for e in errors))
            # Double shortcode emitted by the PHP stub, not simulated in JS.
            page.set_content(duplicate_html,wait_until='load')
            ok(width,'duplicate_shortcode_one_instance',page.locator('[data-fvx-ledger]').count()==1 and page.locator('script#fv-apollo-r158-js').count()==1)
            ok(width,'duplicate_shortcode_has_return_link',page.locator('a[href="#fv-apollo-r158-root"]').count()==1)
            page.set_content(htmlperf,wait_until='load')
            page.evaluate('''()=>{document.querySelectorAll('details').forEach(el=>el.open=false);document.activeElement?.blur();scrollTo(0,0)}''')
            page.wait_for_timeout(150)
            perf=page.evaluate('window.__apolloPerf')
            lab.append({'width':width,'last_lcp_ms':round(perf['lcp'][-1],2) if perf['lcp'] else None,'lab_cls':round(sum(perf['cls']),6),'scope':'PHP_CLI_HTML_INJECTED_NOT_WORDPRESS_FIELD'})
            filename=f'r158-php-{width}.png'
            screenshot=page.screenshot(path=str(out/filename),full_page=True,animations='disabled')
            screenshots.append({'file':filename,'width':width,'sha256':sha(screenshot)})
            ctx.close()
        browser.close()
    # Mutation proof: tamper the generated JS asset and rerun the actual PHP adapter.
    js=server_dir/'fv-apollo-r158/assets/research-desk.js'
    js.write_bytes(js.read_bytes()+b'\n/* deliberate QA mutation */\n')
    bad=php_render()
    ok('mutation','tampered_js_causes_safe_fallback','Research Desk preview unavailable' in bad and 'fv-ex2-ledger__grid' not in bad)
    ok('mutation','fallback_link_preserved','the-hatch-opened-inward-apollo-1' in bad)
    receipt={'scope':'REAL_PHP_OUTPUT_WORDPRESS_API_SHIM_NOT_WORDPRESS_STAGING','package_sha256':sha(Path(args.package).read_bytes()),'status':'STAGING_HOLD',
      'chrome':str(args.chromium),'axe':'NOT_EXECUTED_UNAVAILABLE','wp_theme':'NOT_TESTED','qualified_sessions':None,'paid_sales':None,
      'checks':check,'screenshots':screenshots,'lab':lab,'runtime_errors':errors,
      'summary':{'passed':sum(x['pass'] for x in check),'failed':sum(not x['pass'] for x in check)}}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (out/'SHA256SUMS').write_text(''.join(f"{x['sha256']}  {x['file']}\n" for x in screenshots))
    print(json.dumps(receipt['summary'],sort_keys=True))
    return int(receipt['summary']['failed']!=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',required=True);p.add_argument('--out',required=True);p.add_argument('--chromium',default='/usr/bin/chromium')
    raise SystemExit(main(p.parse_args()))
