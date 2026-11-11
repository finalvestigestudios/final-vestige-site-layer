#!/usr/bin/env python3
"""R278: real R277 PHP under six isolated sibling states, then actual Chromium.
Offline DOM simulation is NOT installed WordPress or browser-over-HTTP QA.
"""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve()
ROOT=HERE.parents[2]
SRC=ROOT/'apollo-r277'/'apollo-review-shortcode.php'
REAL=ROOT/'apollo-r273'/'review-custody.php'
CSS=ROOT/'apollo-r273'/'assets/review-custody.css'
NASA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r278')
OUT.mkdir(parents=True,exist_ok=True)
states={
 'source_missing':None,
 'source_empty_php':'<?php /* partial file */\n',
 'source_wrong_symbol':'<?php function unrelated_function() {}\n',
 'source_parse_error':'<?php function broken( {\n',
 'source_throws':'<?php throw new RuntimeException("secret path /tmp/evidence");\n',
 'source_renderer_exception':"<?php function fv_ex2_r273_review_panel($records){ throw new RuntimeException(\"secret path /tmp/evidence\"); }\n",
 'source_renderer_type_error':"<?php function fv_ex2_r273_review_panel($records):string { return []; }\n",
 'source_renderer_null':"<?php function fv_ex2_r273_review_panel($records){ return null; }\n",
 'source_renderer_empty':"<?php function fv_ex2_r273_review_panel($records){ return \"\"; }\n",
 'source_echo_leak':"<?php echo \"LEAKED_SIBLING_TEXT\"; function unrelated_function() {}\n",
 'source_renderer_echo_and_exception':"<?php function fv_ex2_r273_review_panel($records){ echo \"LEAKED_SIBLING_TEXT\"; throw new RuntimeException(\"secret path /tmp/evidence\"); }\n",
 'source_renderer_extra_merchant':"<?php function fv_ex2_r273_review_panel($records){ return '<aside class=\"fv-r273\" data-fv-review-ready=\"false\"><a href=\"https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/\">NASA 1</a><a href=\"https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/\">NASA 2</a><a href=\"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/\">FREE</a><a href=\"https://merchant.invalid/buy\">BUY</a></aside>'; }\n",
 'source_renderer_inline_script':"<?php function fv_ex2_r273_review_panel($records){ return '<aside class=\"fv-r273\" data-fv-review-ready=\"false\"><a href=\"https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/\">NASA 1</a><a href=\"https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/\">NASA 2</a><a href=\"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/\">FREE</a><script>alert(1)</script></aside>'; }\n",
 'source_original':REAL.read_text(),
}
php_fixture="""<?php
define('ABSPATH','/offline-test/');
function add_action($a,$b,$c=10){}
function add_shortcode($a,$b){}
function plugins_url($a,$b){return '/assets/review-custody.css';}
function wp_style_is($a,$b){return true;}
require __DIR__.'/apollo-r277/apollo-review-shortcode.php';
echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://merchant.invalid/buy']);
"""
php_pass=[]; html_cases={}
with tempfile.TemporaryDirectory(prefix='apollo-r278-') as d:
  root=Path(d)/'experience2'
  (root/'apollo-r273').mkdir(parents=True)
  (root/'apollo-r277').mkdir()
  shutil.copyfile(SRC,root/'apollo-r277'/'apollo-review-shortcode.php')
  (root/'fixture.php').write_text(php_fixture)
  for name,source in states.items():
    target=root/'apollo-r273'/'review-custody.php'
    if source is None:target.unlink(missing_ok=True)
    else:target.write_text(source)
    proc=subprocess.run(['php',str(root/'fixture.php')],capture_output=True,text=True)
    assert proc.returncode==0,(name,proc.stderr)
    html=proc.stdout; html_cases[name]=html
    assert NASA in html and FREE in html,name
    assert 'merchant.invalid' not in html and 'secret path' not in html and 'LEAKED_SIBLING_TEXT' not in html and '<script' not in html,name
    assert ('data-fv-review-ready="false"' in html) if name=='source_original' else ('The review panel is unavailable' in html),name
    assert html.count('href=')==(3 if name=='source_original' else 2),name
    php_pass.append(name)
browser_cases=[];screens={}
with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,html in html_cases.items():
    for width,js in ((320,True),(390,False),(768,True),(1440,False),(1920,True)):
      ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=width<400)
      page=ctx.new_page();req=[];page.on('request',lambda r:req.append(r.url))
      style='<style>'+CSS.read_text()+'</style>' if name=='source_original' else ''
      page.set_content('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+style+'<body>'+html+'</body></html>',wait_until='domcontentloaded',timeout=5000)
      assert page.locator('a[href="'+FREE+'"]').count()==1
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(name,width)
      if name=='source_original':
        assert page.get_by_role('heading',name='Editorial review remains open').count()==1
        page.locator('summary').focus();page.keyboard.press('Enter')
        assert page.locator('a[href="'+NASA+'"]').first.is_visible()
      else:
        assert page.get_by_role('complementary',name='Apollo 1 research custody').count()==1
        assert page.get_by_role('link',name='NASA Apollo 204 Review Board report').count()==1
      assert not req,(name,req)
      if width==390 and not js and name in ('source_original','source_wrong_symbol'):
        filename=name+'-390-nojs.png';f=OUT/filename
        page.screenshot(path=str(f),full_page=False,animations='disabled',timeout=5000)
        screens[filename]=hashlib.sha256(f.read_bytes()).hexdigest()
      browser_cases.append({'case':name,'width':width,'js':js,'pass':True})
      ctx.close()
  browser.close()
receipt={'php_cases':php_pass,'chromium_cases':browser_cases,'screenshot_sha256':screens,
 'http_browser_csp':'BLOCKED_BY_ADMINISTRATOR','axe_core':'NOT_EXECUTED',
 'installed_wordpress':'NOT_TESTED','production_release':'HARD_HOLD'}
f=OUT/'receipt.json';f.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(f'R279 PHP {len(php_pass)}/{len(php_pass)} PASS; Chromium {len(browser_cases)}/{len(browser_cases)} PASS; receipt SHA-256 {hashlib.sha256(f.read_bytes()).hexdigest()}')
