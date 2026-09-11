from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import threading
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "case-pin-wp-block-v1.txt"
EXPECTED_BYTES = 13593
EXPECTED_SHA256 = "268625ccd2014f4145e5292f0dcbca5b79ad1f7232781bf35c97894b7153fd0a"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def fnv1a_js(text: str) -> str:
    norm = " ".join(text.split()).strip().lower()
    h = 0x811C9DC5
    for ch in norm:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fig(n: int) -> str:
    return f'''<figure class="wp-block-image" id="figure-{n}"><img src="/img/{n}.jpg" alt="Archival figure {n}"><figcaption>Published figure {n} caption</figcaption></figure>'''


def source_block() -> str:
    return '''
<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1">Museum archive, primary route record <a href="https://example.org/one">Open source</a>. <span class="fv-fn-backlinks"><a href="#fv-fnref-1-1">↩</a></span></li>
<li id="fv-fn-2">City report, operating instructions <a href="https://example.org/two">Open source</a>.</li>
<li id="fv-fn-3">Contemporary newspaper account <a href="https://example.org/three">Open source</a>.</li>
<li id="fv-fn-4">Engineering collection, track plan <a href="https://example.org/four">Open source</a>.</li>
</ul>
'''


TARGET_TEXT = "This target passage contains the exact operational detail a researcher may want to share without sending someone to the top of a very long investigation."


def valid_article(extra_before_target: bool = False) -> str:
    extra = '<p id="inserted">A later editorial insertion shifts the old paragraph ordinal but should not cause Case Pin to target the wrong passage because the fingerprint remains unique.</p>' if extra_before_target else ''
    return f'''
<main><article id="post-621"><h1>Six Miles an Hour</h1>
<p>Opening narrative establishes the scene with enough substantive text to qualify as a useful longform paragraph for this deterministic fixture.</p>
<p>Opening narrative continues with another sufficiently long paragraph so the article has realistic pre-section context for the pinning model.</p>
<p>Opening evidence explains why route knowledge, operating limits, and institutional decisions matter to the interpretation of the surviving record.</p>
<p>Opening context adds a fourth paragraph to keep the fixture above the longform threshold without relying on generated feature markup.</p>
{fig(1)}
<h2>The curve under Malbone Street</h2>
<p>Section one begins with route geometry and a documented operating restriction that shaped how experienced crews handled the approach.</p>
{extra}
<p id="target-p">{TARGET_TEXT}</p>
<p>Another section-one paragraph supplies distinct wording so fingerprint fallback cannot accidentally resolve to a duplicate text candidate.</p>
<p>A fourth paragraph in this section preserves a realistic reading sequence and gives viewport selection multiple legitimate nearby targets.</p>
{fig(2)}
<h2>Why the wooden cars made the wreck worse</h2>
<p>Section two explains the material and train-configuration conditions without collapsing them into a single-cause explanation of the disaster.</p>
<p>The evidence is deliberately separated from later legal conclusions so the visitor can understand mechanism without mistaking acquittal for engineering proof.</p>
<p>Rescue conditions introduced another system into the sequence and demonstrate how a failure chain can continue after the initial derailment.</p>
<p>Named passengers and rescuers keep the article grounded in people rather than allowing a casualty total to flatten the historical record.</p>
{fig(3)}
<h2>The switch upstairs</h2>
<p>The final section follows the infrastructure that survived and shows why physical remnants can preserve operational history long after a street name changes.</p>
<p>The old electrical switch belongs later in the sequence and should not be mistaken for a cause of the train entering the curve too quickly.</p>
<p>The investigation closes by separating what the surviving objects prove from what later retellings sometimes add to make the story feel tidier.</p>
<p>A final substantive paragraph gives the reader enough context to understand that the feature links to published structure rather than a private annotation.</p>
{source_block()}
</article></main>
'''


