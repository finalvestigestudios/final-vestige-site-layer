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
PAYLOAD = ROOT / "payloads" / "case-packet-wp-block-r1.txt"
EXPECTED_BYTES = 20410
EXPECTED_SHA256 = "2b661516a5932a0e4d50c183aba25eec306d8163b10017069104777d5ef8b90c"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def cite(section: str, i: int, n: int, wrapped: bool = False) -> str:
    a = f'<a href="#fv-fn-{n}" class="fv-fn-ref" data-fv-fn="{n}" id="ref-{section}-{i}">{n}</a>'
    return f'<sup class="fv-fn-mark">{a}</sup>' if wrapped else a


def para(section: str, i: int, n: int | None = None, wrapped: bool = False) -> str:
    citation = "" if n is None else cite(section, i, n, wrapped)
    return (
        f'<p id="p-{section}-{i}">{section} narrative paragraph {i} preserves enough published wording '
        f'to create a stable Case Packet research fixture without inventing editorial context. {citation}</p>'
    )


def figure(section: str, i: int) -> str:
    return (
        f'<figure class="wp-block-image"><img src="/fixture-{section}-{i}.jpg" alt="Alt text for {section} figure {i}">'
        f'<figcaption>Published caption for {section} figure {i}.</figcaption></figure>'
    )


def source_block(origin: str, n: int = 7) -> str:
    items: list[str] = []
    for i in range(1, n + 1):
        if i == 1:
            links = (
                f'<a href="https://sources.example/{i}">archival catalog record</a> and '
                f'<a href="https://mirror.example/{i}">institutional mirror</a> '
                f'<a href="{origin}/internal/{i}">same-site utility</a> '
                f'<a href="/relative/{i}">relative utility</a>'
            )
        else:
            links = f'<a href="https://sources.example/{i}">source record {i}</a>'
        items.append(
            f'<li id="fv-fn-{i}">Published source note {i} with archival context and {links}. '
            f'<span class="fv-fn-backlinks"><a href="#ref-opening-1">↩</a></span></li>'
        )
    return (
        '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
        '<ul class="fv-source-list" data-fv-footnotes>' + "".join(items) + "</ul>"
    )


def valid_article(origin: str, wrapped: bool = False) -> str:
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
{para("opening",1,1,wrapped)}{para("opening",2,None,wrapped)}{figure("opening",1)}{para("opening",3,3,wrapped)}
<h2>The curve under Malbone Street</h2>{para("curve",1,1,wrapped)}{para("curve",2,3,wrapped)}{figure("curve",1)}{para("curve",3,1,wrapped)}
<h2>Why the wooden cars made the wreck worse</h2>{para("cars",1,5,wrapped)}{para("cars",2,3,wrapped)}{figure("cars",1)}{para("cars",3,1,wrapped)}
<h2>The switch upstairs</h2>{para("switch",1,2,wrapped)}{figure("switch",1)}{para("switch",2,None,wrapped)}{para("switch",3,2,wrapped)}
{source_block(origin)}</article></main>'''


def fixture(payload: str, mode: str, origin: str) -> str:
    wrapped = mode == "legacy-wrapper"
    article = valid_article(origin, wrapped)
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
        block = source_block(origin)
        heading = '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
        notes = block.split('</h2>', 1)[1]
        article = valid_article(origin, False).replace(block, heading).replace('<h1>Six Miles an Hour</h1>', '<h1>Six Miles an Hour</h1>' + notes, 1)
    elif mode == "duplicate-note-root":
        article = article.replace(source_block(origin), source_block(origin) + '<ul data-fv-footnotes><li id="fv-fn-30">Duplicate root</li></ul>')
    elif mode == "missing-note":
        article = article.replace('href="#fv-fn-3" class="fv-fn-ref" data-fv-fn="3"', 'href="#fv-fn-30" class="fv-fn-ref" data-fv-fn="30"', 1)
    elif mode == "too-few-citations":
        article = re.sub(r'<a href="#fv-fn-\d+" class="fv-fn-ref"[^>]*>\d+</a>', '', article, count=5)
    elif mode not in {"valid", "legacy-wrapper"}:
        raise ValueError(mode)

    invalid = {
        "mixed-id-only", "mixed-class-only", "partial-only", "ambiguous-exact",
        "misleading-later-partial", "reversed-boundary", "duplicate-note-root",
        "missing-note", "too-few-citations",
    }
    assertions = f'''
