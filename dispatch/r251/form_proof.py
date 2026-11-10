"""R251 non-submitting DOM acceptance probe for existing Jetpack signup blocks.

Only accepts visible, accessible email controls paired to a usable submission
control IN THE SAME FORM. This is a narrower positive proof than R250.
Never types, submits, navigates, reads identities, or contacts a website.
"""
from __future__ import annotations

# Evaluated in the already-open anonymous browser page. Intentionally no network.
DOM_PROOF_JS = r"""() => {
  const containers = [...document.querySelectorAll('.wp-block-jetpack-subscriptions,[role="dialog"]')];
  const visible = el => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) > 0 && r.width > 0 && r.height > 0;
  };
  const label = el => {
    const aria = (el.getAttribute('aria-label') || '').trim();
    const ref = (el.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean)
      .map(id => document.getElementById(id)?.textContent?.trim() || '').join(' ').trim();
    const html = [...(el.labels || [])].map(e => e.textContent.trim()).join(' ').trim();
    return Boolean(aria || ref || html);
  };
  const outcomes = [];
  for (const box of containers) {
    for (const input of box.querySelectorAll('input[type=email]')) {
      const form = input.closest('form');
      const buttons = form ? [...form.querySelectorAll('button,input[type=submit]')] : [];
      const usable = buttons.filter(b => {
        const type = b.tagName === 'BUTTON' ? (b.getAttribute('type') || 'submit').toLowerCase() : 'submit';
        return type === 'submit' && visible(b) && !b.disabled && !b.closest('[inert]');
      });
      const sameContainer = form && box.contains(form) && form.contains(input);
      const hasIdentity = Boolean(form && (!form.action || new URL(form.action).origin === location.origin));
      const fieldReady = visible(input) && !input.disabled && !input.readOnly && !input.closest('[inert]');
      const passes = fieldReady && label(input) && sameContainer && usable.length > 0 && hasIdentity;
      outcomes.push({present:true,visible:visible(input),accessible_name:label(input),field_enabled:!input.disabled && !input.readOnly,
        form_bound:Boolean(sameContainer),same_origin_form:Boolean(hasIdentity),usable_submits:usable.length,
        classification:passes ? 'FORM_BINDING_VISUALLY_VALID_UNSUBMITTED':'FORM_BINDING_NOT_PROVEN'});
    }
  }
  return {visible_form_binding_proven:outcomes.some(x=>x.classification==='FORM_BINDING_VISUALLY_VALID_UNSUBMITTED'),
    candidates:outcomes,inspection_only:true,submitted:false,confirmed_signup:false,mail_received:false,revenue_verified:false};
}"""

async def inspect_browser_dom(page):
    """Inspect DOM; never activate controls or make network requests."""
    return await page.evaluate(DOM_PROOF_JS)
