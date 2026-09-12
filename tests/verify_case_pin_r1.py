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
PAYLOAD = ROOT / "payloads" / "case-pin-wp-block-r1.txt"
EXPECTED_BYTES = 13909
EXPECTED_SHA256 = "828c3c79025c6347619233a2c8043f24b0996a4ff154b1d5f2b20b37af287613"


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
<li id="fv-fn-1">Museum archive, primary route record <a href="https://example.org/one">Open source</a>. <span class="fv-fn-backlinks"><a href="#fv-fnref-1-1">back</a></span></li>
<li id="fv-fn-2">City report, operating instructions <a href="https://example.org/two">Open source</a>.</li>
<li id="fv-fn-3">Contemporary newspaper account <a href="https://example.org/three">Open source</a>.</li>
<li id="fv-fn-4">Engineering collection, track plan <a href="https://example.org/four">Open source</a>.</li>
</ul>
'''


TARGET_TEXT = "This target passage contains the exact operational detail a researcher may want to share without sending someone to the top of a very long investigation."


def target_markup(mode: str) -> str:
    attrs = 'id="target-p"'
    if mode == "incoming-owned-zero":
        attrs += ' tabindex="0" class="publisher-owned fvcp-target"'
    elif mode == "incoming-owned-neg":
        attrs += ' tabindex="-7" class="publisher-owned"'
    return f'<p {attrs}>{TARGET_TEXT}</p>'


def valid_article(mode: str = "valid", extra_before_target: bool = False) -> str:
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
{target_markup(mode)}
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
    incoming_modes = {"incoming-absent", "incoming-owned-zero", "incoming-owned-neg", "shifted"}
    fragment = ""
    if mode in {"valid", *incoming_modes, "stale"}:
        article = valid_article(mode=mode, extra_before_target=(mode == "shifted"))
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
    if mode in incoming_modes:
        fragment = "#fv-pin=" + urllib.parse.quote(f"p:1:2:{target_hash}", safe="")
    elif mode == "stale":
        fragment = "#fv-pin=" + urllib.parse.quote("p:1:2:ffffffff", safe="")

    assertions = f'''
