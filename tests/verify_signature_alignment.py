from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "signature-alignment-wp-block-v1.txt"
EXPECTED_BYTES = 2740
EXPECTED_SHA256 = "ddc23041c3f5e78d300e45f6b35d8e5b5cf7ce807631bd83a520254e343f008b"


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
    require('<script id="fv-signature-alignment-v1-js">' in text, "versioned script id missing")
    require("window.__fvSignatureAlignment" in text, "duplicate-init guard missing")

    require("querySelector('[data-fv-align-stage]')" in text, "real stage selector missing")
    require("pointerdown" in text and "mousedown" in text, "pointer and mouse drag support missing")
    require("keydown" in text and "ArrowLeft" in text and "ArrowRight" in text, "keyboard alignment missing")

    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"\beval\s*\(": "eval",
        r"localStorage|sessionStorage|document\.cookie": "unexpected persistence",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-signature-alignment-v1-js">\n(.*?)\n</script>', text, flags=re.S)
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
        r"// FV_SIGNATURE_ALIGNMENT_GATE_START\n(.*?)\n// FV_SIGNATURE_ALIGNMENT_GATE_END",
        js,
        flags=re.S,
    )
    require(gate_match is not None, "gate test seam missing")
    behavior = gate_match.group(1) + r"""
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
assert(fvSaShouldRun({hasStage:true,hasDivider:true,hasMapPanel:true,hasBadge:true})===true,'must run when all four real elements exist');
assert(fvSaShouldRun({hasStage:true,hasDivider:false,hasMapPanel:true,hasBadge:true})===false,'must not run without the real divider');
assert(fvSaShouldRun({hasStage:false,hasDivider:true,hasMapPanel:true,hasBadge:true})===false,'must not run without the real stage');
assert(fvSaShouldRun(null)===false,'must fail closed on missing context');
console.log('SIGNATURE ALIGNMENT BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("SIGNATURE ALIGNMENT BEHAVIOR: PASS" in proc.stdout, "behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    full_match = re.search(r'<script id="fv-signature-alignment-v1-js">\n(.*)\n</script>', text, flags=re.S)
    require(full_match is not None, "unable to extract full JavaScript")
    full_js = full_match.group(1)
    harness = r"""
const listeners = {};
const makeEl = () => {
  const el = {
    _attrs: {},
    _classes: new Set(),
    style: {},
    addEventListener(type, cb) { listeners[el._name + ':' + type] = cb; },
    setAttribute(k, v) { this._attrs[k] = String(v); },
    getAttribute(k) { return this._attrs[k]; },
    classList: {
      add: (c) => el._classes.add(c),
      remove: (c) => el._classes.delete(c),
      contains: (c) => el._classes.has(c),
    },
    focus() {},
    getBoundingClientRect() { return { left: 0, width: 100 }; },
  };
  return el;
};
const stage = makeEl(); stage._name = 'stage';
const divider = makeEl(); divider._name = 'divider';
const mapPanel = makeEl(); mapPanel._name = 'mapPanel';
const badge = makeEl(); badge._name = 'badge';
badge.setAttribute('data-revealed', '0');
stage.querySelector = (sel) => ({
  '[data-fv-align-divider]': divider,
  '.fv-align__panel--map': mapPanel,
  '[data-fv-align-badge]': badge,
}[sel] || null);
global.window = { addEventListener(type, cb) { listeners['window:' + type] = cb; } };
global.document = { querySelector: (sel) => (sel === '[data-fv-align-stage]' ? stage : null) };

""" + full_js + r"""

const assert=(condition,message)=>{if(!condition){throw new Error(message)}};

assert(stage.getAttribute('aria-valuenow')==='20','initial aria-valuenow must reflect the real starting position, not a value inside the aligned band');
assert(badge.getAttribute('data-revealed')==='0','badge must not be revealed before any user interaction');
assert(!stage.classList.contains('fv-align--locked'),'stage must not start locked before any user interaction');
assert(!/^aligned/.test(stage.getAttribute('aria-valuetext')),'initial aria-valuetext must not claim alignment before interaction');

const keydown = listeners['stage:keydown'];
assert(typeof keydown === 'function', 'keydown handler must be registered for keyboard alignment');
for (let i = 0; i < 7; i++) { keydown({ key: 'ArrowRight', preventDefault(){} }); }
assert(badge.getAttribute('data-revealed')==='1','badge must reveal once the user drags into the aligned band');
assert(stage.classList.contains('fv-align--locked'),'stage must lock once aligned by real interaction');
assert(/^aligned/.test(stage.getAttribute('aria-valuetext')),'aria-valuetext must update to report alignment once aligned');

for (let i = 0; i < 4; i++) { keydown({ key: 'ArrowRight', preventDefault(){} }); }
assert(badge.getAttribute('data-revealed')==='0','badge must clear once the user drags back out of the aligned band');
assert(!stage.classList.contains('fv-align--locked'),'stage must unlock once dragged out of the aligned band');
assert(!/^aligned/.test(stage.getAttribute('aria-valuetext')),'aria-valuetext must stop claiming alignment once out of the aligned band');

console.log('SIGNATURE ALIGNMENT INITIAL-STATE REGRESSION: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(harness)
        harness_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(harness_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"regression test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require(
            "SIGNATURE ALIGNMENT INITIAL-STATE REGRESSION: PASS" in proc.stdout,
            "regression test did not report PASS",
        )
    finally:
        harness_path.unlink(missing_ok=True)

    print(
        "PASS: Signature Alignment exact payload identity, real-element gating, pointer/mouse/"
        "keyboard drag interaction, no dependencies/network calls, JavaScript syntax, and "
        "initial-non-aligned-state regression verified"
    )


if __name__ == "__main__":
    main()
