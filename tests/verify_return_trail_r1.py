from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "return-trail-wp-block-r1.txt"
EXPECTED_BYTES = 11597
EXPECTED_SHA256 = "9f93b6cf024495217d5ebffa9989f28cc8671aeec3fb903744b78c9e4151545d"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def article_markup(mode: str) -> str:
    owned = mode == "article-owned"
    target_attrs = 'id="jump-target"'
    if owned:
        target_attrs += ' tabindex="-7" class="publisher-owned fv-return-trail-flash"'
    paras = []
    for i in range(14):
        attrs = target_attrs if i == 2 else f'id="p-{i}"'
        paras.append(
            f'<p {attrs}>Paragraph {i} records a concrete part of the investigation with enough published narrative text '
            'to qualify as longform material while keeping the deterministic fixture readable. '
            'The wording is intentionally specific enough to exceed the qualification threshold without relying on feature-generated text.</p>'
        )
    source = '<h2 id="sources" class="fv-source-heading">Sources</h2><ul data-fv-footnotes><li id="fv-fn-1">Source one</li></ul>'
    if mode == "ambiguous-source":
        source = '<div class="fv-source-heading">Competing partial marker</div>' + source
    return '<main><article><h1>Return Trail Fixture</h1><h2>Opening section</h2>' + ''.join(paras[:7]) + '<h2>Second section</h2>' + ''.join(paras[7:]) + source + '</article></main>'


def seed_script(mode: str) -> str:
    if mode == "landing-mixed":
        return r'''<script>
const t=Date.now(),ttl=30*24*60*60*1000;
localStorage.setItem('fvReturnTrailV1',JSON.stringify([
 {path:'/valid-one/',title:'Valid One',index:2,heading:'One',percent:42,updated:t-1000},
 {path:'/expired/',title:'Expired',index:1,heading:'Old',percent:33,updated:t-ttl-1},
 {path:'https://evil.example/x',title:'Unsafe',index:1,heading:'Bad',percent:20,updated:t-2000},
 {path:'/valid-two/',title:'Valid Two',index:4,heading:'Two',percent:55,updated:t-3000}
]));
</script>'''
    if mode == "landing-all-expired":
        return r'''<script>
const t=Date.now(),ttl=30*24*60*60*1000;
localStorage.setItem('fvReturnTrailV1',JSON.stringify([
 {path:'/expired-a/',title:'Expired A',index:1,heading:'Old',percent:33,updated:t-ttl},
 {path:'/expired-b/',title:'Expired B',index:2,heading:'Older',percent:44,updated:t-ttl-5000}
]));
</script>'''
    if mode.startswith("article-"):
        return r'''<script>
const t=Date.now(),ttl=30*24*60*60*1000;
localStorage.setItem('fvReturnTrailV1',JSON.stringify([
 {path:location.pathname,title:'This article',index:3,heading:'Opening section',percent:40,updated:t-1000},
 {path:'/expired/',title:'Expired',index:1,heading:'Old',percent:33,updated:t-ttl-1}
]));
</script>'''
    if mode == "ambiguous-source":
        return r'''<script>
localStorage.setItem('fvReturnTrailV1',JSON.stringify([
 {path:location.pathname,title:'This article',index:3,heading:'Opening section',percent:40,updated:Date.now()-1000}
]));
</script>'''
    return ""


