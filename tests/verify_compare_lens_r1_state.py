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
PAYLOAD = ROOT / "payloads" / "compare-lens-wp-block-r1.txt"
EXPECTED_BYTES = 19152
EXPECTED_SHA256 = "5275862a6a81f5f9e3a093a7a71780e15fa6bbb5e2d6599615ed88867fb5c5e3"
MODES = ("absent-repeat", "owned", "scroll-fail", "focus-fail")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def article() -> str:
    return """<main><article class="post type-post"><div class="entry-content">
<h1>Case</h1><h2>Section One</h2>
<figure class="wp-block-image publisher-one" id="fig-1"><img src="/img/1.jpg" alt="Figure one"><figcaption>Figure one caption</figcaption></figure>
<figure class="wp-block-image publisher-two fv-compare-lens-flash" id="fig-2" tabindex="-7"><img src="/img/2.jpg" alt="Figure two"><figcaption>Figure two caption</figcaption></figure>
<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>
<ul class="fv-source-list" data-fv-footnotes><li>Source one</li></ul>
</div></article></main>"""


def runtime(mode: str) -> str:
    common = """
const fail=m=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
const pass=()=>document.body.dataset.fvTest='pass';
const launch=document.querySelector('.fv-compare-lens-launch');if(!launch)return fail('launcher missing');
const opener=launch.querySelector('.fv-compare-lens-open');const fig1=document.getElementById('fig-1'),fig2=document.getElementById('fig-2');
const c1=fig1.getAttribute('class'),c2=fig2.getAttribute('class');
"""
    if mode == "absent-repeat":
        body = """
let scrollCount=0,focusCount=0;fig1.scrollIntoView=()=>{scrollCount++};fig1.addEventListener('focus',()=>focusCount++);
const jump=again=>{opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
 if(scrollCount<(again?1:2)||focusCount<(again?1:2))return fail('story-jump focus path did not execute');
 if(document.activeElement!==fig1)return fail('story target did not receive focus');
 if(fig1.getAttribute('tabindex')!=='-1')return fail('feature-owned temporary tabindex missing while target is focused');
 if(!fig1.classList.contains('fv-compare-lens-flash'))return fail('feature-owned temporary highlight missing while target is focused');
 opener.focus();setTimeout(()=>{try{
  if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==c1)return fail('absent-state target was not restored after blur');
  if(again)return jump(false);pass();
 }catch(e){fail(e.message)}},45);
}catch(e){fail(e.message)}},90)}catch(e){fail(e.message)}},35)};jump(true);
"""
    elif mode == "owned":
        body = """
let scrollCount=0;fig2.scrollIntoView=()=>{scrollCount++};opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');const s=d.querySelector('[data-select="0"]');s.value='1';s.dispatchEvent(new Event('change',{bubbles:true}));d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
 if(scrollCount<1)return fail('owned-state story-jump path did not execute');
 if(document.activeElement!==fig2)return fail('pre-owned target did not receive focus');
 if(fig2.getAttribute('tabindex')!=='-7'||fig2.getAttribute('class')!==c2)return fail('pre-owned tabindex/class was damaged');pass();
}catch(e){fail(e.message)}},90)}catch(e){fail(e.message)}},35);
"""
    elif mode == "scroll-fail":
        body = """
fig1.scrollIntoView=()=>{throw new Error('forced scroll failure')};opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
 if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==c1)return fail('scroll failure mutated target');
 if(document.activeElement!==opener)return fail('scroll failure focus recovery missing');pass();
}catch(e){fail(e.message)}},90)}catch(e){fail(e.message)}},35);
"""
    elif mode == "focus-fail":
        body = """
let scrollCount=0;fig1.scrollIntoView=()=>{scrollCount++};Object.defineProperty(fig1,'focus',{configurable:true,value:()=>{}});opener.click();setTimeout(()=>{try{const d=document.querySelector('.fv-compare-lens-dialog');d.querySelector('[data-original="0"]').click();setTimeout(()=>{try{
 if(scrollCount<1)return fail('focus-failure jump path did not execute');
 if(fig1.hasAttribute('tabindex')||fig1.getAttribute('class')!==c1)return fail('focus failure did not restore target');
 if(document.activeElement!==opener)return fail('focus failure recovery missing');pass();
}catch(e){fail(e.message)}},90)}catch(e){fail(e.message)}},35);
"""
    else:
        raise ValueError(mode)
    return f"<script>const run=()=>{{try{{{common}{body}}}catch(e){{fail(e.message)}}}};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{{once:true}});else run();</script>"


def fixture(payload: str, mode: str) -> str:
    # Headless --dump-dom does not guarantee a compositor frame. Preserve the
    # post-close async boundary while making rAF deterministic for the fixture.
    bootstrap = "<script>window.requestAnimationFrame=cb=>setTimeout(()=>cb(performance.now()),0);</script>"
    return f"<!doctype html><html><head><meta charset='utf-8'>{bootstrap}</head><body class='single-post'>{article()}{payload}{runtime(mode)}</body></html>"


def run() -> None:
    raw = PAYLOAD.read_bytes(); payload = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "payload SHA-256 drifted")
    selected = os.environ.get("FV_STATE_MODE")
    modes = (selected,) if selected else MODES
    require(all(mode in MODES for mode in modes), f"unknown state mode: {selected}")
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); (root / "img").mkdir()
        for name in ("1.jpg", "2.jpg"):
            (root / "img" / name).write_bytes(b"\xff\xd8\xff\xd9")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            for mode in modes:
                page = root / f"state-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--virtual-time-budget=2500", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25,
                )
                require(proc.returncode == 0, f"browser mode {mode} failed: {proc.stderr[-400:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(f"FAIL: state mode {mode}: {reason.group(1) if reason else 'runtime assertion failed'}")
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)
    print(f"PASS: Compare Lens R1 browser state preservation mode(s): {', '.join(modes)}")


if __name__ == "__main__":
    run()
