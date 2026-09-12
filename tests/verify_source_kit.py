from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "source-kit-wp-block-v1.txt"
EXPECTED_BYTES = 11198
EXPECTED_SHA256 = "841ea1e40de12b43d1aaf616fe1277c13ce55e8ac4419e9cd2d65309f5b661e6"

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
    require('<style id="fv-source-kit-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-source-kit-v1-js">' in text, "versioned script id missing")
    require("window.__fvSourceKit" in text, "duplicate-init guard missing")
    require("sourcePattern" in text and "references?" in text, "source-section qualification missing")
    require("sourceRecords.length<2" in text, "minimum-source fail-closed qualification missing")
    require("navigator.clipboard" in text and "document.execCommand('copy')" in text, "clipboard + fallback paths missing")
    require("new Blob" in text and "URL.createObjectURL" in text and "URL.revokeObjectURL" in text, "local Markdown download lifecycle missing")
    require('role="status"' in text and 'aria-live="polite"' in text, "accessible action status missing")
    require("min-height:44px" in text, "44px minimum controls missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion rule missing")
    require("@media(max-width:380px)" in text, "small-mobile behavior missing")
    banned = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"localStorage": "localStorage",
        r"sessionStorage": "sessionStorage",
        r"indexedDB": "IndexedDB",
        r"<script[^>]+src=": "external script dependency",
    }
    for pattern, label in banned.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")
    match = re.search(r'<script id="fv-source-kit-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    print("PASS: Source Kit payload identity, safety invariants, accessibility hooks, and JavaScript syntax verified")

if __name__ == "__main__":
    main()
