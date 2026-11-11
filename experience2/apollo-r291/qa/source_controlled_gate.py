#!/usr/bin/env python3
"""R291 strict local PHP/Chromium native disclosure + print preservation gate.
No HTTP, installed WordPress, field CWV or axe-core is asserted by this test.
"""
from pathlib import Path
import hashlib, json, subprocess, sys
import fitz
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]/'apollo-r281'
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/r291-source-controlled-QA')
OUT.mkdir(parents=True,exist_ok=True)
php="""define('ABSPATH','/qa/');function add_action($a,$b,$c=10){} function add_shortcode($a,$b){}
function plugins_url($p,$f){return '/qa.css';}function wp_style_is($a,$b){return true;}
require 'apollo-source-experience.php';echo fv_r281_render();echo fv_r281_render();"""
r=subprocess.run(['php','-r',php],cwd=ROOT,capture_output=True,text=True,timeout=20)
assert r.returncode==0,r.stderr
css=(ROOT/'assets/apollo-source-experience.css').read_text()
html='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+r.stdout+'</body></html>'
assert r.stdout.count('class="fv-r291__authority-disclosure"')==2
checks=[];screens={};printed={}
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [320,390,768,1440,1920]:
        for js in [False,True]:
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                 reduced_motion='reduce',has_touch=width<=390,forced_colors='active' if width==320 else 'none')
            pg=ctx.new_page();network=[];pg.on('request',lambda q:network.append(q.url))
            pg.set_content(html)
            details=pg.locator('.fv-r291__authority-disclosure')
            assert details.count()==2 and details.evaluate_all('xs=>xs.every(x=>!x.open)')
            compact=pg.evaluate('document.documentElement.scrollHeight')
            summary=details.first.locator('summary');summary.focus();summary.press('Enter')
            assert details.first.evaluate('el=>el.open')
            summary.press('Enter');assert not details.first.evaluate('el=>el.open')
            jump=pg.locator('.fv-r281__authority-jump a').first
            dest=jump.get_attribute('href')[1:];jump.focus();jump.press('Enter')
            assert details.first.evaluate('el=>el.open') and pg.evaluate('document.activeElement.id')==dest
            assert pg.evaluate('document.documentElement.scrollHeight')>compact+150
            back=pg.locator('#'+dest+' .fv-r281__authority-return a');back.focus();back.press('Enter')
            assert pg.evaluate('document.activeElement.id')=='fv-r281-1-event-2'
            for size in [16,32,64]:
                pg.evaluate('(s)=>document.documentElement.style.fontSize=s+"px"',size)
                assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,js,size)
            pg.evaluate('document.documentElement.style.fontSize=""')
            assert pg.locator('.fv-r281__next a').count()==2 and not network
            pg.emulate_media(media='print')
            assert pg.locator('.fv-r281__boundary').first.evaluate('el=>getComputedStyle(el).backgroundColor')=='rgb(255, 255, 255)'
            if width in [390,1440] and not js:
                fresh=ctx.new_page();fresh.set_content(html)
                path=OUT/f'r291-{width}-compact.png';fresh.screenshot(path=str(path),full_page=True,animations='disabled')
                screens[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
                fresh.emulate_media(media='print');pdf=OUT/f'r291-{width}-print.pdf';fresh.pdf(path=str(pdf),format='A4',print_background=True)
                doc=fitz.open(pdf);txt=' '.join(p.get_text() for p in doc)
                assert all(s in txt for s in ['January 27 · oral authority','January 31 · dated memorandum received','February 3 · written confirmation','nasa.gov/history/Apollo204/narr.html','Read the free Apollo 1 investigation'])
                links=[l.get('uri','') for p in doc for l in p.get_links()]
                assert any('nasa.gov/history/Apollo204/proceed.html' in u for u in links)
                assert any('finalvestige.com/2026/08/20/' in u for u in links)
                printed[pdf.name]={'pages':len(doc),'nasa_link_count':sum('nasa.gov' in u for u in links)}
                fresh.close()
            checks.append({'width':width,'js':js,'summary':'PASS','native_anchor_autoopen':'PASS','focus':'PASS','text_zoom':'PASS','print_contrast':'PASS'})
            ctx.close()
    browser.close()
receipt={'suite':'R291 actual-PHP offline Chromium/print contract','contexts':checks,'screenshots':screens,'print':printed,
         'php_sha256':hashlib.sha256((ROOT/'apollo-source-experience.php').read_bytes()).hexdigest(),
         'css_sha256':hashlib.sha256(css.encode()).hexdigest(),'axe':'NOT_TESTED','field_CWV':'NOT_VERIFIED','installed_WP':'NOT_TESTED','release':'HARD_HOLD'}
(OUT/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(f"R291 {len(checks)}/10 Chromium contexts, {len(printed)}/2 print PDFs PASS; receipt SHA256 "+hashlib.sha256((OUT/'receipt.json').read_bytes()).hexdigest())
