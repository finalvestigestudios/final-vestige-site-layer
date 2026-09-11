from __future__ import annotations
import hashlib, re, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "scale-board-wp-block-v1.txt"
EXPECTED_BYTES = 16198
EXPECTED_SHA256 = "7e0109c4315e2206ee73ed1f1fa1ed808953362561a7a82652fc4541ad7fe729"

def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")

def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "payload SHA-256 drifted")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single wp:html block required")
    require('<style id="fv-scale-board-v1-css">' in text and '<script id="fv-scale-board-v1-js">' in text, "versioned style/script IDs missing")
    require("window.__fvScaleBoardV1" in text, "duplicate-init guard missing")
    require("querySelectorAll('#sources,.fv-source-heading')" in text, "all source-boundary candidates must be inspected")
    require("boundaryCandidates.length!==1" in text, "ambiguous/partial source boundaries must fail closed")
    require("sourceHeading.tagName!=='H2'||sourceHeading.id!=='sources'||!sourceHeading.classList.contains('fv-source-heading')" in text, "exact canonical Sources H2 required")
    require("noteRoots.length!==1" in text and "!follows(sourceHeading,notesRoot)" in text, "unique later notes root required")
    require("paragraphs.length<12||paragraphs.length>120" in text, "bounded longform qualification missing")
    required_units = [
        "Speed · miles per hour", "Speed · kilometers per hour", "Percent",
        "Distance · feet", "Distance · miles", "Distance · meters",
        "Voltage", "Power", "Pressure", "Speed · knots",
        "Mass · kilograms", "Mass · pounds", "Mass · tons",
        "Duration · seconds", "Duration · minutes", "Duration · hours",
        "Duration · days", "Duration · weeks", "Duration · years",
        "Temperature · Fahrenheit", "Temperature · Celsius"
    ]
    for unit in required_units:
        require(unit in text, f"supported unit family missing: {unit}")
    require("items.length<2||items.length>80" in text, "bounded extraction missing")
    require("new Set(arr.map(x=>x.value)).size>=2" in text, "at least two distinct same-unit values required")
    require("Number.isFinite(value)||value<0" in text, "non-finite/negative values must be rejected")
    require("parseNumber" in text and "numberPattern" in text, "explicit number parser missing")
    require("See the quantities in proportion." in text and "Open Scale Board" in text, "prominent launcher missing")
    require("Bars compare magnitude, not importance, causation, confidence, or evidence quality." in text, "truthfulness boundary missing")
    require("View in story" in text and "scrollIntoView" in text and "p.focus" in text, "story-return path missing")
    require("dialog.showModal()" in text and "aria-labelledby" in text, "native modal semantics missing")
    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:640px)" in text and "@media(max-width:360px)" in text, "mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility media handling missing")
    require("dialog.addEventListener('close',()=>launch.focus())" in text, "focus return missing")
    banned = [
        "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket",
        "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "posthog", "gtag(", "<iframe", "<script src=", "navigator.clipboard",
        "history.pushState", "history.replaceState"
    ]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected external/persistent behavior: {token}")
    match = re.search(r'<script id="fv-scale-board-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(path)], check=True)
    finally:
        path.unlink(missing_ok=True)
    print("PASS: Scale Board exact identity, bounded explicit-measure extraction, trust boundary, accessibility, privacy, and JavaScript syntax")

if __name__ == "__main__":
    main()
