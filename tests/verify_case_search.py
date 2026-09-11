from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "case-search-wp-block-v1.txt"
EXPECTED_BYTES = 16098
EXPECTED_SHA256 = "1c9e61ccf0614f02e3b46cb3c16040a00dc6d9ac346fa710aef8c62255baa3f6"


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
    require('<style id="fv-case-search-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-case-search-v1-js">' in text, "versioned script id missing")
    require("window.__fvCaseSearch" in text, "duplicate-init guard missing")

    require("single-post" in text and "single" in text, "single-article gate missing")
    require("[data-fv-footnotes],.fv-source-list" in text, "source-trail selector missing")
    require("prose.length<12||totalText<3000||sources.length<2" in text, "longform/source fail-closed threshold missing")
    require("figure.wp-block-image" in text and "figcaption" in text, "figure-caption indexing contract missing")
    require("h2,h3" in text and "sectionFor" in text, "section-context indexing contract missing")
    require("featureUi" in text and ".fv-passage-kit" in text and ".fv-reading-focus" in text, "feature-UI exclusion contract missing")

    require("CASE SEARCH" in text, "feature label missing")
    require("Find a detail without losing the thread." in text, "visitor-job microcopy missing")
    require("Search this investigation" in text, "launcher/dialog copy missing")
    require("No search query is sent anywhere." in text, "privacy-boundary microcopy missing")
    require("Browser Find still works normally." in text, "browser Find non-interference copy missing")
    require("data-scope=\"all\"" in text and "data-scope=\"story\"" in text and "data-scope=\"sources\"" in text and "data-scope=\"figures\"" in text, "scope controls missing")

    require("const buildIndex=()=>{if(index)return index" in text, "lazy one-time page index missing")
    require("tokens.every(token=>item.search.includes(token))" in text, "multi-token AND matching missing")
    require("matches.slice(0,60)" in text, "bounded result rendering missing")
    require("SOURCE ${num}" in text and "kind:'FIGURE'" in text and "kind:'STORY'" in text and "kind:'SECTION'" in text, "typed result labels missing")
    require("renderSnippet" in text and "document.createElement('mark')" in text, "safe highlighted snippets missing")
    require("textContent=item.kind" in text and "textContent=item.context" in text, "result content must be text-node based")

    require("HTMLDialogElement" in text and "dialog.showModal()" in text, "native modal dialog path missing")
    require("aria-labelledby','fv-case-search-title'" in text, "dialog accessible name missing")
    require('role="status"' in text and 'aria-live="polite"' in text, "polite result announcement missing")
    require("ArrowDown" in text and "ArrowUp" in text and "Home" in text and "End" in text, "keyboard result navigation missing")
    require("target.focus({preventScroll:true})" in text, "jump destination focus handoff missing")
    require("if(!jumped)open.focus()" in text, "non-jump focus return missing")
    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:360px)" in text, "small-mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion support missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "location.href", "posthog", "gtag(", "sendBeacon", "WebSocket",
        "ctrlKey", "metaKey",
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/shortcut token: {token}")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-case-search-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Case Search payload identity, scoped in-page retrieval, keyboard/accessibility contract, browser-Find non-interference, no-persistence/no-network boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
