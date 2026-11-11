#!/usr/bin/env python3
"""R294 reproducible gate. Local HTTP/PHP evidence plus OFFLINE Chromium.
Browser HTTP is strictly withheld when the administrator blocks navigation;
this test cannot certify installed WordPress, axe, field CWV or release readiness.
"""
import hashlib, json, re, socket, subprocess, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
OUT=ROOT/'QA'; OUT.mkdir(exist_ok=True)
VERSION='r294-'+hashlib.sha256(CSS.read_bytes()).hexdigest()[:12]
assert VERSION=='r294-de213c4f113f','versioned CSS changed without PHP version update'
assert "FV_R294_STYLE_VERSION = '"+VERSION+"'" in PHP.read_text()
checks=[]
def check(condition,message):
    assert condition,message
    checks.append(message)
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}/local_http_fixture.php'
server=subprocess.Popen(['php','-S',f'127.0.0.1:{port}',str(HERE/'local_http_fixture.php')],stderr=subprocess.DEVNULL)
try:
    for i in range(50):
        try:
            with urllib.request.urlopen(base,timeout=1) as r:break
        except Exception:time.sleep(.1)
    check(r.status==200,'PHP server returns 200')
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/assets/apollo-source-experience.css?ver={VERSION}') as r:
        check(r.status==200 and r.read()==CSS.read_bytes(),'actual CSS HTTP response matches reviewed CSS bytes')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        rows=[]
        for width,js in [(w,j) for j in (False,True) for w in (320,390,768,1440,1920)]:
            queue=js
            with urllib.request.urlopen(base+('?queue=1' if queue else '')) as response:
                raw=response.read().decode();csp=response.headers.get('Content-Security-Policy','')
                check(response.status==200 and "default-src 'none'" in csp and "style-src 'self'" in csp,'localhost PHP response includes restrictive CSP')
            check(len(re.findall(r'<link rel="stylesheet"',raw))==1,'one CSS link in real PHP response')
            check('ver='+VERSION in raw,'real response includes reviewed CSS cache version')
            # System-managed Chromium blocks even localhost page.goto (ERR_BLOCKED_BY_ADMINISTRATOR).
            # Render the exact returned PHP HTML with exact CSS injected on an offline page.
            html=re.sub(r'<link rel="stylesheet"[^>]+>', '', raw)
            html=html.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=js,reduced_motion='reduce')
            page=context.new_page();page.set_content(html,wait_until='domcontentloaded')
            check(page.locator('.fv-r281__plate').count()==3,'three evidence plates exist')
            check(page.locator('.fv-r281__source-list>li').count()==3,'three NASA source records exist')
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),'no horizontal overflow')
            page.locator('.fv-r292__source-route a').click()
            check(page.evaluate("location.hash.endsWith('-source-1')"),'native source navigation works')
            check(page.locator('.fv-r281__source-list li').first.evaluate('(e)=>e===document.activeElement'),'source target receives focus')
            page.locator('.fv-r281__source-return a').first.click()
            check(page.evaluate("location.hash.endsWith('-event-1')"),'native claim return works')
            if not js and width in (390,1440):
                page.screenshot(path=str(OUT/f'r294-{width}-nojs.png'),full_page=True,animations='disabled')
            rows.append({'width':width,'js':js,'queue':queue,'status':'OFFLINE CHROMIUM PASS, not browser HTTP'})
            context.close()
        context=browser.new_context(java_script_enabled=False)
        with urllib.request.urlopen(base+'?instances=2') as r:double=r.read().decode()
        check(len(re.findall(r'<link rel="stylesheet"',double))==1,'two PHP instances produce one CSS link')
        page=context.new_page();page.set_content(re.sub(r'<link rel="stylesheet"[^>]+>','',double).replace('</head>','<style>'+CSS.read_text()+'</style></head>'))
        ids=page.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)')
        check(len(ids)==len(set(ids)),'two instances have unique target IDs')
        context.close();browser.close()
    receipt={'status':'LOCAL_PHP_AND_OFFLINE_CHROMIUM_PASS; HTTP_BROWSER_BLOCKED',
        'checks':len(checks),'contexts':rows,'version':VERSION,
        'php_sha256':hashlib.sha256(PHP.read_bytes()).hexdigest(),
        'css_sha256':hashlib.sha256(CSS.read_bytes()).hexdigest(),
        'browser_http':'BLOCKED: ERR_BLOCKED_BY_ADMINISTRATOR verified in separate strict probe',
        'axe':'NOT RUN: genuine axe-core unavailable','real_LCP_CLS':'NOT MEASURED: offline about:blank is not a site navigation',
        'installed_wordpress':'NOT TESTED','production':'NOT LIVE'}
    (OUT/'r294-release-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(f'PASS {len(rows)}/10 offline Chromium contexts and {len(checks)} assertions; actual PHP HTTP/CSP/CSS verified by urllib; browser HTTP/axe/field CWV BLOCKED')
finally:
    server.terminate();server.wait(timeout=5)
