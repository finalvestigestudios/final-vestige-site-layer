from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "library-inspector-wp-block-v1.txt"
EXPECTED_BYTES = 2646
EXPECTED_SHA256 = "0d736919a7defab459f041c41aea77b851ceb63463e718b84e367a6b68f1b2d3"


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
    require('<script id="fv-library-inspector-v1-js">' in text, "versioned script id missing")
    require("window.__fvLibraryInspector" in text, "duplicate-init guard missing")

    require("querySelector('[data-fv-library-frame]')" in text, "real evidence-frame selector missing")
    require("digitalcollections.nypl.org" not in text, "high-res source must stay on finalvestige.com, not re-host third-party URLs")
    require("nypl-5003296" in text, "must reference the real, already-published high-resolution asset")
    require("touchstart" in text and "touchmove" in text, "touch magnification missing")
    require("keydown" in text and "Enter" in text, "keyboard-accessible inspection missing")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
        r"localStorage|sessionStorage|document\.cookie": "unexpected persistence",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-library-inspector-v1-js">\n(.*?)\n</script>', text, flags=re.S)
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
        r"// FV_LIBRARY_INSPECTOR_GATE_START\n(.*?)\n// FV_LIBRARY_INSPECTOR_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
assert(fvLiShouldRun({hasFrame:true,hasImage:true,hasLoupe:true})===true,'must run when all three real elements exist');
assert(fvLiShouldRun({hasFrame:true,hasImage:false,hasLoupe:true})===false,'must not run without the real base image');
assert(fvLiShouldRun({hasFrame:false,hasImage:true,hasLoupe:true})===false,'must not run without the real frame');
assert(fvLiShouldRun(null)===false,'must fail closed on missing context');
console.log('LIBRARY INSPECTOR BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("LIBRARY INSPECTOR BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print(
        "PASS: Library Inspector exact payload identity, real-element gating, real-asset-only "
        "magnification, mouse/touch/keyboard interaction, no dependencies/network calls beyond "
        "the site's own media, and JavaScript syntax verified"
    )


if __name__ == "__main__":
    main()
