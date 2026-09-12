from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "scale-board-wp-block-r7.txt"
EXPECTED_BYTES = 19224
EXPECTED_SHA256 = "1935cab812ffa875a41beeba6d5e744fff8b195e3ba06dec03a9f72fc73e72a6"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def browser_run(prefix: str, suffix: str, label: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium unavailable")
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / f"scale-board-r7-{label}.html"
        page.write_bytes((ROOT / prefix).read_bytes() + PAYLOAD.read_bytes() + (ROOT / suffix).read_bytes())
        try:
            proc = subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--virtual-time-budget=3000", "--dump-dom", page.as_uri()],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15,
            )
        except subprocess.TimeoutExpired as exc:
            diagnostic = ROOT / f"scale-board-r7-{label}-failure.txt"
            stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            diagnostic.write_text(f"reason=browser-timeout\n--- STDERR ---\n{stderr}\n--- DOM ---\n{stdout}", encoding="utf-8")
            require(False, f"browser fixture {label} timed out")
        if proc.returncode != 0:
            diagnostic = ROOT / f"scale-board-r7-{label}-failure.txt"
            diagnostic.write_text(f"returncode={proc.returncode}\n--- STDERR ---\n{proc.stderr}\n--- DOM ---\n{proc.stdout}", encoding="utf-8")
            require(False, f"browser fixture {label} failed: {proc.stderr[-500:]}")
        if 'data-fv-test="pass"' not in proc.stdout:
            reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
            reason_text = reason.group(1) if reason else "no reason surfaced"
            diagnostic = ROOT / f"scale-board-r7-{label}-failure.txt"
            diagnostic.write_text(f"reason={reason_text}\n--- STDERR ---\n{proc.stderr}\n--- DOM ---\n{proc.stdout}", encoding="utf-8")
            require(False, f"browser fixture {label} failed: {reason_text}")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    actual_sha = hashlib.sha256(raw).hexdigest()
    require(len(raw) == EXPECTED_BYTES, f"payload bytes drifted: {len(raw)}")
    require(actual_sha == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    for token in (
        'id="fv-scale-board-r7-css"', 'id="fv-scale-board-r7-js"', "window.__fvScaleBoardR7",
        "boundaryCandidates.length!==1", "sourceHeading.id!=='sources'", "noteRoots.length!==1",
        "invalidNumericExpressionPrefix", "⁄", "∕", "selected.some(existing=>overlaps(candidate,existing))",
        "Bars compare magnitude, not importance, causation, confidence, or evidence quality.",
        "min-height:44px", "@media(max-width:360px)", "prefers-reduced-motion:reduce", "forced-colors:active",
    ):
        require(token in text, f"preserved contract missing: {token}")

    require("ensureId" not in text and "Math.random" not in text, "random story-point id mutation remains")
    require("hadTabindex=p.hasAttribute('tabindex')" in text, "pre-owned tabindex detection missing")
    require("hadFlash=p.classList.contains('fvsb-flash'),hadClass=p.hasAttribute('class'),priorClass=p.getAttribute('class')" in text, "pre-owned flash/class-state detection missing")
    require("let addedTabindex=false,addedFlash=false" in text, "feature ownership flags missing")
    require("if(!hadTabindex){p.setAttribute('tabindex','-1');addedTabindex=true}" in text, "temporary focusability guard missing")
    require("const restoreTabindex=()=>{if(!addedTabindex)return;p.removeAttribute('tabindex');addedTabindex=false}" in text, "temporary tabindex restoration helper missing")
    require("try{p.focus({preventScroll:true})}catch(error){restoreTabindex();throw error}" in text, "focus-throw tabindex restoration missing")
    require("if(document.activeElement!==p){restoreTabindex();throw new Error('story-focus-not-established')}" in text, "focus establishment verification missing")
    require("if(addedTabindex)p.addEventListener('blur',restoreTabindex,{once:true})" in text, "temporary focusability blur restoration missing")
    require("if(!hadFlash){" in text and "p.classList.add('fvsb-flash');addedFlash=true" in text, "feature flash ownership missing")
    require("const restoreFlash=()=>{if(!addedFlash)return;if(hadClass)p.setAttribute('class',priorClass);else p.removeAttribute('class');addedFlash=false}" in text, "exact class-state flash restoration missing")
    require("setTimeout(()=>restoreFlash(),1400)" in text and "restoreFlash();" in text, "timer/failure flash restoration wiring missing")
    require("setAttribute('id'" not in text and ".id=`fvsb-" not in text, "story-point id mutation remains")

    scroll_i = text.index("p.scrollIntoView")
    close_i = text.index("dialog?.close()")
    tab_i = text.index("p.setAttribute('tabindex','-1')")
    focus_i = text.index("p.focus({preventScroll:true})")
    require(scroll_i < close_i < tab_i < focus_i, "jump transaction ordering drifted")
    require("let dialog=null,pendingSuppressedCloses=0" in text, "close-event accounting state missing")
    require("pendingSuppressedCloses++" in text, "close-event suppression accounting missing")
    require("pendingSuppressedCloses=Math.max(0,pendingSuppressedCloses-1)" in text, "failed-close counter rollback missing")
    require("if(pendingSuppressedCloses>0){pendingSuppressedCloses--;return}launch.focus()" in text, "close-event focus suppression contract missing")
    require("suppressNextCloseFocus" not in text, "boolean close suppression race remains")
    require("const recoverJump=(trigger)=>" in text and "if(dialog&&!dialog.open){try{dialog.showModal()}" in text, "dialog recovery helper missing")
    require("const primary=trigger?.isConnected&&dialog?.open&&dialog.contains(trigger)?trigger:null" in text, "deterministic recovery ownership check missing")
    require("document.activeElement===recovery" in text and "document.activeElement===fallback" in text, "recovery active-element verification missing")
    require("j.addEventListener('click',()=>jump(item,j))" in text, "jump trigger ownership not passed into transaction")

    for token in ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "<script src="):
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")

    script = re.search(r'<script id="fv-scale-board-r7-js">\n(.*?)\n</script>', text, re.S)
    require(script is not None, "unable to extract R7 JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script.group(1))
        js = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js)], check=True)
    finally:
        js.unlink(missing_ok=True)

    r4 = (ROOT / "tests/fixtures/scale-board-r4-truth-prefix.html").read_text(encoding="utf-8")
    for value in ("3/4 miles", "1/2 feet", "3⁄4 miles", "3 ⁄ 4 feet", "1⁄2 feet", "3∕4 miles", "3 ∕ 4 feet", "1 ∕ 2 miles", "3:4 feet", "3×4 feet", "3*4 feet", "3^4 feet", "3–4 feet", "3 to 4 feet", "1 000 feet", "1\u00a0000 feet", "1\u202f000 feet", "1'000 feet", "1’000 feet", "12 34 feet"):
        require(value in r4, f"missing prior adversarial fixture: {value!r}")

    r7 = (ROOT / "tests/fixtures/scale-board-r7-focus-prefix.html").read_text() + (ROOT / "tests/fixtures/scale-board-r7-focus-suffix.html").read_text()
    for value in (
        "forced-scroll-failure-absent", "forced-scroll-failure-owned-tab", "forced-scroll-failure-owned-class",
        "forced-focus-failure", "forced-timer-failure", "scroll failure did not recover jump focus",
        "focus failure did not reopen dialog", "successful absent jump did not focus story target",
        "temporary absent tabindex not restored on blur", "owned-id temporary tabindex not restored on blur",
        'tabindex="0"', 'tabindex="-7"', 'id="publisher-owned-point"', 'class="published-copy fvsb-flash"',
        "repeat success focus/dialog drift", "repeat temporary tabindex not restored on blur", "feature leaked interaction error",
    ):
        require(value in r7, f"missing R7 focus/dialog regression: {value}")

    state = (ROOT / "tests/fixtures/scale-board-r5-dom-state-prefix.html").read_text() + (ROOT / "tests/fixtures/scale-board-r5-dom-state-suffix.html").read_text()
    for value in ('tabindex="0"', 'tabindex="-7"', 'id="publisher-owned-point"', 'class="published-copy fvsb-flash"', "repeat jump drifted absent state"):
        require(value in state, f"missing preserved R5 DOM-state regression: {value}")

    browser_run("tests/fixtures/scale-board-r7-focus-prefix.html", "tests/fixtures/scale-board-r7-focus-suffix.html", "focus-dialog-atomicity")
    browser_run("tests/fixtures/scale-board-r5-dom-state-prefix.html", "tests/fixtures/scale-board-r5-dom-state-suffix.html", "r5-dom-state")
    browser_run("tests/fixtures/scale-board-r4-truth-prefix.html", "tests/fixtures/scale-board-r4-truth-suffix.html", "r4-truth")
    browser_run("tests/fixtures/scale-board-r3-truth-prefix.html", "tests/fixtures/scale-board-r3-truth-suffix.html", "r3-truth")
    browser_run("tests/fixtures/scale-board-r2-truth-prefix.html", "tests/fixtures/scale-board-r2-truth-suffix.html", "r2-truth")
    browser_run("tests/fixtures/scale-board-r1-truth-prefix.html", "tests/fixtures/scale-board-r1-truth-suffix.html", "r1-truth")
    browser_run("tests/fixtures/scale-board-r2-ambiguous-prefix.html", "tests/fixtures/scale-board-r2-fail-suffix.html", "ambiguous-sources")
    print("PASS: Scale Board R7 exact identity, failure-atomic focus/dialog recovery, temporary focusability restoration, publisher-state restoration, close-event accounting, R1-R6 truth/state regressions, Sources integrity, accessibility and privacy contract")


if __name__ == "__main__":
    main()
