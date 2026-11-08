#!/usr/bin/env python3
"""Isolated FV seven-chapter QA: execute real review PHP with WP stubs, then Chromium.
Does NOT execute WordPress core/Assembler/Jetpack and MUST NOT be treated as release approval.
Requires: PHP CLI, Python Playwright, installed Chromium, protected review ZIP (not in Git).
Usage: python verify_php_playground_renderer_browser.py --bundle path.zip --out ./qa-evidence
"""
import argparse, asyncio, hashlib, json, subprocess, tempfile, zipfile
from pathlib import Path
from playwright.async_api import async_playwright

PLUGIN = 'mu-plugins/fv-ex2-playground-review.php'
PIN = '7fe27aecc6f5f2b8033ab826dcb5146b6e31ae4dbcaf2a7825859b48dc5b51ee'
PHP_STUB = r'''<?php
// Isolated stub, not WordPress. No DB/CMS/network writes.
define('ABSPATH', '/tmp/fv-php-stub/');
define('WP_ENVIRONMENT_TYPE', 'development');
$GLOBALS['actions']=[]; $GLOBALS['shortcodes']=[]; $GLOBALS['css']=[]; $GLOBALS['js']=[];
function home_url($x=''){return 'http://localhost:9913/'.ltrim($x,'/');}
function wp_parse_url($u,$p=-1){return parse_url($u,$p);}
function get_option($key,$fallback=''){return $key==='fv_ex2_playground_review_only'?'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1':$fallback;}
function is_page($p){return $p==='fv-ex2-review';}
function add_action($h,$fn){$GLOBALS['actions'][$h][]=$fn;}
function add_shortcode($t,$fn){$GLOBALS['shortcodes'][$t]=$fn;}
function wp_register_style(...$x){} function wp_enqueue_style(...$x){}
function wp_add_inline_style($h,$s){$GLOBALS['css'][]=$s;}
function wp_register_script(...$x){} function wp_enqueue_script(...$x){}
function wp_add_inline_script($h,$s){$GLOBALS['js'][]=$s;}
require $argv[1];
if (!isset($GLOBALS['shortcodes']['fv_ex2_playground']))throw new RuntimeException('Preview registration denied');
foreach ($GLOBALS['actions']['wp_enqueue_scripts']??[] as $cb)$cb();
$body=$GLOBALS['shortcodes']['fv_ex2_playground']();
if (!str_contains($body,'data-fv-home-flagship')||strlen($body)<10000)throw new RuntimeException('Incomplete PHP render');
$html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0;background:#0a0a09}</style><style>'.implode("\n",$GLOBALS['css']).'</style></head><body>'.$body.'<script>'.implode("\n",$GLOBALS['js']).'</script></body></html>';
file_put_contents($argv[2],$html);
echo json_encode(['html_bytes'=>strlen($html),'body_bytes'=>strlen($body),'css_bytes'=>strlen(implode("\n",$GLOBALS['css'])),'js_bytes'=>strlen(implode("\n",$GLOBALS['js']))]);
'''

