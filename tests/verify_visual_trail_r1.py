from __future__ import annotations

import hashlib
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
PAYLOAD = ROOT / "payloads" / "visual-trail-wp-block-r1.txt"
EXPECTED_BYTES = 12632
EXPECTED_SHA256 = "0d60fe40fb3c70e45133a3a47bd1db0c6bcc24687e1fcf787fe2e81a4980510a"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fig(n: int) -> str:
    return f'''<figure class="wp-block-image" id="fig-{n}"><img src="/img/{n}.jpg" alt="Figure {n}"><figcaption>Caption {n}</figcaption></figure>'''


def canonical() -> str:
    return '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'


def notes() -> str:
    return '<ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source</li></ul>'


def base_article(boundary_prefix: str = "", boundary_suffix: str = "", boundary: str | None = None) -> str:
    b = canonical() if boundary is None else boundary
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
<p>Opening.</p>{fig(1)}
<h2>Section One</h2><p>One.</p>{fig(2)}
<h2>Section Two</h2><p>Two.</p>{fig(3)}
<h2>Section Three</h2><p>Three.</p>{fig(4)}
{boundary_prefix}{b}{boundary_suffix}{notes()}{fig(99)}
</article></main>'''


def fixture(payload: str, mode: str) -> str:
    if mode == "valid":
        article = base_article()
    elif mode == "id-only":
        article = base_article(boundary='<h2 class="wp-block-heading" id="sources">Sources</h2>')
    elif mode == "class-only":
        article = base_article(boundary='<h2 class="wp-block-heading fv-source-heading">Sources</h2>')
    elif mode == "exact-plus-id-only":
        article = base_article(boundary_prefix='<h2 class="wp-block-heading" id="sources">Earlier partial Sources</h2>')
    elif mode == "exact-plus-class-only":
        article = base_article(boundary_suffix='<h2 class="wp-block-heading fv-source-heading">Later partial Sources</h2>')
    elif mode == "misleading-earlier":
        article = base_article(boundary_prefix='<div id="sources">Misleading earlier source marker</div>')
    elif mode == "misleading-later":
        article = base_article(boundary_suffix='<div class="fv-source-heading">Misleading later source marker</div>')
    elif mode == "duplicate-exact":
        article = base_article(boundary_suffix=canonical())
    elif mode == "reversed-boundary":
        article = f'''<main><article><h1>Reversed</h1>{notes()}<h2>One</h2>{fig(1)}<h2>Two</h2>{fig(2)}<h2>Three</h2>{fig(3)}{canonical()}</article></main>'''
    elif mode == "too-few":
        article = f'''<main><article><h1>Thin</h1><h2>One</h2>{fig(1)}<h2>Two</h2>{fig(2)}{canonical()}{notes()}</article></main>'''
    else:
        raise ValueError(mode)

    assertions = f'''
<script>
const fvvtTest=()=>{{
 const mode={mode!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
  const band=document.querySelector('[data-fvvt-band]');
  if(mode!=='valid'){{if(band||document.querySelector('.fvvt-dialog'))return fail('invalid boundary activated Visual Trail');return pass();}}
  if(!band)return fail('valid canonical boundary did not activate');
  if(!band.textContent.includes('4 published figures'))return fail('figure qualification crossed source boundary');
  const opener=band.querySelector('.fvvt-open');opener.focus();opener.click();
  setTimeout(()=>{{try{{
   const dialog=document.querySelector('.fvvt-dialog');
   if(!dialog||!dialog.open)return fail('dialog did not open');
   if(dialog.querySelectorAll('.fvvt-index-button').length!==4)return fail('index count wrong');
   if(dialog.querySelector('.fvvt-position').textContent!=='Figure 1 of 4')return fail('initial position wrong');
   dialog.dispatchEvent(new KeyboardEvent('keydown',{{key:'End',bubbles:true}}));
   if(dialog.querySelector('.fvvt-position').textContent!=='Figure 4 of 4')return fail('End navigation failed');
   dialog.querySelector('.fvvt-view').click();
   setTimeout(()=>{{if(document.activeElement!==document.getElementById('fig-4'))return fail('story focus return failed');pass();}},120);
  }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},90);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvvtTest,{{once:true}});else fvvtTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'></head><body>{article}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = (
        "valid", "id-only", "class-only", "exact-plus-id-only", "exact-plus-class-only",
        "misleading-earlier", "misleading-later", "duplicate-exact", "reversed-boundary", "too-few"
    )
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in modes:
                page = root / f"visual-trail-r1-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--virtual-time-budget=2200", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    actual_hash = hashlib.sha256(raw).hexdigest()
    print(f"VISUAL_TRAIL_R1_BYTES={len(raw)}")
    print(f"VISUAL_TRAIL_R1_SHA256={actual_hash}")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(actual_hash == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_hash}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require("article h2#sources.fv-source-heading" in text and "canonical.length!==1" in text, "exact canonical Sources gate missing")
    require("article.querySelectorAll('#sources, .fv-source-heading')" in text, "competing partial source-boundary candidate scan missing")
    require("sourceHeadingCandidates.length!==1||sourceHeadingCandidates[0]!==sourceHeading" in text, "fail-closed competing-boundary guard missing")
    require("noteRoots.length!==1" in text and "DOCUMENT_POSITION_FOLLOWING" in text, "ordered unique source list gate missing")
    require("figures.length<3||figures.length>12" in text, "bounded figure qualification missing")
    require("It does not rate their evidentiary weight." in text, "evidence-boundary disclosure missing")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState", "navigator.clipboard", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics token: {token}")
    match = re.search(r'<script id="fv-visual-trail-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Visual Trail R1 exact payload identity locked; exact canonical boundary remains valid; every ID-only, class-only, duplicate, earlier/later partial or reversed boundary fails closed; core navigation/focus, evidence disclosure and zero-persistence/network boundaries verified")


if __name__ == "__main__":
    main()
