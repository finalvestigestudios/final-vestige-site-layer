#!/usr/bin/env python3
"""R32: actual sealed PHP HTTP CSP projected into Chromium meta policy.

Local PHP + WordPress-function stubs, NOT real WP, and about:blank/set_content,
NOT browser navigation under HTTP headers. CSP frame-ancestors cannot be tested
through meta; only permitted meta directives are tested by actual Chromium.
No network sources or user/media writes. Exact R29 archive is SHA-pinned by R31.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
from urllib.error import URLError

import http_response_gate_r31 as previous

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
EXPECTED = {
    'default-src': "'none'", 'img-src': "'none'", 'font-src': "'none'",
    'connect-src': "'none'", 'object-src': "'none'", 'base-uri': "'none'",
    'form-action': "'none'", 'frame-ancestors': "'self'",
}

def digest(data: bytes) -> str:
    return sha256(data).hexdigest()

def project_policy(header: str, nonce: str) -> str:
    """Fail closed on missing, duplicated or expanded CSP; exclude HTTP-only frames."""
    clauses = [c.strip() for c in header.split(';') if c.strip()]
    pairs = [c.split(None, 1) for c in clauses]
    if any(len(p) != 2 for p in pairs):
        raise AssertionError('malformed CSP directive')
    directives = dict(pairs)
    if len(directives) != len(pairs) or len(directives) != 10:
        raise AssertionError('CSP duplicated or unexpected directives')
    for name, value in EXPECTED.items():
        if directives.get(name) != value:
            raise AssertionError('CSP required restriction changed: '+name)
    for name in ('script-src', 'style-src'):
        if directives.get(name) != "'nonce-" + nonce + "'":
            raise AssertionError('CSP nonce or permissions changed: '+name)
    if not re.fullmatch(r'[A-Za-z0-9+/=]{16,128}', nonce):
        raise AssertionError('invalid CSP nonce')
    return '; '.join(c for c in clauses if not c.startswith('frame-ancestors '))

def projected_html(body: bytes, policy: str, nonce: str, *, probes: bool) -> str:
    """Project exact response body, adding one metadata tag and controlled probes."""
    html = body.decode('utf-8')
    if html.count('<head>') != 1 or html.count('</body>') != 1:
        raise AssertionError('unexpected sealed HTML structure')
    if len(re.findall(r'<style nonce="'+re.escape(nonce)+'"', html)) != 1:
        raise AssertionError('missing/duplicate source CSS nonce')
    if len(re.findall(r'<script nonce="'+re.escape(nonce)+'"', html)) != 1:
        raise AssertionError('missing/duplicate source JS nonce')
    if re.search(r'<meta\s+http-equiv\s*=\s*["\']Content-Security-Policy',html,re.I):
        raise AssertionError('source already defines another meta CSP')
    meta = '<meta http-equiv="Content-Security-Policy" content="'+escape(policy,quote=True)+'">'
    html = html.replace('<head>','<head>'+meta,1)
    if probes:
        # Synthetic in-document paint metrics, not real HTTP navigation or field CWV.
        monitor = ('<script nonce="'+nonce+'">(function(){window.__r32_perf={lcpMs:null,cls:0,shifts:0};'
                   'try{new PerformanceObserver(l=>{for(const x of l.getEntries())'
                   'window.__r32_perf.lcpMs=x.startTime}).observe({type:"largest-contentful-paint",buffered:true})}catch(e){};'
                   'try{new PerformanceObserver(l=>{for(const x of l.getEntries())if(!x.hadRecentInput)'
                   '{window.__r32_perf.cls+=x.value;window.__r32_perf.shifts++}}).observe({type:"layout-shift",buffered:true})}'
                   'catch(e){}})();</script>')
        html=html.replace(meta,meta+monitor,1)
    if probes:
        # Approved and disallowed probes have distinct side effects; the real
        # source nonce must authorize the former but not the latter.
        probes_html = (
            '<div id="r32-approved-style">CSP probe</div>'
            '<div id="r32-denied-style">Blocked style probe</div>'
            '<style nonce="'+nonce+'">#r32-approved-style{color:rgb(3,90,15)}</style>'
            '<style>#r32-denied-style{color:rgb(255,0,0)!important}</style>'
            '<script nonce="'+nonce+'">window.__r32_allowed=true</script>'
            '<script>window.__r32_blocked=true</script>'
            '<script src="https://untrusted-csp-probe.invalid/payload.js"></script>'
        )
        html=html.replace('</body>', probes_html+'</body>',1)
    return html

@contextmanager
def authorized_php_response(bundle: Path):
    php = previous.verify_zip(bundle)
    with tempfile.TemporaryDirectory(prefix='fv-apollo-r32-') as temp:
        root=Path(temp)
        (root/'fv-ex2-apollo-sealed.php').write_bytes(php)
        (root/'index.php').write_text(previous.STUB,encoding='utf-8')
        with socket.socket() as s:
            s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
        server=subprocess.Popen(['php','-S',f'127.0.0.1:{port}','-t',str(root)],
                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            url=f'http://127.0.0.1:{port}/index.php?_wpnonce=LOCALTEST'
            for _ in range(60):
                try:
                    status,headers,body=previous.fetch(url)
                    break
                except URLError: time.sleep(.08)
            else: raise RuntimeError('local PHP server did not start')
            audited=previous.audit(status,headers,body)
            policy=project_policy(headers['Content-Security-Policy'],audited['nonce'])
            yield body, audited, policy
        finally:
            server.terminate()
            try:server.wait(timeout=5)
            except subprocess.TimeoutExpired:server.kill();server.wait()

def inspect_page(page, width: int, no_js=False) -> dict:
    state=page.evaluate('''() => ({
      scrollWidth:document.documentElement.scrollWidth,
      clientWidth:document.documentElement.clientWidth,
      records:document.querySelectorAll('#source-concordance [data-concordance-record]').length,
      holds:document.querySelectorAll('[data-media-hold="true"]').length,
      catalog:document.querySelectorAll('[data-crosswalk-review="hold"]').length,
      geo:document.querySelectorAll('#atlas [data-lat],#atlas [data-lon]').length,
      approved:window.__r32_allowed===true,
      blocked:window.__r32_blocked===true,
      approvedColor:getComputedStyle(document.querySelector('#r32-approved-style')||document.body).color,
      deniedColor:getComputedStyle(document.querySelector('#r32-denied-style')||document.body).color,
      comparisonReady:!!document.querySelector('[data-ex2-compare-tools]:not([hidden])')
    })''')
    if state['scrollWidth']>state['clientWidth']+1:
        raise AssertionError(f'{width}px horizontal scroll overflow: {state}')
    if (state['records'],state['holds'],state['catalog'],state['geo'])!=(6,6,1,0):
        raise AssertionError('evidence/media/Atlas content changed: '+str(state))
    if not no_js:
        if state['approved'] is not True or state['blocked'] or not state['comparisonReady']:
            raise AssertionError('CSP did not execute only approved source JS')
        if state['approvedColor']!='rgb(3, 90, 15)' or state['deniedColor']=='rgb(255, 0, 0)':
            raise AssertionError('CSP did not permit nonce CSS and block injected CSS')
    else:
        if state['approved'] or state['blocked']:
            raise AssertionError('JavaScript executed with JS disabled')
    return state

def run(bundle: Path, shots: Path) -> dict:
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True,exist_ok=True)
    with authorized_php_response(bundle) as (body,audited,policy):
        nonce=audited['nonce']
        source_sha=audited['normalized_html_sha256']
        html=projected_html(body,policy,nonce,probes=True)
        widths=[]; screenshots=[]
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',
                                               headless=True,args=['--no-sandbox'])
            try:
                for width in WIDTHS:
                    context=browser.new_context(viewport={'width':width,'height':900},
                                                reduced_motion='reduce')
                    page=context.new_page();errors=[];attempted=[];denied=[];routed=[];violations=[]
                    page.route('**/*',lambda route:(routed.append(route.request.url),route.abort()))
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.on('request',lambda r:attempted.append(r.url))
                    page.on('requestfailed',lambda r:denied.append((r.url,r.failure)))
                    page.on('console',lambda m:violations.append(m.text) if 'Content Security Policy' in m.text else None)
                    page.set_content(html,wait_until='load',timeout=30000)
                    page.wait_for_timeout(120)
                    state=inspect_page(page,width)
                    perf=page.evaluate('window.__r32_perf||null')
                    if errors or routed or len(attempted)!=1 or denied!=[(attempted[0],'csp')]:
                        raise AssertionError(f'{width}px errors or CSP request: {errors}/{attempted}/{denied}/{routed}')
                    if len(violations)<2:raise AssertionError('malicious CSS/JS not blocked by Chromium CSP')
                    page.locator('#fv-ex2-research-desk-crosswalk>summary').focus()
                    page.keyboard.press('Enter')
                    if not page.locator('#fv-ex2-research-desk-crosswalk').evaluate('(e)=>e.open'):
                        raise AssertionError('keyboard evidence disclosure failed')
                    if width in (390,1440):
                        path=shots/f'r32-projected-csp-{width}.png'
                        page.locator('#fv-ex2-research-desk-crosswalk').screenshot(path=str(path),animations='disabled')
                        screenshots.append({'file':path.name,'sha256':digest(path.read_bytes())})
                    widths.append({'width':width,'status':'PASS','blocked_csp_console_messages':len(violations),'csp_blocked_external_requests':len(denied),
                                   'source_records':state['records'],'overflow':False,'real_browser_csp_meta':True,
                                   'synthetic_document_paint':perf})
                    context.close()
                context=browser.new_context(viewport={'width':390,'height':850},java_script_enabled=False,
                                            reduced_motion='reduce')
                page=context.new_page()
                page.set_content(html,wait_until='load')
                inspect_page(page,390,no_js=True)
                page.locator('#fv-ex2-research-desk-crosswalk>summary').click()
                if not page.locator('#fv-ex2-research-desk-crosswalk').evaluate('(e)=>e.open'):
                    raise AssertionError('no-JS evidence disclosure inaccessible')
                context.close()
                touch_context=browser.new_context(viewport={'width':390,'height':850},
                                                  has_touch=True,is_mobile=True,
                                                  reduced_motion='reduce')
                page=touch_context.new_page()
                page.set_content(html,wait_until='load')
                page.locator('#fv-ex2-research-desk-crosswalk>summary').tap()
                if not page.locator('#fv-ex2-research-desk-crosswalk').evaluate('(e)=>e.open'):
                    raise AssertionError('touch evidence disclosure inaccessible')
                touch_context.close()
            finally:browser.close()
    return {
        'status':'PASS_META_PROJECTED_BROWSER_CSP_RELEASE_HOLD',
        'source_zip_sha256':previous.ZIP_SHA,
        'sealed_php_sha256':previous.PHP_SHA,
        'normalized_php_http_body_sha256':source_sha,
        'projected_http_csp_without_frame_ancestors':policy.replace(nonce,'Z'*len(nonce)),
        'browser':'Chromium 144 / Playwright set_content about:blank',
        'widths':widths,'screenshots':screenshots,
        'javascript_disabled_evidence':'PASS','keyboard_disclosure':'PASS',
        'touch_disclosure':'PASS','reduced_motion':'EMULATED_REDUCE_ALL_WIDTHS',
        'csp_meta_enforced_by_real_browser':True,'csp_http_response_enforced_by_browser':False,
        'axe_core':'NOT_RUN_NO_VERIFIED_BUNDLE','wordpress_staging':'NOT_TESTED',
        'hosted_lcp_cls':'NOT_MEASURED',
        'paint_method':'Chromium PerformanceObserver on set_content about:blank (synthetic, not URL navigation/p75)',
        'limitations':'HTTP policy was faithfully projected as meta; frame-ancestors is HTTP-only. Source from actual PHP HTTP with mocked WP auth; not HTTP navigation, WP staging, or production release.',
        'release':'HOLD',
    }

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--r29-zip',type=Path,required=True)
    p.add_argument('--shots',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args(); result=run(a.r29_zip,a.shots)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R32: 7/7 real Chromium CSP-meta checks; release HOLD')
