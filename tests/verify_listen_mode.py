from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "listen-mode-wp-block-v1.txt"
EXPECTED_BYTES = 12842
EXPECTED_SHA256 = "87e33999aed82a79992f4875ce22278202b55e5b545e70dfd806a2fac9b2fb99"


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
    require('<style id="fv-listen-mode-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-listen-mode-v1-js">' in text, "versioned script id missing")
    require("window.__fvListenMode" in text, "duplicate-init guard missing")

    require("single-post" in text and "single" in text, "single-article gate missing")
    require("[data-fv-footnotes],.fv-source-list" in text, "source-trail selector missing")
    require("prose.length<12||totalText<3000" in text, "longform fail-closed threshold missing")
    require(".fv-fn-mark" in text and "spokenText" in text, "footnote-marker exclusion missing")
    require("h2,h3" in text and "sectionFor" in text, "story-section narration context missing")
    require("featureUi" in text and ".fv-reading-focus" in text and ".fv-case-search" in text, "feature-UI exclusion contract missing")

    require("LISTEN MODE" in text, "feature label missing")
    require("Listen to the investigation without losing your place." in text, "visitor-job microcopy missing")
    require("Listen to this investigation" in text, "launcher copy missing")
    require("Final Vestige does not send article text to a speech service." in text, "privacy-boundary microcopy missing")
    require("Narrative only · source notes stay on the page" in text, "source-boundary microcopy missing")

    require("'speechSynthesis'in window" in text and "'SpeechSynthesisUtterance'in window" in text, "native speech capability gate missing")
    require("new SpeechSynthesisUtterance(item.text)" in text, "utterance construction missing")
    require("synth.speak(utterance)" in text, "speech playback missing")
    require("synth.pause()" in text and "synth.resume()" in text and "synth.cancel()" in text, "playback controls incomplete")
    require('data-action="prev"' in text and 'data-action="next"' in text and 'data-action="stop"' in text, "transport controls missing")
    require('data-rate="0.8"' in text and 'data-rate="1.5"' in text, "bounded rate controls missing")
    require("fv-listen-mode-current" in text and "scrollIntoView" in text, "current-passage follow-along missing")
    require("e.key==='Escape'" in text and "open.focus()" in text, "Escape/focus-return contract missing")
    require('role="status"' in text and 'aria-live="polite"' in text, "polite playback announcement missing")

    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:360px)" in text, "small-mobile behavior missing")
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
        r"getVoices\s*\(": "voice enumeration dependency",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-listen-mode-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Listen Mode payload identity, progressive native narration, story/source boundary, transport/rate controls, accessibility behavior, no-persistence/no-network boundary, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
