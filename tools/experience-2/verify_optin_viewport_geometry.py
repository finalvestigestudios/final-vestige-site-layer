#!/usr/bin/env python3
"""Read-only, fail-closed mobile opt-in geometry and operability probe.

Only measures anonymous DOM structure and geometry. This is NOT Jetpack
confirmation, a conversion metric, a WCAG audit, or a Lighthouse measurement.
Never reads, fills or submits email values or forms.
"""
from typing import Any

PROBE_JS = r"""() => {
  const inputs = [...document.querySelectorAll('.wp-block-jetpack-subscriptions input[type="email"]')];
  const viewport = {w: document.documentElement.clientWidth || innerWidth,
                    h: document.documentElement.clientHeight || innerHeight};
  const noPointer = node => getComputedStyle(node).pointerEvents === 'none';
  const eligibleAncestors = el => {
    let opacity = 1;
    for (let node = el; node && node.nodeType === 1; node = node.parentElement) {
      const st = getComputedStyle(node);
      const alpha = Number(st.opacity);
      if (st.display === 'none' || st.visibility === 'hidden' || st.visibility === 'collapse' ||
          !Number.isFinite(alpha) || noPointer(node)) return false;
      opacity *= alpha;
      if (opacity <= 0.05 || node.hasAttribute('inert') ||
          (node.getAttribute('aria-hidden') || '').toLowerCase() === 'true') return false;
    }
    return true;
  };
  const notClipped = (el, box) => {
    // An element's own client rect is insufficient when a parent clips half of it.
    for (let node = el.parentElement; node; node = node.parentElement) {
      const st = getComputedStyle(node);
      const b = node.getBoundingClientRect();
      if (/^(hidden|clip|auto|scroll|overlay)$/.test(st.overflowX) &&
          (box.left < b.left - 2 || box.right > b.right + 2)) return false;
      if (/^(hidden|clip|auto|scroll|overlay)$/.test(st.overflowY) &&
          (box.top < b.top - 2 || box.bottom > b.bottom + 2)) return false;
    }
    return true;
  };
  return inputs.slice(0, 10).map(el => {
    const box = el.getBoundingClientRect();
    const visuallyPresent = box.width > 0 && box.height > 0 && eligibleAncestors(el);
    const inViewport = visuallyPresent && box.left >= -2 && box.right <= viewport.w + 2 &&
      box.top >= -2 && box.bottom <= viewport.h + 2 && notClipped(el, box);
    const samples = [];
    if (inViewport) for (const fy of [0.15, 0.5, 0.85])
      for (const fx of [0.15, 0.5, 0.85]) {
        const x = Math.max(0, Math.min(viewport.w - 1, box.left + fx * box.width));
        const y = Math.max(0, Math.min(viewport.h - 1, box.top + fy * box.height));
        const top = document.elementFromPoint(x, y);
        samples.push(!!top && (top === el || el.contains(top)));
      }
    // A lone uncovered center cannot certify an input mostly covered by a popup.
    const unobstructed = inViewport && samples.length === 9 && samples.every(Boolean);
    const associatedLabels = (el.labels ? [...el.labels] : []).some(label =>
      !!label.textContent.trim() && !label.closest('[aria-hidden="true"], [inert]'));
    const hasAriaLabel = !!(el.getAttribute('aria-label') || '').trim();
    const labelledby = (el.getAttribute('aria-labelledby') || '').trim().split(/\s+/).filter(Boolean);
    const hasAriaLabelledby = labelledby.length > 0 && labelledby.every(id =>
      document.getElementById(id)?.textContent?.trim());
    // :disabled includes the disabled fieldset rule, unlike el.disabled alone.
    const enabled = !el.matches(':disabled') && !el.readOnly && el.tabIndex >= 0;
    return {
      visible_by_style: visuallyPresent,
      in_first_viewport: inViewport,
      unobstructed_at_center: !!samples[4], // Backward-compatible diagnostic only.
      unobstructed_first_viewport: unobstructed,
      unobstructed_sample_count: samples.filter(Boolean).length,
      accessible_name_markup: !!(associatedLabels || hasAriaLabel || hasAriaLabelledby),
      enabled,
      bounds: {left: Math.round(box.left), top: Math.round(box.top),
               width: Math.round(box.width), height: Math.round(box.height)},
      obstruction_detected: inViewport && !unobstructed
      // Never return field values, names, placeholder text, email or labels.
    };
  });
}"""


async def inspect_optin_viewport(page: Any) -> dict:
    """Inspect guest DOM without writes; embedded frames are diagnostic only.

    A field visible inside a nested frame can be wholly hidden by its parent
    iframe. Until parent-frame occlusion is independently checked, it cannot
    establish first-viewport accessibility on the main page.
    """
    fields = []
    frame_errors = 0
    embedded_frame_fields = 0
    for frame in page.frames:
        try:
            rows = await frame.evaluate(PROBE_JS)
            if isinstance(rows, list):
                is_main_frame = frame == page.main_frame
                for row in rows:
                    row["in_main_document"] = is_main_frame
                    fields.append(row)
                if not is_main_frame:
                    embedded_frame_fields += len(rows)
        except Exception:  # Detached/cross-origin/corrupt frame: no positive evidence.
            frame_errors += 1
    admitted = [x for x in fields if x["in_main_document"]]
    return {
        "fields_seen": len(fields),
        "main_document_fields": len(admitted),
        "embedded_frame_fields_unverified": embedded_frame_fields,
        "visible_by_style": sum(bool(x["visible_by_style"]) for x in admitted),
        "in_first_viewport": sum(bool(x["in_first_viewport"]) for x in admitted),
        "unobstructed_first_viewport": sum(bool(x["unobstructed_first_viewport"]) for x in admitted),
        "labeled_unobstructed_first_viewport": sum(
            bool(x["unobstructed_first_viewport"] and x["accessible_name_markup"] and x["enabled"])
            for x in admitted),
        "frame_errors": frame_errors,
        "fields": fields,
        "scope": "ANONYMOUS_DOM_GEOMETRY_ONLY_NOT_VERIFIED_SIGNUP_OR_WCAG",
    }
