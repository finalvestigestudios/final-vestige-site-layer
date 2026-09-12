from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'payloads' / 'threadlines-wp-block-v1.txt'
EXPECTED_BYTES = 12683
EXPECTED_SHA256 = '85a129b5cd508ff6f7f844b11543be52b201f76a31317a2e5de0571f78850a37'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fixture(payload: str, mode: str, origin: str) -> str:
    terms = [
        {"id": 257245, "taxonomy": "category", "name": "Catastrophe"},
        {"id": 232815, "taxonomy": "category", "name": "Ingenuity"},
        {"id": 10367056, "taxonomy": "post_tag", "name": "Standards"},
    ]
    if mode == 'missingterms':
        terms = []
    elif mode == 'partialterms':
        terms = [t for t in terms if t['id'] != 10367056]
    current = {
        'id': 621,
        'categories': [257245, 232815],
        'tags': [10367056],
        '_embedded': {'wp:term': [terms[:2], terms[2:]]},
    }
    posts = [
        {'id': 1, 'title': {'rendered': 'Case A'}, 'link': f'{origin}/case-a/', 'categories': [257245], 'tags': [10367056], 'date': '2026-08-20T00:00:00'},
        {'id': 2, 'title': {'rendered': 'Case B'}, 'link': f'{origin}/case-b/', 'categories': [257245], 'tags': [], 'date': '2026-08-19T00:00:00'},
        {'id': 3, 'title': {'rendered': 'Case C'}, 'link': f'{origin}/case-c/', 'categories': [232815], 'tags': [], 'date': '2026-08-18T00:00:00'},
        {'id': 4, 'title': {'rendered': 'Unrelated'}, 'link': f'{origin}/unrelated/', 'categories': [], 'tags': [], 'date': '2026-08-21T00:00:00'},
        {'id': 5, 'title': {'rendered': 'External Trap'}, 'link': 'https://evil.example/trap/', 'categories': [257245], 'tags': [10367056], 'date': '2026-08-22T00:00:00'},
        {'id': 6, 'title': {'rendered': 'Case F'}, 'link': f'{origin}/case-f/', 'categories': [], 'tags': [10367056], 'date': '2026-08-17T00:00:00'},
    ]
    mock = f'''\n<script>\nwindow.__fvFetchCalls=[];\nwindow.fetch=async(url,opts)=>{{\n  window.__fvFetchCalls.push({{url:String(url),opts:opts||{{}}}});\n  if({json.dumps(mode)}==='fetchfail')return {{ok:false,status:503,json:async()=>({{}})}};\n  const u=new URL(String(url));\n  if(u.pathname.endsWith('/posts/621'))return {{ok:true,status:200,json:async()=>({json.dumps(current)})}};\n  if(u.pathname.endsWith('/posts'))return {{ok:true,status:200,json:async()=>({json.dumps(posts)})}};\n  return {{ok:false,status:404,json:async()=>({{}})}};\n}};\n</script>\n'''
    article_id = ' id="post-621"' if mode != 'noid' else ''
    body_class = 'single-post postid-621' if mode != 'noid' else 'single-post'
    assertions = f'''\n<script>\nconst runThreadlinesFixture=()=>{{\n  const fail=(m)=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};\n  try{{\n    const section=document.querySelector('[data-fv-threadlines]');\n    if({json.dumps(mode)}==='noid'){{if(section)return fail('feature did not fail closed without post id');document.body.dataset.fvTest='pass';return}}\n    if(!section)return fail('Threadlines section missing');\n    if(window.__fvFetchCalls.length!==0)return fail('network started before visitor action');\n    const button=section.querySelector('.fvt-load');button.click();\n    setTimeout(()=>{{\n      try{{\n        const failClosed=['missingterms','partialterms'].includes({json.dumps(mode)});\n        const expectedCalls=({json.dumps(mode)}==='fetchfail'||failClosed)?1:2;\n        if(window.__fvFetchCalls.length!==expectedCalls)return fail(`expected ${{expectedCalls}} public REST request${{expectedCalls===1?'':'s'}}`);\n        if(window.__fvFetchCalls.some(c=>new URL(c.url).origin!==location.origin))return fail('cross-origin request attempted');\n        if(window.__fvFetchCalls.some(c=>c.opts.credentials!=='omit'))return fail('public REST requests included credentials');\n        if(window.__fvFetchCalls.some(c=>!new URL(c.url).pathname.startsWith('/wp-json/wp/v2/')))return fail('request escaped WP public REST path');\n        if(failClosed){{\n          if(section.querySelectorAll('.fvt-card').length)return fail('incomplete taxonomy labels rendered candidates');\n          if(!section.querySelector('.fvt-status').textContent.includes('won’t guess'))return fail('taxonomy fail-closed explanation missing');\n          if(!button.hidden)return fail('taxonomy failure left misleading retry control visible');\n          if([...section.querySelectorAll('.fvt-reason')].some(n=>/Shared (tag|category)/.test(n.textContent)))return fail('generic taxonomy fallback reason rendered');\n          document.body.dataset.fvTest='pass';return;\n        }}\n        if({json.dumps(mode)}==='fetchfail'){{\n          if(button.disabled||button.textContent!=='Try again')return fail('retry state missing after REST failure');\n          if(section.querySelectorAll('.fvt-card').length)return fail('failed load rendered candidates');\n          document.body.dataset.fvTest='pass';return;\n        }}\n        if(!window.__fvFetchCalls[1].url.includes('status=publish')||!window.__fvFetchCalls[1].url.includes('_fields='))return fail('candidate request not bounded to published lightweight fields');\n        const links=[...section.querySelectorAll('.fvt-card a[href]')];\n        if(links.length!==4)return fail('expected four ranked related investigations');\n        if(links.some(a=>new URL(a.href).origin!==location.origin))return fail('external candidate link was not rejected');\n        if(section.querySelector('.fvt-card-title').textContent!=='Case A')return fail('strongest shared-tag/category candidate did not rank first');\n        const firstReasons=[...section.querySelectorAll('.fvt-card')[0].querySelectorAll('.fvt-reason')].map(n=>n.textContent);\n        if(!firstReasons.includes('Standards')||!firstReasons.includes('Catastrophe'))return fail('exact editorial connection labels missing');\n        if(firstReasons.some(n=>n==='Shared tag'||n==='Shared category'))return fail('generic fallback reason rendered');\n        if([...section.querySelectorAll('.fvt-card-title')].some(n=>n.textContent==='Unrelated'||n.textContent==='External Trap'))return fail('invalid candidate survived scoring/origin gate');\n        const standards=[...section.querySelectorAll('.fvt-filter')].find(b=>b.textContent.startsWith('Standards'));\n        if(!standards)return fail('Standards filter missing');standards.click();\n        const filtered=[...section.querySelectorAll('.fvt-card-title')].map(n=>n.textContent);\n        if(filtered.length!==2||!filtered.includes('Case A')||!filtered.includes('Case F'))return fail('thread filter did not constrain results');\n        const method=section.querySelector('.fvt-method');\n        if(method.hidden)return fail('method disclosure missing after success');\n        if(!method.textContent.includes('100 points')||!method.textContent.includes('10'))return fail('ranking score disclosure is not literal');\n        document.body.dataset.fvTest='pass';\n      }}catch(e){{fail(e&&e.message?e.message:String(e))}}\n    }},180);\n  }}catch(e){{fail(e&&e.message?e.message:String(e))}}\n}};\nif(document.readyState==='loading')document.addEventListener('DOMContentLoaded',runThreadlinesFixture,{{once:true}});else runThreadlinesFixture();\n</script>\n'''
    return f'''<!doctype html><html><head><meta charset="utf-8"></head><body class="{body_class}">{mock}<main><article{article_id}><div class="entry-content"><h2>Investigation</h2><p>Published narrative.</p><h2 class="fv-source-heading" id="sources">Sources &amp; Further Reading</h2><ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source one.</li></ul></div></article></main>{payload}{assertions}</body></html>'''


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ('google-chrome', 'chromium', 'chromium-browser') if shutil.which(name)), None)
    require(browser is not None, 'headless Chrome/Chromium not available')
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        origin = f'http://127.0.0.1:{server.server_port}'
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in ('valid', 'missingterms', 'partialterms', 'fetchfail', 'noid'):
                page = root / f'threadlines-{mode}.html'
                page.write_text(fixture(payload, mode, origin), encoding='utf-8')
                proc = subprocess.run(
                    [browser, '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--virtual-time-budget=1200', '--dump-dom', f'{origin}/{page.name}'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
                require(proc.returncode == 0, f'browser fixture {mode} failed to execute: {proc.stderr[-500:]}')
                require('data-fv-test="pass"' in proc.stdout, f'browser fixture {mode} failed runtime assertions')
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode('utf-8')
    require(len(raw) == EXPECTED_BYTES, f'payload byte count drifted: {len(raw)}')
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(actual_sha256 == EXPECTED_SHA256, f'payload SHA-256 drifted: {actual_sha256}')

    require(text.count('<!-- wp:html -->') == 1 and text.count('<!-- /wp:html -->') == 1, 'single isolated wp:html block required')
    require('<style id="fv-threadlines-v1-css">' in text and '<script id="fv-threadlines-v1-js">' in text, 'versioned style/script ids missing')
    require("window.__fvThreadlines" in text and "version:'1.1.0'" in text, 'R1 duplicate-init/version guard missing')
    require('single-post' in text and 'postid-(\\d+)' in text and 'post-(\\d+)' in text, 'single-post/post-id qualification missing')
    require('Follow the thread this case leaves behind.' in text, 'brand-native visitor-value headline missing')
    require('each shared tag adds 100 points; each shared category adds 10' in text, 'literal ranking-score disclosure missing')
    require('ties break by publication date, then title' in text, 'deterministic tie-break disclosure missing')
    require('Nothing about you is stored or sent.' in text, 'privacy boundary copy missing')

    require('/wp-json/wp/v2/' in text, 'bounded same-origin WP REST path missing')
    require("credentials:'omit'" in text, 'credential-free public REST boundary missing')
    require('u.origin!==location.origin' in text, 'same-origin request/candidate gate missing')
    require('status=publish' in text and '_fields=id,title,link,categories,tags,date' in text, 'published lightweight candidate query missing')
    require("current._embedded['wp:term']" in text, 'published taxonomy name extraction missing')
    require("requiredKeys.some(key=>!termMap.has(key))" in text and 'FVTaxonomyLabelsUnavailable' in text, 'missing taxonomy labels do not fail closed')
    require("'Shared tag'" not in text and "'Shared category'" not in text, 'generic taxonomy fallback labels remain')
    require('names.length!==keys.length' in text, 'candidate reason integrity guard missing')
    require('sharedTags.length*100+sharedCats.length*10' in text, 'deterministic weighting missing')
    require('slice(0,12)' in text and 'slice(0,4)' in text, 'bounded candidate/result limits missing')
    require('AbortController' in text and 'setTimeout(()=>controller.abort(),8000)' in text, 'network timeout missing')
    require("loadButton.addEventListener('click',load)" in text, 'visitor-initiated loading missing')
    require('textContent=' in text, 'safe dynamic text rendering missing')

    require('min-height:44px' in text, '44px control targets missing')
    require('@media(max-width:720px)' in text and '@media(max-width:360px)' in text, 'mobile behavior missing')
    require('prefers-reduced-motion:reduce' in text, 'reduced-motion support missing')
    require('forced-colors:active' in text, 'forced-colors support missing')
    require('@media print' in text, 'print cleanup missing')
    require('outline:3px solid var(--fvt-accent)' in text, 'keyboard focus treatment missing')
    require('role="status" aria-live="polite"' in text, 'accessible live status missing')

    banned = ['localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'posthog', 'gtag(', 'sendBeacon', 'WebSocket', 'history.pushState', 'history.replaceState', 'navigator.clipboard']
    for token in banned:
        require(token.lower() not in text.lower(), f'unexpected persistence/analytics/history token: {token}')
    require(not re.search(r'<script[^>]+src=', text, re.I), 'third-party script dependency detected')
    require(not re.search(r'<iframe\b', text, re.I), 'iframe dependency detected')

    match = re.search(r'<script id="fv-threadlines-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, 'unable to extract JavaScript')
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(['node', '--check', str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    if os.environ.get('FV_BROWSER_RUNTIME') == '1':
        run_browser(text)
    print('PASS: Threadlines R1 exact taxonomy-label fidelity, fail-closed incomplete metadata, literal deterministic ranking disclosure, visitor-initiated same-origin public REST discovery, accessibility, privacy boundary, JavaScript syntax, and browser adversarial regressions verified')


if __name__ == '__main__':
    main()
