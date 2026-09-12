from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "reading-focus-wp-block-v1.txt"
EXPECTED_BYTES = 11622
EXPECTED_SHA256 = "b37a88379c49774ce05bd4bbdda2cf314af544acbb57f71e2a2547bdba5aeb12"


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
    require('<style id="fv-reading-focus-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-reading-focus-v1-js">' in text, "versioned script id missing")
    require("window.__fvReadingFocus" in text, "duplicate-init guard missing")

    require("single-post" in text and "single" in text, "single-article fail-closed gate missing")
    require("prose.length<12||totalText<3000" in text, "longform qualification threshold missing")
    require("[data-fv-footnotes],.fv-source-list,figcaption" in text, "source/caption exclusion contract missing")
    require("Adjust text size, reading width, or guide one paragraph at a time. Nothing is saved." in text, "privacy + visitor-value microcopy missing")

    require("Text 100%" in text and "Text ${value}%" in text, "text-size controls missing")
    require("Width standard" in text and "measures=['standard','narrow','wide']" in text, "reading-width controls missing")
    require("Paragraph guide" in text and "Previous paragraph" in text and "Next paragraph" in text, "paragraph guide controls missing")
    require("aria-live" in text and "role','status'" in text, "live status semantics missing")
    require("aria-pressed" in text, "pressed-state semantics missing")
    require('aria-keyshortcuts="Escape"' in text, "escape discoverability missing")
    require("document.querySelector('dialog[open]')" in text, "open-dialog Escape guard missing")
    require("launcher.focus()" in text, "exit focus return missing")

    require("min-height:44px" in text and "min-width:44px" in text, "44px control target missing")
    require("@media(max-width:360px)" in text, "small-mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion rule missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")
    require("line-height:1.75" in text and "max-width:44rem" in text, "readability defaults missing")
    require("font-size:1.30em" in text, "130 percent text-size option missing")

    require("body[data-fv-reading-focus=\"on\"] .fv-site-header" in text, "decluttered header behavior missing")
    require("body[data-fv-reading-focus=\"on\"] footer" in text, "decluttered footer behavior missing")
    require("history.pushState" not in text, "feature must not rewrite URL/history")
    require("cloneNode(" not in text, "feature must not clone article content")
    require("innerHTML=root" not in text, "feature must not replace article content")

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

    match = re.search(r'<script id="fv-reading-focus-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Reading Focus payload identity, fail-closed longform gate, accessibility controls, privacy boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
