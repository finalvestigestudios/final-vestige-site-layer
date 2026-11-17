/** R422: proof separation for Final Vestige's existing Jetpack list. No network or mail. */
const BAD = new Set(['invalid_email','error','blocked_email','opted_out','blocked']);
const TOKEN = /^[a-zA-Z0-9:_-]{8,128}$/;
export function focusGiftSurface({search='', className=''}={}) {
  let status = null;
  try { status = new URLSearchParams(search).get('subscribe'); } catch {}
  const queryUnlock = Boolean(status && !BAD.has(status));
  const classUnlock = /\bis-subscriber\b/.test(className);
  return {giftVisible: queryUnlock || classUnlock, confirmedSignup: false,
    proofLevel:'CLIENT_UI_ONLY', queryUnlock, classUnlock};
}
export function providerConfirmedSignup(ev={}, alreadySeen=[]) {
  // This validates an incoming, independently authenticated provider witness.
  // It never fetches records, sends mail, or manufactures evidence from a browser.
  if (!ev || typeof ev !== 'object' || Array.isArray(ev)) return {status:'HOLD', reason:'NO_PROVIDER_RECORD'};
  if (ev.provenance !== 'authenticated_provider_export') return {status:'HOLD', reason:'UNAUTHENTICATED_PROVENANCE'};
  if (ev.provider !== 'jetpack') return {status:'HOLD', reason:'UNRECOGNIZED_PROVIDER'};
  if (ev.subscriptionStatus !== 'confirmed') return {status:'HOLD', reason:'NOT_CONFIRMED'};
  if (ev.scope !== 'dispatch_newsletter') return {status:'HOLD', reason:'WRONG_CONSENT_SCOPE'};
  if (ev.suppressed !== false || ev.unsubscribed !== false) return {status:'HOLD', reason:'NOT_MAIL_ELIGIBLE'};
  if (!ev.providerAttested || ev.providerAttested !== true) return {status:'HOLD', reason:'NO_PROVIDER_ATTESTATION'};
  if (typeof ev.eventKey !== 'string' || !TOKEN.test(ev.eventKey)) return {status:'HOLD', reason:'INVALID_OPAQUE_KEY'};
  if (/[.@]/.test(ev.eventKey) || 'email' in ev || 'address' in ev) return {status:'HOLD', reason:'PII_NOT_ACCEPTED'};
  if (!Array.isArray(alreadySeen)) return {status:'HOLD', reason:'UNSAFE_DEDUP_CONTEXT'};
  if (alreadySeen.includes(ev.eventKey)) return {status:'NO_NEW_EVENT', reason:'DUPLICATE'};
  return {status:'ELIGIBLE_FOR_ONE_EVENT', eventName:'confirmed_signup', eventKey:ev.eventKey,
    caveat:'SYNTHETIC_ONLY_UNTIL_AUTHENTICATED_PROVIDER_WITNESS_RECORDED'};
}
export const PILOT_RELEASE = Object.freeze({issues:[1,2,3,4,5,6], editorial:[1,2,4,6], commercial:[3,5], all:'HOLD_UNSENT'});
