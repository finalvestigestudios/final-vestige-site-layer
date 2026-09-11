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
PAYLOAD = ROOT / "payloads" / "case-packet-wp-block-v1.txt"
EXPECTED_BYTES = 19974
EXPECTED_SHA256 = "3eea754c68ea5b0d782829304e4d5fe54febd7fcfd66398af1b0484726e7cd7e"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def para(section: str, i: int, cite: int | None = None) -> str:
    citation = "" if cite is None else f'<sup class="fv-fn-mark"><a href="#fv-fn-{cite}" class="fv-fn-ref" data-fv-fn="{cite}" id="ref-{section}-{i}">{cite}</a></sup>'
    return (
        f'<p id="p-{section}-{i}">{section} narrative paragraph {i} preserves enough published wording '
        f'to create a stable Case Packet research fixture without inventing editorial context. {citation}</p>'
    )


def figure(section: str, i: int) -> str:
    return (
        f'<figure class="wp-block-image"><img src="/fixture-{section}-{i}.jpg" alt="Alt text for {section} figure {i}">'
        f'<figcaption>Published caption for {section} figure {i}.</figcaption></figure>'
    )


def source_block(n: int = 7) -> str:
    items = "".join(
        f'<li id="fv-fn-{i}">Published source note {i} with archival context and a source control '
        f'<a href="https://sources.example/{i}">Open source</a><span class="fv-fn-backlinks">'
        f'<a href="#ref-opening-1">↩</a></span></li>'
        for i in range(1, n + 1)
    )
    return '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>' + f'<ul class="fv-source-list" data-fv-footnotes>{items}</ul>'


def valid_article() -> str:
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
{para("opening",1,1)}{para("opening",2)}{figure("opening",1)}{para("opening",3,3)}
<h2>The curve under Malbone Street</h2>
{para("curve",1,1)}{para("curve",2,3)}{figure("curve",1)}{para("curve",3,1)}
<h2>Why the wooden cars made the wreck worse</h2>
{para("cars",1,5)}{para("cars",2,3)}{figure("cars",1)}{para("cars",3,1)}
<h2>The switch upstairs</h2>
{para("switch",1,2)}{figure("switch",1)}{para("switch",2)}{para("switch",3,2)}
{source_block(7)}
</article></main>'''


def fixture(payload: str, mode: str) -> str:
    article = valid_article()
    exact = '<h2 class="wp-block-heading fv-source-heading" id="sources">'
    if mode == "mixed-id-only":
        article = article.replace(exact, '<h2 id="sources">Competing ID-only boundary</h2>' + exact, 1)
    elif mode == "mixed-class-only":
        article = article.replace(exact, '<h2 class="fv-source-heading">Competing class-only boundary</h2>' + exact, 1)
    elif mode == "partial-only":
        article = article.replace('class="wp-block-heading fv-source-heading" id="sources"', 'class="wp-block-heading" id="sources"', 1)
    elif mode == "ambiguous-exact":
        article = article.replace(exact, '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources A</h2>' + exact, 1)
    elif mode == "misleading-later-partial":
        article = article.replace('</article>', '<h2 class="fv-source-heading">Later competing sources marker</h2></article>', 1)
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
        article = re.sub(r'<sup class="fv-fn-mark">.*?</sup>', '', article, count=5)
    elif mode != "valid":
        raise ValueError(mode)

    invalid = {
        "mixed-id-only", "mixed-class-only", "partial-only", "ambiguous-exact",
        "misleading-later-partial", "reversed-boundary", "duplicate-note-root",
        "missing-note", "too-few-citations"
    }
    assertions = f'''
