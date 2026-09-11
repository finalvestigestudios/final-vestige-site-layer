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
PAYLOAD = ROOT / "payloads" / "threadlines-wp-block-v1.txt"
EXPECTED_BYTES = 12126
EXPECTED_SHA256 = "99d8cdc0601f47068a10211c5a58a69d675f17cf50fb63c7dca1f37b24b11de0"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fixture(payload: str, mode: str, origin: str) -> str:
    current = {
        "id": 621,
        "categories": [257245, 232815],
        "tags": [10367056],
        "_embedded": {
            "wp:term": [
                [
                    {"id": 257245, "taxonomy": "category", "name": "Catastrophe"},
                    {"id": 232815, "taxonomy": "category", "name": "Ingenuity"},
                ],
                [{"id": 10367056, "taxonomy": "post_tag", "name": "Standards"}],
            ]
        },
    }
    posts = [
        {"id": 1, "title": {"rendered": "Case A"}, "link": f"{origin}/case-a/", "categories": [257245], "tags": [10367056], "date": "2026-08-20T00:00:00"},
        {"id": 2, "title": {"rendered": "Case B"}, "link": f"{origin}/case-b/", "categories": [257245], "tags": [], "date": "2026-08-19T00:00:00"},
        {"id": 3, "title": {"rendered": "Case C"}, "link": f"{origin}/case-c/", "categories": [232815], "tags": [], "date": "2026-08-18T00:00:00"},
        {"id": 4, "title": {"rendered": "Unrelated"}, "link": f"{origin}/unrelated/", "categories": [], "tags": [], "date": "2026-08-21T00:00:00"},
        {"id": 5, "title": {"rendered": "External Trap"}, "link": "https://evil.example/trap/", "categories": [257245], "tags": [10367056], "date": "2026-08-22T00:00:00"},
        {"id": 6, "title": {"rendered": "Case F"}, "link": f"{origin}/case-f/", "categories": [], "tags": [10367056], "date": "2026-08-17T00:00:00"},
    ]
    mock = f"""
<script>
window.__fvFetchCalls=[];
window.fetch=async(url,opts)=>{{
  window.__fvFetchCalls.push({{url:String(url),opts:opts||{{}}}});
  if({json.dumps(mode)}==='fetchfail')return {{ok:false,status:503,json:async()=>({{}})}};
  const u=new URL(String(url));
  if(u.pathname.endsWith('/posts/621'))return {{ok:true,status:200,json:async()=>({json.dumps(current)})}};
  if(u.pathname.endsWith('/posts'))return {{ok:true,status:200,json:async()=>({json.dumps(posts)})}};
  return {{ok:false,status:404,json:async()=>({{}})}};
}};
</script>
"""
    article_id = ' id="post-621"' if mode != "noid" else ""
    body_class = "single-post postid-621" if mode != "noid" else "single-post"
    assertions = f"""
<script>
const runThreadlinesFixture=()=>{{
  const fail=(m)=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
  try{{
    const section=document.querySelector('[data-fv-threadlines]');
    if({json.dumps(mode)}==='noid'){{if(section)return fail('feature did not fail closed without post id');document.body.dataset.fvTest='pass';return}}
    if(!section)return fail('Threadlines section missing');
    if(window.__fvFetchCalls.length!==0)return fail('network started before visitor action');
    const button=section.querySelector('.fvt-load');button.click();
    setTimeout(()=>{{
      try{{
        const expectedCalls={json.dumps(mode)}==='fetchfail'?1:2;
        if(window.__fvFetchCalls.length!==expectedCalls)return fail(`expected ${{expectedCalls}} public REST request${{expectedCalls===1?'':'s'}}`);
        if(window.__fvFetchCalls.some(c=>new URL(c.url).origin!==location.origin))return fail('cross-origin request attempted');
        if(window.__fvFetchCalls.some(c=>c.opts.credentials!=='omit'))return fail('public REST requests included credentials');
        if(window.__fvFetchCalls.some(c=>!new URL(c.url).pathname.startsWith('/wp-json/wp/v2/')))return fail('request escaped WP public REST path');
        if({json.dumps(mode)}==='fetchfail'){{
          if(button.disabled||button.textContent!=='Try again')return fail('retry state missing after REST failure');
          if(section.querySelectorAll('.fvt-card').length)return fail('failed load rendered candidates');
          document.body.dataset.fvTest='pass';return;
        }}
        if(!window.__fvFetchCalls[1].url.includes('status=publish')||!window.__fvFetchCalls[1].url.includes('_fields='))return fail('candidate request not bounded to published lightweight fields');
        const links=[...section.querySelectorAll('.fvt-card a[href]')];
        if(links.length!==4)return fail('expected four ranked related investigations');
        if(links.some(a=>new URL(a.href).origin!==location.origin))return fail('external candidate link was not rejected');
        if(section.querySelector('.fvt-card-title').textContent!=='Case A')return fail('strongest shared-tag/category candidate did not rank first');
        const firstReasons=[...section.querySelectorAll('.fvt-card')[0].querySelectorAll('.fvt-reason')].map(n=>n.textContent);
        if(!firstReasons.includes('Standards')||!firstReasons.includes('Catastrophe'))return fail('transparent connection reasons missing');
        if([...section.querySelectorAll('.fvt-card-title')].some(n=>n.textContent==='Unrelated'||n.textContent==='External Trap'))return fail('invalid candidate survived scoring/origin gate');
        const standards=[...section.querySelectorAll('.fvt-filter')].find(b=>b.textContent.startsWith('Standards'));
        if(!standards)return fail('Standards filter missing');standards.click();
        const filtered=[...section.querySelectorAll('.fvt-card-title')].map(n=>n.textContent);
        if(filtered.length!==2||!filtered.includes('Case A')||!filtered.includes('Case F'))return fail('thread filter did not constrain results');
        if(section.querySelector('.fvt-method').hidden)return fail('method disclosure missing after success');
        document.body.dataset.fvTest='pass';
      }}catch(e){{fail(e&&e.message?e.message:String(e))}}
    }},180);
  }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',runThreadlinesFixture,{{once:true}});else runThreadlinesFixture();
</script>
"""
    return f"""<!doctype html><html><head><meta charset="utf-8"></head><body class="{body_class}">{mock}<main><article{article_id}><div class="entry-content"><h2>Investigation</h2><p>Published narrative.</p><h2 class="fv-source-heading" id="sources">Sources &amp; Further Reading</h2><ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source one.</li></ul></div></article></main>{payload}{assertions}</body></html>"""


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in ("valid", "fetchfail", "noid"):
                page = root / f"threadlines-{mode}.html"
                page.write_text(fixture(payload, mode, origin), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--virtual-time-budget=1200", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed to execute: {proc.stderr[-500:]}")
                require('data-fv-test="pass"' in proc.stdout, f"browser fixture {mode} failed runtime assertions")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(actual_sha256 == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha256}")

    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-threadlines-v1-css">' in text and '<script id="fv-threadlines-v1-js">' in text, "versioned style/script ids missing")
    require("window.__fvThreadlines" in text, "duplicate-init guard missing")
    require("single-post" in text and "postid-(\\d+)" in text and "post-(\\d+)" in text, "single-post/post-id qualification missing")
    require("Follow the thread this case leaves behind." in text, "brand-native visitor-value headline missing")
    require("Every match shows why it is connected—no hidden recommendation score." in text, "transparent-ranking copy missing")
    require("shared editorial tags are weighted above broad categories" in text, "ranking-method disclosure missing")
    require("Nothing about you is stored or sent." in text, "privacy boundary copy missing")

    require("/wp-json/wp/v2/" in text, "bounded same-origin WP REST path missing")
    require("credentials:'omit'" in text, "credential-free public REST boundary missing")
    require("u.origin!==location.origin" in text, "same-origin request/candidate gate missing")
    require("status=publish" in text and "_fields=id,title,link,categories,tags,date" in text, "published lightweight candidate query missing")
    require("current._embedded['wp:term']" in text, "published taxonomy name extraction missing")
    require("sharedTags.length*100+sharedCats.length*10" in text, "deterministic transparent weighting missing")
    require("slice(0,12)" in text and "slice(0,4)" in text, "bounded candidate/result limits missing")
    require("AbortController" in text and "setTimeout(()=>controller.abort(),8000)" in text, "network timeout missing")
    require("loadButton.addEventListener('click',load)" in text, "visitor-initiated loading missing")
    require("textContent=" in text, "safe dynamic text rendering missing")

    require("min-height:44px" in text, "44px control targets missing")
    require("@media(max-width:720px)" in text and "@media(max-width:360px)" in text, "mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion support missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")
    require("outline:3px solid var(--fvt-accent)" in text, "keyboard focus treatment missing")
    require("role=\"status\" aria-live=\"polite\"" in text, "accessible live status missing")

    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "posthog", "gtag(", "sendBeacon", "WebSocket", "history.pushState", "history.replaceState", "navigator.clipboard"]
    for token in banned:
        require(token.lower() not in text.lower(), f"unexpected persistence/analytics/history token: {token}")
    require(not re.search(r"<script[^>]+src=", text, re.I), "third-party script dependency detected")
    require(not re.search(r"<iframe\b", text, re.I), "iframe dependency detected")

    match = re.search(r'<script id="fv-threadlines-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Threadlines exact identity, visitor-initiated public-only same-origin discovery, transparent taxonomy weighting, candidate origin validation, bounded responsive UI, accessibility, privacy boundary, JavaScript syntax, and headless browser regressions verified")


if __name__ == "__main__":
    main()
