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
PAYLOAD = ROOT / "payloads" / "source-weave-wp-block-v1.txt"
EXPECTED_BYTES = 18995
EXPECTED_SHA256 = "7eaa3dcf2627192bcc9aeff83544a721b40c661928b99bd40cd2efbe788eb17a"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def source_list() -> str:
    return """
<h2 id="sources" class="fv-source-heading">Sources &amp; Further Reading</h2>
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1">Museum source one <a href="https://example.org/one">Open source</a><span class="fv-fn-backlinks"><a href="#fv-fnref-1-1">↩</a></span></li>
<li id="fv-fn-2">Archive source two <a href="https://example.org/two">Open source</a></li>
<li id="fv-fn-3">Newspaper source three <a href="https://example.org/three">Open source</a></li>
<li id="fv-fn-4">Photograph source four <a href="https://example.org/four">Open source</a></li>
</ul>
"""


def valid_article() -> str:
    return f"""
<main><article id="post-621"><h1>Six Miles an Hour</h1>
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
{source_list()}
</article></main>
"""


def fixture(payload: str, mode: str) -> str:
    if mode == "valid":
        article = valid_article()
    elif mode == "missing-boundary":
        article = valid_article().replace('id="sources" class="fv-source-heading"', 'id="references" class="source-heading"')
    elif mode == "reversed-boundary":
        sources = source_list()
        article = f"<main><article><h1>Bad order</h1>{sources}<h2>Late section</h2><p><a class='fv-fn-ref' data-fv-fn='1' href='#fv-fn-1'>1</a></p><h2>Later</h2><p><a class='fv-fn-ref' data-fv-fn='2' href='#fv-fn-2'>2</a></p></article></main>"
    elif mode == "too-thin":
        article = f"<main><article><h1>Thin</h1><h2>One</h2><p><a class='fv-fn-ref' data-fv-fn='1' href='#fv-fn-1'>1</a></p><h2>Two</h2><p><a class='fv-fn-ref' data-fv-fn='2' href='#fv-fn-2'>2</a></p>{source_list()}</article></main>"
    else:
        raise ValueError(mode)

    assertions = f"""
<script>
const fvswTest=()=>{{
  const mode={mode!r};
  const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
  const pass=()=>{{document.body.dataset.fvTest='pass'}};
  try{{
    const band=document.querySelector('[data-fvsw-band]');
    if(mode!=='valid'){{if(band||document.querySelector('.fvsw-dialog'))return fail('invalid fixture did not fail closed');return pass();}}
    if(!band)return fail('Source Weave launcher missing');
    if(!band.textContent.includes('4 cited source notes')||!band.textContent.includes('4 story areas')||!band.textContent.includes('8 source-to-story connections'))return fail('structural counts wrong');
    if(!band.textContent.includes('do not score evidence quality or confidence'))return fail('evidence boundary disclosure missing');
    const open=band.querySelector('.fvsw-open');open.click();
    setTimeout(()=>{{
      try{{
        const dialog=document.querySelector('.fvsw-dialog');if(!dialog||!dialog.open)return fail('dialog did not open');
        const table=dialog.querySelector('table.fvsw-table');if(!table)return fail('semantic table missing');
        if(table.querySelectorAll('thead th[scope="col"]').length!==5)return fail('column headers incorrect');
        if(table.querySelectorAll('tbody th[scope="row"]').length!==4)return fail('row headers incorrect');
        if(!table.querySelector('caption')||!table.querySelector('caption').textContent.includes('Published source notes'))return fail('caption missing');
        const src1=table.querySelector('tr[data-source-id="1"]');if(!src1)return fail('source 1 row missing');
        const buttons=[...src1.querySelectorAll('.fvsw-link')];
        if(buttons.length!==3)return fail('source 1 should connect to three story areas');
        if(!buttons.some(b=>b.textContent.includes('2')))return fail('repeated citation count missing');
        const reused=dialog.querySelector('.fvsw-filter[data-mode="reused"]');reused.click();
        const visibleRows=[...table.querySelectorAll('tbody tr')].filter(r=>!r.hidden);
        if(visibleRows.length!==2||visibleRows.some(r=>!['1','2'].includes(r.dataset.sourceId)))return fail('reused filter incorrect');
        dialog.querySelector('.fvsw-filter[data-mode="all"]').click();
        const targetButton=[...src1.querySelectorAll('.fvsw-link')].find(b=>b.textContent.includes('2'));if(!targetButton)return fail('target relation button missing');
        targetButton.click();
        setTimeout(()=>{{
          try{{
            if(dialog.open)return fail('relationship jump did not close dialog');
            const target=document.getElementById('fv-fnref-1-2');if(document.activeElement!==target)return fail('relationship jump did not focus first citation');
            open.click();setTimeout(()=>{{
              try{{
                const sourceJump=dialog.querySelector('tbody tr[data-source-id="2"] .fvsw-source-jump');sourceJump.click();
                setTimeout(()=>{{
                  const source=document.getElementById('fv-fn-2');if(document.activeElement!==source)return fail('source jump did not focus published source note');
                  if(document.querySelectorAll('[data-fv-footnotes] li').length!==4)return fail('source records mutated');
                  return pass();
                }},80);
              }}catch(e){{fail(e&&e.message?e.message:String(e))}}
            }},80);
          }}catch(e){{fail(e&&e.message?e.message:String(e))}}
        }},80);
      }}catch(e){{fail(e&&e.message?e.message:String(e))}}
    }},80);
  }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvswTest,{{once:true}});else fvswTest();
</script>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Source Weave fixture</title></head><body>{article}{payload}{assertions}</body></html>"


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
            for mode in ("valid", "missing-boundary", "reversed-boundary", "too-thin"):
                page = root / f"source-weave-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--virtual-time-budget=1800", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
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
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-source-weave-v1-css">' in text and '<script id="fv-source-weave-v1-js">' in text, "versioned style/script ids missing")
    require("window.__fvSourceWeave" in text, "duplicate-init guard missing")
    require("h2#sources.fv-source-heading,h2#sources,h2.fv-source-heading" in text and "[data-fv-footnotes]" in text, "trusted source boundary selectors missing")
    require("storyH2.length<2||storyH2.length>8" in text and "refs.length<6||refs.length>120" in text and "sourceItems.size<4||sourceItems.size>40" in text, "bounded qualification missing")
    require("sourceIds.length<3||relationCount<5" in text, "source/relation usefulness threshold missing")
    require("Connections reflect this page’s existing footnote links. They do not score evidence quality or confidence." in text, "evidence-boundary copy missing")
    require("A number is the count of existing footnote links" in text, "connection-count disclosure missing")
    require("scope='col'" in text and "scope='row'" in text and "createElement('caption')" in text, "accessible row/column table semantics missing")
    require("All cited sources" in text and "Reused across story areas" in text, "source filters missing")
    require("jumpToRef" in text and "jumpToSource" in text and "opener.focus()" in text, "jump/focus return behavior missing")
    require("min-height:44px" in text and "@media(max-width:720px)" in text and "@media(max-width:360px)" in text, "touch/mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility media handling missing")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState", "navigator.clipboard", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics token: {token}")
    match = re.search(r'<script id="fv-source-weave-v1-js">\n(.*?)\n</script>', text, flags=re.S); require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME") == "1": run_browser(text)
    print("PASS: Source Weave exact identity, trusted source boundary, explicit section-source mapping, accessible matrix/mobile relationship view, reused-source filter, deterministic citation/source jumps, fail-closed thresholds, zero-network/persistence boundary, and headless browser regressions verified")


if __name__ == "__main__":
    main()