def assertion_script(mode: str) -> str:
    return f'''<script>
(()=>{{
 const mode={mode!r},fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}},pass=()=>{{document.body.dataset.fvTest='pass'}};
 const later=(fn,ms)=>setTimeout(()=>{{try{{fn()}}catch(e){{fail(e&&e.message?e.message:String(e))}}}},ms);
 try{{
  const raw=localStorage.getItem('fvReturnTrailV1');
  if(mode==='landing-mixed'){{
    const rows=JSON.parse(raw||'[]');
    if(rows.length!==2)return fail('mixed purge did not persist exactly two valid rows');
    if(rows[0].path!=='/valid-one/'||rows[1].path!=='/valid-two/')return fail('valid rows were not preserved in original order');
    if(rows.some(x=>x.path==='/expired/'||String(x.path).startsWith('http')))return fail('expired or unsafe row remained physically stored');
    if(!document.querySelector('.fv-return-trail-card'))return fail('valid landing resume card missing');
    return pass();
  }}
  if(mode==='landing-all-expired'){{
    if(raw!==null)return fail('all-expired storage key was not physically removed');
    if(document.querySelector('.fv-return-trail-card'))return fail('expired record produced a resume card');
    return pass();
  }}
  if(mode==='ambiguous-source'){{
    if(document.querySelector('.fv-return-trail-card'))return fail('ambiguous Sources boundary did not fail closed');
    return pass();
  }}
  const rows=JSON.parse(raw||'[]');
  if(rows.length!==1||rows[0].path!==location.pathname)return fail('article read did not physically purge expired row');
  const target=document.getElementById('jump-target');
  const beforeTab=target.getAttribute('tabindex'),beforeClass=target.getAttribute('class'),beforeHasClass=target.hasAttribute('class');
  const go=document.querySelector('.fv-return-trail-card__button');
  if(!go)return fail('same-article Return Trail card missing');
  go.focus();go.click();
  later(()=>{{
    if(document.activeElement!==target)return fail('resume did not focus the published target');
    if(mode==='article-absent'&&target.getAttribute('tabindex')!=='-1')return fail('temporary feature-owned tabindex missing');
    if(mode==='article-owned'&&target.getAttribute('tabindex')!==beforeTab)return fail('pre-owned tabindex changed');
    if(mode==='article-owned'&&target.getAttribute('class')!==beforeClass)return fail('pre-owned class changed during resume');
    go.focus();
    later(()=>{{
      if(mode==='article-absent'&&target.hasAttribute('tabindex'))return fail('temporary tabindex not restored after blur');
      if(mode==='article-owned'&&(target.getAttribute('tabindex')!==beforeTab||target.getAttribute('class')!==beforeClass))return fail('publisher-owned state drifted after blur');
      go.click();
      later(()=>{{
        if(document.activeElement!==target)return fail('repeat resume did not focus target');
        go.focus();
        later(()=>{{
          if(mode==='article-absent'&&target.hasAttribute('tabindex'))return fail('repeat resume left tabindex behind');
          if(mode==='article-owned'&&(target.getAttribute('tabindex')!==beforeTab||target.getAttribute('class')!==beforeClass||target.hasAttribute('class')!==beforeHasClass))return fail('repeat resume drifted publisher state');
          later(()=>{{
            if(mode==='article-absent'&&target.classList.contains('fv-return-trail-flash'))return fail('feature flash class not cleaned');
            if(mode==='article-absent'&&target.hasAttribute('class'))return fail('originally absent class attribute was not restored to absent');
            if(mode==='article-owned'&&target.getAttribute('class')!==beforeClass)return fail('pre-owned flash/publisher class was removed');
            return pass();
          }},1500);
        }},80);
      }},80);
    }},80);
  }},100);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}})();
</script>'''


def fixture(payload: str, mode: str) -> str:
    if mode.startswith("landing"):
        body_class = "home"
        content = "<main><h1>Landing</h1></main>"
    else:
        body_class = "single-post"
        content = article_markup(mode)
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Return Trail R1</title></head><body class='{body_class}'>{seed_script(mode)}{content}{payload}{assertion_script(mode)}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = ("landing-mixed", "landing-all-expired", "article-absent", "article-owned", "ambiguous-source")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in modes:
                page = root / f"return-trail-r1-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                profile = root / f"profile-{mode}"
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     f"--user-data-dir={profile}", "--virtual-time-budget=4200", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=35,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    require('<style id="fv-return-trail-r1-css">' in text and '<script id="fv-return-trail-r1-js">' in text, "R1 ids missing")
    require("window.__fvReturnTrailR1" in text, "R1 duplicate-init guard missing")
    require("TTL=30*24*60*60*1000" in text and "MAX=3" in text, "retention/count bounds missing")
    require("raw!==null&&raw!==canonical" in text and "localStorage.removeItem(KEY)" in text and "localStorage.setItem(KEY,canonical)" in text, "destructive first-read canonical purge missing")
    require("t-x.updated>=0&&t-x.updated<TTL" in text, "strict TTL test missing")
    require("validPath" in text and "!p.startsWith('//')" in text and "!/[?#]/.test(p)" in text, "same-origin path-only validation missing")
    require("saved only in this browser for up to 30 days." in text, "retention microcopy missing")
    require("boundaries.length!==1||canonical.length!==1" in text and "h2#sources.fv-source-heading" in text, "unique canonical Sources gate missing")
    require("target.scrollIntoView" in text and "if(!hadTab){target.setAttribute('tabindex','-1');ownedTab=true}" in text, "nondestructive focus transaction missing")
    require("target.addEventListener('blur',restoreTab,{once:true})" in text, "temporary tabindex blur restoration missing")
    require("hadClassAttr" in text and "target.removeAttribute('class')" in text, "class-attribute ownership restoration missing")
    require("fvReturnTrailIndex" not in text and "fv-return-trail-marker" not in text, "feature must not permanently annotate publisher nodes")
    require("min-height:44px" in text and "forced-colors:active" in text and "prefers-reduced-motion:reduce" in text, "accessibility CSS contract missing")
    require("location.href" not in text and "document.cookie" not in text and "sessionStorage" not in text and "indexedDB" not in text, "privacy boundary drifted")
    for pattern, label in {
        r"\bfetch\s*\(": "fetch",
        r"XMLHttpRequest": "XHR",
        r"navigator\.sendBeacon": "sendBeacon",
        r"\bWebSocket\b": "WebSocket",
        r"<script[^>]+src=": "external script",
    }.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-return-trail-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    run_browser(text)
    print(f"PASS: Return Trail R1 {len(raw)} bytes sha256={actual}; destructive TTL purge, state preservation, repeat resume, privacy/accessibility contracts verified")


if __name__ == "__main__":
    main()
