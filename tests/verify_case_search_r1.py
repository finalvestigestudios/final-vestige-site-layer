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
PAYLOAD = ROOT / "payloads" / "case-search-wp-block-r1.txt"
EXPECTED_BYTES = 19312
EXPECTED_SHA256 = "53128560c03f2cc5dcdfbde948090ea39bf251ba934c41d87e783d3da44de725"

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

def prose(i: int, body: str = "", attrs: str = "") -> str:
    filler = (
        f"Published investigation passage {i} provides concrete narrative context and enough surrounding detail "
        "to exercise Case Search without inventing evidence or changing the article. The paragraph deliberately "
        "contains a longer run of ordinary prose so the browser fixture can verify that a normalized match is "
        "centered in its real context instead of falling back to the beginning of the record. "
    )
    tail = (
        " Additional published context follows the distinctive test phrase and keeps the passage above the "
        "qualification threshold while preserving deterministic story order for keyboard and focus checks."
    )
    return f'<p id="passage-{i}"{attrs}>{filler}{body}{tail}</p>'

def article() -> str:
    composed = (
        " ANCHOR-BEFORE The café ledger places José beside the harbor manifest ANCHOR-AFTER, "
        "which is the exact normalized multi-term location this regression must center and visibly mark."
    )
    decomposed = (
        " SECOND-ANCHOR The Cafe\u0301 register records a decomposed accent sequence beside a dated entry, "
        "allowing a composed query to resolve back to the original published characters."
    )
    owned = (
        " OWNED-ANCHOR quartzsignal appears only in this publisher-owned focusable paragraph so repeated jumps "
        "can prove that Case Search does not steal its tabindex or pre-existing highlight token."
    )
    paragraphs = [
        prose(1), prose(2), prose(3), prose(4), prose(5),
        prose(6, composed),
        prose(7, decomposed),
        prose(8, owned, ' tabindex="0" class="publisher-class fv-case-search-target"'),
        prose(9), prose(10), prose(11), prose(12),
    ]
    return f"""<main><article><h1>Case Search R1 Fixture</h1>
<h2>Opening records</h2>
{''.join(paragraphs[:6])}
<h2>Second section</h2>
{''.join(paragraphs[6:])}
<h2 id="sources" class="fv-source-heading">Sources</h2>
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1">Source one records the harbor ledger and date.</li>
<li id="fv-fn-2">Source two records the second published note.</li>
</ul></article></main>"""

