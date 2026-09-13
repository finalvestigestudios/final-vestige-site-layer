from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "margins-wire-wp-block-v1.txt"
EXPECTED_BYTES = 4392
EXPECTED_SHA256 = "004b6462e663155e5fede0620dd6f60fa13729984fbf69117aa1672a2e6102de"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(actual_sha256 == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha256}")

    require(text.count("<!-- wp:html -->") == 1, "payload must contain exactly one wp:html opener")
    require(text.count("<!-- /wp:html -->") == 1, "payload must contain exactly one wp:html closer")
    require('<style id="fv-margins-wire-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-margins-wire-v1-js">' in text, "versioned script id missing")
    require("window.__fvMarginsWire" in text, "duplicate-init guard missing")

    # Must enhance the real, already-published margin-strip markup in place --
    # never duplicate or fabricate its 72 real items.
    require("querySelector('.fv-margin-strip')" in text, "real margin-strip root selector missing")
    require("querySelectorAll('.fv-margin-strip__item')" in text, "must read the real existing items, not invent its own")
    require("el.textContent" not in text and "item.textContent" not in text, "must not overwrite real item text content")

    # Accessible, pausable, keyboard-navigable rotation, per the design brief.
    require("ArrowRight" in text and "ArrowLeft" in text, "keyboard prev/next navigation missing")
    require("'Previous fragment'" in text, "previous control label missing")
    require("'Next fragment'" in text, "next control label missing")
    require("Pause rotation" in text and "Resume rotation" in text, "pause/resume control labels missing")
    require("mouseenter" in text and "focusin" in text, "hover/focus pause missing")
    require("prefers-reduced-motion: reduce" in text, "reduced-motion autoplay gate missing")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
        r"localStorage|sessionStorage|document\.cookie": "unexpected persistence",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-margins-wire-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    js = match.group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(js)
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    gate_match = re.search(
        r"// FV_MARGINS_WIRE_GATE_START\n(.*?)\n// FV_MARGINS_WIRE_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
assert(fvMwShouldRun([1,2,3])===true,'must run with multiple real items');
assert(fvMwShouldRun([1])===false,'must not run with a single item (nothing to rotate)');
assert(fvMwShouldRun([])===false,'must not run with zero items');
assert(fvMwShouldRun(null)===false,'must fail closed on a non-array');
console.log('MARGINS WIRE BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("MARGINS WIRE BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print(
        "PASS: Margins Wire exact payload identity, real-content-only enhancement, "
        "keyboard/pause/resume accessibility contract, reduced-motion gating, no "
        "dependencies/network calls, and JavaScript syntax verified"
    )


if __name__ == "__main__":
    main()