<script>
const fvcpTest=()=>{{
 const mode={mode!r},invalid={sorted(invalid)!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
  const band=document.querySelector('[data-fvcp-band]');
  if(invalid.includes(mode)){{if(band||document.querySelector('.fvcp-dialog'))return fail('invalid fixture did not fail closed');return pass()}}
  if(!band)return fail('Case Packet launcher missing');
  const launch=band.querySelector('.fvcp-button');launch.focus();launch.click();
  setTimeout(()=>{{try{{
   const d=document.querySelector('.fvcp-dialog');if(!d||!d.open)return fail('dialog did not open');
   const choices=[...d.querySelectorAll('.fvcp-section-choice input')];if(choices.length!==4)return fail('expected four story areas');
   d.querySelector('.fvcp-toolbar .fvcp-linkbutton:nth-child(2)').click();
   const boxes=[...d.querySelectorAll('.fvcp-section-choice input')];boxes[1].click();boxes[3].click();d.querySelector('[data-fvcp-preview]').click();
   setTimeout(()=>{{try{{
    const body=d.querySelector('.fvcp-preview-body'),text=body.textContent;
    if(!text.includes('The curve under Malbone Street')||!text.includes('The switch upstairs'))return fail('selected sections missing');
    if(text.includes('Why the wooden cars made the wreck worse')||text.includes('Opening context'))return fail('unselected sections leaked');
    if(!text.includes('[1]')||!text.includes('[2]'))return fail('citation numbers not normalized from live anchor contract');
    if(!text.includes('archival catalog record')||!text.includes('institutional mirror'))return fail('semantic external-anchor text was lost');
    if(text.includes('↩'))return fail('backlink utility text leaked into source note');
    const firstSource=body.querySelector('.fvcp-source-list ol > li');const links=[...firstSource.querySelectorAll('.fvcp-source-links a')];
    if(links.length!==2)return fail('expected exactly two legitimate external source links, got '+links.length);
    if(!links[0].href.startsWith('https://sources.example/1')||!links[1].href.startsWith('https://mirror.example/1'))return fail('external source links not deterministic');
    if(links.some(a=>a.href.includes('/internal/')||a.href.includes('/relative/')||a.getAttribute('href').startsWith('#')))return fail('internal/backlink utility URL promoted');
    if(!text.includes('Published source note 1')||!text.includes('Published source note 2')||!text.includes('Published source note 3'))return fail('selected source provenance incomplete');
    if(text.includes('Published source note 5'))return fail('uncited source leaked');
    if(!text.includes('Figure references'))return fail('figure references missing');
    if(text.includes('?campaign=abc')||text.includes('#frag'))return fail('query/fragment leaked into packet URL');
    d.querySelector('.fvcp-close').click();setTimeout(()=>{{if(document.activeElement!==launch)return fail('focus return failed');pass()}},70);
   }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},80);
  }}catch(e){{fail(e&&e.message?e.message:String(e))}}}},80);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvcpTest,{{once:true}});else fvcpTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Case Packet R1 fixture</title><script>window.print=()=>{{document.body.dataset.printCalled='yes'}};</script></head><body>{article}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = (
        "valid", "legacy-wrapper", "mixed-id-only", "mixed-class-only", "partial-only", "ambiguous-exact",
        "misleading-later-partial", "reversed-boundary", "duplicate-note-root", "missing-note", "too-few-citations",
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
                page = root / f"case-packet-r1-{mode}.html"
                page.write_text(fixture(payload, mode, origin), encoding="utf-8")
                url = f"{origin}/{page.name}?campaign=abc#frag"
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--virtual-time-budget=3500", "--dump-dom", url],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=40,
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
    require("querySelectorAll('.fv-fn-ref[data-fv-fn]')" in text and "sup.fv-fn-mark > a.fv-fn-ref" not in text, "wrapper-independent citation discovery required")
    require("clone.querySelectorAll('.fv-fn-ref[data-fv-fn]')" in text, "wrapper-independent paragraph normalization required")
    require("c.querySelectorAll('a').forEach(a=>a.replaceWith(document.createTextNode(a.textContent||'')))" in text, "source-note semantic anchor text preservation required")
    require("a.closest('.fv-fn-backlinks')" in text and "u.origin===location.origin" in text and "out.length===4" in text, "bounded external-link provenance filtering required")
    require("boundaryCandidates.length!==1" in text and "noteRoots.length!==1" in text and "!follows(sourceHeading,notesRoot)" in text, "unique ordered sources boundary required")
    require('Build case packet' in text and 'Preview packet' in text and 'Print / Save PDF' in text and 'Linked source notes' in text, "core packet controls missing")
    require('not a separate edition, revision history, or evidence score' in text and 'does not score evidence, infer citations' in text, "truthfulness boundary missing")
    require('min-height:44px' in text and '@media(max-width:360px)' in text and 'prefers-reduced-motion:reduce' in text and 'forced-colors:active' in text and '@media print' in text, "accessibility/responsive contract missing")
    banned = ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'WebSocket', 'localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'posthog', 'gtag(', '<iframe', '<script src=', 'navigator.clipboard', 'history.pushState', 'history.replaceState']
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected network/persistence/analytics/navigation token: {token}")
    match = re.search(r'<script id="fv-case-packet-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(['node', '--check', str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    run_browser(text)
    print(f'PASS: Case Packet R1 {len(raw)} bytes {actual}; wrapper-free + legacy citations, semantic source text, deterministic external links, fail-closed boundaries')


if __name__ == '__main__':
    main()
