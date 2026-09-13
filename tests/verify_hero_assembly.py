from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "hero-assembly-wp-block-v1.txt"
EXPECTED_BYTES = 1137
EXPECTED_SHA256 = "5535880f3db7805b17b2766bcb8e8f6381456c037f8c67c3944f30c8aa8f86d0"


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
    require('<script id="fv-hero-assembly-v1-js">' in text, "versioned script id missing")
    require("window.__fvHeroAssembly" in text, "duplicate-init guard missing")

    # This payload only toggles attributes on real, already-rendered homepage
    # markup -- it must never create, remove, or hide any element itself.
    require("document.createElement" not in text, "must not create DOM nodes")
    require("removeChild" not in text, "must not remove DOM nodes")
    require("querySelector('[data-fv-assembly]')" in text, "real hero root selector missing")
    require("prefers-reduced-motion: reduce" in text, "reduced-motion gate missing")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
        r"localStorage|sessionStorage": "unexpected persistence",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-hero-assembly-v1-js">\n(.*?)\n</script>', text, flags=re.S)
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
        r"// FV_HERO_ASSEMBLY_GATE_START\n(.*?)\n// FV_HERO_ASSEMBLY_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate/timeline test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
assert(fvHaShouldRun({hasRoot:true})===true,'must run when the real hero root exists');
assert(fvHaShouldRun({hasRoot:false})===false,'must not run without the real hero root');
assert(fvHaShouldRun({hasRoot:true,reducedMotion:true})===false,'must not run under prefers-reduced-motion');
assert(fvHaShouldRun(null)===false,'must fail closed on missing context');
const timeline=fvHaTimeline();
assert(Array.isArray(timeline)&&timeline.length===3,'timeline must have run/in/connect stages');
assert(timeline[0].stage==='run'&&timeline[0].delay===0,'timeline must start immediately');
for(let i=1;i<timeline.length;i++){
  assert(timeline[i].delay>timeline[i-1].delay,'timeline stages must be strictly increasing in time');
}
assert(timeline[timeline.length-1].delay<3000,'choreography must resolve well within the hero’s first few seconds');
console.log('HERO ASSEMBLY BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("HERO ASSEMBLY BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    print(
        "PASS: Hero Assembly exact payload identity, real-root/reduced-motion gating, "
        "no DOM creation/removal, no dependencies/network calls, and JavaScript syntax verified"
    )


if __name__ == "__main__":
    main()
