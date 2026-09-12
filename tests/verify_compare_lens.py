from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "compare-lens-wp-block-v1.txt"
EXPECTED_BYTES = 17616
EXPECTED_SHA256 = "b78476ffd1732c78f35e33a3ca7af7433bcc3abe087e37ac0581ab997a1e53ef"


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
    require('<style id="fv-compare-lens-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-compare-lens-v1-js">' in text, "versioned script id missing")
    require("window.__fvCompareLens" in text, "duplicate-init guard missing")

    require("single-post" in text and "single" in text, "single-article gate missing")
    require("HTMLDialogElement" in text and "showModal" in text, "native dialog capability gate missing")
    require("[data-fv-footnotes],.fv-source-list" in text, "source boundary selector missing")
    require("beforeSources" in text, "source-boundary filtering missing")
    require("rawFigures" in text and "figures.length<2" in text, "two-figure fail-closed gate missing")
    require("figure.wp-block-image" in text, "published figure selector missing")
    require("!f.closest('[data-fv-feature-ui]')" in text, "feature UI exclusion missing")

    require("COMPARE LENS" in text, "feature label missing")
    require("Put two published figures side by side." in text, "visitor-job microcopy missing")
    require("Compare figures" in text, "launcher/dialog copy missing")
    require("they do not alter the published images or imply that two figures are equivalent evidence" in text, "evidence-boundary microcopy missing")
    require("Published caption" in text and "View in story" in text, "published context controls missing")

    require("bestImage" in text and "srcset" in text, "lazy best-available image selection missing")
    require("panel.image.src=bestImage(figure.img)" in text, "on-demand image load missing")
    require("open.addEventListener('click'" in text and "load(panels[0]);load(panels[1]);dialog.showModal()" in text, "load-on-open contract missing")
    require("Sync zoom and pan" in text and "syncFrom" in text, "synchronized inspection missing")
    require('data-action="swap"' in text, "figure swap control missing")
    require('data-zoom-out="${i}"' in text and 'data-zoom-in="${i}"' in text and 'data-reset="${i}"' in text, "zoom/reset controls missing")
    require("pointerdown" in text and "pointermove" in text and "setPointerCapture" in text, "pointer pan behavior missing")
    require("ArrowLeft" in text and "ArrowRight" in text and "ArrowUp" in text and "ArrowDown" in text, "keyboard pan behavior missing")
    require("scale:clamp(next.scale,1,6)" in text, "bounded zoom range missing")
    require("returnToFigure" in text and "figure.focus" in text, "view-in-story focus handoff missing")
    require("dialog.addEventListener('close'" in text and "open.focus()" in text, "dialog focus-return contract missing")
    require('role="status"' in text and 'aria-live="polite"' in text, "polite status announcements missing")

    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:760px)" in text and "@media(max-width:360px)" in text, "mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion support missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "posthog", "gtag(", "sendBeacon", "WebSocket",
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

    match = re.search(r'<script id="fv-compare-lens-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Compare Lens payload identity, two-figure qualification, lazy comparison, synchronized zoom/pan, source-boundary preservation, accessibility behavior, no-persistence/no-network boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
