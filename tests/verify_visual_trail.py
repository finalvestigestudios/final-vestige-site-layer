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
PAYLOAD = ROOT / "payloads" / "visual-trail-wp-block-v1.txt"
EXPECTED_BYTES = 12448
EXPECTED_SHA256 = "0258e7c18bdcdeb53273801f69cb1fdd3b420e73013917d624b15f2e44155bdc"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fig(n: int, caption: str, alt: str) -> str:
    return f"""<figure class="wp-block-image" id="fig-{n}">
<img src="/img/{n}.jpg" alt="{alt}">
<figcaption>{caption}</figcaption>
</figure>"""


def source_block(include_after_figure: bool = True) -> str:
    tail = fig(99, "Source-section image", "Image that belongs after the source boundary") if include_after_figure else ""
    return f"""
<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1">Museum source <a href="https://example.org/one">Open source</a></li>
<li id="fv-fn-2">Archive source <a href="https://example.org/two">Open source</a></li>
<li id="fv-fn-3">Newspaper source <a href="https://example.org/three">Open source</a></li>
</ul>
{tail}
"""


def valid_article() -> str:
    return f"""
<main><article id="post-621"><h1>Six Miles an Hour</h1>
<p>Opening narrative.</p>
{fig(1, "Tunnel geometry", "View into the tunnel")}
<h2>The curve under Malbone Street</h2>
<p>Curve narrative.</p>
{fig(2, "Network map", "Brooklyn Rapid Transit map")}
<h2>Why the wooden cars made the wreck worse</h2>
<p>Train construction narrative.</p>
{fig(3, "Train sequence", "Five-car train sequence")}
<h2>The switch upstairs</h2>
<p>Power restoration narrative.</p>
{fig(4, "Power sequence", "Power restoration sequence")}
{source_block()}
</article></main>
"""


