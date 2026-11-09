#!/usr/bin/env python3
"""Read-only, no-PII check for a usable Jetpack email + submit-button PAIR.

The existing geometry check establishes input visibility, not whether a visitor
can submit anything. This independent gate requires a *same-form*, usable,
accessible action. Does not fill or submit, and cannot confirm actual signup.
"""

PAIR_PROBE_JS = r'''() => {
  const viewport = {w: document.documentElement.clientWidth || innerWidth,
                    h: document.documentElement.clientHeight || innerHeight};
  const normalize = s => (s || '').trim();
  const styleReady = el => {
    let opacity = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const st = getComputedStyle(n);
      const a = Number(st.opacity);
      if (!Number.isFinite(a) || st.display === 'none' ||
          st.visibility === 'hidden' || st.visibility === 'collapse' ||
          st.pointerEvents === 'none' || n.hasAttribute('inert') ||
          n.getAttribute('aria-hidden') === 'true') return false;
      opacity *= a;
      if (opacity <= 0.05) return false;
    }
    return true;
  };
  const accessibleName = el => {
    const direct = normalize(el.getAttribute('aria-label'));
    if (direct) return true;
    const names = normalize(el.getAttribute('aria-labelledby')).split(/\s+/).filter(Boolean);
    if (names.length && names.every(id => normalize(document.getElementById(id)?.textContent))) return true;
    if ([...el.labels || []].some(n => normalize(n.textContent) && !n.closest('[aria-hidden="true"],[inert]'))) return true;
    if (el.tagName === 'BUTTON') return !!normalize(el.innerText || el.textContent);
    if (el.type === 'submit') return !!normalize(el.value);
    return false;
  };
  const operable = el => {
    const b = el.getBoundingClientRect();
    if (!styleReady(el) || el.matches(':disabled') || el.tabIndex < 0 ||
        ('readOnly' in el && el.readOnly) || b.width < 24 || b.height < 24 ||
        b.left < -2 || b.top < -2 || b.right > viewport.w + 2 || b.bottom > viewport.h + 2 ||
        !accessibleName(el)) return false;
    for (let n = el.parentElement; n; n = n.parentElement) {
      const s = getComputedStyle(n), r = n.getBoundingClientRect();
      if (/^(hidden|clip|auto|scroll|overlay)$/.test(s.overflowX) &&
          (b.left < r.left - 2 || b.right > r.right + 2)) return false;
      if (/^(hidden|clip|auto|scroll|overlay)$/.test(s.overflowY) &&
          (b.top < r.top - 2 || b.bottom > r.bottom + 2)) return false;
    }
    for (const y of [0.15, 0.5, 0.85]) for (const x of [0.15, 0.5, 0.85]) {
      const at = document.elementFromPoint(b.left + x*b.width, b.top + y*b.height);
      if (!(at && (at === el || el.contains(at)))) return false;
    }
    return true;
  };
  const entries = [];
  for (const field of [...document.querySelectorAll('.wp-block-jetpack-subscriptions input[type="email"]')].slice(0,10)) {
    // An unrelated form's submit button must never make this field count as ready.
    const form = field.form;
    const buttons = form ? [...form.querySelectorAll('button, input[type="submit"]')].filter(b =>
      b.form === form && (b.type || 'submit').toLowerCase() === 'submit') : [];
    const fieldUsable = operable(field);
    const buttonUsable = buttons.some(operable);
    entries.push({same_form_submit_count:buttons.length, input_usable:fieldUsable,
                  submit_usable:buttonUsable, complete_pair:fieldUsable && buttonUsable});
  }
  return entries;
}'''


async def inspect_signup_pair(page):
    """No form values or personal information ever read or returned."""
    entries = []
    frame_errors = 0
    nested_fields_unverified = 0
    for frame in page.frames:
        try:
            rows = await frame.evaluate(PAIR_PROBE_JS)
            if frame == page.main_frame:
                entries.extend(rows)
            else:
                nested_fields_unverified += len(rows)
        except Exception:
            frame_errors += 1
    return {
        'main_document_pairs_ready': sum(bool(x['complete_pair']) for x in entries),
        'main_document_inputs_checked': len(entries),
        'nested_frame_inputs_unverified': nested_fields_unverified,
        'frame_errors': frame_errors,
        'entries': entries,
        'scope': 'OFFLINE_OR_READ_ONLY_BROWSER_ACTIONABILITY_NOT_SUBSCRIPTION_VERIFICATION',
    }