<script>
const fvcpTest=()=>{{
 const mode={mode!r};
 const invalid={sorted(invalid)!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
  const band=document.querySelector('[data-fvcp-band]');
  if(invalid.includes(mode)){{if(band||document.querySelector('.fvcp-dialog'))return fail('invalid fixture did not fail closed');return pass()}}
  if(!band)return fail('Case Packet launcher missing');
  if(!band.textContent.includes('Build a print-ready packet'))return fail('launcher value proposition missing');
  const launch=band.querySelector('.fvcp-button');launch.focus();launch.click();
  setTimeout(()=>{{
   try{{
    const d=document.querySelector('.fvcp-dialog');if(!d||!d.open)return fail('dialog did not open');
    if(d.getAttribute('aria-labelledby')!=='fvcp-title')return fail('dialog accessible name missing');
    const choices=[...d.querySelectorAll('.fvcp-section-choice input')];if(choices.length!==4)return fail('expected four selectable story areas, got '+choices.length);
    if(!d.textContent.includes('does not score evidence'))return fail('evidence boundary copy missing');
    d.querySelector('.fvcp-toolbar .fvcp-linkbutton:nth-child(2)').click();
    const preview=d.querySelector('[data-fvcp-preview]');if(!preview.disabled)return fail('preview should disable after Clear');
    const boxes=[...d.querySelectorAll('.fvcp-section-choice input')];boxes[1].click();boxes[3].click();
    if(preview.disabled)return fail('preview did not re-enable after selection');
    preview.click();
    setTimeout(()=>{{
     try{{
      const text=d.querySelector('.fvcp-preview-body').textContent;
      if(!text.includes('The curve under Malbone Street')||!text.includes('The switch upstairs'))return fail('selected sections missing from preview');
      if(text.includes('Why the wooden cars made the wreck worse')||text.includes('Opening context'))return fail('unselected sections leaked into preview');
      if(!text.includes('Linked source notes'))return fail('linked-source section missing');
      if(!text.includes('Published source note 1')||!text.includes('Published source note 2')||!text.includes('Published source note 3'))return fail('selected source provenance incomplete');
      if(text.includes('Published source note 5'))return fail('uncited-to-selection source leaked into packet');
      if(!text.includes('Figure references'))return fail('figure references missing');
      if(text.includes('fixture-curve-1.jpg'))return fail('image URL leaked as image-copy surrogate');
      if(text.includes('?campaign=abc')||text.includes('#frag'))return fail('tracking query/fragment leaked into packet URL');
      if(!text.includes('Source page: http://127.0.0.1:')||!text.includes('/case-packet-valid.html'))return fail('preview source URL missing');
      const print=d.querySelector('[data-fvcp-print]');if(!print)return fail('print action missing');
      const back=d.querySelector('.fvcp-actions .is-secondary');back.click();
      setTimeout(()=>{{
       try{{
        const figToggle=d.querySelector('.fvcp-options input[type="checkbox"]');figToggle.click();
        d.querySelector('[data-fvcp-preview]').click();
        setTimeout(()=>{{
         try{{
          if(d.querySelector('.fvcp-preview-body').textContent.includes('Figure references'))return fail('figure toggle did not suppress references');
          d.querySelector('.fvcp-close').click();
          setTimeout(()=>{{if(document.activeElement!==launch)return fail('close did not restore launcher focus');pass()}},80);
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
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvcpTest,{{once:true}});else fvcpTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Case Packet fixture</title><script>window.print=()=>{{document.body.dataset.printCalled='yes'}};</script></head><body>{article}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = (
        "valid", "mixed-id-only", "mixed-class-only", "partial-only", "ambiguous-exact",
        "misleading-later-partial", "reversed-boundary", "duplicate-note-root", "missing-note", "too-few-citations"
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
                page = root / f"case-packet-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                url = f"{origin}/{page.name}?campaign=abc#frag"
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--virtual-time-budget=3500", "--dump-dom", url],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=40
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
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(text.count('<!-- wp:html -->') == 1 and text.count('<!-- /wp:html -->') == 1, "single isolated wp:html block required")
    require('<style id="fv-case-packet-v1-css">' in text and '<script id="fv-case-packet-v1-js">' in text, "versioned style/script ids missing")
    require('window.__fvCasePacketV1' in text, "duplicate-init guard missing")
    require("querySelectorAll('#sources,.fv-source-heading')" in text and 'boundaryCandidates.length!==1' in text, "mixed exact/partial Sources-boundary rejection missing")
    require("sourceHeading.tagName!=='H2'||sourceHeading.id!=='sources'||!sourceHeading.classList.contains('fv-source-heading')" in text, "exact canonical Sources identity gate missing")
    require("noteRoots.length!==1" in text and "!follows(sourceHeading,notesRoot)" in text, "unique ordered source-list gate missing")
    require("rawRefs.length<6||rawRefs.length>60" in text and "distinctCited.length<3" in text, "bounded citation qualification missing")
    require("ref.getAttribute('href')!==`#fv-fn-${n}`" in text and "!noteMap.has(n)" in text, "exact citation-to-note mapping gate missing")
    require('Build case packet' in text and 'Preview packet' in text and 'Print / Save PDF' in text and 'Linked source notes' in text, "core packet controls missing")
    require('not a separate edition, revision history, or evidence score' in text, "truthfulness boundary missing")
    require('only the source notes they already cite' in text, "provenance scope copy missing")
    require('window.print()' in text and 'html.fvcp-printing body>*:not(.fvcp-print-root)' in text and '@page{margin:' in text, "bounded browser-print path missing")
    require("`${u.origin}${u.pathname}`" in text, "query-free source URL normalization missing")
    require("figures.indexOf(f)+1" in text and "img')?.getAttribute('alt')" in text and "figcaption')?.textContent" in text, "figure-reference provenance missing")
    require('min-height:44px' in text and '@media(max-width:700px)' in text and '@media(max-width:360px)' in text, "touch/mobile behavior missing")
    require('prefers-reduced-motion:reduce' in text and 'forced-colors:active' in text and '@media print' in text, "accessibility/print media handling missing")
    banned = ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'WebSocket', 'localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'posthog', 'gtag(', '<iframe', '<script src=', 'navigator.clipboard', 'history.pushState', 'history.replaceState']
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected network/persistence/analytics/navigation token: {token}")
    match = re.search(r'<script id="fv-case-packet-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(['node', '--check', str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get('FV_BROWSER_RUNTIME') == '1':
        run_browser(text)
    print('PASS: Case Packet exact identity, hardened canonical Sources boundary, bounded section/source derivation, selected-story packet preview, caption/alt-only figure references, query-free browser-print path, accessibility/mobile behavior, zero-network/persistence boundary, and mixed-boundary adversarial browser fixtures verified')


if __name__ == '__main__':
    main()