<script>
const fvcpTest=()=>{{
 const mode={mode!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 const later=(fn,ms=100)=>setTimeout(()=>{{try{{fn()}}catch(e){{fail(e&&e.message?e.message:String(e))}}}},ms);
 try{{
   const opener=document.querySelector('.fvcp-launch');
   const band=document.querySelector('.fvcp-band');
   if(['partial-boundary','ambiguous-boundary','reversed-boundary','too-thin'].includes(mode)){{
     if(opener||band||document.querySelector('.fvcp-dialog'))return fail('invalid fixture did not fail closed');
     return pass();
   }}
   if(!opener||!band)return fail('Case Pin launch surfaces missing');
   if(!band.textContent.includes('Share the exact point'))return fail('visitor-value microcopy missing');

   if(['incoming-absent','incoming-owned-zero','incoming-owned-neg','shifted'].includes(mode)){{
     const target=document.getElementById('target-p');
     const beforeTab=target.getAttribute('tabindex');
     const beforeClass=target.getAttribute('class');
     const beforeHasClass=target.hasAttribute('class');
     return later(()=>{{
       if(!document.querySelector('.fvcp-marker'))return fail('incoming shared-point marker missing');
       if(document.querySelector('.fvcp-stale'))return fail('valid pin incorrectly marked stale');
       if(!target.classList.contains('fvcp-target'))return fail('incoming target highlight missing');
       if(mode==='incoming-absent'){{
         if(target.getAttribute('tabindex')!=='-1')return fail('feature-owned temporary tabindex missing');
         if(beforeTab!==null||beforeHasClass)return fail('fixture state invalid');
       }}
       if(mode==='incoming-owned-zero'&&target.getAttribute('tabindex')!=='0')return fail('pre-owned tabindex=0 mutated on activation');
       if(mode==='incoming-owned-neg'&&target.getAttribute('tabindex')!=='-7')return fail('pre-owned tabindex=-7 mutated on activation');
       const dismiss=document.querySelector('.fvcp-dismiss');
       dismiss.focus();dismiss.click();
       later(()=>{{
         if(document.querySelector('.fvcp-marker'))return fail('dismiss did not remove marker');
         if(mode==='incoming-absent'){{
           if(target.hasAttribute('tabindex'))return fail('feature-owned tabindex was not removed');
           if(target.hasAttribute('class'))return fail('originally absent class attribute was not restored to absent');
         }} else {{
           if(target.getAttribute('tabindex')!==beforeTab)return fail('pre-owned tabindex did not survive dismissal byte-for-byte');
           if(target.hasAttribute('class')!==beforeHasClass||target.getAttribute('class')!==beforeClass)return fail('pre-owned class state did not survive dismissal byte-for-byte');
         }}
         if(mode==='shifted'&&target.id!=='target-p')return fail('shifted fingerprint recovery targeted wrong element');
         return pass();
       }},60);
     }},140);
   }}

   if(mode==='stale'){{
     if(!document.querySelector('.fvcp-stale'))return fail('stale pin warning missing');
     if(document.querySelector('.fvcp-target'))return fail('stale pin substituted another target');
     return pass();
   }}

   document.getElementById('target-p').scrollIntoView({{block:'center'}});
   later(()=>{{
     opener.focus();opener.click();
     later(()=>{{
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
       later(()=>{{
         if(document.activeElement!==opener)return fail('close did not return focus');
         opener.click();
         later(()=>{{
           if(!dialog.open)return fail('repeat open failed');
           dialog.querySelector('.fvcp-close').click();
           later(()=>{{if(document.activeElement!==opener)return fail('repeat close did not return focus');return pass()}},50);
         }},50);
       }},50);
     }},60);
   }},80);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvcpTest,{{once:true}});else fvcpTest();
</script>
'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Case Pin R1 fixture</title></head><body>{article}{payload}{assertions}</body></html>", fragment


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = (
        "valid", "incoming-absent", "incoming-owned-zero", "incoming-owned-neg", "shifted", "stale",
        "partial-boundary", "ambiguous-boundary", "reversed-boundary", "too-thin",
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
                html, fragment = fixture(payload, mode)
                page = root / f"case-pin-r1-{mode}.html"
                page.write_text(html, encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                     "--virtual-time-budget=2800", "--dump-dom", f"{origin}/{page.name}{fragment}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-case-pin-r1-css">' in text and '<script id="fv-case-pin-r1-js">' in text, "R1 style/script ids missing")
    require("window.__fvCasePinR1" in text, "R1 duplicate-init guard missing")
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
    require("ownedTabindex=!target.hasAttribute('tabindex')" in text, "tabindex mutation ownership tracking missing")
    require("ownedTargetClass=!target.classList.contains('fvcp-target')" in text and "hadClassAttr=target.hasAttribute('class')" in text, "class mutation ownership tracking missing")
    require("if(ownedTabindex&&target.getAttribute('tabindex')==='-1')target.removeAttribute('tabindex')" in text, "owned-only tabindex cleanup missing")
    require("if(!hadClassAttr&&target.getAttribute('class')==='')target.removeAttribute('class')" in text, "absent class-attribute restoration missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text and "forced-colors:active" in text and "prefers-reduced-motion:reduce" in text and "@media print" in text, "mobile/touch/accessibility media handling missing")
    banned = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics/history token: {token}")
    match = re.search(r'<script id="fv-case-pin-r1-js">\n(.*?)\n</script>', text, flags=re.S)
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
    print("PASS: Case Pin R1 exact identity, provenance/stale-link contract, nondestructive incoming-marker tabindex/class restoration, repeat dialog focus, accessibility, and zero persistence/network/history behavior verified")


if __name__ == "__main__":
    main()
