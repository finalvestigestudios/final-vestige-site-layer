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
PAYLOAD = ROOT / "payloads" / "passage-kit-wp-block-r1.txt"
EXPECTED_BYTES = 8001
EXPECTED_SHA256 = "9fd62e21ddc4b0673fc8287a536cc1c28f950e74b32febe373947e860baa7467"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def prose(i: int, citation: str = "") -> str:
    text = (
        f"Published narrative passage {i} records a concrete part of the investigation in enough detail "
        "to exercise Passage Kit without inventing evidence, changing the article, or obscuring the source trail. "
        "This fixture deliberately keeps the prose long enough to qualify as narrative and repeats factual context "
        "only for deterministic browser verification of the copy boundary, citation cleanup, and source append behavior. "
    )
    return f'<p id="passage-{i}">{text}{citation}</p>'


def article() -> str:
    live = '<a href="#fv-fn-1" class="fv-fn-ref" data-fv-fn="1">991</a>'
    unresolved = '<a href="#fv-fn-99" class="fv-fn-ref" data-fv-fn="99">777</a>'
    wrapped = '<sup class="fv-fn-mark"><a href="#fv-fn-2" class="fv-fn-ref" data-fv-fn="2">992</a></sup>'
    paragraphs = [
        prose(1, live),
        prose(2),
        prose(3, unresolved),
        prose(4, wrapped),
        *[prose(i) for i in range(5, 13)],
    ]
    return f'''<main><article><h1>Passage Kit Runtime Fixture</h1>
<h2>First section</h2>
{"".join(paragraphs)}
<h2 class="fv-source-heading" id="sources">Sources</h2>
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1">Source one published note. <a href="https://example.org/source-one">source one link</a> <span class="fv-fn-backlinks"><a href="#passage-1">back</a></span></li>
<li id="fv-fn-2">Source two published note. <a href="https://example.org/source-two">source two link</a> <span class="fv-fn-backlinks"><a href="#passage-4">back</a></span></li>
</ul></article></main>'''


def fixture(payload: str) -> str:
    setup = r'''<script>
window.__copies=[];
window.prompt=(label,text)=>{window.__copies.push(text);return text};
Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copies.push(text);}}});
</script>'''
    before = r'''<script>
window.__original={
 p1:document.querySelector('#passage-1').innerHTML,
 p2:document.querySelector('#passage-2').innerHTML,
 p3:document.querySelector('#passage-3').innerHTML,
 p4:document.querySelector('#passage-4').innerHTML,
 s1:document.querySelector('#fv-fn-1').innerHTML,
 s2:document.querySelector('#fv-fn-2').innerHTML
};
</script>'''
    assertions = r'''<script>
const fvpkTest=()=>{
 const fail=m=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
 const pass=()=>{document.body.dataset.fvTest='pass'};
 const copies=window.__copies;
 const same=()=>{
  const o=window.__original;
  return document.querySelector('#passage-1').innerHTML===o.p1 &&
   document.querySelector('#passage-2').innerHTML===o.p2 &&
   document.querySelector('#passage-3').innerHTML===o.p3 &&
   document.querySelector('#passage-4').innerHTML===o.p4 &&
   document.querySelector('#fv-fn-1').innerHTML===o.s1 &&
   document.querySelector('#fv-fn-2').innerHTML===o.s2;
 };
 try{
  const toggle=document.querySelector('.fv-passage-kit__toggle');
  if(!toggle)return fail('launcher missing');
  toggle.click();
  const buttons=[...document.querySelectorAll('.fv-passage-kit-action button')];
  if(buttons.length!==12)return fail('expected 12 passage copy actions, got '+buttons.length);
  const click=async i=>{buttons[i].click();await new Promise(r=>setTimeout(r,40));return copies[copies.length-1]||''};
  (async()=>{
   let t=await click(0);
   if(t.includes('991'))return fail('live citation marker leaked into cited quote');
   if(!t.includes('Linked source note:')||!t.includes('[1] Source one published note.'))return fail('resolvable cited source was not appended');
   if((t.match(/\[1\]/g)||[]).length!==1)return fail('resolved source appended more than once');
   if(!same())return fail('published DOM mutated after cited export');

   t=await click(1);
   if(t.includes('Linked source note'))return fail('uncited passage invented a source section');
   if(!t.includes('Published narrative passage 2'))return fail('uncited narrative missing');
   if(!same())return fail('published DOM mutated after uncited export');

   t=await click(2);
   if(t.includes('777'))return fail('unresolved citation marker leaked into quote');
   if(t.includes('[99]')||t.includes('Linked source note'))return fail('unresolved citation invented or substituted a source');
   if(!t.includes('Published narrative passage 3'))return fail('unresolved-reference narrative missing');
   if(!same())return fail('published DOM mutated after unresolved-reference export');

   t=await click(3);
   if(t.includes('992'))return fail('wrapped live citation marker leaked into quote');
   if(!t.includes('[2] Source two published note.'))return fail('wrapped resolvable source was not appended');
   if((t.match(/\[2\]/g)||[]).length!==1)return fail('wrapped source appended more than once');
   if(!same())return fail('published DOM mutated after wrapped cited export');

   pass();
  })().catch(e=>fail(e&&e.message?e.message:String(e)));
 }catch(e){fail(e&&e.message?e.message:String(e))}
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvpkTest,{once:true});else fvpkTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Passage Kit R1 fixture</title>{setup}</head><body class='single-post'>{article()}{before}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            page = root / "passage-kit-r1.html"
            page.write_text(fixture(payload), encoding="utf-8")
            proc = subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                 "--virtual-time-budget=3500", "--dump-dom", f"http://127.0.0.1:{server.server_port}/{page.name}?campaign=abc#frag"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=40,
            )
            require(proc.returncode == 0, f"browser fixture failed: {proc.stderr[-500:]}")
            if 'data-fv-test="pass"' not in proc.stdout:
                reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                raise SystemExit(f"FAIL: browser fixture: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(actual_sha256 == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha256}")

    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-passage-kit-r1-css">' in text and '<script id="fv-passage-kit-r1-js">' in text, "R1 versioned asset ids missing")
    require(".fv-fn-ref[data-fv-fn]" in text, "live citation derivation contract missing")
    require("clone.querySelectorAll('.fv-fn-ref[data-fv-fn],.fv-fn-mark,.fv-passage-kit-action')" in text, "live citation marker cleanup missing")
    require("cloneNode(true)" in text, "copy cleanup must operate on clones")
    require("document.getElementById('fv-fn-'+num)" in text, "source-note lookup missing")
    require(".map(sourceFor).filter(Boolean)" in text, "unresolved references must fail closed rather than fabricate sources")
    require("Linked source " in text, "resolved source append boundary missing")
    require("location.origin+location.pathname" in text, "query-free same-origin page reference missing")

    require("PASSAGE KIT" in text and "Carry a published passage with its linked source notes." in text, "visitor-facing Passage Kit contract missing")
    require("Copies published wording and linked source notes. It does not rate the evidence." in text, "evidence-boundary copy missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text, "touch/mobile contract missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility media behavior missing")
    require("e.key==='Escape'" in text and "toggle.focus()" in text, "Escape/focus return missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "location.href", "posthog", "gtag(", "sendBeacon", "WebSocket"
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")
    for pattern, label in {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
    }.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-passage-kit-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    run_browser(text)
    print(f"PASS: Passage Kit R1 {len(raw)} bytes {actual_sha256}; cited/uncited/unresolved/wrapped export behavior, no marker leakage, no published-node mutation")


if __name__ == "__main__":
    main()
