from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "scale-board-wp-block-r4.txt"
EXPECTED_BYTES = 17520
EXPECTED_SHA256 = "ecd9a6aed288061abd2ec55d53a049595174f8579178be773802d8ce7b325fee"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def browser_run(prefix: Path, suffix: Path, label: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium unavailable")
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / f"scale-board-r4-{label}.html"
        page.write_bytes(prefix.read_bytes() + PAYLOAD.read_bytes() + suffix.read_bytes())
        proc = subprocess.run(
            [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--dump-dom", page.as_uri()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        require(proc.returncode == 0, f"browser fixture {label} failed: {proc.stderr[-500:]}")
        if 'data-fv-test="pass"' not in proc.stdout:
            reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
            detail = reason.group(1) if reason else "no fixture reason surfaced"
            require(False, f"browser fixture {label} assertions failed: {detail}")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload bytes drifted: {len(raw)}")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "payload SHA-256 drifted")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('id="fv-scale-board-r4-css"' in text and 'id="fv-scale-board-r4-js"' in text, "R4 versioned ids missing")
    require("window.__fvScaleBoardR4" in text, "R4 duplicate-init guard missing")
    require("boundaryCandidates.length!==1" in text and "sourceHeading.id!=='sources'" in text and "noteRoots.length!==1" in text, "canonical Sources fail-closed contract missing")
    require("invalidNumericExpressionPrefix" in text, "numeric-expression boundary guard missing")
    require("⁄" in text and "∕" in text, "U+2044/U+2215 boundary guards missing")
    require("(?:[\\/:÷×*^+\\-−–—⁄∕]|[xX])" in text, "R4 operator/separator boundary set missing Unicode slashes")
    require("[\\d,.+\\-−–—_'’\\/:÷×*^⁄∕]$" in text, "R4 immediate-prefix boundary set missing Unicode slashes")
    require("(?:to|through|or)" in text, "textual range boundary guard missing")
    require("if(/\\d\\s+$/.test(left))return true" in text, "R2 digit-plus-whitespace boundary guard missing")
    require("selected.some(existing=>overlaps(candidate,existing))" in text, "R1 overlap truth repair missing")
    require("candidates.sort((a,b)=>a.start-b.start||(b.end-b.start)-(a.end-a.start)||a.rank-b.rank" in text, "deterministic longest-span ordering missing")
    require("Bars compare magnitude, not importance, causation, confidence, or evidence quality." in text, "truthful comparison disclaimer missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text and "prefers-reduced-motion:reduce" in text and "forced-colors:active" in text, "accessibility/mobile contract missing")
    for token in ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "<script src="):
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")

    script = re.search(r'<script id="fv-scale-board-r4-js">\n(.*?)\n</script>', text, re.S)
    require(script is not None, "unable to extract R4 JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    r4_prefix = ROOT / "tests" / "fixtures" / "scale-board-r4-truth-prefix.html"
    r4_suffix = ROOT / "tests" / "fixtures" / "scale-board-r4-truth-suffix.html"
    r3_prefix = ROOT / "tests" / "fixtures" / "scale-board-r3-truth-prefix.html"
    r3_suffix = ROOT / "tests" / "fixtures" / "scale-board-r3-truth-suffix.html"
    r2_prefix = ROOT / "tests" / "fixtures" / "scale-board-r2-truth-prefix.html"
    r2_suffix = ROOT / "tests" / "fixtures" / "scale-board-r2-truth-suffix.html"
    r1_prefix = ROOT / "tests" / "fixtures" / "scale-board-r1-truth-prefix.html"
    r1_suffix = ROOT / "tests" / "fixtures" / "scale-board-r1-truth-suffix.html"
    amb_prefix = ROOT / "tests" / "fixtures" / "scale-board-r2-ambiguous-prefix.html"
    fail_suffix = ROOT / "tests" / "fixtures" / "scale-board-r2-fail-suffix.html"

    fixture_text = r4_prefix.read_text(encoding="utf-8")
    required_adversarial = (
        "3/4 miles", "1/2 feet",
        "3⁄4 miles", "3 ⁄ 4 feet", "1⁄2 feet",
        "3∕4 miles", "3 ∕ 4 feet", "1 ∕ 2 miles",
        "3:4 feet", "3×4 feet", "3*4 feet", "3^4 feet", "3–4 feet", "3 to 4 feet",
        "1 000 feet", "1\u00a0000 feet", "1\u202f000 feet", "1'000 feet", "1’000 feet", "12 34 feet",
    )
    for value in required_adversarial:
        require(value in fixture_text, f"missing adversarial fixture: {value!r}")

    browser_run(r4_prefix, r4_suffix, "r4-unicode-slash-truth")
    browser_run(r3_prefix, r3_suffix, "r3-truth-regression")
    browser_run(r2_prefix, r2_suffix, "r2-truth-regression")
    browser_run(r1_prefix, r1_suffix, "r1-truth-regression")
    browser_run(amb_prefix, fail_suffix, "ambiguous-sources")
    print("PASS: Scale Board R4 exact identity, U+2044/U+2215 fraction-boundary hardening, R1-R3 truth regressions, Sources integrity, truthful comparison semantics, and accessibility/privacy contract")


if __name__ == "__main__":
    main()
