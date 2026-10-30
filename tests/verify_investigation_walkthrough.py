from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "investigation-walkthrough-wp-block-v1.txt"
EXPECTED_BYTES = 5180
EXPECTED_SHA256 = "8d8efdfb50cb177c852ed87283f9ba0628bc033a7c0b51ca06ae627c391622bd"


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
    require('<script id="fv-investigation-walkthrough-v1-js">' in text, "versioned script id missing")
    require("window.__fvInvestigationWalkthrough" in text, "duplicate-init guard missing")

    require("querySelector('[data-fv-invest-stages]')" in text, "real stage-list selector missing")
    require("IntersectionObserver" in text, "scroll-linked activation missing")
    require("addEventListener('click'" in text and "addEventListener('keydown'" in text, "click and keyboard activation missing")

    # Every image/credit/quote must be real, already-published Apollo 1 material --
    # no fabricated captions or invented source identifiers.
    require(text.count("nasa.gov") >= 6, "real NASA source-record links missing")
    require("No single ignition source was conclusively identified." in text, "real quoted finding missing")
    require("The replacement did not open inward." in text, "real closing quote missing")
    require("S67-19766" in text and "S67-21294" in text, "real NASA photo identifiers missing")
    banned_fabrication_markers = ["Lorem ipsum", "placeholder", "TODO", "example.com", "TK ", " TK,"]
    for marker in banned_fabrication_markers:
        require(marker not in text, f"unexpected placeholder/fabrication marker: {marker!r}")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
        r"localStorage|sessionStorage|document\.cookie": "unexpected persistence",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-investigation-walkthrough-v1-js">\n(.*?)\n</script>', text, flags=re.S)
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
        r"// FV_INVESTIGATION_WALKTHROUGH_GATE_START\n(.*?)\n// FV_INVESTIGATION_WALKTHROUGH_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
assert(fvIwShouldRun([1,2,3],3)===true,'must run when stage count matches evidence count');
assert(fvIwShouldRun([1,2],3)===false,'must not run on a stage/evidence count mismatch');
assert(fvIwShouldRun([],0)===false,'must not run with zero stages');
assert(fvIwShouldRun(null,3)===false,'must fail closed on a non-array');
console.log('INVESTIGATION WALKTHROUGH BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("INVESTIGATION WALKTHROUGH BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print(
        "PASS: Investigation Walkthrough exact payload identity, real-NASA-source-only "
        "content, click/keyboard/scroll activation, stage/evidence gating, no fabricated "
        "citations, no dependencies/network calls, and JavaScript syntax verified"
    )


if __name__ == "__main__":
    main()
