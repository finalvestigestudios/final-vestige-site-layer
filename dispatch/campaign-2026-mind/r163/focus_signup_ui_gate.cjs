'use strict';
/** Offline diagnostic for the Focus/Dispatch gift UI. No network, collection, or sending. */
function evaluateSignupUI({
  providerEmailStatus = 'unknown',
  providerConsentVerified = false,
  currentlySuppressed = false,
  welcomeReceiptVerified = false,
  postSignupUrl = '',
  hasSubscriberCssClass = false,
  clickObserved = false,
} = {}) {
  const statuses = ['subscribed', 'reader_only', 'pending', 'bounced', 'paused', 'unsubscribed', 'unknown'];
  if (!statuses.includes(providerEmailStatus)) throw new TypeError('Unrecognized provider status');
  const confirmed = providerEmailStatus === 'subscribed' && providerConsentVerified === true && currentlySuppressed === false;
  // The client must never mint confirmation from a URL, CSS class, or click.
  const display = confirmed ? 'VERIFIED_SUBSCRIBED' : 'CHECK_YOUR_EMAIL';
  return Object.freeze({
    display,
    canRecordConfirmedSignup: confirmed,
    canRecordDeliveredWelcome: confirmed && welcomeReceiptVerified === true,
    canClaimEmailReachable: false, // requires independent provider deliverability proof
    emailPreviewValidated: false,
    clientSignalsIgnored: Boolean(postSignupUrl || hasSubscriberCssClass || clickObserved),
    release: 'HOLD_UNSENT',
    commercialRelease: 'HOLD_MERCHANT',
  });
}
module.exports = { evaluateSignupUI };
