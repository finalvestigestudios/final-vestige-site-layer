"""Dispatch R252: conservative, anonymous, non-submitting Jetpack action-route review.

A real browser DOM is required; this script never clicks, types, navigates, sends mail,
accepts consent, fetches a user profile, or calls a merchant. A visually bound POST
form is *not* a confirmed working subscribe path. JS-only Jetpack handling remains
UNKNOWN, not broken. Tested offline with Playwright Chromium.
"""
from __future__ import annotations

DOM_ROUTE_JS = r'''() => {
  const containers = [...document.querySelectorAll('.wp-block-jetpack-subscriptions,[role="dialog"]')];
  const isVisible = el => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility === 'visible' && Number(s.opacity) > 0 && r.width > 0 && r.height > 0;
  };
  const hasLabel = el => Boolean((el.getAttribute('aria-label') || '').trim()
      || (el.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean)
          .some(id => Boolean(document.getElementById(id)?.textContent?.trim()))
      || [...(el.labels || [])].some(x => Boolean(x.textContent?.trim())));
  const actionable = el => {
    if(!isVisible(el) || el.matches(':disabled') || el.closest('[inert]')) return false;
    if(getComputedStyle(el).pointerEvents === 'none') return false;
    const r = el.getBoundingClientRect();
    const x = Math.max(0, Math.min(innerWidth - 1, r.left + r.width/2));
    const y = Math.max(0, Math.min(innerHeight - 1, r.top + r.height/2));
    // Offscreen needs independent keyboard/scroll QA; cannot be called actionable here.
    if(r.bottom <= 0 || r.top >= innerHeight || r.right <= 0 || r.left >= innerWidth) return false;
    const hit = document.elementFromPoint(x,y);
    return Boolean(hit && (el === hit || el.contains(hit)));
  };
  const candidates=[];
  for(const box of containers) {
    const inputs = [...box.querySelectorAll('input[type="email"]')];
    for(const input of inputs) {
      const form=input.closest('form');
      const actionAttr=form?.getAttribute('action');
      let destination=null;
      try { destination = form && actionAttr ? new URL(actionAttr,document.baseURI) : null; } catch {}
      const origin = location.origin==='null' ? new URL(document.baseURI).origin : location.origin;
      const explicitSameOrigin=Boolean(destination && /^https?:$/.test(destination.protocol) && destination.origin === origin);
      const method=(form?.getAttribute('method') || 'get').trim().toLowerCase();
      const buttons=form ? [...form.querySelectorAll('button,input[type="submit"]')] : [];
      const submitButtons=buttons.filter(b => {
        const type=b.tagName === 'BUTTON' ? (b.getAttribute('type') || 'submit').toLowerCase() : 'submit';
        return type==='submit' && b.form===form;
      });
      const usable=submitButtons.filter(actionable);
      const formInBox=Boolean(form && box.contains(form));
      const fieldReady=isVisible(input) && !input.disabled && !input.readOnly && !input.closest('[inert]') && hasLabel(input);
      const postRoute=method==='post' && explicitSameOrigin;
      const strongVisual=Boolean(formInBox && fieldReady && usable.length && postRoute);
      const reasons=[];
      if(!formInBox)reasons.push('NO_FORM_BOUND_IN_BLOCK');
      if(!fieldReady)reasons.push('EMAIL_FIELD_NOT_VISIBLE_ENABLED_AND_LABELED');
      if(!usable.length)reasons.push('NO_VISIBLE_UNOBSTRUCTED_SUBMIT_BOUND_TO_THIS_FORM');
      if(method!=='post')reasons.push('GET_OR_UNKNOWN_FORM_METHOD');
      if(!explicitSameOrigin)reasons.push('EXPLICIT_SAME_ORIGIN_ACTION_NOT_OBSERVED');
      candidates.push({classification:strongVisual?'POST_FORM_VISUALLY_PLAUSIBLE_UNSUBMITTED':'ACTION_PATH_UNVERIFIED',
        reasons,fieldReady,formInBlock:formInBox,method,explicitSameOrigin,usableSubmitCount:usable.length,
        submitted:false,providerConfirmed:false});
    }
  }
  return {inspectionOnly:true,interactiveActionsPerformed:false,formSubmitted:false,
    confirmedSignup:false,welcomeReceived:false,merchantRightsVerified:false,
    visuallyPlausiblePostForm:candidates.some(x=>x.classification==='POST_FORM_VISUALLY_PLAUSIBLE_UNSUBMITTED'),
    candidates,unknownJsOnlyForms:containers.length>0 && candidates.length===0,
    releaseAuthorized:false};
}'''

async def inspect_route(page):
    """Inspect an already-loaded, anonymous page. No network, input, click or submit."""
    return await page.evaluate(DOM_ROUTE_JS)
