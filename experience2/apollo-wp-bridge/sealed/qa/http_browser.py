#!/usr/bin/env python3
"""Browser-enforced HTTP/CSP and guarded-iframe QA using exact PR215 sealed PHP.

This is a real localhost HTTP transport through a *synthetic* PHP WordPress
function shim, NOT an installed WordPress staging environment. The shim also
checks role/nonce gates. Rebuilds canonical output from pinned 12 Git blobs.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import urlopen
import zipfile
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SEALED = HERE.parent
sys.path.insert(0, str(SEALED))
from build_sealed import build, ROOT, PIN
SCREENSHOTS = HERE / 'http-screenshots'
SCREENSHOTS.mkdir(exist_ok=True, parents=True)
RESULT = HERE / 'HTTP_BROWSER_RESULTS.json'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def start_server(plugin: Path):
    port = free_port()
    env = dict(os.environ, FV_TEST_APOLLO_PLUGIN=str(plugin))
    proc = subprocess.Popen(['php', '-S', f'127.0.0.1:{port}', str(HERE/'http_router_entry.php')],
                            env=env, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    base = f'http://127.0.0.1:{port}'
    for _ in range(60):
        if proc.poll() is not None:
            raise RuntimeError('PHP server died: ' + proc.stderr.read().decode()[:1200])
        try:
            with urlopen(base + '/health', timeout=1) as r:
                if r.status == 200:
                    return base, proc
        except Exception:
            time.sleep(0.08)
    proc.terminate()
    raise RuntimeError('PHP HTTP stub not ready')


def build_plugin(path: Path):
    zipfile_path = path / 'preview.zip'
    manifest = build(zipfile_path)
    with zipfile.ZipFile(zipfile_path) as z:
        plugin_content = z.read(ROOT+'/fv-ex2-apollo-sealed.php')
    plugin_path = path / 'fv-ex2-apollo-sealed.php'
    plugin_path.write_bytes(plugin_content)
    return plugin_path, manifest, zipfile_path


def main():
    with tempfile.TemporaryDirectory(prefix='fv-apollo-http-') as tmp:
        plugin, manifest, bundle = build_plugin(Path(tmp))
        second = Path(tmp) / 'preview-second.zip'
        assert build(second) == manifest and second.read_bytes() == bundle.read_bytes()
        base, proc = start_server(plugin)
        report = {
            'pinned_upstream_commit': PIN,
            'source_file_pin_count': 12,
            'php_sha256': manifest['plugin_sha256'],
            'deterministic_plugin_zip_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
            'transport': 'real localhost HTTP PHP CLI server with synthetic WordPress stub (NOT WordPress staging)',
            'csp': 'browser-enforced response header, not meta imitation',
            'axe_core': 'NOT RUN - verified local axe-core bundle unavailable',
            'field_CWV': 'NOT RUN - lab synthetic measurements only',
            'cases': [], 'screenshots': [], 'failures': [],
        }
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
                for width in (320, 360, 390, 768, 1024, 1440, 1920):
                    ctx = browser.new_context(viewport={'width':width,'height':900}, reduced_motion='reduce' if width==320 else 'no-preference')
                    ctx.add_cookies([{'name':'fv_test_mode','value':'editor','url':base, 'sameSite':'Lax'}])
                    page = ctx.new_page()
                    errors=[];csp=[];bad_http=[]
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.on('console',lambda m:csp.append(m.text) if ('Content Security Policy' in m.text or 'Refused to' in m.text) else None)
                    page.on('response',lambda r:bad_http.append((r.status,r.url)) if r.status >= 400 else None)
                    r=page.goto(base+'/review',wait_until='load',timeout=20000)
                    assert r.status==200
                    iframe=page.locator('iframe[title*="Apollo 1"]')
                    assert iframe.count()==1 and 'allow-same-origin' not in iframe.get_attribute('sandbox')
                    frame = iframe.content_frame
                    frame.locator('#atlas').wait_for(timeout=15000)
                    assert frame.locator('h1').count()==1
                    assert frame.locator('#fv-ex2-custody-receipts [data-custody-receipt]').count()==7
                    assert frame.locator('[data-ex2-stage]').count()==6
                    assert frame.locator('[data-ex2-atlas-item]').count()==6
                    assert frame.locator('[data-ex2-trail-card]').count()==6
                    assert frame.locator('[data-ex2-response-item]').count()==6
                    assert frame.locator('[data-ex2-trail-controls]').is_visible(), (width,'CSP script blocked')
                    assert frame.locator('[data-ex2-response-tools]').is_visible(), (width,'response JS blocked')
                    assert frame.locator('a[href*="fv_ex2_apollo_sealed_download"]').count()==14
                    # Frame is sandboxed as opaque origin even though HTTP cookie was sent to same-site endpoint.
                    frame_origin = frame.locator('body').evaluate('() => location.origin')
                    # URL origin is not DOM effective origin; document.domain access is not reliable. Test sandbox flags directly.
                    viewport=frame.locator('body').evaluate('() => ({innerWidth, scrollWidth:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
                    assert viewport['scrollWidth']<=width+1,(width,viewport)
                    selection=frame.locator('[data-ex2-trail-select]')
                    selection.select_option('05')
                    assert frame.locator('[data-ex2-trail-card]:visible').count()==1
                    frame.locator('[data-ex2-trail-reset]').click()
                    assert frame.locator('[data-ex2-trail-card]:visible').count()==6
                    response=frame.locator('[data-ex2-response-filter]')
                    response.select_option('hardware')
                    assert frame.locator('[data-ex2-response-item]:visible').count()==3
                    frame.locator('[data-ex2-response-reset]').click()
                    assert frame.locator('[data-ex2-response-item]:visible').count()==6
                    frame.locator('#trail-02 summary').click()
                    assert frame.locator('#trail-02 details').evaluate('(n) => n.open')
                    if width in (390,1440):
                        for part,sel in (('hero','.ex2-hero'),('atlas','#atlas'),('research','#research-desk')):
                            path=SCREENSHOTS / f'http-{part}-{width}.png'
                            frame.locator(sel).screenshot(path=str(path), animations='disabled')
                            report['screenshots'].append({'path':str(path.relative_to(HERE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
                    # Browser performance observations: Navigation Timing / paint / layout-shift. LCP may be unavailable.
                    metrics = frame.locator('body').evaluate('''() => ({
                      fcp:performance.getEntriesByType('paint').find(x=>x.name==='first-contentful-paint')?.startTime??null,
                      navigation:performance.getEntriesByType('navigation').map(n=>({responseEnd:n.responseEnd,domContentLoaded:n.domContentLoadedEventEnd})),
                      cls:performance.getEntriesByType('layout-shift').filter(e=>!e.hadRecentInput).reduce((a,e)=>a+e.value,0)
                    })''')
                    assert not errors,(width,errors)
                    # Only CSP-blocks from our own code would be failures. An unavailable HTTP stub route is also a failure.
                    assert not bad_http,(width,bad_http)
                    report['cases'].append({'width':width,'status':'PASS','stage_count':6,'atlas_records':6,'trail_records':6,'csp_console':csp,
                       'viewport':viewport,'no_page_errors':True,'http_errors':bad_http, 'metrics':metrics})
                    ctx.close()
                # Browser no-JS at 390: native details and full source content still accessible.
                ctx=browser.new_context(viewport={'width':390,'height':850},java_script_enabled=False)
                ctx.add_cookies([{'name':'fv_test_mode','value':'editor','url':base}])
                page=ctx.new_page();page.goto(base+'/review');frame=page.locator('iframe').content_frame
                assert frame.locator('[data-ex2-trail-card]:visible').count()==6
                assert frame.locator('[data-ex2-response-item]:visible').count()==6
                assert frame.locator('[data-ex2-atlas-item]:visible').count()==6
                assert not frame.locator('[data-ex2-trail-controls]').is_visible()
                frame.locator('#trail-02 summary').click()
                assert frame.locator('#trail-02 details').evaluate('(n)=>n.open')
                report['no_js'] = 'PASS';ctx.close()
                # HTTP access control with REAL status code and response body.
                for mode in ('guest','reader','production','off'):
                    ctx=browser.new_context()
                    ctx.add_cookies([{'name':'fv_test_mode','value':mode,'url':base}]);page=ctx.new_page()
                    response=page.goto(base+'/review')
                    assert response.status==200
                    assert page.locator('iframe').count()==0,(mode,'private iframe leaked')
                    # forged nonce must not defeat eligibility checks.
                    resp=page.request.get(base+'/wp-admin/admin-ajax.php?action=fv_ex2_apollo_sealed_page&_wpnonce=http-stub-fixed-nonce')
                    assert resp.status==403 and not await_no_bytes(resp),(mode,resp.status)
                    report['cases'].append({'mode':mode,'status':'PASS','private_preview_exposed':False,'forged_nonce_http':403})
                    ctx.close()
                # Editor valid vs invalid nonce, traversal and downloads.
                ctx=browser.new_context()
                ctx.add_cookies([{'name':'fv_test_mode','value':'editor','url':base}]);rq=ctx.request
                def get(action, nonce='http-stub-fixed-nonce', file=None):
                    from urllib.parse import urlencode
                    data={'action':action,'_wpnonce':nonce}
                    if file is not None:data['file']=file
                    return rq.get(base+'/wp-admin/admin-ajax.php?'+urlencode(data))
                unauthorized=get('fv_ex2_apollo_sealed_page','wrong')
                assert unauthorized.status==403 and not await_no_bytes(unauthorized)
                allowed=get('fv_ex2_apollo_sealed_page')
                assert allowed.status==200
                assert 'Content-Security-Policy' in allowed.headers and 'nonce-' in allowed.headers['content-security-policy']
                assert "frame-ancestors 'self'" in allowed.headers['content-security-policy']
                assert 'noindex' in allowed.headers.get('x-robots-tag','')
                assert 'nosniff' in allowed.headers.get('x-content-type-options','')
                assert '<section class="fv-ex2-apollo"' in allowed.text()
                download_hashes={}
                for name in ('evidence-export.csv','evidence-export.json','response-export.csv','response-export.json','source-context.json','atlas-admission.json','media-rights.json'):
                    resp=get('fv_ex2_apollo_sealed_download',file=name)
                    expected=((SEALED.parent/'generated'/name).read_bytes() if name not in ('source-context.json','atlas-admission.json','media-rights.json')
                              else __import__('source_concordance').build_context_index().encode('utf-8') if name=='source-context.json'
                              else __import__('atlas_admission').build_atlas_admission()[2].encode('utf-8') if name=='atlas-admission.json'
                              else __import__('media_rights_ledger').build_media_rights()[2].encode('utf-8'))
                    assert resp.status==200 and resp.body()==expected
                    assert resp.headers.get('content-disposition','').startswith('attachment;')
                    download_hashes[name]=hashlib.sha256(resp.body()).hexdigest()
                traversal=get('fv_ex2_apollo_sealed_download',file='../fragment.html')
                assert traversal.status==404 and not await_no_bytes(traversal)
                report['download_sha256']=download_hashes
                report['http_security']='PASS'
                ctx.close();browser.close()
        except Exception as exc:
            report['failures'].append(repr(exc))
            raise
        finally:
            proc.terminate()
            try:proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:proc.kill()
            RESULT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print('HTTP_BROWSER_PASS 7 widths; actual PHP response CSP/iframe/cookies; no-JS; deny-gates; CSV/JSON exact')
        return report


def await_no_bytes(response):
    return len(response.body()) > 0


if __name__=='__main__':main()
