from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "case-compass-wp-block-v1.txt"
EXPECTED_BYTES = 16752
EXPECTED_SHA256 = "0d36b0dcdccc36404f9aa5b1236199de4ac5d86950dbf9e4adb86e5867c62731"

BROWSER_MODES = ("citation-focus", "state-absent-repeat", "state-owned", "scroll-fail", "focus-fail", "dialog-keyboard")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def article() -> str:
    filler = (
        "Published records, witness accounts, engineering notes, dates, and surviving objects "
        "are compared here so the reader can follow what the record establishes and what remains uncertain. "
        "This paragraph is intentionally long enough to qualify as substantive narrative without relying on citation UI. "
    )
    paras = []
    for i in range(12):
        marker = f'<a class="fv-fn-ref" data-fv-fn="{(i % 3) + 1}" href="#fv-fn-{(i % 3) + 1}">[{(i % 3) + 1}]</a>' if i in (0, 4, 8) else ""
        attrs = ""
        if i == 0:
            attrs = ' id="opening-target"'
        paras.append(f"<p{attrs}>{filler}{filler}{marker}</p>")
    return f"""<main><article class="post type-post"><div class="entry-content">
<h1>Case</h1>
{paras[0]}
<h2 class="wp-block-heading" id="section-one">Section One <a class="fv-fn-ref" data-fv-fn="1" href="#fv-fn-1">[1]</a></h2>
{''.join(paras[1:5])}
<figure class="wp-block-image"><img src="/one.jpg" alt="One"><figcaption>Figure one</figcaption></figure>
<h2 class="wp-block-heading publisher-owned fvcc-arrived" id="section-two" tabindex="-7">Section Two <span class="fv-fn-mark"><a class="fv-fn-ref" data-fv-fn="2" href="#fv-fn-2">[2]</a></span></h2>
{''.join(paras[5:9])}
<h2 class="wp-block-heading" id="section-three">Section Three <a class="fv-fn-ref" data-fv-fn="3" href="#fv-fn-3">[3]</a></h2>
{''.join(paras[9:])}
<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>
<ul class="fv-source-list" data-fv-footnotes>
<li id="fv-fn-1">Source one</li><li id="fv-fn-2">Source two</li><li id="fv-fn-3">Source three</li>
</ul>
</div></article></main>"""


def runtime_script(mode: str) -> str:
    setup = """
const fail=m=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
const pass=()=>document.body.dataset.fvTest='pass';
const shell=document.querySelector('[data-fv-case-compass]');
if(!shell)return fail('Case Compass did not activate');
const mini=[...shell.querySelectorAll('.fvcc-mini button')];
const open=shell.querySelector('.fvcc-open');
const one=document.getElementById('section-one');
const two=document.getElementById('section-two');
const opening=document.getElementById('opening-target');
"""
    if mode == "citation-focus":
        body = """
const names=[...shell.querySelectorAll('.fvcc-mini-name')].map(n=>n.textContent);
if(names.join('|')!=='Opening|Section One|Section Two|Section Three')return fail('citation UI leaked into structural labels: '+names.join('|'));
mini[1].focus();
const cs=getComputedStyle(mini[1]);
if(parseFloat(cs.outlineWidth)<2||cs.outlineStyle==='none'||cs.outlineColor==='rgba(0, 0, 0, 0)')return fail('mini rail focus is not visibly styled');
open.click();
setTimeout(()=>{try{
 const d=document.querySelector('.fvcc-dialog');const cards=[...d.querySelectorAll('.fvcc-card button')];
 if(document.activeElement!==cards[0])return fail('dialog did not focus active card');
 cards[0].focus();const ds=getComputedStyle(cards[0]);
 if(parseFloat(ds.outlineWidth)<2||ds.outlineStyle==='none')return fail('dialog control focus is not visibly styled');
 pass();
}catch(e){fail(e.message)}},100);
"""
    elif mode == "state-absent-repeat":
        body = """
const initialClass=opening.getAttribute('class');
const initialTab=opening.getAttribute('tabindex');
const click=idx=>mini[idx].click();
click(0);
setTimeout(()=>{try{
 if(opening.hasAttribute('tabindex'))return fail('temporary tabindex survived first jump');
 click(1);
 setTimeout(()=>{try{
  click(0);
  setTimeout(()=>{try{
   if(opening.getAttribute('tabindex')!==initialTab)return fail('absent tabindex drifted');
   if(opening.getAttribute('class')!==initialClass)return fail('absent class state drifted');
   pass();
  }catch(e){fail(e.message)}},1700);
 }catch(e){fail(e.message)}},60);
}catch(e){fail(e.message)}},60);
"""
    elif mode == "state-owned":
        body = """
const initialClass=two.getAttribute('class'),initialTab=two.getAttribute('tabindex');
mini[2].click();
setTimeout(()=>{try{
 if(two.getAttribute('tabindex')!==initialTab)return fail('pre-owned tabindex changed');
 if(two.getAttribute('class')!==initialClass)return fail('pre-owned class changed');
 if(document.activeElement!==two)return fail('pre-owned target did not receive focus');
 pass();
}catch(e){fail(e.message)}},100);
"""
    elif mode == "scroll-fail":
        body = """
opening.scrollIntoView=()=>{throw new Error('forced')};
const launcher=mini[0];launcher.focus();launcher.click();
setTimeout(()=>{try{
 if(opening.hasAttribute('tabindex')||opening.hasAttribute('class'))return fail('scroll failure mutated target');
 if(document.activeElement!==launcher)return fail('scroll failure did not recover focus');
 pass();
}catch(e){fail(e.message)}},80);
"""
    elif mode == "focus-fail":
        body = """
Object.defineProperty(opening,'focus',{configurable:true,value:()=>{}});
const launcher=mini[0];launcher.focus();launcher.click();
setTimeout(()=>{try{
 if(opening.hasAttribute('tabindex')||opening.hasAttribute('class'))return fail('focus failure did not restore target');
 if(document.activeElement!==launcher)return fail('focus failure did not recover launcher focus');
 pass();
}catch(e){fail(e.message)}},80);
"""
    elif mode == "dialog-keyboard":
        body = """
open.click();
setTimeout(()=>{try{
 const d=document.querySelector('.fvcc-dialog'),cards=[...d.querySelectorAll('.fvcc-card button')];
 if(document.activeElement!==cards[0])return fail('first card not focused');
 cards[0].dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));
 if(document.activeElement!==cards[1])return fail('ArrowDown did not move focus');
 d.querySelector('.fvcc-close').click();
 setTimeout(()=>{try{
  if(document.activeElement!==open)return fail('ordinary close did not restore opener focus');
  pass();
 }catch(e){fail(e.message)}},50);
}catch(e){fail(e.message)}},100);
"""
    else:
        raise ValueError(mode)
    return f"""<script>
const run=()=>{{try{{{setup}{body}}}catch(e){{fail(e.message)}}}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{{once:true}});else run();
</script>"""


