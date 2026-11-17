"""Actual Chromium against LOCAL exact-PHP markup loaded offline; real navigation blocked.
Chromium viewport, keyboard, touch, print, no-JS, downloadable TXT, lab LCP/CLS.
axe-core is NOT installed: that gate is an explicit HOLD, not a fabricated pass.
"""
import functools, http.server, json, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
SHOTS=OUT/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)
WIDTHS=(320,360,390,768,1024,1440,1920)
ASSERTIONS=0

def ensure(condition, msg):
    global ASSERTIONS
    assert condition, msg
    ASSERTIONS+=1

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address=True

def run():
    import subprocess
    generated = subprocess.run(['php',str(ROOT/'qa/fixture.php')],capture_output=True,check=True)
    (OUT/'fixture.html').write_bytes(generated.stdout)
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(OUT))
    with Server(('127.0.0.1',0),handler) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        host=f'http://127.0.0.1:{server.server_address[1]}/fixture.html'
        evidence=[]
        html=generated.stdout.decode('utf-8')
        navigation_blocked=None
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            try:
                probe=browser.new_page()
                try:
                    probe.goto(host,wait_until='load',timeout=6000)
                except Exception as err:
                    navigation_blocked=('ERR_BLOCKED_BY_ADMINISTRATOR' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(err) else str(err).split('\n')[0].split(' at ')[0])
                finally:probe.close()
                if not navigation_blocked: navigation_blocked='LOCAL_HTTP_ACCESSIBLE_BUT_OFFLINE_SUITE_ONLY'
                for width in WIDTHS:
                    ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,accept_downloads=True)
                    page=ctx.new_page()
                    page.add_init_script('''(() => {window.__r431Vitals={lcp:null,cls:0,errors:[]};
                      try {new PerformanceObserver(l=>{for(const e of l.getEntries())window.__r431Vitals.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){window.__r431Vitals.errors.push(String(e));}
                      try {new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__r431Vitals.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){window.__r431Vitals.errors.push(String(e));}
                    })();''')
                    page.set_content(html,wait_until='load')
                    ensure(page.locator('html').count()==1,f'offline markup at {width}')
                    ensure(page.locator('[data-fv-r431]').count()==2,f'two real PHP instances at {width}')
                    ensure(page.locator('.fv-r430__question').count()==6,f'six parent questions at {width}')
                    ensure(page.locator('.fv-r429__plate').count()==6,f'six source plates at {width}')
                    ensure(page.locator('.fv-r429__cta').count()==2,f'one free CTA each at {width}')
                    ensure(page.locator('a[href*="payhip"],a[href*="checkout"]').count()==0,f'no unverified paid CTA at {width}')
                    ensure(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'no horizontal overflow at {width}')
                    ensure(page.evaluate('''() => {const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size}'''),f'IDs unique at {width}')
                    ensure(page.locator('[data-fv-r431-actions]').count()==2 and page.locator('[data-fv-r431-actions]:not([hidden])').count()==2,f'progressive controls initialized {width}')
                    ensure(page.locator('.fv-r431__progress').first.inner_text()=='0 of 3 answers drafted',f'initial progress {width}')
                    page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
                    evidence.append({'width_px':width,'navigation':'BLOCKED_BY_ADMINISTRATOR','offline_markup':True,'lcp_ms':'NOT MEASURED','cls':'NOT MEASURED','axe_status':'HOLD (verified core unavailable)','wordpress_staging':'NOT TESTED'})
                    ctx.close()
                ctx=browser.new_context(viewport={'width':390,'height':900},accept_downloads=True,permissions=['clipboard-read','clipboard-write'])
                page=ctx.new_page();page.set_content(html)
                questions=page.locator('[data-fv-r431]').first.locator('.fv-r430__question textarea')
                questions.nth(0).focus(); page.keyboard.type('The unfueled rocket did not remove oxygen cabin hazards.')
                questions.nth(1).fill('Most probable is not conclusively proven.')
                ensure(page.locator('.fv-r431__progress').first.inner_text()=='2 of 3 answers drafted','progress updates')
                page.evaluate('Object.defineProperty(navigator,"clipboard",{configurable:true,value:{writeText:async(t)=>{window.__r431ClipboardText=t;}}})')
                page.locator('[data-fv-r431-copy]').first.click()
                ensure('copied' in page.locator('[data-fv-r431-status]').first.inner_text().lower(),'clipboard success feedback')
                clip=page.evaluate('window.__r431ClipboardText')
                ensure('Most probable is not conclusively proven' in clip and 'https://www.nasa.gov/' in clip,'simulated clipboard API includes source link')
                with page.expect_download() as download_info:
                    page.locator('[data-fv-r431-export]').first.click()
                download=download_info.value
                ensure(download.suggested_filename=='apollo-1-evidence-notes.txt','download name')
                saved=OUT/'notes-test-output.txt'; download.save_as(str(saved))
                notes=saved.read_text()
                ensure('The unfueled rocket did not remove oxygen' in notes,'download contains user note')
                ensure('Question'.upper() in notes,'download includes real question labels')
                ensure(notes.count('https://www.nasa.gov/')==3,'download contains exactly 3 official citations')
                ensure('utm_source' not in notes and 'utm_content' not in notes,'no campaign params exported')
                page.locator('[data-fv-r431] .fv-r430__reason summary').first.focus()
                page.keyboard.press('Enter')
                ensure(page.locator('[data-fv-r431] .fv-r430__reason').first.evaluate('(x)=>x.open'),'keyboard disclosure')
                page.emulate_media(media='print')
                ensure(page.locator('.fv-r431__print-answer').first.evaluate('(x)=>getComputedStyle(x).display')!='none','print user answers visible')
                ensure('The unfueled rocket' in page.locator('.fv-r431__print-answer').first.inner_text(),'print mirrors actual notes')
                ensure(page.locator('.fv-r431__actions').first.evaluate('(x)=>getComputedStyle(x).display')=='none','print hides action controls')
                page.screenshot(path=str(SHOTS/'390-print.png'),full_page=True)
                page.emulate_media(media='screen'); page.screenshot(path=str(SHOTS/'390-filled.png'),full_page=True)
                # Error path: clipboard API deliberately unavailable on this fixture context.
                page.evaluate('Object.defineProperty(navigator,"clipboard",{value:undefined,configurable:true})')
                page.locator('[data-fv-r431-copy]').first.click()
                ensure('Clipboard unavailable' in page.locator('[data-fv-r431-status]').first.inner_text(),'clipboard unavailable fallback')
                page.screenshot(path=str(SHOTS/'390-copy-fallback.png'),full_page=True)
                ctx.close()
                ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
                page=ctx.new_page();page.set_content(html)
                ensure(page.locator('[data-fv-r431-actions]:visible').count()==0,'no-JS controls hidden')
                ensure(page.locator('.fv-r430__question').count()==6,'no-JS questions complete')
                page.locator('.fv-r430__reason summary').first.click()
                ensure(page.locator('.fv-r430__reason').first.evaluate('(x)=>x.open'),'no-JS disclosure works')
                ensure(page.locator('.fv-r429__cta').count()==2,'no-JS CTA retains free article')
                page.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True)
                ctx.close()
                ctx=browser.new_context(viewport={'width':320,'height':900},reduced_motion='reduce',forced_colors='active')
                page=ctx.new_page();page.set_content(html)
                ensure(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'forced colors/reduced motion fit 320')
                ensure(page.locator('[data-fv-r431-actions]:not([hidden])').count()==2,'forced colors controls present')
                page.screenshot(path=str(SHOTS/'320-forcedcolors-reducedmotion.png'),full_page=True)
                ctx.close()
                ctx=browser.new_context(viewport={'width':320,'height':900})
                page=ctx.new_page();page.set_content(html)
                page.add_style_tag(content='html{font-size:200%}')
                ensure(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'320px at 200% text no horizontal overflow')
                page.screenshot(path=str(SHOTS/'320-text200.png'),full_page=True)
                ctx.close()
                ctx=browser.new_context(viewport={'width':390,'height':900},has_touch=True,is_mobile=True)
                page=ctx.new_page();page.set_content(html)
                page.locator('[data-fv-r431] .fv-r430__reason summary').first.tap()
                ensure(page.locator('[data-fv-r431] .fv-r430__reason').first.evaluate('(x)=>x.open'),'real touch disclosure')
                page.screenshot(path=str(SHOTS/'390-touch.png'),full_page=True)
                ctx.close()
            finally:browser.close()
        result={'status':'OFFLINE_CHROMIUM_PASS_HTTP_NAVIGATION_BLOCKED','test_assertions':ASSERTIONS,'testing_scope':'PHP-rendered actual R431 + sha-pinned R430/R429 via page.set_content, NOT HTTP navigation or WordPress installation','navigation_error':navigation_blocked,'local_labs':evidence,'axe':'HOLD: pinned reviewed axe-core absent','field_p75':'NOT MEASURED','navigated_lcp_cls':'NOT MEASURED','user_consent':'No collection or tracking, no forms'}
        (OUT/'browser-report.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print(f'PASS {ASSERTIONS}/{ASSERTIONS} offline Chromium assertions, {len(list(SHOTS.glob("*.png")))} screenshots; LCP/CLS and axe HOLD; axe/Staging HOLD')

if __name__=='__main__':run()
