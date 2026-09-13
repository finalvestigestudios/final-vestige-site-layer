from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "vestige-assembly-wp-block-v1.txt"
EXPECTED_BYTES = 8648
EXPECTED_SHA256 = "91a080938c87cd5242d01ca91b76530ae5667f0f920470c76b23a08b17f1fe11"


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
    require('<style id="fv-vestige-assembly-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-vestige-assembly-v1-js">' in text, "versioned script id missing")
    require("window.__fvVestigeAssembly" in text, "duplicate-init guard missing")

    # Homepage-only, one-time, opt-out gating.
    require("classList.contains('home')" in text, "front-page gate missing")
    require("fvVestigeAssemblySeenV1" in text, "session one-time gate missing")
    require("prefers-reduced-motion: reduce" in text, "reduced-motion JS gate missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion CSS fallback missing")
    require("forced-colors: active" in text, "forced-colors JS gate missing")
    require("forced-colors:active" in text, "forced-colors CSS fallback missing")
    require("@media print" in text, "print cleanup missing")

    # Decorative, non-blocking overlay contract: never hides real content from
    # assistive tech, never intercepts pointer input, never traps focus.
    require("setAttribute('aria-hidden','true')" in text, "aria-hidden decorative contract missing")
    require("pointer-events:none" in text, "click-through contract missing")
    require("'inert' in root" in text, "inert feature-detect missing")

    # Never fabricated as real evidence: only the brief-specified brand lines.
    require("Buried in a footnote." in text, "brand line 1 missing")
    require("Split across six files." in text, "brand line 2 missing")
    require("Marked on a map nobody thought to compare." in text, "brand line 3 missing")
    require("Left in a photograph taken eighty years ago." in text, "brand line 4 missing")
    banned_evidence_literals = ["NARA", "BOX ", "FRAME ", "1934", "SOURCE 0"]
    for token in banned_evidence_literals:
        require(token not in text, f"unexpected fabricated-citation literal: {token}")

    # No dependency introduction, no persistence beyond the one-time session flag,
    # no network calls, no unrelated tracking.
    banned_literals = [
        "localStorage", "indexedDB", "document.cookie", "location.href",
        "posthog", "gtag(", "sendBeacon", "WebSocket",
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/tracking token: {token}")
    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    # Hard failsafe against a stuck curtain.
    require("setTimeout(finish,12000)" in text, "hard failsafe removal missing")

    match = re.search(r'<script id="fv-vestige-assembly-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    js = match.group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(js)
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    gate_match = re.search(
        r"// FV_VESTIGE_ASSEMBLY_GATE_START\n(.*?)\n// FV_VESTIGE_ASSEMBLY_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate/timeline test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};

assert(fvVaShouldRun({isHomeClass:true})===true,'must run on the homepage by default');
assert(fvVaShouldRun({isHomeClass:false,pathname:'/blog/'})===false,'must not run off the homepage');
assert(fvVaShouldRun({isHomeClass:false,pathname:'/'})===true,'root pathname is an acceptable fallback signal when the home body class is absent');
assert(fvVaShouldRun({isHomeClass:true,reducedMotion:true})===false,'must not run under prefers-reduced-motion');
assert(fvVaShouldRun({isHomeClass:true,forcedColors:true})===false,'must not run under forced-colors');
assert(fvVaShouldRun({isHomeClass:true,sessionSeen:true})===false,'must not replay within the same session');
assert(fvVaShouldRun(null)===false,'must fail closed on missing context');

const timeline=fvVaTimeline();
assert(Array.isArray(timeline)&&timeline.length>0,'timeline must be a non-empty ordered list');
assert(timeline[0].stage==='run'&&timeline[0].delay===0,'timeline must start immediately with the run stage');
for(let i=1;i<timeline.length;i++){
  assert(timeline[i].delay>timeline[i-1].delay,'timeline stages must be strictly increasing in time');
}
const totalMs=timeline[timeline.length-1].delay;
assert(totalMs>=6000&&totalMs<=9000,'automatic choreography must resolve within the 6-9s brand target, got '+totalMs);
assert(timeline.some(s=>s.stage==='fade'),'timeline must include a fade-out stage before removal');
assert(timeline[timeline.length-1].stage==='remove','timeline must end by removing the curtain');

console.log('VESTIGE ASSEMBLY BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("VESTIGE ASSEMBLY BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print(
        "PASS: Vestige Assembly exact payload identity, homepage/one-time/reduced-motion/forced-colors "
        "gating, non-blocking decorative contract, no fabricated evidence, no added dependencies/network "
        "calls, bounded 6-9s choreography, hard failsafe removal, and JavaScript syntax verified"
    )


if __name__ == "__main__":
    main()
