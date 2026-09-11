from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "scale-board-wp-block-r5.txt"
EXPECTED_BYTES = 17579
EXPECTED_SHA256 = "772e1c9557d10420cfff741fdaa32a8be53a299038f60c4dd0ed011f468e373f"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def browser_run(prefix: str, suffix: str, label: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium unavailable")
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / f"scale-board-r5-{label}.html"
        page.write_bytes((ROOT / prefix).read_bytes() + PAYLOAD.read_bytes() + (ROOT / suffix).read_bytes())
        proc = subprocess.run(
            [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--dump-dom", page.as_uri()],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
        )
        require(proc.returncode == 0, f"browser fixture {label} failed: {proc.stderr[-500:]}")
        if 'data-fv-test="pass"' not in proc.stdout:
            reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
            require(False, f"browser fixture {label} failed: {reason.group(1) if reason else 'no reason surfaced'}")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    actual_sha = hashlib.sha256(raw).hexdigest()
    require(len(raw) == EXPECTED_BYTES, f"payload bytes drifted: {len(raw)}")
    require(actual_sha == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    for token in (
        'id="fv-scale-board-r5-css"', 'id="fv-scale-board-r5-js"', "window.__fvScaleBoardR5",
        "boundaryCandidates.length!==1", "sourceHeading.id!=='sources'", "noteRoots.length!==1",
        "invalidNumericExpressionPrefix", "⁄", "∕", "selected.some(existing=>overlaps(candidate,existing))",
        "Bars compare magnitude, not importance, causation, confidence, or evidence quality.",
        "min-height:44px", "@media(max-width:360px)", "prefers-reduced-motion:reduce", "forced-colors:active",
    ):
        require(token in text, f"preserved contract missing: {token}")

    require("ensureId" not in text and "Math.random" not in text, "random story-point id mutation remains")
    require("hadTabindex=p.hasAttribute('tabindex')" in text, "pre-owned tabindex detection missing")
    require("if(!hadTabindex)p.setAttribute('tabindex','-1')" in text, "temporary focusability guard missing")
    require("finally{if(!hadTabindex)p.removeAttribute('tabindex')}" in text, "absent tabindex restoration missing")
    require("hadFlash=p.classList.contains('fvsb-flash')" in text, "pre-owned flash-class detection missing")
    require("if(!hadFlash)p.classList.add('fvsb-flash')" in text and "if(!hadFlash)p.classList.remove('fvsb-flash')" in text, "flash-class preservation missing")
    require("setAttribute('id'" not in text and ".id=`fvsb-" not in text, "story-point id mutation remains")

    for token in ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "<script src="):
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")

    script = re.search(r'<script id="fv-scale-board-r5-js">\n(.*?)\n</script>', text, re.S)
    require(script is not None, "unable to extract R5 JavaScript")
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

    state = (ROOT / "tests/fixtures/scale-board-r5-dom-state-prefix.html").read_text() + (ROOT / "tests/fixtures/scale-board-r5-dom-state-suffix.html").read_text()
    for value in ('tabindex="0"', 'tabindex="-7"', 'id="publisher-owned-point"', 'class="published-copy fvsb-flash"', "repeat jump drifted absent state"):
        require(value in state, f"missing R5 DOM-state regression: {value}")

    browser_run("tests/fixtures/scale-board-r5-dom-state-prefix.html", "tests/fixtures/scale-board-r5-dom-state-suffix.html", "dom-state")
    browser_run("tests/fixtures/scale-board-r4-truth-prefix.html", "tests/fixtures/scale-board-r4-truth-suffix.html", "r4-truth")
    browser_run("tests/fixtures/scale-board-r3-truth-prefix.html", "tests/fixtures/scale-board-r3-truth-suffix.html", "r3-truth")
    browser_run("tests/fixtures/scale-board-r2-truth-prefix.html", "tests/fixtures/scale-board-r2-truth-suffix.html", "r2-truth")
    browser_run("tests/fixtures/scale-board-r1-truth-prefix.html", "tests/fixtures/scale-board-r1-truth-suffix.html", "r1-truth")
    browser_run("tests/fixtures/scale-board-r2-ambiguous-prefix.html", "tests/fixtures/scale-board-r2-fail-suffix.html", "ambiguous-sources")
    print("PASS: Scale Board R5 exact identity, nondestructive DOM state, R1-R4 truth regressions, Sources integrity, accessibility and privacy contract")


if __name__ == "__main__":
    main()
