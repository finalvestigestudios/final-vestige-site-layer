#!/usr/bin/env python3
"""Execute the EXACT unpublished EX2 PHP MU-plugin in PHP CLI using WP API stubs.
Not a WordPress/Assembler, axe, Lighthouse, real-media, or production acceptance test.
Run: python3 experience2/home-flagship/playground/verify_php_shortcode_execution.py
"""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
BLUEPRINT = HERE / 'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json'
STUB = '''<?php
// Test-only substitutes; DOES NOT create a WordPress site or database.
define('ABSPATH','/fv-isolated-test/');
$GLOBALS['s']=['enabled'=>$argv[2]==='1','page'=>$argv[3]==='1','hooks'=>[],'shortcodes'=>[],'css'=>[],'js'=>[]];
function get_option($k,$default=''){return $GLOBALS['s']['enabled']?'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1':$default;}
function is_page($slug){return $slug==='fv-ex2-review' && $GLOBALS['s']['page'];}
function add_action($name,$fn){$GLOBALS['s']['hooks'][$name][]=$fn;}
function add_shortcode($name,$fn){$GLOBALS['s']['shortcodes'][$name]=$fn;}
function wp_register_style(...$args){} function wp_enqueue_style(...$args){}
function wp_register_script(...$args){} function wp_enqueue_script(...$args){}
function wp_add_inline_style($handle,$css){$GLOBALS['s']['css'][]=$css;}
function wp_add_inline_script($handle,$js){$GLOBALS['s']['js'][]=$js;}
include $argv[1];
foreach(($GLOBALS['s']['hooks']['wp_enqueue_scripts']??[]) as $fn){$fn();}
$fn=$GLOBALS['s']['shortcodes']['fv_ex2_playground']??null;
echo json_encode(['html'=>$fn?$fn():'','css'=>implode('',$GLOBALS['s']['css']),'js'=>implode('',$GLOBALS['s']['js'])],JSON_THROW_ON_ERROR);
'''

def segment(src,kind):
    start=f"<<<'FVPG_{kind}_END'\n"; end=f'\nFVPG_{kind}_END'
    assert src.count(start)==src.count(end)==1,kind
    return src.split(start,1)[1].split(end,1)[0]

def run():
    source=json.loads(BLUEPRINT.read_text())['steps'][2]['data']
    assert 'fv_ex2_playground_review_only' in source
    results=[]
    with tempfile.TemporaryDirectory(prefix='fv-ex2-php-') as td:
        td=Path(td);(td/'plugin.php').write_text(source);(td/'stub.php').write_text(STUB)
        lint=subprocess.run(['php','-l',str(td/'plugin.php')],capture_output=True,text=True,check=True)
        assert 'No syntax errors' in lint.stdout
        def exec_php(guard,page):
            p=subprocess.run(['php',str(td/'stub.php'),str(td/'plugin.php'),str(int(guard)),str(int(page))],capture_output=True,text=True,timeout=20,check=True)
            return json.loads(p.stdout)
        actual=exec_php(True,True)
        for k in ['HTML','CSS','JS']:
            assert actual[k.lower()]==segment(source,k),f'PHP emitted altered {k}'
            results.append(f'php_exact_{k.lower()}')
        assert actual['html'].count('class="fv-margin-strip__item"')==72
        assert actual['html'].count('href="https://finalvestige.com/focus/"')==5
        assert actual['html'].count('class="fv-hf__chapter-nav"')==1
        assert 'DESIGN CANDIDATE · NOT LIVE' in actual['html']
        results.append('72_records_7_chapters_5_focus_nonlive')
        for enabled,page in [(False,True),(True,False),(False,False)]:
            bad=exec_php(enabled,page)
            assert all(not bad[k] for k in ['html','css','js']),(enabled,page)
            results.append(f'isolation_guard_{int(enabled)}_{int(page)}')
        html='<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+actual['css']+'</style><main>'+actual['html']+'</main><script>'+actual['js']+'</script></html>'
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for width,height in [(320,568),(360,640),(390,667),(768,900),(1440,900),(1920,900)]:
                for no_js in [False,True]:
                    ctx=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=not no_js,reduced_motion='reduce' if no_js else 'no-preference')
                    ctx.route('**/*',lambda route:route.abort()) # No external media requests succeed.
                    page=ctx.new_page(); errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                    page.set_content(html,wait_until='domcontentloaded');page.wait_for_timeout(100)
                    m=page.evaluate('''() => {let a=document.querySelector('.fv-hf__opening-actions a[href*="/focus/"]').getBoundingClientRect();let ids=new Set([...document.querySelectorAll('[id]')].map(x=>x.id));return {scroll:document.documentElement.scrollWidth,records:document.querySelectorAll('.fv-margin-strip__item').length,chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length,badanchors:[...document.querySelectorAll('a[href^="#"]')].filter(x=>!ids.has(x.hash.slice(1))).length,top:a.top,bottom:a.bottom,height:a.height}}''')
                    assert m['scroll']<=width+1 and m['records']==72 and m['chapters']==7 and m['badanchors']==0 and m['height']>=44 and not errors,(width,no_js,m,errors)
                    if width==390:assert m['bottom']<=height,(no_js,m)
                    results.append(f'chromium_php_{width}_{"nojs" if no_js else "js"}')
                    ctx.close()
            browser.close()
    print(json.dumps({'PASS':len(results),'blueprint_sha256':hashlib.sha256(BLUEPRINT.read_bytes()).hexdigest(),'scope':'real PHP CLI with WordPress stubs + static Chromium, NOT WordPress/Assembler/WCAG/Lighthouse','checks':results},indent=2))

if __name__=='__main__':run()