def fixture(payload: str) -> str:
    assertions = r"""<script>
const fvCaseSearchR1Test=()=>{
 const fail=m=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
 const pass=()=>{document.body.dataset.fvTest='pass'};
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const q=async value=>{
   const input=document.querySelector('.fv-case-search__query');
   input.value=value;
   input.dispatchEvent(new Event('input',{bubbles:true}));
   await sleep(140);
   return [...document.querySelectorAll('.fv-case-search__result')];
 };
 const open=async()=>{
   document.querySelector('.fv-case-search__open').click();
   await sleep(40);
 };
 const close=async()=>{
   const d=document.querySelector('.fv-case-search-dialog');
   if(d.open)document.querySelector('.fv-case-search__close').click();
   await sleep(30);
 };
 const normalized=s=>s.normalize('NFD').replace(/\p{M}/gu,'').toLocaleLowerCase();
 const snapshot=el=>({
   hasTab:el.hasAttribute('tabindex'),tab:el.getAttribute('tabindex'),
   hasClass:el.hasAttribute('class'),cls:el.getAttribute('class')
 });
 const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 (async()=>{
   const launcher=document.querySelector('.fv-case-search__open');
   if(!launcher)return fail('launcher missing');
   const p6=document.querySelector('#passage-6');
   const p7=document.querySelector('#passage-7');
   const p8=document.querySelector('#passage-8');
   const p6Before=snapshot(p6);
   const p8Before=snapshot(p8);

   await open();
   let buttons=await q('cafe\u0301 jose\u0301');
   if(buttons.length!==1)return fail('normalized multi-term query expected one result, got '+buttons.length);
   let snippet=buttons[0].querySelector('.fv-case-search__snippet');
   if(!snippet.textContent.includes('ANCHOR-BEFORE')||!snippet.textContent.includes('ANCHOR-AFTER'))return fail('multi-term snippet not centered on normalized match context');
   let marks=[...snippet.querySelectorAll('mark')].map(m=>normalized(m.textContent));
   if(!marks.includes('cafe')||!marks.includes('jose'))return fail('multi-term normalized hits not visibly marked: '+marks.join('|'));
   buttons[0].click();
   await sleep(80);
   if(document.activeElement!==p6)return fail('jump did not focus composed-accent story target');
   if(p6.getAttribute('tabindex')!=='-1')return fail('feature-owned temporary tabindex missing on absent-tab target');
   launcher.focus();
   await sleep(40);
   if(!equal(snapshot(p6),p6Before))return fail('absent tabindex/class state not restored after jump');

   await open();
   buttons=await q('Café');
   const decomp=buttons.find(b=>b.textContent.includes('SECOND-ANCHOR'));
   if(!decomp)return fail('composed query did not find decomposed published text');
   snippet=decomp.querySelector('.fv-case-search__snippet');
   marks=[...snippet.querySelectorAll('mark')].map(m=>m.textContent.normalize('NFC'));
   if(!marks.includes('Café'))return fail('decomposed published hit not highlighted with original characters');

   await close();
   await open();
   buttons=await q('quartzsignal');
   let owned=buttons.find(b=>b.textContent.includes('OWNED-ANCHOR'));
   if(!owned)return fail('pre-owned state result missing; result count '+buttons.length);
   owned.click();
   await sleep(80);
   if(document.activeElement!==p8)return fail('jump did not focus pre-owned tabindex target');
   launcher.focus();
   await sleep(40);
   if(!equal(snapshot(p8),p8Before))return fail('pre-owned tabindex/class state changed after first jump');

   await open();
   buttons=await q('quartzsignal');
   owned=buttons.find(b=>b.textContent.includes('OWNED-ANCHOR'));
   if(!owned)return fail('pre-owned state result missing on repeated query');
   owned.click();
   await sleep(80);
   launcher.focus();
   await sleep(40);
   if(!equal(snapshot(p8),p8Before))return fail('pre-owned state drifted after repeated jump');

   await open();
   buttons=await q('cafe\u0301 jose\u0301');
   buttons[0].click();
   await sleep(80);
   launcher.focus();
   await sleep(40);
   if(!equal(snapshot(p6),p6Before))return fail('absent state drifted after repeated normalized jump');

   pass();
 })().catch(e=>fail(e&&e.message?e.message:String(e)));
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvCaseSearchR1Test,{once:true});else fvCaseSearchR1Test();
</script>"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Case Search R1</title></head><body class='single-post'>{article()}{payload}{assertions}</body></html>"

def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            page = root / "case-search-r1.html"
            page.write_text(fixture(payload), encoding="utf-8")
            proc = subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                 "--virtual-time-budget=5000", "--dump-dom", f"http://127.0.0.1:{server.server_port}/{page.name}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45,
            )
            require(proc.returncode == 0, f"browser fixture failed: {proc.stderr[-500:]}")
            if 'data-fv-test="pass"' not in proc.stdout:
                reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                raise SystemExit(f"FAIL: browser fixture: {reason.group(1) if reason else 'runtime assertions failed'}")
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
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    require('<style id="fv-case-search-r1-css">' in text and '<script id="fv-case-search-r1-js">' in text, "R1 asset ids missing")
    require("normalizeMap" in text and "bestRanges" in text and "tokenHits" in text, "normalization-to-original offset map missing")
    require("tokens.every(token=>item.search.includes(token))" in text, "normalized multi-token AND match contract missing")
    require("snippet.appendChild(renderSnippet(item,tokens))" in text, "snippet renderer must receive normalized tokens")
    require("document.createElement('mark')" in text, "visible snippet marks missing")
    require("target.scrollIntoView" in text and "restoreOwnedState" in text, "state-safe jump contract missing")
    require("addedTab:!target.hasAttribute('tabindex')" in text, "temporary tabindex ownership tracking missing")
    require("addedFlash:!target.classList.contains('fv-case-search-target')" in text, "temporary class ownership tracking missing")
    require("!state.hadClassAttr&&!target.getAttribute('class')" in text, "originally absent class restoration missing")
    require("target.focus({preventScroll:true})" in text and "document.activeElement!==target" in text, "focus establishment verification missing")
    require("No search query is sent anywhere." in text and "Browser Find still works normally." in text, "privacy/browser-find copy missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text, "touch/mobile contract missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility media behavior missing")
    banned = ["localStorage","sessionStorage","indexedDB","document.cookie","posthog","gtag(","sendBeacon","WebSocket"]
    for token in banned:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")
    for pattern,label in {r"\bfetch\s*\(":"network fetch",r"XMLHttpRequest":"XHR",r"<script[^>]+src=":"external script"}.items():
        require(not re.search(pattern,text,flags=re.I), f"unexpected {label}")
    match = re.search(r'<script id="fv-case-search-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node","--check",str(js_path)],check=True)
    finally:
        js_path.unlink(missing_ok=True)
    run_browser(text)
    print(f"PASS: Case Search R1 {len(raw)} bytes {actual}; composed/decomposed normalized snippets, multi-term highlighting, and nondestructive repeated jump state verified")

if __name__ == "__main__":
    main()
