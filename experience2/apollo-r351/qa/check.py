#!/usr/bin/env python3
"""Apollo R351: local native HTTP headers, real Chromium DOM/print, failed-source regression.
No production traffic, paid services, WordPress writes or platform/commerce integrations.
Chromium network navigation is administrator-blocked here: browser checks use set_content.
"""
import json, socket, subprocess, time, urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copytree
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
EX2 = ROOT / 'experience2'
OUT = EX2 / 'apollo-r351' / 'QA'
OUT.mkdir(exist_ok=True, parents=True)

def php(root, function):
    entry = root/'apollo-r348/source-custody.php'
    code = 'define("ABSPATH", true); require '+json.dumps(str(entry))+'; $index='+json.dumps(str(root/'apollo-r347/source-index.php'))+'; if (is_readable($index)) require_once $index; echo '+function+';'
    return subprocess.check_output(['php','-r',code],text=True)

# Missing modules must never cause unreviewed NASA fallbacks to bypass custody.
with TemporaryDirectory(prefix='apollo-r351-failover-') as td:
    copy = Path(td)/'experience2'
    copytree(EX2, copy, ignore=lambda directory, items: {'QA'} & set(items))
    (copy/'apollo-r339/chronology-rail.php').unlink()
    index = php(copy,'fv_apollo_r347_index_shortcode()')
    assert 'data-fv-source-review-required="true"' in index
    assert 'href="https://www.nasa.gov/' not in index
    (copy/'apollo-r347/source-index.php').unlink()
    drawer = php(copy,'fv_apollo_r348_drawer_shortcode()')
    assert 'data-fv-source-review-required="true"' in drawer
    assert 'href="https://www.nasa.gov/' not in drawer

with socket.socket() as s:
    s.bind(('127.0.0.1', 0)); PORT=s.getsockname()[1]
proc = subprocess.Popen(['php','-S',f'127.0.0.1:{PORT}','-t',str(ROOT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
url=f'http://127.0.0.1:{PORT}/experience2/apollo-r351/qa/http_entry.php'
receipts=[]
try:
    for _ in range(40):
        try:
            response=urllib.request.urlopen(url,timeout=1);break
        except Exception: time.sleep(.1)
    else: raise AssertionError('Local PHP HTTP server unavailable')
    headers=dict(response.headers.items())
    served_html=response.read().decode('utf-8')
    assert served_html.count('data-fv-r339-cta="editorial"')==1
    assert "script-src 'self'" in headers['Content-Security-Policy']
    assert "'unsafe-inline'" not in headers['Content-Security-Policy']
    assert headers['X-Content-Type-Options']=='nosniff'
    receipts.append({'case':'native HTTP response + restrictive CSP headers','pass':True})

    # Chromium navigation to localhost and mocked domains returns
    # ERR_BLOCKED_BY_ADMINISTRATOR in this runtime, even with page.route.
    # Consequently browser DOM/keyboard/PDF checks DO NOT verify CSP enforcement.
    rendered=php(EX2,'fv_apollo_r348_experience_shortcode()')
    css='\n'.join((EX2/p).read_text() for p in [
        'apollo-r339/assets/chronology-rail.css',
        'apollo-r345/evidence-plate.css',
        'apollo-r340/assets/accession-gallery.css',
        'apollo-r347/assets/source-index.css',
        'apollo-r348/assets/source-custody.css'])
    script=(EX2/'apollo-r347/assets/source-index.js').read_text()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width,js,touch,zoom in [(320,True,False,4),(390,False,False,1),(768,True,True,1),(1440,True,False,1),(1920,True,False,1)]:
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=touch,is_mobile=touch,reduced_motion='reduce')
            page=context.new_page()
            page.set_content('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+css+'</style><body>'+rendered+'</body></html>')
            if js:page.add_script_tag(content=script)
            if zoom!=1: page.evaluate('(z)=>document.documentElement.style.fontSize=(16*z)+"px"',zoom)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),f'{width} overflow'
            assert page.locator('[data-fv-custody-source]').count()==8
            assert page.locator('[data-fv-r339-cta="editorial"]').count()==1
            if js:
                assert page.locator('.fv-apollo-r347__filters button').count()==5
                page.locator('.fv-apollo-r347__filters button').last.click()
                assert page.locator('.fv-apollo-r347__group:visible').count()==1
            else:
                assert page.locator('.fv-apollo-r347__group:visible').count()==4
            summary=page.locator('.fv-apollo-r348__detail summary').first
            if touch: summary.tap()
            else: summary.focus();page.keyboard.press('Enter')
            assert page.locator('.fv-apollo-r348__detail').first.get_attribute('open') is not None
            if width in (320,390,1440):page.screenshot(path=str(OUT/f'r351-http-{width}-{int(js)}.png'),full_page=True)
            receipts.append({'case':f'isolated Chromium {width}px JS={js} touch={touch} rootZoom={zoom}x','pass':True,'network_mode':'set_content; HTTP/CSP blocked by administrator'})
            if width==390:
                pdf=page.pdf(print_background=True)
                (OUT/'r351-native-http-dossier.pdf').write_bytes(pdf)
            context.close()
        browser.close()
finally:
    proc.terminate()
    try:proc.wait(timeout=3)
    except subprocess.TimeoutExpired:proc.kill()
(OUT/'r351-qa.json').write_text(json.dumps({'environment':'Native PHP server headers via urllib; Chromium DOM via set_content because browser navigation was blocked by administrator. NOT browser HTTP/CSP acceptance nor WordPress','browser_http_csp_executed':False,'axe_core_executed':False,'production_verified':False,'results':receipts},indent=2)+'\n')
print('PASS',len(receipts),'native HTTP header and isolated browser/failover checks; Chromium HTTP/CSP blocked')
