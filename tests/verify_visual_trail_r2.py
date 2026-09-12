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
PAYLOAD = ROOT / "payloads" / "visual-trail-wp-block-r2.txt"
EXPECTED_BYTES = 13261
EXPECTED_SHA256 = "20000f451ca59962b77bb24db7ffaae84b5de4693dddf32751e47b98b83d9992"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fig(n: int, *, alt: str | None = None, caption: str | None = None, extra_attrs: str = "") -> str:
    alt_attr = "" if alt is None else f' alt="{alt}"'
    caption_html = "" if caption is None else f"<figcaption>{caption}</figcaption>"
    owned_class = " fvvt-story-focus" if n == 4 else ""
    return f'''<figure class="wp-block-image{owned_class}" id="fig-{n}"{extra_attrs}><img src="/img/{n}.jpg"{alt_attr}>{caption_html}</figure>'''


def canonical() -> str:
    return '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'


def notes() -> str:
    return '<ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source</li></ul>'


def valid_figures() -> str:
    return "\n".join([
        fig(1, alt="", caption="Caption only 1"),
        fig(2, alt="Alt only 2"),
        fig(3, alt="  Exact alt 3  ", caption="Caption 3"),
        fig(4, alt="Alt 4", caption="Caption 4", extra_attrs=' tabindex="-7" data-owned="yes"'),
    ])


def base_article(boundary_prefix: str = "", boundary_suffix: str = "", boundary: str | None = None) -> str:
    b = canonical() if boundary is None else boundary
    figs = valid_figures().splitlines()
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
<p>Opening.</p>{figs[0]}
<h2>Section One</h2><p>One.</p>{figs[1]}
<h2>Section Two</h2><p>Two.</p>{figs[2]}
<h2>Section Three</h2><p>Three.</p>{figs[3]}
{boundary_prefix}{b}{boundary_suffix}{notes()}{fig(99, alt="After sources", caption="After")}
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
        article = f'''<main><article><h1>Reversed</h1>{notes()}<h2>One</h2>{fig(1, alt="A", caption="A")}<h2>Two</h2>{fig(2, alt="B", caption="B")}<h2>Three</h2>{fig(3, alt="C", caption="C")}{canonical()}</article></main>'''
    elif mode == "too-few":
        article = f'''<main><article><h1>Thin</h1><h2>One</h2>{fig(1, alt="A", caption="A")}<h2>Two</h2>{fig(2, alt="B", caption="B")}{canonical()}{notes()}</article></main>'''
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
   const image=dialog.querySelector('.fvvt-image'),caption=dialog.querySelector('.fvvt-caption');
   if(image.getAttribute('alt')!=='')return fail('caption-only empty alt was not preserved exactly');
   if(caption.textContent!=='Caption only 1'||caption.hasAttribute('aria-hidden'))return fail('caption-only context semantics wrong');
   dialog.querySelector('.fvvt-next').click();
   if(image.getAttribute('alt')!=='Alt only 2')return fail('alt-only image alt drifted');
   if(caption.textContent!=='Alt only 2'||caption.getAttribute('aria-hidden')!=='true')return fail('alt-only fallback must be visual but AT-suppressed');
   dialog.querySelector('.fvvt-next').click();
   if(image.getAttribute('alt')!=='  Exact alt 3  ')return fail('alt+caption exact published alt whitespace drifted');
   if(caption.textContent!=='Caption 3'||caption.hasAttribute('aria-hidden'))return fail('alt+caption visible caption semantics wrong');
   const fig3=document.getElementById('fig-3');
   if(fig3.hasAttribute('tabindex')||fig3.classList.contains('fvvt-story-focus'))return fail('fixture 3 pre-state wrong');
   dialog.querySelector('.fvvt-view').click();
   setTimeout(()=>{{try{{
    if(document.activeElement!==fig3)return fail('story focus return failed for absent tabindex');
    opener.focus();
    setTimeout(()=>{{try{{
     if(fig3.hasAttribute('tabindex')||fig3.classList.contains('fvvt-story-focus'))return fail('temporary story focus state not restored');
     opener.click();
     setTimeout(()=>{{try{{
      const d2=document.querySelector('.fvvt-dialog');d2.dispatchEvent(new KeyboardEvent('keydown',{{key:'End',bubbles:true}}));
      const fig4=document.getElementById('fig-4');
      if(fig4.getAttribute('tabindex')!=='-7'||!fig4.classList.contains('fvvt-story-focus'))return fail('fixture 4 owned state wrong');
      d2.querySelector('.fvvt-view').click();
      setTimeout(()=>{{try{{
       if(document.activeElement!==fig4)return fail('story focus return failed for owned state');
       opener.focus();
       setTimeout(()=>{{try{{
        if(fig4.getAttribute('tabindex')!=='-7'||!fig4.classList.contains('fvvt-story-focus'))return fail('pre-owned state was damaged after first jump');
        opener.click();
        setTimeout(()=>{{try{{
         const d3=document.querySelector('.fvvt-dialog');d3.dispatchEvent(new KeyboardEvent('keydown',{{key:'End',bubbles:true}}));d3.querySelector('.fvvt-view').click();
         setTimeout(()=>{{opener.focus();setTimeout(()=>{{
          if(fig4.getAttribute('tabindex')!=='-7'||!fig4.classList.contains('fvvt-story-focus'))return fail('pre-owned state drifted after repeated jump');
          pass();
         }},40);}},80);
        }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},80);
       }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},40);
      }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},80);
     }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},80);
    }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},40);
   }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},80);
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
                page = root / f"visual-trail-r2-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--virtual-time-budget=3600", "--dump-dom", f"{origin}/{page.name}"],
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
    print(f"VISUAL_TRAIL_R2_BYTES={len(raw)}")
    print(f"VISUAL_TRAIL_R2_SHA256={actual_hash}")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(actual_hash == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_hash}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require("article h2#sources.fv-source-heading" in text and "canonical.length!==1" in text, "exact canonical Sources gate missing")
    require("article.querySelectorAll('#sources, .fv-source-heading')" in text, "competing partial source-boundary candidate scan missing")
    require("sourceHeadingCandidates.length!==1||sourceHeadingCandidates[0]!==sourceHeading" in text, "fail-closed competing-boundary guard missing")
    require("noteRoots.length!==1" in text and "DOCUMENT_POSITION_FOLLOWING" in text, "ordered unique source list gate missing")
    require("figures.length<3||figures.length>12" in text, "bounded figure qualification missing")
    require("const hasAlt=img.hasAttribute('alt')" in text and "img.getAttribute('alt')" in text, "exact published alt capture missing")
    require("if(item.hasAlt)image.setAttribute('alt'" in text and "else image.removeAttribute('alt')" in text, "exact modal alt semantics missing")
    require("caption.setAttribute('aria-hidden','true')" in text, "alt-only duplicate AT suppression missing")
    require("hadFocusClass=target.classList.contains('fvvt-story-focus')" in text, "owned-class preservation missing")
    require("if(!hadTab)target.removeAttribute('tabindex')" in text and "target.setAttribute('tabindex',oldTab)" in text, "tabindex restoration contract missing")
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
    print("PASS: Visual Trail R2 exact payload identity locked; caption-only empty alt, alt-only duplicate suppression, alt+caption exact alt fidelity, nondestructive repeated story-focus state restoration, R1 Sources boundaries, and zero-persistence/network guardrails verified")


if __name__ == "__main__":
    main()
