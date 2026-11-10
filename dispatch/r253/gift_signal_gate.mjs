/** R253: read-only conversion boundary for Focus gift UI vs confirmed email consent.
 * Caller must not infer subscription from DOM, query, downloads or CTA clicks.
 * This library neither fetches subscriber identities nor transmits analytics.
 */
const NEGATIVE = new Set(['invalid_email','error','blocked_email','opted_out','blocked']);
export function queryWouldShowGift(url) {
  let value;
  try { value = new URL(url, 'https://finalvestige.com/focus/').searchParams.get('subscribe'); }
  catch { return false; }
  return Boolean(value) && !NEGATIVE.has(value);
}
export function assessFocusEvidence({ url='https://finalvestige.com/focus/',
  giftVisible=false, jetpackClass='', providerStatus='',
  providerTransitionVerified=false, emailConsentVerified=false,
  dedupeVerified=false }={}) {
  const uiQuery = queryWouldShowGift(url);
  const uiClass = /(?:^|\s)is-subscriber(?:\s|$)/.test(jetpackClass);
  const confirmed = providerTransitionVerified === true &&
    emailConsentVerified === true && dedupeVerified === true &&
    providerStatus === 'Subscribed';
  return Object.freeze({
    classification: confirmed?'PROVIDER_CONFIRMED':'UI_ONLY_NOT_CONFIRMED',
    queryWouldShowGift:uiQuery, classWouldShowGift:uiClass,
    giftVisible:Boolean(giftVisible), confirmed_signup:confirmed,
    mayCountLead:confirmed, maySendCampaign:false,
    merchantAuthorized:false, verifiedPaidOrder:false,
    netRevenue:null
  });
}
export function releaseBoundary(evidence={}) {
  const req = ['emailAffiliatePermission','merchantEarningURL','approvedBuyerGuide',
    'actualEmailEligibleAggregate','welcomeReceived','postalAddressReceived',
    'unsubscribeReceivedAndWorking','finalFounderSendApproval'];
  const unmet=req.filter(key=>evidence[key]!==true);
  return Object.freeze({ status:'HOLD_UNSENT',unmet,sendAuthorized:false,
    commercialIssue03:'HOLD_MERCHANT',commercialIssue05:'HOLD_MERCHANT'});
}
