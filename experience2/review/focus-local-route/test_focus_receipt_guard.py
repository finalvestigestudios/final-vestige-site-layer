#!/usr/bin/env python3
"""Offline integration regression: protected PHP shortcode/filter/footer + Chromium.
NOT native WordPress Core, real network navigation, image bytes or Jetpack.
"""
import argparse,asyncio,io,json,subprocess,tempfile,zipfile
from pathlib import Path
from playwright.async_api import async_playwright
from repair_focus_receipt import build,RECEIPT

STUB='''<?php
define('ABSPATH','/isolated/');define('WP_ENVIRONMENT_TYPE','development');
$GLOBALS['actions']=[];$GLOBALS['filters']=[];$GLOBALS['shortcodes']=[];$GLOBALS['css']=[];$GLOBALS['js']=[];
function home_url($p=''){return 'https://wpsandbox.wordpress.net/'.ltrim($p,'/');}
function wp_parse_url($u,$p=-1){return parse_url($u,$p);}
function get_option($k,$f=''){return $k==='fv_ex2_playground_review_only'?'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1':$f;}
function is_page($p){return $p==='fv-ex2-review';}
function add_action($n,$fn,$p=10){$GLOBALS['actions'][$n][]=$fn;}
function add_filter($n,$fn,$p=10,$a=1){$GLOBALS['filters'][$n][]=$fn;}
function add_shortcode($n,$fn){$GLOBALS['shortcodes'][$n]=$fn;}
function esc_url($s){return $s;}
function wp_register_style(...$a){} function wp_enqueue_style(...$a){}
function wp_add_inline_style($h,$s){$GLOBALS['css'][]=$s;}
function wp_register_script(...$a){} function wp_enqueue_script(...$a){}
function wp_add_inline_script($h,$s){$GLOBALS['js'][]=$s;}
require $argv[1];require $argv[2];require $argv[3];
foreach($GLOBALS['actions']['wp_enqueue_scripts']??[] as $f)$f();
$body=$GLOBALS['shortcodes']['fv_ex2_playground']();
foreach($GLOBALS['filters']['do_shortcode_tag']??[] as $f)$body=$f($body,'fv_ex2_playground',[],[]);
ob_start();foreach($GLOBALS['actions']['wp_footer']??[] as $f)$f();$footer=ob_get_clean();
file_put_contents($argv[4],'<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><base href="https://wpsandbox.wordpress.net/fv-ex2-review/"><style>html,body{margin:0}</style><style>'.implode("\n",$GLOBALS['css']).'</style></head><body><div class="wp-site-blocks">'.$body.'</div><script>'.implode("\n",$GLOBALS['js']).'</script>'.$footer.'</body></html>');
'''

def render(z):
 with tempfile.TemporaryDirectory() as d:
  d=Path(d)
  with zipfile.ZipFile(io.BytesIO(z)) as pack:
   for source,dest in [('mu-plugins/fv-ex2-playground-review.php','home.php'),('mu-plugins/fv-ex2-focus-local-route.php','route.php'),(RECEIPT,'receipt.php')]: (d/dest).write_bytes(pack.read(source))
  (d/'stub.php').write_text(STUB)
  call=subprocess.run(['php',str(d/'stub.php'),str(d/'home.php'),str(d/'route.php'),str(d/'receipt.php'),str(d/'page.html')],capture_output=True,text=True)
  if call.returncode:raise RuntimeError(call.stderr)
  return (d/'page.html').read_text()

async def verify(parent):
 fixed,old,new=build(parent)
 assert old!=new
 before=render(parent);after=render(fixed)
 count=0
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for w,h in [(320,568),(390,667),(768,1024),(1440,900)]:
   for js in (True,False):
    context=await browser.new_context(viewport={'width':w,'height':h},java_script_enabled=js)
    await context.route('**/*',lambda r:r.abort())
    page=await context.new_page();await page.set_content(after)
    assert await page.locator('.fv-margin-strip__item').count()==72
    assert await page.locator('.fv-hf__chapter-nav a').count()==7
    assert await page.locator('[data-fv-ex2-isolated-focus]').count()==5
    count+=3
    if js:
     await page.locator('#fv-ex2-run').evaluate('(e)=>e.click()')
     r=json.loads(await page.locator('#fv-ex2-receipt-output').inner_text())
     assert r['focus_destinations']==5 and not any(k.startswith('FOCUS_') for k in r['blockers'])
     count+=1
    await context.close()
  context=await browser.new_context(viewport={'width':390,'height':667})
  await context.route('**/*',lambda r:r.abort())
  page=await context.new_page();await page.set_content(before)
  await page.locator('#fv-ex2-run').evaluate('(e)=>e.click()')
  r=json.loads(await page.locator('#fv-ex2-receipt-output').inner_text())
  assert r['focus_destinations']==0 and 'FOCUS_LINKS_NOT_5' in r['blockers'];count+=1
  for code,expected in [
   ("a.href='https://finalvestige.com/focus/'",'FOCUS_PRODUCTION_LEAK'),
   ("a.removeAttribute('data-fv-ex2-isolated-focus')",'FOCUS_LOCAL_UNMARKED_LINK'),
   ("a.href+='?subscribe=anything'",'FOCUS_LOCAL_LINKS_NOT_5_OR_INVALID'),
   ("a.parentNode.appendChild(a.cloneNode(true))",'FOCUS_LOCAL_LINKS_NOT_5_OR_INVALID'),
   ("a.href='https://attacker.invalid/fv-ex2-focus-review/'",'FOCUS_LOCAL_LINKS_NOT_5_OR_INVALID')]:
   await page.set_content(after)
   await page.evaluate("() => {let a=document.querySelector('a[data-fv-ex2-isolated-focus]');"+code+";}")
   await page.locator('#fv-ex2-run').evaluate('(e)=>e.click()')
   r=json.loads(await page.locator('#fv-ex2-receipt-output').inner_text())
   assert expected in r['blockers'],(code,r['blockers']);count+=1
  await context.close();await browser.close()
 return count
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--parent',required=True,type=Path);args=ap.parse_args()
 n=asyncio.run(verify(args.parent.read_bytes()));print(json.dumps({'passed':n,'failed':0,'scope':'WP stubs + Chromium; no WordPress Core, media or Jetpack'}))
