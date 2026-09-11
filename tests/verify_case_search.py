from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "case-search-wp-block-v1.txt"
EXPECTED_BYTES = 17534
EXPECTED_SHA256 = "e313db1e31ff1fce01b8bbd5d8dda03673b9a52aadcc7cbecafd2cec50dcc6a7"


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
    require('data-scope="all"' in text and 'data-scope="story"' in text and 'data-scope="sources"' in text and 'data-scope="figures"' in text, "scope controls missing")

    require("const buildIndex=()=>{if(index)return index" in text, "lazy one-time page index missing")
    require("tokens.every(token=>item.search.includes(token))" in text, "multi-token AND matching missing")
    require("matches.slice(0,60)" in text, "bounded result rendering missing")
    require("SOURCE ${num}" in text and "kind:'FIGURE'" in text and "kind:'STORY'" in text and "kind:'SECTION'" in text, "typed result labels missing")
    require("findNormalizedSpans" in text and "snippetSegments" in text, "normalization-consistent snippet helpers missing")
    require("document.createElement('mark')" in text, "safe highlighted snippets missing")
    require("mark.textContent=seg.text" in text, "marked query output must use textContent")
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
        r"innerHTML\s*=.*(?:input\.value|\bq\b|rawTokens)": "query interpolation into innerHTML",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-case-search-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    js = match.group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(js)
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    helper_match = re.search(
        r"// FV_CASE_SEARCH_NORMALIZED_HELPERS_START\n(.*?)\n// FV_CASE_SEARCH_NORMALIZED_HELPERS_END",
        js,
        flags=re.S,
    )
    require(helper_match is not None, "normalized helper test seam missing")
    behavior = helper_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
const marks=result=>result.segments.filter(s=>s.kind==='mark').map(s=>s.text);
let r=snippetSegments('The café opened beside the archive.', ['cafe']);
assert(marks(r).includes('café'),'composed diacritic match must be visibly marked');
r=snippetSegments('The cafe\u0301 opened beside the archive.', ['cafe']);
assert(marks(r).some(v=>v.normalize('NFC')==='café'),'decomposed diacritic match must be visibly marked');
r=snippetSegments('The café report was filed after review.', ['cafe','report']);
const multi=marks(r).map(v=>normalize(v));
assert(multi.includes('cafe')&&multi.includes('report'),'multi-term normalized AND terms must both be marked');
const long='x'.repeat(140)+' café '+'y'.repeat(160);
r=snippetSegments(long,['cafe']);
assert(r.start>0,'contextual snippet must center a distant normalized match instead of starting at block start');
assert(r.segments[0].text==='…','centered snippet must show leading ellipsis');
assert(marks(r).includes('café'),'centered normalized match must remain marked');
const span=findNormalizedSpans('Résumé and resume',['resume']);
assert(span.length>=2,'normalization must find composed and plain equivalents');
console.log('CASE SEARCH BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("CASE SEARCH BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print("PASS: Case Search exact payload identity, normalization-consistent snippets/highlights, contextual centering, scoped retrieval, accessibility, privacy boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