async def test_browser(html, out, checks):
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        version=browser.version
        for w in [320,360,390,768,1440,1920]:
            for enabled in [True,False]:
                ctx=await browser.new_context(viewport={'width':w,'height':900},java_script_enabled=enabled,reduced_motion='reduce')
                await ctx.route('**/*',lambda route:route.abort() if route.request.url.startswith(('https:','http:')) else route.continue_())
                page=await ctx.new_page(); errors=[]
                page.on('pageerror', lambda e:errors.append(str(e)))
                await page.set_content(html,wait_until='load');await page.wait_for_timeout(70)
                state=await page.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,
                    chapters:[...document.querySelectorAll('.fv-hf__chapter-nav a')].map(a=>({target:a.getAttribute('href'),found:!!document.querySelector(a.getAttribute('href'))})),
                    focus:!!document.querySelector('.fv-hf__text-link--focus'),
                    margins:document.querySelectorAll('.fv-margin-strip__item').length,
                    images:document.querySelectorAll('[data-fv-archive-img]').length})''')
                prefix=f'{w}/{"js" if enabled else "nojs"}'
                checks.append({'test':prefix+'/no_horizontal_overflow','pass':state['scroll']<=w+2,'observation':state['scroll']})
                checks.append({'test':prefix+'/seven_live_anchors','pass':len(state['chapters'])==7 and all(x['found'] for x in state['chapters'])})
                checks.append({'test':prefix+'/focus_path','pass':state['focus']})
                checks.append({'test':prefix+'/no_pageerror','pass':not errors,'observation':errors})
                if w==390 and enabled:
                    checks.append({'test':'preserve_72_margins','pass':state['margins']==72,'observation':state['margins']})
                    checks.append({'test':'rights_hold_two_archive_images','pass':state['images']==2,'observation':state['images']})
                    for selector,chosen in [('[data-fv-case-button]',1),('[data-fv-chronicle-view]',1),('[data-fv-observer-switch]',1)]:
                        controls=page.locator(selector)
                        if await controls.count()>chosen:
                            await controls.nth(chosen).click()
                            if 'chronicle' in selector:
                                actual=await page.locator('[data-fv-chronicle-mode]').first.get_attribute('data-fv-chronicle-mode')
                                okay=actual in ('1848','later','addition')
                            else:
                                actual=await controls.nth(chosen).get_attribute('aria-pressed')
                                okay=actual=='true'
                            checks.append({'test':'interaction/'+selector,'pass':okay,'observation':actual})
                        else: checks.append({'test':'interaction/'+selector,'pass':False,'observation':'control absent'})
                    summary=page.locator('.fv-hf details summary').last
                    await summary.click()
                    checks.append({'test':'interaction/details','pass':await page.locator('.fv-hf details[open]').count()>=1})
                    await page.evaluate('document.documentElement.style.zoom="2";scrollTo(0,0)')
                    z=await page.evaluate('''() => ({w:innerWidth,scroll:document.documentElement.scrollWidth})''')
                    checks.append({'test':'200pct_css_zoom_no_overflow','pass':z['scroll']<=z['w']+2,'observation':z})
                    await page.screenshot(path=str(out/'php_390_css_zoom200.png'))
                elif w==390:
                    await page.screenshot(path=str(out/'php_390_nojs.png'))
                if enabled and w in (390,1440):
                    if w==390:await page.evaluate('document.documentElement.style.zoom="1";scrollTo(0,0)')
                    await page.screenshot(path=str(out/f'php_{w}_js.png'))
                await ctx.close()
        await browser.close()
        return version

def run():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.bundle) as z:
        data=z.read(PLUGIN)
    digest=hashlib.sha256(data).hexdigest()
    if digest!=PIN: raise SystemExit('HOLD: protected PHP renderer SHA mismatch; no execution')
    with tempfile.TemporaryDirectory(prefix='fv-ex2-php-stub-') as tmp:
        tmp=Path(tmp);src=tmp/'plugin.php';src.write_bytes(data)
        stub=tmp/'stub.php';stub.write_text(PHP_STUB)
        dest=tmp/'rendered.html'
        run=subprocess.run(['php',str(stub),str(src),str(dest)],capture_output=True,text=True,check=True)
        meta=json.loads(run.stdout);html=dest.read_text()
    checks=[]
    chromium=asyncio.run(test_browser(html,args.out,checks))
    result={'scope':'PHP renderer exercised through simulated WordPress callbacks; real Chromium; NOT WordPress core or hosted acceptance',
            'source_sha256':digest,'zip_sha256':hashlib.sha256(args.bundle.read_bytes()).hexdigest(),
            'rendered_sha256':hashlib.sha256(html.encode()).hexdigest(),'php':meta,'chromium':chromium,
            'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks,
            'release':'HOLD','missing':['native WordPress core/Assembler','actual image response bytes','axe/WCAG','true browser zoom/screen-reader testing','hosted Lighthouse/CWV','live Jetpack signup truth','merchant-confirmed conversions','CI/QD/founder approval']}
    (args.out/'results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ('source_sha256','chromium','passed','failed','release')}))
    if result['failed']: raise SystemExit(1)
if __name__=='__main__':run()
