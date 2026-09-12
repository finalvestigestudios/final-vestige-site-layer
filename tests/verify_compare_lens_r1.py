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
    return """
<figure class="wp-block-image publisher-one" id="fig-1"><a href="/img/original-1.jpg"><img src="/img/1.jpg" srcset="https://evil.example/1-big.jpg 2200w, /img/1-large.jpg 1200w" alt="Figure one"><figcaption>Figure one caption</figcaption></a></figure>
<figure class="wp-block-image publisher-two fv-compare-lens-flash" id="fig-2" tabindex="-7"><img src="/img/2.jpg" srcset="https://evil.example/2-big.jpg 2200w, /img/2-large.jpg 1200w" alt="Figure two"><figcaption>Figure two caption</figcaption></figure>
<figure class="wp-block-image publisher-external" id="fig-3"><img src="https://evil.example/3.jpg" srcset="https://evil.example/3-big.jpg 2200w" alt="External only"><figcaption>External-only figure</figcaption></figure>
"""


def article(mode: str) -> str:
    story = f"""<main><article class="post type-post"><div class="entry-content">
<h1>Case</h1><h2>Section One</h2><p>Opening context for the figures.</p>{figures()}
"""
    if mode == "valid":
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


def fixture(payload: str, mode: str) -> str:
    runtime = f"""
<script>
const fvclTest=()=>{{
 const mode={mode!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>document.body.dataset.fvTest='pass';
 try{{
  const launch=document.querySelector('.fv-compare-lens-launch');
  if(mode!=='valid'){{if(launch||document.querySelector('.fv-compare-lens-dialog'))return fail('invalid source boundary activated');return pass();}}
  if(!launch)return fail('valid canonical boundary did not activate');
  const opener=launch.querySelector('.fv-compare-lens-open');
  opener.click();
  setTimeout(()=>{{try{{
   const dialog=document.querySelector('.fv-compare-lens-dialog');
   if(!dialog||!dialog.open)return fail('dialog did not open');
   const selects=[...dialog.querySelectorAll('.fv-compare-lens-select')];
   if(selects.length!==2||selects[0].options.length!==2)return fail('unsafe external-only image was not excluded');
   const modalImages=[...dialog.querySelectorAll('.fv-compare-lens-image')];
   if(modalImages.some(img=>new URL(img.src).origin!==location.origin))return fail('modal image selected cross-origin URL');
   if(!modalImages[0].src.endsWith('/img/original-1.jpg'))return fail('same-origin original link was not preferred');
   if(!modalImages[1].src.endsWith('/img/2-large.jpg'))return fail('cross-origin srcset candidate was not ignored');
   const fig1=document.getElementById('fig-1'),fig2=document.getElementById('fig-2');
   const fig1Class=fig1.getAttribute('class'),fig2Class=fig2.getAttribute('class');
   if(fig1.hasAttribute('tabindex'))return fail('fixture 1 should start without tabindex');
   dialog.querySelector('[data-original="0"]').click();
   setTimeout(()=>{{try{{
    if(document.activeElement!==fig1)return fail('absent-tabindex figure did not receive focus');
    opener.focus();
    setTimeout(()=>{{try{{
     if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('temporary state was not restored');
     opener.click();
     setTimeout(()=>{{try{{
      const d2=document.querySelector('.fv-compare-lens-dialog');
      d2.querySelector('[data-original="0"]').click();
      setTimeout(()=>{{try{{
       if(document.activeElement!==fig1)return fail('repeat jump did not focus target');
       opener.focus();
       setTimeout(()=>{{try{{
        if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('repeat jump drifted publisher state');
        opener.click();
        setTimeout(()=>{{try{{
         const d3=document.querySelector('.fv-compare-lens-dialog');
         const firstSelect=d3.querySelector('[data-select="0"]');firstSelect.value='1';firstSelect.dispatchEvent(new Event('change',{{bubbles:true}}));
         d3.querySelector('[data-original="0"]').click();
         setTimeout(()=>{{try{{
          if(document.activeElement!==fig2)return fail('pre-owned tabindex target did not focus');
          opener.focus();
          setTimeout(()=>{{try{{
           if(fig2.getAttribute('tabindex')!=='-7'||fig2.getAttribute('class')!==fig2Class)return fail('pre-owned tabindex/class was damaged');
           const savedScroll=fig1.scrollIntoView;fig1.scrollIntoView=()=>{{throw new Error('forced scroll failure')}};
           opener.click();
           setTimeout(()=>{{try{{
            const d4=document.querySelector('.fv-compare-lens-dialog');const s4=d4.querySelector('[data-select="0"]');s4.value='0';s4.dispatchEvent(new Event('change',{{bubbles:true}}));d4.querySelector('[data-original="0"]').click();
            setTimeout(()=>{{try{{
             if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('scroll failure mutated publisher state');
             if(document.activeElement!==opener)return fail('scroll failure did not recover focus');
             fig1.scrollIntoView=savedScroll;
             const savedFocus=fig1.focus;fig1.focus=()=>{{}};
             opener.click();
             setTimeout(()=>{{try{{
              const d5=document.querySelector('.fv-compare-lens-dialog');const s5=d5.querySelector('[data-select="0"]');s5.value='0';s5.dispatchEvent(new Event('change',{{bubbles:true}}));d5.querySelector('[data-original="0"]').click();
              setTimeout(()=>{{try{{
               if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==fig1Class)return fail('focus failure did not restore publisher state');
               if(document.activeElement!==opener)return fail('focus failure did not recover focus');
               fig1.focus=savedFocus;pass();
              }}catch(e){{fail(e.message)}}}},100);
             }}catch(e){{fail(e.message)}}}},80);
            }}catch(e){{fail(e.message)}}}},100);
           }}catch(e){{fail(e.message)}}}},80);
          }}catch(e){{fail(e.message)}}}},40);
         }}catch(e){{fail(e.message)}}}},100);
        }}catch(e){{fail(e.message)}}}},80);
       }}catch(e){{fail(e.message)}}}},40);
      }}catch(e){{fail(e.message)}}}},100);
     }}catch(e){{fail(e.message)}}}},80);
    }}catch(e){{fail(e.message)}}}},40);
   }}catch(e){{fail(e.message)}}}},100);
  }}catch(e){{fail(e.message)}}}},100);
 }}catch(e){{fail(e.message)}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvclTest,{{once:true}});else fvclTest();
</script>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'></head><body class='single-post'>{article(mode)}{payload}{runtime}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = ("valid", "missing-boundary", "id-only", "class-only", "exact-plus-partial", "duplicate-exact", "reversed-notes")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "img").mkdir()
        for name in ("1.jpg", "original-1.jpg", "1-large.jpg", "2.jpg", "2-large.jpg"):
            (root / "img" / name).write_bytes(b"\xff\xd8\xff\xd9")
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            for mode in modes:
                page = root / f"compare-lens-r1-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--host-resolver-rules=MAP evil.example 127.0.0.1", "--virtual-time-budget=6000", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=35,
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
    print(f"COMPARE_LENS_R1_BYTES={len(raw)}")
    print(f"COMPARE_LENS_R1_SHA256={actual_hash}")
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
    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Compare Lens R1 trusted Sources boundary, same-origin image selection, nondestructive repeated story focus, failure-atomic restoration, accessibility, and zero-persistence/network API contracts verified")


if __name__ == "__main__":
    main()