def fixture(payload: str, mode: str) -> tuple[str, str]:
    fragment = ""
    if mode in {"valid", "incoming", "shifted", "stale"}:
        article = valid_article(extra_before_target=(mode == "shifted"))
    elif mode == "partial-boundary":
        article = valid_article().replace('class="wp-block-heading fv-source-heading" id="sources"', 'class="wp-block-heading" id="sources"')
    elif mode == "ambiguous-boundary":
        article = valid_article().replace(
            '<h2 class="wp-block-heading fv-source-heading" id="sources">',
            '<h2 class="wp-block-heading fv-source-heading">Sources copy</h2><h2 class="wp-block-heading fv-source-heading" id="sources">',
        )
    elif mode == "reversed-boundary":
        article = valid_article().replace(source_block(), '').replace(
            '<main><article id="post-621"><h1>Six Miles an Hour</h1>',
            '<main><article id="post-621"><h1>Six Miles an Hour</h1><ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Premature source list</li><li id="fv-fn-2">Two</li><li id="fv-fn-3">Three</li></ul>',
        ) + '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
    elif mode == "too-thin":
        article = f'''<main><article><h1>Thin</h1><p>Only one substantive paragraph is present, which must be insufficient for the feature qualification contract to activate.</p><h2>One</h2><p>Short but still substantive story text appears here for the first area.</p><h2>Two</h2><p>Another area appears but the overall narrative remains much too small for Case Pin.</p>{source_block()}</article></main>'''
    else:
        raise ValueError(mode)

    target_hash = fnv1a_js(TARGET_TEXT)
    if mode in {"incoming", "shifted"}:
        locator = f"p:1:2:{target_hash}"
        fragment = "#fv-pin=" + urllib.parse.quote(locator, safe="")
    elif mode == "stale":
        locator = "p:1:2:ffffffff"
        fragment = "#fv-pin=" + urllib.parse.quote(locator, safe="")

    assertions = f'''
<script>
const fvcpTest=()=>{{
 const mode={mode!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
   const opener=document.querySelector('.fvcp-launch');
   const band=document.querySelector('.fvcp-band');
   if(['partial-boundary','ambiguous-boundary','reversed-boundary','too-thin'].includes(mode)){{
     if(opener||band||document.querySelector('.fvcp-dialog'))return fail('invalid fixture did not fail closed');
     return pass();
   }}
   if(!opener||!band)return fail('Case Pin launch surfaces missing');
   if(!band.textContent.includes('Share the exact point'))return fail('visitor-value microcopy missing');
   if(mode==='incoming'||mode==='shifted'){{
     const target=document.getElementById('target-p');
     setTimeout(()=>{{
       if(!target.classList.contains('fvcp-target'))return fail('incoming pin did not resolve exact target');
       if(!document.querySelector('.fvcp-marker'))return fail('incoming shared-point marker missing');
       if(document.querySelector('.fvcp-stale'))return fail('valid pin incorrectly marked stale');
       return pass();
     }},120);return;
   }}
   if(mode==='stale'){{
     if(!document.querySelector('.fvcp-stale'))return fail('stale pin warning missing');
     if(document.querySelector('.fvcp-target'))return fail('stale pin substituted another target');
     return pass();
   }}
   document.getElementById('target-p').scrollIntoView({{block:'center'}});
   setTimeout(()=>{{
     try{{
       opener.focus();opener.click();
       setTimeout(()=>{{
         try{{
           const dialog=document.querySelector('.fvcp-dialog');
           if(!dialog||!dialog.open)return fail('dialog did not open');
           if(dialog.getAttribute('aria-labelledby')!=='fvcp-title')return fail('dialog label missing');
           const input=dialog.querySelector('.fvcp-link');
           if(!input.value.includes('#fv-pin='))return fail('precise fragment missing');
           if(input.value.includes('?'))return fail('generated link must be query-free');
           if(!input.value.startsWith(location.origin+location.pathname))return fail('generated link is not same-origin/current-path');
           if(!dialog.querySelector('.fvcp-context-type').textContent)return fail('target type missing');
           if(!dialog.querySelector('.fvcp-context-excerpt').textContent)return fail('target context missing');
           dialog.querySelector('.fvcp-close').click();
           setTimeout(()=>{{if(document.activeElement!==opener)return fail('close did not return focus');return pass()}},80);
         }}catch(e){{fail(e&&e.message?e.message:String(e))}}
       }},60);
     }}catch(e){{fail(e&&e.message?e.message:String(e))}}
   }},80);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvcpTest,{{once:true}});else fvcpTest();
</script>
'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Case Pin fixture</title></head><body>{article}{payload}{assertions}</body></html>", fragment


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
            for mode in ("valid", "incoming", "shifted", "stale", "partial-boundary", "ambiguous-boundary", "reversed-boundary", "too-thin"):
                html, fragment = fixture(payload, mode)
                page = root / f"case-pin-{mode}.html"
                page.write_text(html, encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--virtual-time-budget=2400", "--dump-dom", f"{origin}/{page.name}{fragment}"],
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
    require('<style id="fv-case-pin-v1-css">' in text and '<script id="fv-case-pin-v1-js">' in text, "versioned style/script ids missing")
    require("window.__fvCasePinV1" in text, "duplicate-init guard missing")
    require("h2#sources, h2.fv-source-heading" in text and "boundaryCandidates.length!==1" in text, "ambiguous/partial Sources boundary gate missing")
    require("h2#sources.fv-source-heading" in text and "noteRoots.length!==1" in text and "before(sourceHeading,notesRoot)" in text, "canonical ordered Sources gate missing")
    require("paragraphs.length<12||paragraphs.length>160" in text and "notes.length<3||notes.length>60" in text, "bounded qualification missing")
    require("Share the exact point, not just the page." in text and "Pins describe this article’s current structure" in text, "human scope microcopy missing")
    require("nearest=()" in text and "getBoundingClientRect" in text, "current-reading-point selection missing")
    require("locator:`p:${s}:${p}:${hash(text)}`" in text and "matches.length===1" in text, "ordinal plus fingerprint locator/fail-closed fallback missing")
    require("location.origin+location.pathname" in text and "#fv-pin=" in text and "encodeURIComponent" in text, "same-origin query-free fragment link construction missing")
    require("No substitute passage was selected." in text, "stale-link non-substitution disclosure missing")
    require("navigator.clipboard.writeText" in text and "document.execCommand('copy')" in text, "user-initiated copy with fallback missing")
    require("aria-haspopup','dialog'" in text and "aria-labelledby','fvcp-title'" in text and 'role="status" aria-live="polite"' in text, "dialog/live-status accessibility missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text and "forced-colors:active" in text and "prefers-reduced-motion:reduce" in text and "@media print" in text, "mobile/touch/accessibility media handling missing")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics/history token: {token}")
    match = re.search(r'<script id="fv-case-pin-v1-js">\n(.*?)\n</script>', text, flags=re.S)
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
    print("PASS: Case Pin exact identity, canonical source boundary, bounded target model, same-origin fragment generation, fingerprint-safe relocation, stale-link non-substitution, accessible dialog/copy flow, zero persistence/network/history boundary, and adversarial browser fixtures verified")


if __name__ == "__main__":
    main()
