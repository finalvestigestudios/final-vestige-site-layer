from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "case-compass-wp-block-v1.txt"
EXPECTED_BYTES = 15713
EXPECTED_SHA256 = "6e4e0a8abb25676924d7a4f7bbfcbe024e7a3a19c1f267854ca16849dd7c37ee"


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
    require('<style id="fv-case-compass-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-case-compass-v1-js">' in text, "versioned script id missing")
    require("window.__fvCaseCompass" in text, "duplicate-init guard missing")

    require("single-post" in text, "single-post qualification missing")
    require("HTMLDialogElement" in text and "showModal" in text, "native dialog capability gate missing")
    require("h2#sources.fv-source-heading" in text, "trusted Sources heading selector missing")
    require(".fv-source-list[data-fv-footnotes]" in text, "trusted source-note list selector missing")
    require("if(!sourceHeading||!notes)return" in text, "missing-source fail-closed gate missing")
    require("sourceHeading.compareDocumentPosition(notes)&Node.DOCUMENT_POSITION_FOLLOWING" in text, "heading-before-notes contract missing")
    require("if(!root.contains(notes)||!root.contains(sourceHeading))return" in text, "same-content-root source contract missing")
    require("h2s.length<3||paragraphs.length<12" in text and "storyChars<2800" in text, "longform fail-closed thresholds missing")
    require("if(sections.length<4)return" in text, "minimum structural map threshold missing")

    require("CASE COMPASS" in text.upper(), "feature label missing")
    require("See the investigation before you enter it." in text, "prominent visitor-value copy missing")
    require("Structure only—not an evidence or confidence score." in text, "non-scoring boundary copy missing")
    require("Counts describe page structure only." in text, "structural-count boundary copy missing")
    require("Opening" in text and "Investigation map" in text, "structural map copy missing")

    require("new Set()" in text and ".fv-fn-ref[data-fv-fn]" in text, "distinct linked-note counting missing")
    require("figure.wp-block-image" in text, "figure structure counting missing")
    require(".fv-fn-mark,[data-fv-feature-ui]" in text, "citation/feature UI cleaning missing")
    require("textContent=" in text, "safe dynamic text rendering missing")
    require("innerHTML='<div class=" in text, "static feature shell missing")

    require("IntersectionObserver" in text and "rootMargin:'-18% 0px -72% 0px'" in text, "current-section observation missing")
    require("requestAnimationFrame" in text, "observation/fallback scheduling missing")
    require("aria-current" in text and 'role="status"' in text and 'aria-live="polite"' in text, "current-location accessibility state missing")
    require("ArrowDown" in text and "ArrowUp" in text and "Home" in text and "End" in text, "dialog keyboard navigation missing")
    require("pendingTarget" in text and "dialog.addEventListener('close'" in text and "open.focus()" in text, "focus-return/handoff contract missing")
    require("scrollIntoView" in text and "prefers-reduced-motion" in text, "motion-aware story jump missing")

    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:700px)" in text and "@media(max-width:360px)" in text, "mobile behavior missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "posthog", "gtag(", "sendBeacon", "WebSocket", "history.pushState",
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics/history token: {token}")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"<iframe\b": "embedded external frame",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-case-compass-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Case Compass payload identity, trusted-source fail-closed qualification, structural navigation, current-section state, accessibility behavior, no-persistence/no-network boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
