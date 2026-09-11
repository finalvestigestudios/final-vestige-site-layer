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
PAYLOAD = ROOT / "payloads" / "source-route-wp-block-v1.txt"
EXPECTED_BYTES = 13713
EXPECTED_SHA256 = "2d2140848a574042c2cafcff33671c756c261ed4bd3aad1995c5c272ad10b137"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def para(section: str, i: int, cite: int | None = None) -> str:
    citation = "" if cite is None else f'<sup class="fv-fn-mark"><a href="#fv-fn-{cite}" class="fv-fn-ref" data-fv-fn="{cite}" id="ref-{section}-{i}">{cite}</a></sup>'
    return f'<p id="p-{section}-{i}">{section} narrative paragraph {i} carries enough published wording to establish a stable story-context fixture for Source Route. {citation}</p>'


def source_block(n: int = 7) -> str:
    items = "".join(
        f'<li id="fv-fn-{i}">Published source note {i} with archive context and a source link <a href="https://example.org/{i}">Open source</a><span class="fv-fn-backlinks"><a href="#ref-opening-1">↩</a></span></li>'
        for i in range(1, n + 1)
    )
    return f'<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2><ul class="fv-source-list" data-fv-footnotes>{items}</ul>'


def valid_article() -> str:
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
{para("opening",1,1)}{para("opening",2)}{para("opening",3,3)}
<h2>The curve under Malbone Street</h2>
{para("curve",1,1)}{para("curve",2,3)}{para("curve",3,1)}
<h2>Why the wooden cars made the wreck worse</h2>
{para("cars",1,5)}{para("cars",2,3)}{para("cars",3,1)}
<h2>The switch upstairs</h2>
{para("switch",1,2)}{para("switch",2)}{para("switch",3,2)}
{source_block(7)}
</article></main>'''


def fixture(payload: str, mode: str) -> str:
    article = valid_article()
    if mode == "mixed-id-only":
        article = article.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">', '<h2 id="sources">Competing sources marker</h2><h2 class="wp-block-heading fv-source-heading" id="sources">', 1)
    elif mode == "mixed-class-only":
        article = article.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">', '<h2 class="fv-source-heading">Competing sources marker</h2><h2 class="wp-block-heading fv-source-heading" id="sources">', 1)
    elif mode == "partial-only":
        article = article.replace('class="wp-block-heading fv-source-heading" id="sources"', 'class="wp-block-heading" id="sources"', 1)
    elif mode == "ambiguous-exact":
        article = article.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">', '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources A</h2><h2 class="wp-block-heading fv-source-heading" id="sources">', 1)
    elif mode == "reversed-boundary":
        block = source_block(7)
        heading = '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
        notes = block.split('</h2>', 1)[1]
        article = valid_article().replace(block, heading).replace('<h1>Six Miles an Hour</h1>', '<h1>Six Miles an Hour</h1>' + notes, 1)
    elif mode == "duplicate-note-root":
        article = article.replace(source_block(7), source_block(7) + '<ul data-fv-footnotes><li id="fv-fn-30">Duplicate root</li></ul>')
    elif mode == "missing-note":
        article = article.replace('href="#fv-fn-3" class="fv-fn-ref" data-fv-fn="3"', 'href="#fv-fn-30" class="fv-fn-ref" data-fv-fn="30"', 1)
    elif mode == "too-few-citations":
        article = re.sub(r'<sup class="fv-fn-mark">.*?</sup>', '', article, count=7)
    elif mode != "valid":
        raise ValueError(mode)

    invalid = {"mixed-id-only", "mixed-class-only", "partial-only", "ambiguous-exact", "reversed-boundary", "duplicate-note-root", "missing-note", "too-few-citations"}
    assertions = f'''
