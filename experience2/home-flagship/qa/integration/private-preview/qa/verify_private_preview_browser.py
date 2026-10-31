#!/usr/bin/env python3
"""Real HTTP/PHP+Chromium smoke of the isolated protected staging fixture.

The fixture is NOT the exact canonical GitHub HTML or an actual WordPress host.
All generated assets are local and original; no WP site is modified.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from zipfile import ZipFile
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE=Path(__file__).resolve().parents[1]
HOME=Path(os.environ.get('FV_EX2_TEST_HOME', str(BASE.parents[2])))
CONTRACT=Path(os.environ.get('FV_EX2_TEST_CONTRACT', str(BASE.parent)))
RESULTS=BASE/'qa/HTTP_BROWSER_RESULTS.json'
ROOT_URL='http://127.0.0.1:18941/'
APPROVED='mock_optin=yes&mock_env=staging&mock_login=yes&mock_edit=yes'

def url(action='fv_ex2_private_render',params=APPROVED,nonce='TEST_NONCE'):
    return ROOT_URL + '?' + '&'.join(['action='+action,'_wpnonce='+nonce,params])

def get(path):
    try:
        with urllib.request.urlopen(path, timeout=6) as r:return (r.status, r.read(),dict(r.headers))
    except urllib.error.HTTPError as e:return(e.code,e.read(),dict(e.headers))

def main():
    with tempfile.TemporaryDirectory(prefix='fv-ex2-private-browser-') as td:
        tdir=Path(td)
        sys.path.insert(0,str(BASE))
        sys.path.insert(0,str(CONTRACT))
        import build_private_preview
        import check_contract
        zip_path=tdir/'staging.zip'
        build_private_preview.create(HOME,BASE/'fv-ex2-private-preview.php',zip_path,
                                     os.environ.get('FV_EX2_EXPECTED_HEAD','c1c00acfa79664163214e1f424a8868e64aa2ee3'),check_contract)
        with ZipFile(zip_path) as z:z.extractall(tdir)
        plugin=tdir/'fv-ex2-private-preview'
        env=dict(os.environ,FV_EX2_MOCK_PLUGIN_ROOT=str(plugin))
        p=subprocess.Popen(['php','-S','127.0.0.1:18941','-t',str(BASE/'mock'),str(BASE/'mock/router.php')],cwd=BASE,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for k in range(60):
                try:
                    get(ROOT_URL)
                    break
                except (urllib.error.URLError,ConnectionError):time.sleep(.1)
            else:raise RuntimeError('PHP local server did not start')
            assertions=[]
            def ck(name,success,detail=None):
                assertions.append({'name':name,'passed':bool(success),'detail':detail})
                if not success:raise AssertionError(f'{name}: {detail}')
            cases=[('production', 'mock_optin=yes&mock_env=production&mock_login=yes&mock_edit=yes'),
                   ('no_flag','mock_optin=no&mock_env=staging&mock_login=yes&mock_edit=yes'),
                   ('logged_out','mock_optin=yes&mock_env=staging&mock_login=no&mock_edit=yes'),
                   ('no_editor_cap','mock_optin=yes&mock_env=staging&mock_login=yes&mock_edit=no')]
            for name,params in cases:
                status,body,_=get(url(params=params))
                ck('blocked_'+name,status==403 and not body,(status,len(body)))
            status,body,_=get(url(nonce='BAD'))
            ck('nonce_mismatch_denied',status==403 and not body,(status,len(body)))
            status,body,_=get(ROOT_URL+'private-payload.php')
            ck('payload_direct_get_denied',status==403 and not body,(status,len(body)))
            status,body,headers=get(url())
            pagehtml=body.decode('utf-8')
            ck('authorized_html_status',status==200,status)
            ck('no_public_script_or_stylesheet_requests','<script src=' not in pagehtml and '<link rel="stylesheet"' not in pagehtml)
            ck('six_nonce_styles',pagehtml.count('data-fv-private-asset=')==10,pagehtml.count('data-fv-private-asset='))
            ck('anti_cache_noindex',headers.get('X-Robots-Tag','').startswith('noindex') and 'no-store' in headers.get('Cache-Control',''))
            ck('nonce_strict_script_csp',"script-src 'nonce-" in headers.get('Content-Security-Policy','') and "'unsafe-eval'" not in headers.get('Content-Security-Policy',''))
            ck('seven_chapter_source_integrity',all(i in pagehtml for i in ('fv-hf-title','fv-hf-evidence','fv-hf-chronicle','fv-hf-inquiry','fv-hf-observer','fv-hf-mind-title','fv-hf-method-title')))
            ck('no_draft_assets_in_payload','FV_EX2_ALLOW_PREVIEW' not in pagehtml and 'private-payload' not in pagehtml)
            # Mutation: tamper one encoded source payload byte while PHP server is running.
            payload_path=plugin/'fv-ex2-private-payload.php'
            original=payload_path.read_text()
            payload_path.write_text(original.replace("'index.html' => '", "'index.html' => 'A",1))
            try:
                tamper_status,tamper_body,_=get(url())
                ck('tampered_payload_returns_503_without_leak',tamper_status==503 and not tamper_body,(tamper_status,len(tamper_body)))
            finally:payload_path.write_text(original)
            restored_status,_,_=get(url())
            ck('untampered_payload_recovers',restored_status==200,restored_status)
            with sync_playwright() as pw:
                browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
                viewport_results=[]
                for width,height in [(320,700),(390,844),(768,900),(1440,1000),(1920,1080)]:
                    context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',service_workers='block')
                    page=context.new_page()
                    errors=[];requests=[]
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.on('request',lambda r:requests.append(r.url))
                    page.set_content(pagehtml,wait_until='domcontentloaded',timeout=12000)
                    page.wait_for_timeout(150)
                    obs=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth+1,
                      chapters:document.querySelectorAll('[data-fv-chapter]').length,
                      links:document.querySelectorAll('[data-fv-reading-trail] a').length,
                      scripts:document.querySelectorAll('script[data-fv-private-asset]').length,
                      styles:document.querySelectorAll('style[data-fv-private-asset]').length,
                      h1:document.querySelectorAll('h1').length})''')
                    # browser source isolation: zero extra JS/CSS HTTP fetches
                    ck('browser_'+str(width)+'_no_overflow',not obs['overflow'],obs)
                    ck('browser_'+str(width)+'_assets_embedded',obs['styles']==6 and obs['scripts']==4,obs)
                    ck('browser_'+str(width)+'_no_page_errors',not errors,errors)
                    ck('browser_'+str(width)+'_no_external_executables',not any(u.endswith(('.js','.css')) for u in requests),requests)
                    ck('browser_'+str(width)+'_one_h1',obs['h1']==1,obs)
                    ck('browser_'+str(width)+'_direction_selector_visible',page.locator('[data-fv-direction-choice="dossier"]').is_visible())
                    ck('browser_'+str(width)+'_reading_trail_enhanced',page.locator('.fv-hf__chapter-nav[data-fv-trail-enhanced]').count()==1)
                    # A regression caught in the first iteration: moving `defer` JS inline
                    # into the head executes before the body exists and silently fails.
                    page.locator('[data-fv-direction-choice="museum"]').click()
                    ck('browser_'+str(width)+'_art_direction_changes',page.locator('[data-fv-home-flagship]').get_attribute('data-fv-direction')=='museum')
                    page.locator('[data-fv-chronicle-view="addition"]').click()
                    ck('browser_'+str(width)+'_chronicle_controls_work',page.locator('[data-fv-chronicle-view="addition"]').get_attribute('aria-pressed')=='true')
                    if width in (390,1440):
                        page.screenshot(path=str(BASE/'qa'/f'private-preview-{width}.png'),full_page=False)
                    viewport_results.append({'width':width,'observation':obs,'requests':requests,'page_errors':errors})
                    context.close()
                # No-JS fallback remains substantive, not an empty shell.
                cx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
                pg=cx.new_page();pg.set_content(pagehtml,wait_until='domcontentloaded',timeout=12000)
                ck('no_js_record_exists',pg.locator('a[href*="historymuseum.ca"]').count()>0)
                ck('no_js_all_three_evidence_cases',pg.locator('[data-fv-case]').count()==3)
                cx.close()
                browser.close()
            result={'scope':'Real local PHP HTTP status/auth/CSP checks; Chromium rendered response via set_content because browser localhost navigation is blocked. Set FV_EX2_TEST_HOME to exact repo checkout for exact-source QA; otherwise local fixture. Not actual WordPress.',
                    'candidate_plugin_sha256':hashlib.sha256((BASE/'fv-ex2-private-preview.php').read_bytes()).hexdigest(),
                    'candidate_builder_sha256':hashlib.sha256((BASE/'build_private_preview.py').read_bytes()).hexdigest(),
                    'source_checkout':str(HOME),'source_ref_label':os.environ.get('FV_EX2_EXPECTED_HEAD','c1c00acfa79664163214e1f424a8868e64aa2ee3')+' (unattested caller input)' ,
                    'assertions':len(assertions),'passed':sum(x['passed'] for x in assertions),'errors':[x for x in assertions if not x['passed']],
                    'viewports':viewport_results,'HTTP_headers':{k:headers.get(k) for k in ['Content-Security-Policy','X-Robots-Tag','Cache-Control']}}
            RESULTS.write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({'passed':result['passed'],'checks':result['assertions'],'viewports':[x['width'] for x in viewport_results],'results':str(RESULTS)},indent=2))
        finally:
            p.terminate()
            try:p.wait(timeout=4)
            except subprocess.TimeoutExpired:p.kill()

if __name__=='__main__':main()
