from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "scale-board-wp-block-r2.txt"
EXPECTED_BYTES = 17306
EXPECTED_SHA256 = "8e9c451eb9ec9bbaec4f172d0c6b07f4f05b95033941c716d83ca75bfc4885d5"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def browser_run(prefix: Path, suffix: Path, label: str) -> None:
    browser = next((shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser") if shutil.which(n)), None)
    require(browser is not None, "headless Chrome/Chromium unavailable")
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / f"scale-board-r2-{label}.html"
        page.write_bytes(prefix.read_bytes() + PAYLOAD.read_bytes() + suffix.read_bytes())
        proc = subprocess.run(
            [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--dump-dom", page.as_uri()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        require(proc.returncode == 0, f"browser fixture {label} failed: {proc.stderr[-500:]}")
        require('data-fv-test="pass"' in proc.stdout, f"browser fixture {label} assertions failed")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload bytes drifted: {len(raw)}")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "payload SHA-256 drifted")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('id="fv-scale-board-r2-css"' in text and 'id="fv-scale-board-r2-js"' in text, "R2 versioned ids missing")
    require("window.__fvScaleBoardR2" in text, "R2 duplicate-init guard missing")
    require("boundaryCandidates.length!==1" in text and "sourceHeading.id!=='sources'" in text and "noteRoots.length!==1" in text, "canonical Sources fail-closed contract missing")
    require("if(/\\d\\s+$/.test(left))return true" in text, "digit-plus-whitespace boundary guard missing")
    require("[\\d,.+\\-_'’]" in text, "adjacent numeric separator boundary guard missing")
    require("selected.some(existing=>overlaps(candidate,existing))" in text, "R1 overlap truth repair missing")
    require("candidates.sort((a,b)=>a.start-b.start||(b.end-b.start)-(a.end-a.start)||a.rank-b.rank" in text, "deterministic longest-span ordering missing")
    require("Bars compare magnitude, not importance, causation, confidence, or evidence quality." in text, "truthful comparison disclaimer missing")
    require("min-height:44px" in text and "@media(max-width:360px)" in text and "prefers-reduced-motion:reduce" in text and "forced-colors:active" in text, "accessibility/mobile contract missing")
    for token in ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "<script src="):
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")

    script = re.search(r'<script id="fv-scale-board-r2-js">\n(.*?)\n</script>', text, re.S)
    require(script is not None, "unable to extract R2 JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    truth_prefix = ROOT / "tests" / "fixtures" / "scale-board-r2-truth-prefix.html"
    truth_suffix = ROOT / "tests" / "fixtures" / "scale-board-r2-truth-suffix.html"
    amb_prefix = ROOT / "tests" / "fixtures" / "scale-board-r2-ambiguous-prefix.html"
    fail_suffix = ROOT / "tests" / "fixtures" / "scale-board-r2-fail-suffix.html"
    fixture_text = truth_prefix.read_text(encoding="utf-8")
    for value in ("1 000 feet", "1\u00a0000 feet", "1\u202f000 feet", "1'000 feet", "1’000 feet", "12 34 feet"):
        require(value in fixture_text, f"missing adversarial fixture: {value!r}")
    browser_run(truth_prefix, truth_suffix, "truth")
    browser_run(amb_prefix, fail_suffix, "ambiguous")
    print("PASS: Scale Board R2 exact identity, grouped-numeral fail-closed boundary, R1 overlap fixes, truthful comparison semantics, accessibility/privacy contract, and exact-payload browser regressions")


if __name__ == "__main__":
    main()
