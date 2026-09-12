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
PAYLOAD = ROOT / "payloads" / "compare-lens-wp-block-r1.txt"
EXPECTED_BYTES = 19152
EXPECTED_SHA256 = "5275862a6a81f5f9e3a093a7a71780e15fa6bbb5e2d6599615ed88867fb5c5e3"

INVALID_MODES = ("missing-boundary", "id-only", "class-only", "exact-plus-partial", "duplicate-exact", "reversed-notes")
VALID_PHASES = ("network", "state-absent", "state-owned", "scroll-fail", "focus-fail")
ALL_BROWSER_MODES = VALID_PHASES + INVALID_MODES


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def canonical() -> str:
    return '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'


def notes() -> str:
    return '<ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source one</li><li id="fv-fn-2">Source two</li></ul>'


def figures() -> str:
    x = "__CROSS__"
    return f"""
<figure class="wp-block-image publisher-one" id="fig-1"><a href="/img/original-1.jpg"><img src="/img/1.jpg" srcset="{x}/img/evil-1.jpg 2200w, /img/1-large.jpg 1200w" alt="Figure one"><figcaption>Figure one caption</figcaption></a></figure>
<figure class="wp-block-image publisher-two fv-compare-lens-flash" id="fig-2" tabindex="-7"><img src="/img/2.jpg" srcset="{x}/img/evil-2.jpg 2200w, /img/2-large.jpg 1200w" alt="Figure two"><figcaption>Figure two caption</figcaption></figure>
<figure class="wp-block-image publisher-external" id="fig-3"><img src="{x}/img/evil-3.jpg" srcset="{x}/img/evil-3-large.jpg 2200w" alt="External only"><figcaption>External-only figure</figcaption></figure>
"""


def article(mode: str) -> str:
    story = f"""<main><article class="post type-post"><div class="entry-content">
<h1>Case</h1><h2>Section One</h2><p>Opening context for the figures.</p>{figures()}
"""
    if mode in VALID_PHASES:
        return story + canonical() + notes() + "</div></article></main>"
    if mode == "missing-boundary":
        return story + notes() + "</div></article></main>"
    if mode == "id-only":
        return story + '<h2 id="sources">Sources</h2>' + notes() + "</div></article></main>"
    if mode == "class-only":
        return story + '<h2 class="fv-source-heading">Sources</h2>' + notes() + "</div></article></main>"
    if mode == "exact-plus-partial":
        return story + '<div class="fv-source-heading">False marker</div>' + canonical() + notes() + "</div></article></main>"
    if mode == "duplicate-exact":
        return story + canonical() + canonical() + notes() + "</div></article></main>"
    if mode == "reversed-notes":
        return story + notes() + canonical() + "</div></article></main>"
    raise ValueError(mode)


def runtime_script(mode: str) -> str:
    if mode in INVALID_MODES:
        return f"""
<script>
const run=()=>{{const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};const pass=()=>document.body.dataset.fvTest='pass';
try{{if(document.querySelector('.fv-compare-lens-launch')||document.querySelector('.fv-compare-lens-dialog'))return fail('invalid source boundary activated');pass()}}catch(e){{fail(e.message)}}}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{{once:true}});else run();
</script>"""
    setup = """
 const launch=document.querySelector('.fv-compare-lens-launch');if(!launch)return fail('valid canonical boundary did not activate');
 const opener=launch.querySelector('.fv-compare-lens-open');const fig1=document.getElementById('fig-1'),fig2=document.getElementById('fig-2');
 const fig1Class=fig1.getAttribute('class'),fig2Class=fig2.getAttribute('class');
"""
    if mode == "network":
        body = """
 opener.click();setTimeout(()=>{try{
  const dialog=document.querySelector('.fv-compare-lens-dialog');if(!dialog||!dialog.open)return fail('dialog did not open');
  const selects=[...dialog.querySelectorAll('.fv-compare-lens-select')];if(selects.length!==2||selects[0].options.length!==2)return fail('unsafe external-only image was not excluded');
  const imgs=[...dialog.querySelectorAll('.fv-compare-lens-image')];if(imgs.some(img=>new URL(img.src).origin!==location.origin))return fail('modal image selected cross-origin URL');
  if(!imgs[0].src.endsWith('/img/original-1.jpg'))return fail('same-origin original link was not preferred');
  if(!imgs[1].src.endsWith('/img/2-large.jpg'))return fail('cross-origin srcset candidate was not ignored');
  pass();
 }catch(e){fail(e.message)}},100);
"""
    elif mode == "state-absent":
        body = """
 let targetFocus=0;const nativeTargetFocus=fig1.focus.bind(fig1);fig1.focus=opts=>{targetFocus++;nativeTargetFocus(opts)};
 const once=repeat=>{opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
  if(targetFocus<(repeat?1:2))return fail('absent-tabindex target focus transaction did not run');opener.focus();setTimeout(()=>{try{
   if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('temporary state was not restored');
   if(repeat)return once(false);pass();
  }catch(e){fail(e.message)}},40);
 }catch(e){fail(e.message)}},100)}catch(e){fail(e.message)}},80)};
 once(true);
"""
    elif mode == "state-owned":
        body = """
 let targetFocus=0;const nativeTargetFocus=fig2.focus.bind(fig2);fig2.focus=opts=>{targetFocus++;nativeTargetFocus(opts)};
 opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');const s=d.querySelector('[data-select="0"]');s.value='1';s.dispatchEvent(new Event('change',{bubbles:true}));d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
  if(targetFocus<1)return fail('pre-owned target focus transaction did not run');opener.focus();setTimeout(()=>{try{
   if(fig2.getAttribute('tabindex')!=='-7'||fig2.getAttribute('class')!==fig2Class)return fail('pre-owned tabindex/class was damaged');pass();
  }catch(e){fail(e.message)}},40);
 }catch(e){fail(e.message)}},100)}catch(e){fail(e.message)}},80);
"""
    elif mode == "scroll-fail":
        body = """
 let recovery=0;const nativeOpenFocus=opener.focus.bind(opener);opener.focus=()=>{recovery++;nativeOpenFocus()};fig1.scrollIntoView=()=>{throw new Error('forced scroll failure')};opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
  if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('scroll failure mutated publisher state');
  if(recovery<1)return fail('scroll failure did not invoke launcher focus recovery');pass();
 }catch(e){fail(e.message)}},100)}catch(e){fail(e.message)}},80);
"""
    elif mode == "focus-fail":
        body = """
 let recovery=0;const nativeOpenFocus=opener.focus.bind(opener);opener.focus=()=>{recovery++;nativeOpenFocus()};fig1.focus=()=>{};opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
  if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('focus failure did not restore publisher state');
  if(recovery<1)return fail('focus failure did not invoke launcher focus recovery');pass();
 }catch(e){fail(e.message)}},100)}catch(e){fail(e.message)}},80);
"""
    else:
        raise ValueError(mode)
    return f"""
<script>
const run=()=>{{const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};const pass=()=>document.body.dataset.fvTest='pass';
try{{{setup}{body}}}catch(e){{fail(e.message)}}}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{{once:true}});else run();
</script>"""


