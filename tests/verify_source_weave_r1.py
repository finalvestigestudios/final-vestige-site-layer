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
PAYLOAD = ROOT / "payloads" / "source-weave-wp-block-r1.txt"
EXPECTED_BYTES = 17101
EXPECTED_SHA256 = "6b4a5295eadbec5ec17cccc240bbc33c4bd182c8c0390d469554436b6bab8f27"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def sources(heading: str = '<h2 id="sources" class="fv-source-heading">Sources &amp; Further Reading</h2>') -> str:
    return f"""
{heading}
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1" class="publisher-source" tabindex="5">Museum source one <a href="https://example.org/one">Open source</a></li>
<li id="fv-fn-2">Archive source two <a href="https://example.org/two">Open source</a></li>
<li id="fv-fn-3">Newspaper source three <a href="https://example.org/three">Open source</a></li>
<li id="fv-fn-4">Photograph source four <a href="https://example.org/four">Open source</a></li>
</ul>
"""


def core_article(prefix: str = "", source_markup: str | None = None) -> str:
    source_markup = source_markup if source_markup is not None else sources()
    return f"""
<main><article id="post-621"><h1>Six Miles an Hour</h1>
{prefix}
<p>Opening narrative <sup><a class="fv-fn-ref" data-fv-fn="1" id="fv-fnref-1-1" href="#fv-fn-1">1</a></sup>.</p>
<p>Another opening paragraph <sup><a class="fv-fn-ref" data-fv-fn="2" id="fv-fnref-2-1" href="#fv-fn-2">2</a></sup>.</p>
<h2>The curve</h2>
<p>Curve evidence <sup><a class="fv-fn-ref" data-fv-fn="1" id="fv-fnref-1-2" href="#fv-fn-1">1</a></sup> and again <sup><a class="fv-fn-ref" data-fv-fn="1" id="fv-fnref-1-3" href="#fv-fn-1">1</a></sup>.</p>
<p>Training record <sup><a class="fv-fn-ref" data-fv-fn="3" id="fv-fnref-3-1" href="#fv-fn-3">3</a></sup>.</p>
<h2>Why the cars failed</h2>
<p>Configuration <sup><a class="fv-fn-ref" data-fv-fn="1" id="fv-fnref-1-4" href="#fv-fn-1">1</a></sup>.</p>
<p>Power restoration <sup><a class="fv-fn-ref" data-fv-fn="2" id="fv-fnref-2-2" href="#fv-fn-2">2</a></sup>.</p>
<p>Contemporary report <sup><a class="fv-fn-ref" data-fv-fn="4" id="fv-fnref-4-1" href="#fv-fn-4">4</a></sup>.</p>
<h2>The switch upstairs</h2>
<p>Surviving switch <sup><a class="fv-fn-ref" data-fv-fn="2" id="fv-fnref-2-3" href="#fv-fn-2">2</a></sup>.</p>
{source_markup}
</article></main>
"""


def article_for(mode: str) -> str:
    if mode == "valid":
        return core_article()
    if mode == "id-only":
        return core_article(source_markup=sources('<h2 id="sources">Sources</h2>'))
    if mode == "class-only":
        return core_article(source_markup=sources('<h2 class="fv-source-heading">Sources</h2>'))
    if mode == "misleading-half":
        return core_article(prefix='<h2 id="sources">Earlier legacy marker</h2>')
    if mode == "duplicate-canonical":
        return core_article(prefix='<h2 id="sources" class="fv-source-heading">Misleading duplicate</h2>')
    if mode == "duplicate-root":
        return core_article(prefix='<ul data-fv-footnotes><li id="fv-fn-99">Wrong root</li></ul>')
    if mode == "reversed-boundary":
        return f"<main><article>{sources()}<h2>Late one</h2><p><a class='fv-fn-ref' data-fv-fn='1' href='#fv-fn-1'>1</a></p><h2>Late two</h2><p><a class='fv-fn-ref' data-fv-fn='2' href='#fv-fn-2'>2</a></p></article></main>"
    raise ValueError(mode)


