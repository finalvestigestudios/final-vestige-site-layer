#!/usr/bin/env python3
"""Read-only viewport geometry probe for rendered Jetpack email opt-in.

This is a guest-browser observation, NOT a subscriber confirmation or field CWV
measurement. No form content is read, entered, submitted or logged.
"""
from typing import Any

PROBE_JS = r"""() => {
  const inputs = [...document.querySelectorAll('.wp-block-jetpack-subscriptions input[type="email"]')];
  return inputs.slice(0, 10).map(el => {
    const box = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    const opacity = Number(style.opacity);
    const visuallyPresent = box.width > 0 && box.height > 0 &&
      style.display !== 'none' && style.visibility !== 'hidden' &&
      Number.isFinite(opacity) && opacity > 0.05;
    const cx = Math.max(0, Math.min(innerWidth - 1, box.left + box.width / 2));
    const cy = Math.max(0, Math.min(innerHeight - 1, box.top + box.height / 2));
    const inViewport = visuallyPresent && box.left >= -2 && box.right <= innerWidth + 2 &&
      box.top >= -2 && box.bottom <= innerHeight + 2;
    const atPoint = inViewport ? document.elementFromPoint(cx, cy) : null;
    const unobstructed = inViewport && !!atPoint && (atPoint === el || el.contains(atPoint));
    const associatedLabels = (el.labels ? [...el.labels] : []).some(x => x.textContent.trim().length > 0);
    const hasAriaLabel = !!(el.getAttribute('aria-label') || '').trim();
    const labelledby = (el.getAttribute('aria-labelledby') || '').trim().split(/\s+/).filter(Boolean);
    const hasAriaLabelledby = labelledby.length > 0 && labelledby.every(id =>
      document.getElementById(id)?.textContent?.trim());
    const accessibleNamePresent = !!(associatedLabels || hasAriaLabel || hasAriaLabelledby);
    return {
      // Geometry only; never include entered values, placeholder text, name or email.
      visible_by_style: visuallyPresent,
      in_first_viewport: inViewport,
      unobstructed_at_center: unobstructed,
      accessible_name_markup: accessibleNamePresent,
      enabled: !el.disabled,
      bounds: {left: Math.round(box.left), top: Math.round(box.top),
               width: Math.round(box.width), height: Math.round(box.height)},
      // A link hidden by an overlay is not equivalent to a usable input.
      obstruction_detected: inViewport && !unobstructed
    };
  });
}"""


async def inspect_optin_viewport(page: Any) -> dict:
    """Inspect all same-origin and nested guest frames without interacting."""
    fields = []
    frame_errors = 0
    for frame in page.frames:
        try:
            rows = await frame.evaluate(PROBE_JS)
            if isinstance(rows, list):
                fields.extend(rows)
        except Exception:  # Cross-origin, detached frame, navigation: fail closed.
            frame_errors += 1
    return {
        "fields_seen": len(fields),
        "visible_by_style": sum(bool(x["visible_by_style"]) for x in fields),
        "in_first_viewport": sum(bool(x["in_first_viewport"]) for x in fields),
        "unobstructed_first_viewport": sum(bool(x["unobstructed_at_center"]) for x in fields),
        "labeled_unobstructed_first_viewport": sum(
            bool(x["unobstructed_at_center"] and x["accessible_name_markup"] and x["enabled"])
            for x in fields),
        "frame_errors": frame_errors,
        "fields": fields,
        "scope": "DOM_GEOMETRY_ONLY_NOT_VERIFIED_SIGNUP",
    }
