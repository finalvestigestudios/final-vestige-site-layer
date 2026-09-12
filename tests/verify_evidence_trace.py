from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "evidence-trace-wp-block-v1.txt"
EXPECTED_BYTES = 9611
EXPECTED_SHA256 = "22185a26b5394f4686da939b68dc7194539ab0c9c5ee1ed8009a16d4bc89d920"


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
    require('<style id="fv-evidence-trace-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-evidence-trace-v1-js">' in text, "versioned script id missing")
    require("window.__fvEvidenceTrace" in text, "duplicate-init guard missing")

    require("[data-fv-footnotes]" in text and ".fv-fn-ref[data-fv-fn]" in text, "existing Final Vestige citation contract missing")
    require("passages.length<4||validNotes.length<3" in text, "fail-closed evidence threshold missing")
    require("Shows where this page links to source notes. It does not score uncited text." in text, "non-scoring evidence disclaimer missing")
    require("Show linked evidence" in text and "Hide linked evidence" in text, "explicit feature-state microcopy missing")
    require("Source note" in text, "source-note labeling missing")

    require("aria-pressed" in text, "toggle pressed state missing")
    require("aria-expanded" in text and "aria-controls" in text, "disclosure relationships missing")
    require("role','region'" in text and "aria-labelledby" in text, "source region semantics missing")
    require("min-height:44px" in text, "44px minimum controls missing")
    require("@media(max-width:360px)" in text, "small-mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion rule missing")
    require("forced-colors:active" in text, "forced-colors support missing")

    require("cloneNode(true)" in text, "source content must derive from the page's existing source note")
    require("fv-fn-backlinks" in text, "backlinks must be removed from cloned source preview")
    require("history.pushState" not in text, "feature must not rewrite article URL/history")

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

    match = re.search(r'<script id="fv-evidence-trace-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    print("PASS: Evidence Trace payload identity, evidence boundaries, accessibility hooks, and JavaScript syntax verified")


if __name__ == "__main__":
    main()
