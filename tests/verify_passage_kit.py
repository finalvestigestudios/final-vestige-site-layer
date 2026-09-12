from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "passage-kit-wp-block-v1.txt"
EXPECTED_BYTES = 7978
EXPECTED_SHA256 = "84029f887442608563ad488cc440612378a3137ad55056890ed5b577512c5f40"


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
    require('<style id="fv-passage-kit-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-passage-kit-v1-js">' in text, "versioned script id missing")
    require("window.__fvPassageKit" in text, "duplicate-init guard missing")

    require("single-post" in text and "single" in text, "single-article gate missing")
    require("prose.length<12||totalText<3000" in text, "longform qualification threshold missing")
    require("[data-fv-footnotes],.fv-source-list" in text, "source-trail qualification missing")
    require("sourceItems.length<2" in text, "minimum source-record threshold missing")
    require("figure,figcaption,header,footer,nav,form" in text, "non-narrative exclusion contract missing")

    require("PASSAGE KIT" in text, "feature label missing")
    require("Carry a published passage with its linked source notes." in text, "visitor-job microcopy missing")
    require("Copies published wording and linked source notes. It does not rate the evidence." in text, "evidence-boundary microcopy missing")
    require("Show copy controls" in text and "Hide copy controls" in text, "opt-in controls missing")
    require("Copy passage + sources" in text and "'Copy passage'" in text, "per-passage actions missing")

    require(".fv-fn-ref[data-fv-fn]" in text, "existing citation-marker derivation missing")
    require("document.getElementById('fv-fn-'+num)" in text, "source-note lookup missing")
    require(".fv-fn-backlinks,.fv-fn-back" in text, "source backlink cleanup missing")
    require("Linked source " in text, "copied source-note boundary missing")
    require("articleTitle" in text and "Section: ${section}" in text, "article/section context missing")
    require("location.origin+location.pathname" in text, "same-origin query-free page reference missing")
    require("quoteFor(block)" in text, "published passage extraction missing")
    require(".fv-fn-mark,.fv-passage-kit-action" in text, "citation/control stripping from copied passage missing")

    require("navigator.clipboard?.writeText" in text, "Clipboard API path missing")
    require("window.prompt('Copy this passage and its source notes:'" in text, "clipboard fallback missing")
    require('role="status"' in text and 'aria-live="polite"' in text, "polite status semantics missing")
    require("aria-label','Passage Kit'" in text, "Passage Kit region label missing")
    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:360px)" in text, "small-mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion support missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")
    require("e.key==='Escape'" in text and "toggle.focus()" in text, "Escape cleanup/focus return missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "location.href", "posthog", "gtag(", "sendBeacon", "WebSocket"
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics token: {token}")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-passage-kit-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Passage Kit payload identity, source-bound passage export, accessibility contract, no-persistence/no-network boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
