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
PAYLOAD = ROOT / "payloads" / "listen-mode-wp-block-r1.txt"
EXPECTED_BYTES = 13303
EXPECTED_SHA256 = "d627607ed5cda5ae6eed5fc972bf83da73d9f70c64e8cb8fd51e40220a810f92"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def prose(i: int, citation: str = "", attrs: str = "") -> str:
    text = (
        f"Published narrative passage {i} records a concrete part of the investigation with enough detail "
        "to exercise Listen Mode without inventing evidence or changing the article. This fixture keeps each "
        "paragraph deliberately long so the longform threshold is deterministic, while the runtime assertions "
        "can prove citation-marker exclusion, source-record exclusion, narration order, and temporary visual-state ownership. "
    )
    return f'<p id="passage-{i}"{attrs}>{text}{citation}</p>'


def article() -> str:
    live = '<a href="#fv-fn-1" class="fv-fn-ref" data-fv-fn="1">991</a>'
    wrapped = '<sup class="fv-fn-mark"><a href="#fv-fn-2" class="fv-fn-ref" data-fv-fn="2">992</a></sup>'
    paragraphs = [
        prose(1, live),
        prose(2, wrapped, ' class="publisher-owned fv-listen-mode-current"'),
        *[prose(i) for i in range(3, 13)],
    ]
    return f'''<main><article><h1>Listen Mode R1 Fixture</h1>
{"".join(paragraphs)}
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1"><p id="source-record">SOURCE RECORD MUST NEVER BE SPOKEN. Source one published note.</p></li>
<li id="fv-fn-2">Source two published note.</li>
</ul></article></main>'''


def fixture(payload: str) -> str:
    setup = r'''<script>
window.__spoken=[];
Object.defineProperty(window,'SpeechSynthesisUtterance',{configurable:true,value:function(text){this.text=text;this.lang='';this.rate=1;this.onstart=null;this.onend=null;this.onerror=null;}});
Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{
 speaking:false,paused:false,
 cancel(){this.speaking=false;this.paused=false;},
 speak(u){this.speaking=true;this.paused=false;window.__spoken.push(u.text);if(u.onstart)u.onstart();},
 pause(){this.paused=true;},
 resume(){this.paused=false;this.speaking=true;}
}});
Element.prototype.scrollIntoView=function(){};
</script>'''
    before = r'''<script>
window.__original={
 p1:document.querySelector('#passage-1').innerHTML,
 p2:document.querySelector('#passage-2').innerHTML,
 p2Class:document.querySelector('#passage-2').getAttribute('class'),
 source:document.querySelector('#source-record').innerHTML
};
</script>'''
    assertions = r'''<script>
const fvlmTest=()=>{
 const fail=m=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
 const pass=()=>{document.body.dataset.fvTest='pass'};
 const wait=ms=>new Promise(r=>setTimeout(r,ms));
 try{
  const open=document.querySelector('.fv-listen-mode__open');
  if(!open)return fail('launcher missing');
  const original=window.__original;
  const samePublished=()=>document.querySelector('#passage-1').innerHTML===original.p1 &&
    document.querySelector('#passage-2').innerHTML===original.p2 &&
    document.querySelector('#source-record').innerHTML===original.source;
  (async()=>{
   open.click();
   const play=document.querySelector('[data-action="play"]');
   const next=document.querySelector('[data-action="next"]');
   const stop=document.querySelector('[data-action="stop"]');
   if(!play||!next||!stop)return fail('transport controls missing');
   play.click();
   await wait(20);
   if(window.__spoken.length!==1)return fail('first passage was not spoken once');
   if(window.__spoken[0].includes('991'))return fail('wrapper-free live citation marker entered utterance text');
   if(!window.__spoken[0].includes('Published narrative passage 1'))return fail('first narrative missing from utterance');
   if(!samePublished())return fail('published DOM changed during first narration');
   for(let i=0;i<11;i++){next.click();await wait(10);}
   if(window.__spoken.length!==12)return fail('expected 12 narrated passages, got '+window.__spoken.length);
   if(window.__spoken.some(t=>t.includes('991')||t.includes('992')))return fail('citation marker text entered narration');
   if(window.__spoken.some(t=>t.includes('SOURCE RECORD MUST NEVER BE SPOKEN')))return fail('source record entered narration');
   if(!window.__spoken[1].includes('Published narrative passage 2'))return fail('wrapped-citation narrative missing');
   if(!samePublished())return fail('published narrative/source innerHTML changed');
   stop.click();
   await wait(20);
   const p1=document.querySelector('#passage-1');
   const p2=document.querySelector('#passage-2');
   if(p1.hasAttribute('class'))return fail('feature left class attribute on originally classless passage');
   if(p2.getAttribute('class')!==original.p2Class)return fail('publisher-owned/pre-owned highlight class drifted');
   if(document.activeElement!==open)return fail('Close did not return focus to launcher');
   open.click();play.click();await wait(10);stop.click();await wait(10);
   if(p1.hasAttribute('class'))return fail('repeat open/close drifted absent class state');
   if(p2.getAttribute('class')!==original.p2Class)return fail('repeat open/close drifted pre-owned class state');
   if(!samePublished())return fail('repeat interaction changed published DOM');
   pass();
  })().catch(e=>fail(e&&e.message?e.message:String(e)));
 }catch(e){fail(e&&e.message?e.message:String(e))}
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvlmTest,{once:true});else fvlmTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Listen Mode R1 fixture</title>{setup}</head><body class='single-post'>{article()}{before}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        webroot = Path(temp)
        handler = partial(QuietHandler, directory=str(webroot))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            page = webroot / "listen-mode-r1.html"
            page.write_text(fixture(payload), encoding="utf-8")
            proc = subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                 "--virtual-time-budget=3500", "--dump-dom", f"http://127.0.0.1:{server.server_port}/{page.name}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=40,
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
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(actual_sha256 == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha256}")

    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-listen-mode-r1-css">' in text and '<script id="fv-listen-mode-r1-js">' in text, "R1 versioned asset ids missing")
    require(".fv-fn-ref[data-fv-fn],.fv-fn-mark" in text, "live citation-marker cleanup missing")
    require("cloneNode(true)" in text, "speech cleanup must operate on detached clones")
    require("sourceRoot" in text and "beforeSource" in text, "source boundary gate missing")
    require("prose.length<12||totalText<3000" in text, "longform fail-closed threshold missing")
    require("'speechSynthesis'in window" in text and "'SpeechSynthesisUtterance'in window" in text, "native speech capability gate missing")
    require("new SpeechSynthesisUtterance(item.text)" in text and "synth.speak(utterance)" in text, "speech execution missing")
    require("markHighlight" in text and "highlightOwned" in text and "highlightHadClassAttr" in text, "temporary highlight ownership tracking missing")
    require("clearHighlight()" in text and "open.focus()" in text and "e.key==='Escape'" in text, "cleanup/focus return contract missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text, "touch/mobile contract missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility media contract missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "posthog", "gtag(", "sendBeacon", "WebSocket",
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")
    for pattern, label in {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"getVoices\s*\(": "voice enumeration dependency",
    }.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-listen-mode-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    run_browser(text)
    print(f"PASS: Listen Mode R1 {len(raw)} bytes {actual_sha256}; live citation/source exclusion, narrative fidelity, and nondestructive repeated highlight state verified")


if __name__ == "__main__":
    main()
