from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "signature-alignment-wp-block-v1.txt"
EXPECTED_BYTES = 2327
EXPECTED_SHA256 = "68ad5cd472f7885dd6aec3bedb6ea601eb0b6330a7ad9a3da657f2962ede4d65"


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
    require('<script id="fv-signature-alignment-v1-js">' in text, "versioned script id missing")
    require("window.__fvSignatureAlignment" in text, "duplicate-init guard missing")

    require("querySelector('[data-fv-align-stage]')" in text, "real stage selector missing")
    require("pointerdown" in text and "mousedown" in text, "pointer and mouse drag support missing")
    require("keydown" in text and "ArrowLeft" in text and "ArrowRight" in text, "keyboard alignment missing")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
        r"localStorage|sessionStorage|document\.cookie": "unexpected persistence",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-signature-alignment-v1-js">\n(.*?)\n</script>', text, flags=re.S)
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
        r"// FV_SIGNATURE_ALIGNMENT_GATE_START\n(.*?)\n// FV_SIGNATURE_ALIGNMENT_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
assert(fvSaShouldRun({hasStage:true,hasDivider:true,hasMapPanel:true,hasBadge:true})===true,'must run when all four real elements exist');
assert(fvSaShouldRun({hasStage:true,hasDivider:false,hasMapPanel:true,hasBadge:true})===false,'must not run without the real divider');
assert(fvSaShouldRun({hasStage:false,hasDivider:true,hasMapPanel:true,hasBadge:true})===false,'must not run without the real stage');
assert(fvSaShouldRun(null)===false,'must fail closed on missing context');
console.log('SIGNATURE ALIGNMENT BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("SIGNATURE ALIGNMENT BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print(
        "PASS: Signature Alignment exact payload identity, real-element gating, pointer/mouse/"
        "keyboard drag interaction, no dependencies/network calls, and JavaScript syntax verified"
    )


if __name__ == "__main__":
    main()