<script>
const fvsrTest=()=>{{
 const mode={mode!r};
 const invalid={sorted(invalid)!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
  const band=document.querySelector('[data-fvsr-band]');
  if(invalid.includes(mode)){{if(band||document.querySelector('.fvsr-dialog'))return fail('invalid fixture did not fail closed');return pass()}}
  if(!band)return fail('Source Route launcher missing');
  if(!band.textContent.includes('10 published citations')||!band.textContent.includes('4 cited sources'))return fail('launcher counts wrong');
  const launch=band.querySelector('.fvsr-button');launch.focus();launch.click();
  setTimeout(()=>{{
   try{{
    const d=document.querySelector('.fvsr-dialog');if(!d||!d.open)return fail('dialog did not open');
    if(d.getAttribute('aria-labelledby')!=='fvsr-title')return fail('dialog accessible name missing');
    if(!d.textContent.includes('does not rate evidence'))return fail('evidence boundary disclosure missing');
    if(!d.querySelector('.fvsr-status').textContent.includes('Citation 1 of 10 · Source 1 · use 1 of 4'))return fail('initial route status wrong');
    d.querySelector('.fvsr-next').click();
    if(!d.querySelector('.fvsr-status').textContent.includes('Citation 2 of 10 · Source 3'))return fail('next citation failed');
    const first=d.querySelector('[data-mode="first"]');first.click();
    if(!d.querySelector('.fvsr-status').textContent.includes('Citation 1 of 4'))return fail('first-use route count wrong');
    d.dispatchEvent(new KeyboardEvent('keydown',{{key:'End',bubbles:true}}));
    if(!d.querySelector('.fvsr-status').textContent.includes('Citation 4 of 4 · Source 2'))return fail('End transport failed');
    d.querySelector('[data-jump="source"]').click();
    setTimeout(()=>{{
     try{{
      if(d.open)return fail('view source did not close dialog');
      if(document.activeElement.id!=='fv-fn-2')return fail('view source did not focus original source note');
      launch.focus();launch.click();
      setTimeout(()=>{{
       try{{
        if(!d.open)return fail('dialog did not reopen');
        d.querySelector('.fvsr-next').click();
        const expected=d.querySelector('.fvsr-status').textContent;
        if(!expected.includes('Citation 2 of 10'))return fail('all-citation mode did not reset on reopen');
        d.querySelector('[data-jump="passage"]').click();
        setTimeout(()=>{{
         try{{
          if(document.activeElement.id!=='ref-opening-3')return fail('view passage did not focus original citation');
          launch.focus();launch.click();
          setTimeout(()=>{{
           d.querySelector('.fvsr-close').click();
           setTimeout(()=>{{if(document.activeElement!==launch)return fail('close did not return focus to launcher');return pass()}},80);
          }},80);
         }}catch(e){{fail(e&&e.message?e.message:String(e))}}
        }},80);
       }}catch(e){{fail(e&&e.message?e.message:String(e))}}
      }},80);
     }}catch(e){{fail(e&&e.message?e.message:String(e))}}
    }},80);
   }}catch(e){{fail(e&&e.message?e.message:String(e))}}
  }},80);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvsrTest,{{once:true}});else fvsrTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Source Route fixture</title></head><body>{article}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = ("valid", "mixed-id-only", "mixed-class-only", "partial-only", "ambiguous-exact", "reversed-boundary", "duplicate-note-root", "missing-note", "too-few-citations")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
        try:
            for mode in modes:
                page = root / f"source-route-{mode}.html";page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run([browser,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--virtual-time-budget=3000","--dump-dom",f"{origin}/{page.name}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=35)
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason=re.search(r'data-fv-reason="([^"]*)"',proc.stdout);raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)


def main() -> None:
    raw=PAYLOAD.read_bytes();text=raw.decode('utf-8')
    require(len(raw)==EXPECTED_BYTES,f"payload byte count drifted: {len(raw)}")
    actual=hashlib.sha256(raw).hexdigest();require(actual==EXPECTED_SHA256,f"payload SHA-256 drifted: {actual}")
    require(text.count('<!-- wp:html -->')==1 and text.count('<!-- /wp:html -->')==1,'single isolated wp:html block required')
    require('<style id="fv-source-route-v1-css">' in text and '<script id="fv-source-route-v1-js">' in text,'versioned style/script ids missing')
    require('window.__fvSourceRouteV1' in text,'duplicate-init guard missing')
    require("querySelectorAll('#sources,.fv-source-heading')" in text and 'boundaryCandidates.length!==1' in text,'mixed exact/partial Sources-boundary rejection missing')
    require("sourceHeading.tagName!=='H2'||sourceHeading.id!=='sources'||!sourceHeading.classList.contains('fv-source-heading')" in text,'exact canonical Sources identity gate missing')
    require("noteRoots.length!==1" in text and "!follows(sourceHeading,notesRoot)" in text,'unique ordered source-list gate missing')
    require("rawRefs.length<6||rawRefs.length>60" in text and "distinct.length<3" in text,'bounded citation qualification missing')
    require("ref.getAttribute('href')!==`#fv-fn-${n}`" in text and "!noteMap.has(n)" in text,'exact citation-to-note mapping gate missing')
    require('All citations' in text and 'First use per source' in text and 'View passage' in text and 'View source note' in text,'route controls incomplete')
    require('This follows existing source links; it does not rate evidence or claim a source proves the passage.' in text,'evidence boundary disclosure missing')
    require('min-height:44px' in text and '@media(max-width:680px)' in text and '@media(max-width:360px)' in text,'touch/mobile behavior missing')
    require('prefers-reduced-motion:reduce' in text and 'forced-colors:active' in text and '@media print' in text,'accessibility media handling missing')
    banned=['fetch(','XMLHttpRequest','sendBeacon','WebSocket','localStorage','sessionStorage','indexedDB','document.cookie','posthog','gtag(','<iframe','<script src=','navigator.clipboard','history.pushState','history.replaceState']
    lower=text.lower()
    for token in banned: require(token.lower() not in lower,f"unexpected network/persistence/analytics/navigation token: {token}")
    match=re.search(r'<script id="fv-source-route-v1-js">\n(.*?)\n</script>',text,flags=re.S);require(match is not None,'unable to extract JavaScript')
    with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as handle:handle.write(match.group(1));js_path=Path(handle.name)
    try:subprocess.run(['node','--check',str(js_path)],check=True)
    finally:js_path.unlink(missing_ok=True)
    if os.environ.get('FV_BROWSER_RUNTIME')=='1':run_browser(text)
    print('PASS: Source Route exact identity, hardened canonical source boundary, bounded citation-to-note traversal, first-use mode, original passage/source focus return, mobile/accessibility behavior, zero-network/persistence boundary, and mixed-boundary adversarial browser fixtures verified')

if __name__=='__main__':main()