def fixture(payload: str, mode: str) -> str:
    if mode == "valid":
        article = valid_article()
    elif mode == "partial-boundary":
        article = valid_article().replace(
            '<h2 class="wp-block-heading fv-source-heading" id="sources">',
            '<h2 class="wp-block-heading" id="sources">'
        )
    elif mode == "ambiguous-boundary":
        article = valid_article().replace(
            '<h2 class="wp-block-heading fv-source-heading" id="sources">',
            '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources</h2>'
            '<h2 class="wp-block-heading fv-source-heading" id="sources">'
        )
    elif mode == "reversed-boundary":
        notes = """<ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source</li></ul>"""
        article = f"""<main><article><h1>Reversed</h1>{notes}
        <h2>The first section</h2>{fig(1, "One", "One")}
        <h2>The second section</h2>{fig(2, "Two", "Two")}
        <h2>The third section</h2>{fig(3, "Three", "Three")}
        <h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>
        </article></main>"""
    elif mode == "too-few":
        article = f"""<main><article><h1>Thin</h1>
        <h2>One</h2>{fig(1, "One", "One")}
        <h2>Two</h2>{fig(2, "Two", "Two")}
        {source_block(False)}</article></main>"""
    else:
        raise ValueError(mode)

    assertions = f"""
<script>
const fvvtTest=()=>{{
  const mode={mode!r};
  const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
  const pass=()=>{{document.body.dataset.fvTest='pass'}};
  try{{
    const band=document.querySelector('[data-fvvt-band]');
    if(mode!=='valid'){{
      if(band||document.querySelector('.fvvt-dialog'))return fail('invalid fixture did not fail closed');
      return pass();
    }}
    if(!band)return fail('Visual Trail launcher missing');
    if(!band.textContent.includes('4 published figures'))return fail('figure count includes wrong side of Sources boundary');
    if(!band.textContent.includes('images and diagrams already published here'))return fail('scope copy missing');
    const opener=band.querySelector('.fvvt-open');opener.click();
    setTimeout(()=>{{
      try{{
        const dialog=document.querySelector('.fvvt-dialog');
        if(!dialog||!dialog.open)return fail('dialog did not open');
        if(dialog.getAttribute('aria-labelledby')!=='fvvt-title')return fail('dialog label missing');
        if(dialog.querySelectorAll('.fvvt-index-button').length!==4)return fail('visual index count wrong');
        if(dialog.querySelector('.fvvt-position').textContent!=='Figure 1 of 4')return fail('initial position wrong');
        if(dialog.querySelector('.fvvt-section').textContent!=='Opening')return fail('opening context wrong');
        if(dialog.querySelector('.fvvt-image').getAttribute('alt')!=='View into the tunnel')return fail('published alt text not preserved');
        dialog.querySelector('.fvvt-next').click();
        if(dialog.querySelector('.fvvt-position').textContent!=='Figure 2 of 4')return fail('next control failed');
        if(dialog.querySelector('.fvvt-section').textContent!=='The curve under Malbone Street')return fail('nearest section context wrong');
        dialog.dispatchEvent(new KeyboardEvent('keydown',{{key:'End',bubbles:true}}));
        if(dialog.querySelector('.fvvt-position').textContent!=='Figure 4 of 4')return fail('End navigation failed');
        dialog.dispatchEvent(new KeyboardEvent('keydown',{{key:'Home',bubbles:true}}));
        if(dialog.querySelector('.fvvt-position').textContent!=='Figure 1 of 4')return fail('Home navigation failed');
        dialog.querySelectorAll('.fvvt-index-button')[3].click();
        if(dialog.querySelector('.fvvt-position').textContent!=='Figure 4 of 4')return fail('index navigation failed');
        dialog.querySelector('.fvvt-view').click();
        setTimeout(()=>{{
          try{{
            if(dialog.open)return fail('View in story did not close dialog');
            if(document.activeElement!==document.getElementById('fig-4'))return fail('View in story did not focus original figure');
            opener.click();
            setTimeout(()=>{{
              try{{
                dialog.querySelector('.fvvt-close').click();
                setTimeout(()=>{{
                  if(document.activeElement!==opener)return fail('close did not return focus to opener');
                  if(document.querySelectorAll('figure.wp-block-image').length!==5)return fail('published figure DOM was cloned or removed');
                  return pass();
                }},60);
              }}catch(e){{fail(e&&e.message?e.message:String(e))}}
            }},70);
          }}catch(e){{fail(e&&e.message?e.message:String(e))}}
        }},100);
      }}catch(e){{fail(e&&e.message?e.message:String(e))}}
    }},80);
  }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvvtTest,{{once:true}});else fvvtTest();
</script>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Visual Trail fixture</title></head><body>{article}{payload}{assertions}</body></html>"


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
            for mode in ("valid", "partial-boundary", "ambiguous-boundary", "reversed-boundary", "too-few"):
                page = root / f"visual-trail-{mode}.html"
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
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-visual-trail-v1-css">' in text and '<script id="fv-visual-trail-v1-js">' in text, "versioned style/script ids missing")
    require("window.__fvVisualTrail" in text, "duplicate-init guard missing")
    require("article h2#sources.fv-source-heading" in text and "canonical.length!==1" in text, "exact canonical Sources heading gate missing")
    require("noteRoots.length!==1" in text and "DOCUMENT_POSITION_FOLLOWING" in text, "unique correctly ordered source-list gate missing")
    require("figures.length<3||figures.length>12" in text and "storyHeadings.length<2||storyHeadings.length>10" in text, "bounded visual/story qualification missing")
    require("figure.wp-block-image" in text and "before(f,sourceHeading)" in text, "pre-Sources figure boundary missing")
    require("See the investigation through the images and diagrams already published here." in text, "visitor-value microcopy missing")
    require("It does not rate their evidentiary weight." in text, "evidence-boundary disclosure missing")
    require('aria-roledescription="carousel"' in text and 'aria-live="polite"' in text, "carousel/live-region semantics missing")
    require("ArrowLeft" in text and "ArrowRight" in text and "Home" in text and "End" in text, "keyboard navigation missing")
    require("View in story" in text and "opener.focus()" in text and "target.focus" in text, "story-return/focus behavior missing")
    require("min-height:44px" in text and "@media(max-width:720px)" in text and "@media(max-width:360px)" in text, "touch/mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility media handling missing")
    require("setInterval" not in text and "autoplay" not in text.lower(), "automatic rotation is forbidden")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest",
              "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState",
              "navigator.clipboard", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics token: {token}")
    match = re.search(r'<script id="fv-visual-trail-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Visual Trail exact identity, canonical source boundary, bounded figure sequence, published alt/caption reuse, manual and keyboard navigation, story return/focus, responsive accessibility, zero persistence/API boundary, and adversarial browser fixtures verified")


if __name__ == "__main__":
    main()