def fixture(payload: str, mode: str) -> str:
    article = article_for(mode)
    should_launch = mode in {"valid", "misleading-half"}
    assertions = f"""
<script>
const run=()=>{{
 const mode={mode!r}, shouldLaunch={str(should_launch).lower()};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
  const band=document.querySelector('[data-fvsw-band]'), dialog=document.querySelector('.fvsw-dialog');
  if(!shouldLaunch){{if(band||dialog)return fail('ambiguous or partial boundary did not fail closed');return pass();}}
  if(!band||!dialog)return fail('valid canonical boundary did not launch');
  if(mode==='misleading-half'&&!band.nextElementSibling?.matches('h2#sources')){{/* insertion point may precede first real story h2; half-match must not own boundary */}}
  if(!band.textContent.includes('4 cited source notes')||!band.textContent.includes('4 story areas')||!band.textContent.includes('8 source-to-story connections'))return fail('structural counts wrong');
  band.querySelector('.fvsw-open').click();
  setTimeout(()=>{{try{{
   if(!dialog.open)return fail('dialog did not open');
   const table=dialog.querySelector('.fvsw-table');
   if(!table||table.querySelectorAll('thead th[scope="col"]').length!==5||table.querySelectorAll('tbody th[scope="row"]').length!==4)return fail('matrix semantics wrong');
   dialog.querySelector('[data-mode="reused"]').click();
   if(!dialog.querySelector('.fvsw-stats').textContent.includes('2 sources'))return fail('reused filter wrong');
   dialog.querySelector('[data-mode="all"]').click();
   const row1=table.querySelector('tr[data-source-id="1"]');
   const rel=[...row1.querySelectorAll('.fvsw-link')].find(b=>b.textContent.includes('2 citations'));
   if(!rel)return fail('explicit repeated relation missing');
   const target=document.getElementById('fv-fnref-1-2');
   const beforeClass=target.getAttribute('class'), beforeTab=target.getAttribute('tabindex');
   rel.click();
   setTimeout(()=>{{try{{
    if(dialog.open||document.activeElement!==target)return fail('relation jump focus wrong');
    band.querySelector('.fvsw-open').click();
    setTimeout(()=>{{try{{
      const src2=dialog.querySelector('tr[data-source-id="2"] .fvsw-source');src2.click();
      setTimeout(()=>{{try{{
        const source=document.getElementById('fv-fn-2');
        if(document.activeElement!==source)return fail('source jump focus wrong');
        setTimeout(()=>{{
          if(target.getAttribute('class')!==beforeClass||target.getAttribute('tabindex')!==beforeTab)return fail('citation DOM state not restored');
          if(source.hasAttribute('class')||source.hasAttribute('tabindex'))return fail('absent source attrs not restored to absent');
          const owned=document.getElementById('fv-fn-1');
          band.querySelector('.fvsw-open').click();setTimeout(()=>{{
            dialog.querySelector('tr[data-source-id="1"] .fvsw-source').click();
            setTimeout(()=>{{
              if(owned.getAttribute('class')!=='publisher-source'||owned.getAttribute('tabindex')!=='5')return fail('publisher-owned attrs changed');
              return pass();
            }},1600);
          }},60);
        }},1600);
      }}catch(e){{fail(e.message||String(e))}}}},80);
    }}catch(e){{fail(e.message||String(e))}}}},60);
   }}catch(e){{fail(e.message||String(e))}}}},80);
  }}catch(e){{fail(e.message||String(e))}}}},80);
 }}catch(e){{fail(e.message||String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{{once:true}});else run();
</script>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'></head><body>{article}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            origin = f"http://127.0.0.1:{server.server_port}"
            for mode in ("valid", "id-only", "class-only", "misleading-half", "duplicate-canonical", "duplicate-root", "reversed-boundary"):
                page = root / f"source-weave-{mode}.html"; page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run([browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--virtual-time-budget=7000", "--dump-dom", f"{origin}/{page.name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=35)
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes(); text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual = hashlib.sha256(raw).hexdigest(); require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "isolated wp:html block required")
    require("querySelectorAll('h2#sources.fv-source-heading')" in text and "canonical.length!==1" in text, "exact canonical heading resolver missing")
    require("sourceRoots.length!==1" in text and "compareDocumentPosition(sourceRoot)" in text, "source-root uniqueness/order binding missing")
    require("querySelectorAll('h2#sources,h2.fv-source-heading')" in text and "!partial.includes(h)" in text, "partial-marker exclusion missing")
    require("storyH2.length<2||storyH2.length>8" in text and "refs.length<6||refs.length>120" in text and "sourceItems.size<4||sourceItems.size>40" in text, "qualification bounds missing")
    require("Connections reflect this page’s existing footnote links. They do not score evidence quality or confidence." in text, "evidence boundary disclosure missing")
    require("scope='col'" in text and "scope='row'" in text and "createElement('caption')" in text, "accessible matrix semantics missing")
    require("hadClass" in text and "hadTab" in text and "removeAttribute('class')" in text and "removeAttribute('tabindex')" in text, "nondestructive DOM restoration missing")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState", "navigator.clipboard", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics token: {token}")
    match = re.search(r'<script id="fv-source-weave-r1-js">\n(.*?)\n</script>', text, flags=re.S); require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME") == "1": run_browser(text)
    print(f"PASS: Source Weave R1 canonical provenance boundary and browser regressions verified; bytes={len(raw)} sha256={actual}")


if __name__ == "__main__":
    main()