def run_browser_mode(payload: str, mode: str) -> None:
    require(mode in BROWSER_MODES, f"unknown browser mode: {mode}")
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        page = root / "case-compass.html"
        page.write_text(
            f"<!doctype html><html><head><meta charset='utf-8'></head><body class='single-post'>{article()}{payload}{runtime_script(mode)}</body></html>",
            encoding="utf-8",
        )
        proc = subprocess.run(
            [
                browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                "--virtual-time-budget=4500", "--dump-dom", page.as_uri(),
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
        )
        require(proc.returncode == 0, f"browser mode {mode} failed: {proc.stderr[-500:]}")
        if 'data-fv-test="pass"' not in proc.stdout:
            reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
            raise SystemExit(f"FAIL: browser mode {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    actual = hashlib.sha256(raw).hexdigest()
    print(f"CASE_COMPASS_R1_BYTES={len(raw)}")
    print(f"CASE_COMPASS_R1_SHA256={actual}")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")

    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    require('<style id="fv-case-compass-r1-css">' in text and '<script id="fv-case-compass-r1-js">' in text, "R1 ids missing")
    require("window.__fvCaseCompass" in text and "version:'1.1.0'" in text, "R1 duplicate-init/version guard missing")
    require("h2#sources.fv-source-heading" in text and ".fv-source-list[data-fv-footnotes]" in text, "trusted source boundary missing")
    require("DOCUMENT_POSITION_FOLLOWING" in text and "if(!root.contains(notes)||!root.contains(sourceHeading))return" in text, "ordered same-root source contract missing")
    require("h2s.length<3||paragraphs.length<12" in text and "storyChars<2800" in text and "if(sections.length<4)return" in text, "longform thresholds missing")

    require(".fv-fn-mark,.fv-fn-ref[data-fv-fn],[data-fv-feature-ui]" in text, "live citation cleaning selector missing")
    require("clean(p).length>30" in text and "n+clean(p).length" in text, "passage qualification must use citation-clean text")
    require("title:clean(heading)" in text, "section titles must use citation-clean text")

    require(".fvcc-mini button:focus-visible" in text and "outline:3px solid var(--fvcc-accent)" in text, "visible standard focus ring missing")
    require("forced-colors:active" in text and "outline:3px solid Highlight" in text, "forced-colors focus ring missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text and "prefers-reduced-motion:reduce" in text, "responsive/accessibility contracts missing")

    require("target.scrollIntoView" in text and text.index("target.scrollIntoView") < text.index("target.setAttribute('tabindex','-1')"), "scroll must occur before publisher-state mutation")
    require("addedTab:!target.hasAttribute('tabindex')" in text and "if(state.addedTab)target.removeAttribute('tabindex')" in text, "tabindex ownership/restoration missing")
    require("addedArrived:!target.classList.contains('fvcc-arrived')" in text and "normalizeClass(target,state.hadClassAttr)" in text, "class ownership/restoration missing")
    require("clearFlash()" in text and "flashCleanup" in text, "repeat-jump flash cleanup missing")
    require("recovery.focus()" in text, "failure focus recovery missing")
    require("sections.forEach(s=>s.target.classList.add" not in text, "publisher targets must not receive permanent feature classes")

    require("ArrowDown" in text and "ArrowUp" in text and "Home" in text and "End" in text, "dialog keyboard navigation missing")
    require("aria-current" in text and 'role="status"' in text and 'aria-live="polite"' in text, "current-location semantics missing")

    banned = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest",
        "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "<script src=",
    ]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected persistence/network/analytics/history token: {token}")

    match = re.search(r'<script id="fv-case-compass-r1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    mode = os.environ.get("FV_BROWSER_MODE")
    if mode:
        run_browser_mode(text, mode)
    print(f"PASS: Case Compass R1 static contract{' + browser mode ' + mode if mode else ''}")


if __name__ == "__main__":
    main()
