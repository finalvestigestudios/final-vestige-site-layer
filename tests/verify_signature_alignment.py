from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "signature-alignment-wp-block-v1.txt"
PAGE = ROOT / "homepage" / "page-6-home.blocks.html"
EXPECTED_BYTES = 4782
EXPECTED_SHA256 = "bffe859b660b49603271bdd8626de9c5c46b18e2f75bfa0d0497ac8943566be8"


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
    require("querySelector('[data-fv-align-reveal]')" in text, "real reveal-panel selector missing")
    require("[data-fv-align-reveal-trigger]" in text, "real reveal-trigger selector missing")
    require("[data-fv-align-status]" in text, "real status-region selector missing")
    require("pointerdown" in text and "mousedown" in text, "pointer and mouse drag support missing")
    require("keydown" in text and "ArrowLeft" in text and "ArrowRight" in text, "keyboard operation missing")
    require("'click'" in text or '"click"' in text, "reveal-trigger click handler missing")
    require("'inert' in document.createElement" in text, "feature-detected inert concealment missing")
    require("fact.inert" in text, "payload does not toggle inert on the concealed fact")

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
const full={hasStage:true,hasDivider:true,hasMapPanel:true,hasBadge:true,hasReveal:true,hasFact:true,hasTrigger:true,hasStatus:true};
assert(fvSaShouldRun(full)===true,'must run when all real elements exist');
assert(fvSaShouldRun({...full,hasDivider:false})===false,'must not run without the real divider');
assert(fvSaShouldRun({...full,hasStage:false})===false,'must not run without the real stage');
assert(fvSaShouldRun({...full,hasReveal:false})===false,'must not run without the real reveal panel');
assert(fvSaShouldRun({...full,hasFact:false})===false,'must not run without the real fact element');
assert(fvSaShouldRun({...full,hasTrigger:false})===false,'must not run without the real reveal-trigger button');
assert(fvSaShouldRun({...full,hasStatus:false})===false,'must not run without the real status region');
assert(fvSaShouldRun(null)===false,'must fail closed on missing context');
console.log('SIGNATURE ALIGNMENT GATE BEHAVIOR: PASS');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(behavior)
        behavior_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(behavior_path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"gate behavior test failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require("SIGNATURE ALIGNMENT GATE BEHAVIOR: PASS" in proc.stdout, "gate behavior test did not report PASS")
    finally:
        behavior_path.unlink(missing_ok=True)

    full_match = re.search(r'<script id="fv-signature-alignment-v1-js">\n(.*)\n</script>', text, flags=re.S)
    require(full_match is not None, "unable to extract full JavaScript")
    full_js = full_match.group(1)

    dom_harness = r"""
const listeners = {};
const makeEl = (name) => {
  const el = {
    _name: name,
    _attrs: {},
    _classes: new Set(),
    style: {},
    disabled: false,
    inert: false,
    textContent: '',
    _focusCalls: 0,
    addEventListener(type, cb) { listeners[el._name + ':' + type] = cb; },
    setAttribute(k, v) { this._attrs[k] = String(v); },
    getAttribute(k) { return this._attrs[k]; },
    removeAttribute(k) { delete this._attrs[k]; },
    classList: {
      add: (c) => el._classes.add(c),
      remove: (c) => el._classes.delete(c),
      contains: (c) => el._classes.has(c),
    },
    focus() { el._focusCalls++; },
    getBoundingClientRect() { return { left: 0, width: 100 }; },
  };
  return el;
};
function buildDom(omit) {
  omit = omit || {};
  const stage = makeEl('stage');
  const divider = omit.divider ? null : makeEl('divider');
  const mapPanel = omit.mapPanel ? null : makeEl('mapPanel');
  const diagramPanel = omit.mapPanel ? null : makeEl('diagramPanel');
  const badge = omit.badge ? null : makeEl('badge');
  badge && badge.setAttribute('data-revealed', '0');
  const reveal = omit.reveal ? null : makeEl('reveal');
  const fact = omit.fact ? null : makeEl('fact');
  const trigger = omit.trigger ? null : makeEl('trigger');
  trigger && (trigger.textContent = 'Show the connection');
  const status = omit.status ? null : makeEl('status');
  stage.querySelector = (sel) => ({
    '[data-fv-align-divider]': divider,
    '.fv-align__panel--map': mapPanel,
    '[data-fv-align-badge]': badge,
  }[sel] || null);
  stage.querySelectorAll = (sel) => (sel === '.fv-align__panel' ? [mapPanel, diagramPanel].filter(Boolean) : []);
  reveal && (reveal.querySelector = (sel) => ({
    '[data-fv-align-fact]': fact,
    '[data-fv-align-reveal-trigger]': trigger,
  }[sel] || null));
  global.window = { addEventListener(type, cb) { listeners['window:' + type] = cb; }, __fvSignatureAlignment: false };
  global.document = {
    createElement: omit.noInertSupport ? () => ({}) : () => ({ inert: false }),
    querySelector: (sel) => ({
      '[data-fv-align-stage]': stage,
      '[data-fv-align-reveal]': reveal,
      '[data-fv-align-status]': status,
      '[data-fv-align-fact]': fact,
      '[data-fv-align-reveal-trigger]': trigger,
    }[sel] || null),
  };
  return { stage, divider, mapPanel, diagramPanel, badge, reveal, fact, trigger, status };
}
const assert=(condition,message)=>{if(!condition){throw new Error(message)}};
"""

    scenario_full_init = dom_harness + "const dom = buildDom();\n" + full_js + r"""
assert(dom.reveal.classList.contains('fv-align__reveal--pending'),'successful init must mark the reveal panel pending (concealed) — this is the only mechanism that conceals it, so a no-JS or failed-init page is never concealed');
assert(dom.badge.getAttribute('data-revealed')==='0','badge must not be revealed before any interaction');
assert(!dom.stage.classList.contains('fv-align--locked'),'stage must not be locked before any interaction');
assert(dom.trigger.disabled===false,'reveal-trigger button must start enabled');
assert(!dom.status.textContent,'status live region must be empty before any discovery');
assert(dom.fact.inert===true,'the concealed fact (and its nested link) must be inert — unfocusable and non-interactive — before discovery');
assert(dom.stage.getAttribute('aria-valuenow')==='20','initial position must be the real, documented starting point (20), not inside any special band');
assert(dom.stage.getAttribute('role')==='slider','successful init must apply slider semantics via JS (never baked into static markup, see the no-JS checks below)');
assert(dom.stage.getAttribute('tabindex')==='0','successful init must make the now-functional stage keyboard-focusable via JS');
assert(dom.stage.getAttribute('aria-describedby')==='fv-align-desc','stage must reference the always-present description of both documents so their content reaches assistive technology despite being nested inside an opaque slider widget');
assert(dom.mapPanel.getAttribute('aria-hidden')==='true' && dom.diagramPanel.getAttribute('aria-hidden')==='true','both nested image panels must be aria-hidden once the slider role is active — their content is conveyed via aria-describedby/aria-valuetext instead, per WAI-ARIA slider authoring practice');

const keydown = listeners['stage:keydown'];
assert(typeof keydown === 'function', 'keydown handler must be registered for keyboard operation');

for (let i = 0; i < 1; i++) { keydown({ key: 'ArrowRight', preventDefault(){} }); }
for (let i = 0; i < 1; i++) { keydown({ key: 'ArrowLeft', preventDefault(){} }); }
assert(dom.badge.getAttribute('data-revealed')==='0','small back-and-forth movement near the start must NOT trigger discovery (return-to-initial-state: insufficient exploration stays undiscovered)');

for (let i = 0; i < 10; i++) { keydown({ key: 'ArrowLeft', preventDefault(){} }); }
assert(Number(dom.stage.getAttribute('aria-valuenow'))<=15,'must be able to reach the low extreme via keyboard');
assert(dom.badge.getAttribute('data-revealed')==='0','visiting only the low extreme must not yet trigger discovery');

for (let i = 0; i < 30; i++) { keydown({ key: 'ArrowRight', preventDefault(){} }); }
assert(Number(dom.stage.getAttribute('aria-valuenow'))>=85,'must be able to reach the high extreme via keyboard');
assert(dom.badge.getAttribute('data-revealed')==='1','visiting BOTH extremes (genuine exploration of both documents) must trigger discovery');
assert(dom.stage.classList.contains('fv-align--locked'),'stage must lock once the connection is found');
assert(dom.reveal.classList.contains('fv-align--found'),'reveal panel must carry the found state so CSS can un-conceal the real fact text — this is what makes the SUBSTANTIVE FINDING visible, not merely the badge');
assert(dom.trigger.disabled===true,'reveal-trigger button should reflect the found state once discovery already happened');
assert(dom.status.textContent.length>0,'accessible status live region must announce the discovery to assistive technology');
assert(/connection found/i.test(dom.status.textContent),'status announcement must describe the discovery, not just say a generic value changed');
assert(dom.fact.inert===false,'the fact (and its link) must become focusable/interactive again immediately after discovery');
assert(dom.fact._focusCalls===0,'keyboard/slider-driven discovery must NOT move focus away from the stage — the brief requires retaining slider focus and only announcing via the live region');
console.log('SIGNATURE ALIGNMENT DISCOVERY (KEYBOARD) REGRESSION: PASS');
"""
    _run_node_scenario(scenario_full_init, "SIGNATURE ALIGNMENT DISCOVERY (KEYBOARD) REGRESSION: PASS")

    scenario_pointer = dom_harness + "const dom = buildDom();\n" + full_js + r"""
const onPointerDown = listeners['stage:pointerdown'] || listeners['stage:mousedown'];
assert(typeof onPointerDown === 'function', 'pointer/mouse down handler must be registered');
const onMove = listeners['window:pointermove'] || listeners['window:mousemove'];
const onUp = listeners['window:pointerup'] || listeners['window:mouseup'];
assert(typeof onMove === 'function' && typeof onUp === 'function', 'pointer/mouse move and up handlers must be registered');

assert(dom.fact.inert===true,'fact must be inert before any pointer interaction');
onPointerDown({ clientX: 5, cancelable: true, preventDefault(){} });
onMove({ clientX: 97 });
onUp();
assert(dom.badge.getAttribute('data-revealed')==='1','a real pointer drag that visits both extremes must trigger discovery exactly like keyboard does');
assert(dom.fact.inert===false,'fact must become interactive again after pointer-driven discovery');
console.log('SIGNATURE ALIGNMENT DISCOVERY (POINTER) REGRESSION: PASS');
"""
    _run_node_scenario(scenario_pointer, "SIGNATURE ALIGNMENT DISCOVERY (POINTER) REGRESSION: PASS")

    scenario_button = dom_harness + "const dom = buildDom();\n" + full_js + r"""
const onClick = listeners['trigger:click'];
assert(typeof onClick === 'function', 'reveal-trigger button must have a click handler — the understandable, non-drag alternative required for accessibility');
assert(dom.badge.getAttribute('data-revealed')==='0','must not be revealed before the button is used');
assert(dom.fact.inert===true,'fact must be inert before the button is used');
onClick();
assert(dom.badge.getAttribute('data-revealed')==='1','clicking the reveal-trigger button must independently trigger the same discovery as dragging, with zero prior drag/keyboard interaction');
assert(dom.reveal.classList.contains('fv-align--found'),'button-triggered discovery must also un-conceal the real fact text');
assert(dom.status.textContent.length>0,'button-triggered discovery must also announce via the accessible status region');
assert(dom.fact.inert===false,'fact must become interactive/focusable immediately after button-triggered discovery');
assert(dom.fact._focusCalls===1,'activating the reveal-trigger button must move focus to the revealed fact exactly once — a predictable destination, not a stranded or lost focus');
onClick();
assert(dom.fact._focusCalls===1,'an already-completed discovery must not re-trigger (no duplicate focus moves or re-announcements) if the handler fires again');
console.log('SIGNATURE ALIGNMENT DISCOVERY (BUTTON ALTERNATIVE) REGRESSION: PASS');
"""
    _run_node_scenario(scenario_button, "SIGNATURE ALIGNMENT DISCOVERY (BUTTON ALTERNATIVE) REGRESSION: PASS")

    scenario_no_inert_support = dom_harness + "const dom = buildDom({noInertSupport:true});\n" + full_js + r"""
assert(dom.reveal.classList.contains('fv-align__reveal--pending')===false,'when the browser does not support inert, the payload must not attempt CSS-only blur concealment either — that would re-introduce the exact defect (a visually illegible but still keyboard-focusable link) this fix exists to prevent');
assert(dom.fact.inert===false || dom.fact.inert===undefined,'fact must never be left inert when inert support could not be confirmed');
assert(dom.stage.getAttribute('role')===undefined,'without confirmed inert support, the payload must not claim slider semantics either — fall back fully to the plain, always-readable static presentation');
assert(dom.stage.getAttribute('tabindex')===undefined,'stage must not be made keyboard-focusable as a slider when the enhancement is not actually safe to run');
assert(listeners['stage:keydown']===undefined,'no interactive wiring at all should happen in the unsupported-inert fallback — it is equivalent to the no-JS case, not a degraded-but-active slider');
console.log('SIGNATURE ALIGNMENT FAIL-CLOSED (NO CONCEALMENT WHEN INERT IS UNSUPPORTED) REGRESSION: PASS');
"""
    _run_node_scenario(
        scenario_no_inert_support,
        "SIGNATURE ALIGNMENT FAIL-CLOSED (NO CONCEALMENT WHEN INERT IS UNSUPPORTED) REGRESSION: PASS",
    )

    scenario_midway_failure = dom_harness + r"""
const dom = buildDom();
dom.stage.addEventListener = () => { throw new Error('simulated failure after concealment began'); };
""" + full_js + r"""
assert(window.__fvSignatureAlignment===false,'a midway failure must reset the duplicate-init guard so a later attempt is not permanently blocked');
assert(dom.fact.inert===false,'a failure that happens AFTER concealment began must not leave the fact permanently inert — point 6 of the brief requires a readable, accessible fallback rather than leaving the evidence concealed');
assert(!dom.reveal.classList.contains('fv-align__reveal--pending'),'a midway failure must also clear the pending/concealed visual class so sighted users are not left with a permanently blurred, unreadable fact either');
assert(dom.stage.getAttribute('role')===undefined,'a midway failure must also strip the role=slider claim — a non-functional element (no listeners survived the crash) must not advertise interactive slider semantics');
assert(dom.stage.getAttribute('tabindex')===undefined,'a midway failure must also strip tabindex so the now-nonfunctional stage is not a dead Tab stop');
assert(dom.stage.getAttribute('aria-describedby')===undefined,'a midway failure must also remove aria-describedby, which only makes sense paired with the slider role');
assert(dom.mapPanel.getAttribute('aria-hidden')===undefined && dom.diagramPanel.getAttribute('aria-hidden')===undefined,'a midway failure must also un-hide the image panels from assistive technology, since without a working slider their content is no longer redundant with anything');
console.log('SIGNATURE ALIGNMENT FAIL-CLOSED (MIDWAY FAILURE LEAVES NO RESIDUAL CONCEALMENT) REGRESSION: PASS');
"""
    _run_node_scenario(
        scenario_midway_failure,
        "SIGNATURE ALIGNMENT FAIL-CLOSED (MIDWAY FAILURE LEAVES NO RESIDUAL CONCEALMENT) REGRESSION: PASS",
    )

    scenario_missing = dom_harness + "const dom = buildDom({trigger:true});\n" + full_js + r"""
assert(dom.reveal.classList.contains('fv-align__reveal--pending')===false,'when a required real element is missing (simulating a failed/partial init, the same condition a no-JS page is in), the payload must no-op and never conceal the real fact text — it must stay visible');
assert(dom.stage.getAttribute('role')===undefined,'a missing-element no-op must never advertise slider semantics on a non-functional element');
assert(dom.stage.getAttribute('tabindex')===undefined,'a missing-element no-op must never add the stage to the keyboard Tab order');
console.log('SIGNATURE ALIGNMENT FAIL-CLOSED (NO CONCEALMENT ON MISSING ELEMENT) REGRESSION: PASS');
"""
    _run_node_scenario(
        scenario_missing, "SIGNATURE ALIGNMENT FAIL-CLOSED (NO CONCEALMENT ON MISSING ELEMENT) REGRESSION: PASS"
    )

    # No-JS / static-content checks against the real page markup (not the payload):
    # the fact text, the real dates/sources, and the aria-live status region's static
    # defaults must all be present as plain HTML so they work with JavaScript disabled.
    # Slider role/tabindex/aria-value* and the panels' aria-hidden must NOT be baked into
    # static markup at all — a nonfunctional comparison stage must not advertise interactive
    # slider semantics or sit in the keyboard Tab order when JS hasn't (or can't) wire it up.
    page_text = PAGE.read_text(encoding="utf-8")
    require('data-fv-align-fact' in page_text, "page markup missing the real fact element")
    require("September" in page_text and "1918" in page_text, "page markup missing the real sourced dates in the fact text")
    require('role="status" aria-live="polite" data-fv-align-status' in page_text, "page markup missing the accessible live-status region")
    require(
        "isn't a record of the wreck" in page_text,
        "fact text must state plainly that the map is not evidence of the wreck itself (avoids implying a literal overlap)",
    )
    stage_tag_match = re.search(r'<div class="fv-align__stage"[^>]*>', page_text)
    require(stage_tag_match is not None, "could not locate the static stage div in page markup")
    stage_tag = stage_tag_match.group(0)
    require(
        stage_tag == '<div class="fv-align__stage" data-fv-align-stage>',
        f"the static stage div must carry no role/tabindex/aria-value* attributes at all — those "
        f"must be added by JS only on successful init — but found: {stage_tag!r}",
    )
    require(
        'id="fv-align-desc"' in page_text and "fv-align__desc" in page_text,
        "page markup missing the always-present visually-hidden description of both documents "
        "(aria-describedby target) that keeps their content reachable by assistive technology "
        "despite being nested inside an opaque slider widget once JS applies the role",
    )
    require(
        "NYPL Digital Collections" in page_text and "Final Vestige reconstruction" in page_text,
        "the fv-align-desc description must draw on the real, already-used source captions, not invented text",
    )

    # The payload's JS-only ARIA/role application and the ARIA-slider-content fix must be present
    # as real code, not just asserted in prose.
    require("stage.setAttribute('role','slider')" in text, "payload does not apply role=slider via JS")
    require("stage.setAttribute('tabindex','0')" in text, "payload does not apply tabindex via JS")
    require("stage.setAttribute('aria-describedby','fv-align-desc')" in text, "payload does not wire aria-describedby to the real description element")
    require("setAttribute('aria-hidden','true')" in text, "payload does not hide the nested image panels from assistive technology once the slider role is active")
    require("if(!supportsInert)return;" in text, "payload does not fall back to the fully readable static presentation when inert support cannot be confirmed")

    print(
        "PASS: Signature Alignment exact payload identity, real-element gating, pointer/mouse/"
        "keyboard/button interaction, genuine-discovery gating (both extremes or the explicit "
        "alternative control, not a decorative badge), inert-based concealment of the unrevealed "
        "fact/link (not focusable, not interactive, before discovery), slider role/tabindex/"
        "aria-value* applied by JS only (never baked into static markup, so a nonfunctional "
        "comparison stage never advertises interactive semantics), aria-describedby wiring both "
        "nested images' real descriptions to an always-present element despite their panels being "
        "aria-hidden inside the opaque slider widget, predictable focus movement on button-"
        "triggered discovery vs. retained stage focus on slider-triggered discovery, accessible "
        "status announcement, fail-closed no-concealment-without-JS, no-concealment-when-inert-"
        "is-unsupported, and no-residual-concealment-on-midway-failure, no dependencies/network "
        "calls, and JavaScript syntax verified. A separate real-browser keyboard/focus test lives "
        "in tests/verify_signature_alignment_keyboard_browser.py (not part of the CI gate; run "
        "manually wherever Playwright is available)."
    )


def _run_node_scenario(script: str, expect_marker: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script)
        path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(path)], capture_output=True, text=True)
        require(proc.returncode == 0, f"regression scenario failed: {proc.stderr.strip() or proc.stdout.strip()}")
        require(expect_marker in proc.stdout, f"regression scenario did not report expected marker: {expect_marker}")
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
