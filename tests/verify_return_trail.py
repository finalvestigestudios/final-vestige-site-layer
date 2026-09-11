from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "return-trail-wp-block-v1.txt"
EXPECTED_BYTES = 9485
EXPECTED_SHA256 = "7c813363095b8ae730d93e2d781286908df3fbfc23af52efe484dc1d6066dd68"


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
    require('<style id="fv-return-trail-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-return-trail-v1-js">' in text, "versioned script id missing")
    require("window.__fvReturnTrail" in text, "duplicate-init guard missing")

    require("const KEY='fvReturnTrailV1'" in text, "dedicated local storage key missing")
    require("TTL=30*24*60*60*1000" in text, "30-day expiration contract missing")
    require("MAX=3" in text and ".slice(0,MAX)" in text, "bounded trail record count missing")
    require("saved only in this browser for up to 30 days." in text, "device-local privacy microcopy missing")
    require("Forget" in text and "localStorage.removeItem(KEY)" in text, "visitor-controlled forget action missing")
    require("record={path,title,index:best,heading:" in text, "minimal reading-position record missing")
    require("updated:now()" in text, "record expiration timestamp missing")

    require("single-post" in text and "single" in text, "single-article gate missing")
    require("prose.length<12||totalText<3000" in text, "longform qualification threshold missing")
    require("[data-fv-footnotes],.fv-source-list,figcaption" in text, "sources/captions exclusion contract missing")
    require("markers.length<10" in text, "minimum navigation-marker threshold missing")
    require("bounded>=95" in text and "bounded<5" in text, "completion/start thresholds missing")
    require("setTimeout(snapshot,850)" in text, "throttled persistence missing")
    require("pagehide" in text and "visibilitychange" in text, "exit/background persistence hooks missing")

    require("Continue reading" in text and "Return trail" in text, "resume microcopy missing")
    require("record.path+'#fv-return-trail'" in text, "one-click cross-page resume marker missing")
    require("location.hash==='#fv-return-trail'" in text, "automatic same-page resume handling missing")
    require("history.replaceState(null,'',path)" in text, "resume marker cleanup missing")
    require("scrollIntoView" in text and "target.focus({preventScroll:true})" in text, "resume movement and focus placement missing")
    require("['/','/blog/','/archive/','/investigations/']" in text, "bounded landing-surface contract missing")

    require("min-height:44px" in text, "44px control target missing")
    require("aria-live" in text and "role','status'" in text, "live status semantics missing")
    require("aria-label','Return trail'" in text, "return-trail region label missing")
    require("@media(max-width:360px)" in text, "small-mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion rule missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")

    require("location.pathname" in text, "same-origin path identity missing")
    require("location.href" not in text, "feature must not persist full URL/query data")
    require("document.cookie" not in text, "feature must not use cookies")
    require("sessionStorage" not in text, "feature must not use sessionStorage")
    require("indexedDB" not in text, "feature must not use IndexedDB")
    require("posthog" not in text.lower(), "feature must not emit PostHog analytics")
    require("gtag(" not in text, "feature must not emit GA analytics")

    banned = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"navigator\.sendBeacon": "sendBeacon",
        r"\bWebSocket\b": "WebSocket",
        r"<script[^>]+src=": "external script dependency",
    }
    for pattern, label in banned.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-return-trail-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Return Trail payload identity, bounded device-local resume state, accessibility contract, no-network boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