def fixture(payload: str, mode: str, cross_origin: str) -> str:
    html = f"<!doctype html><html><head><meta charset='utf-8'></head><body class='single-post'>{article(mode)}{payload}{runtime_script(mode)}</body></html>"
    return html.replace("__CROSS__", cross_origin)


def run_browser_mode(payload: str, mode: str) -> None:
    require(mode in ALL_BROWSER_MODES, f"unknown browser mode: {mode}")
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); (root / "img").mkdir()
        for name in ("1.jpg", "original-1.jpg", "1-large.jpg", "2.jpg", "2-large.jpg", "evil-1.jpg", "evil-2.jpg", "evil-3.jpg", "evil-3-large.jpg"):
            (root / "img" / name).write_bytes(b"\xff\xd8\xff\xd9")
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        cross = f"http://localhost:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            page = root / f"compare-lens-r1-{mode}.html"
            page.write_text(fixture(payload, mode, cross), encoding="utf-8")
            proc = subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                 "--virtual-time-budget=3000", "--dump-dom", f"{origin}/{page.name}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
            )
            require(proc.returncode == 0, f"browser mode {mode} failed to execute: {proc.stderr[-500:]}")
            if 'data-fv-test="pass"' not in proc.stdout:
                reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                raise SystemExit(f"FAIL: browser mode {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes(); text = raw.decode("utf-8"); actual_hash = hashlib.sha256(raw).hexdigest()
    print(f"COMPARE_LENS_R1_BYTES={len(raw)}"); print(f"COMPARE_LENS_R1_SHA256={actual_hash}")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(actual_hash == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_hash}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    require("h2#sources.fv-source-heading" in text and "canonical.length!==1" in text, "canonical source boundary gate missing")
    require("content.querySelectorAll('#sources,.fv-source-heading')" in text and "candidates.length!==1" in text, "competing source markers must fail closed")
    require("noteRoots.length!==1" in text and "DOCUMENT_POSITION_FOLLOWING" in text, "ordered source-note root gate missing")
    require("u.origin===location.origin" in text and "safeUrl(parts[0])" in text, "same-origin srcset guard missing")
    require("if(!imageUrl)return null" in text, "unsafe-only image candidate must be excluded")
    require("target.scrollIntoView" in text and "const state={hadClassAttr" in text, "scroll-before-owned-mutation state contract missing")
    require("addedTab:!target.hasAttribute('tabindex')" in text and "target.getAttribute('tabindex')==='-1'" in text, "tabindex ownership contract missing")
    require("addedFlash:!target.classList.contains('fv-compare-lens-flash')" in text, "publisher class ownership contract missing")
    require("document.activeElement!==target" in text and "restoreFocusState(target,state)" in text, "failure-atomic focus restoration missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text, "mobile/touch target contract missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text, "accessibility media contracts missing")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics token: {token}")
    match = re.search(r'<script id="fv-compare-lens-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    mode = os.environ.get("FV_BROWSER_MODE")
    if mode:
        run_browser_mode(text, mode)
    print(f"PASS: Compare Lens R1 static contract{' + browser mode '+mode if mode else ''}")


if __name__ == "__main__":
    main()
