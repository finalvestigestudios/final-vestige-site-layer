'use strict';
/**
 * Dispatch R161: OFFLINE, read-only subscriber-to-customer reviewer.
 * No sender, network request, CRM writes, tracking, or subscription events.
 * All inputs are permission attestations, NEVER individual subscriber records.
 * Issue 03 is the sole primary commercial hypothesis; issue 05 remains separate.
 */
const EVIDENCE = Object.freeze([
  'provider_email_eligibility', 'provider_confirmed_transition',
  'welcome_received', 'fieldbook_retrieved', 'native_jetpack_preview',
  'fv_postal_verified', 'unsubscribe_verified', 'approved_partner_account',
  'explicit_email_permission', 'approved_earning_link',
  'live_vetted_warmup_guide', 'current_product_terms',
  'adjacent_commercial_disclosure', 'founder_final_campaign_approval'
]);
const PII_RE = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b/i;
function review(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw Error('Object required');
  const keys = Object.keys(input).sort();
  if (keys.some(k => !EVIDENCE.includes(k))) throw Error('Unknown input key — no PII or added trust flags');
  if (PII_RE.test(JSON.stringify(input))) throw Error('Reject subscriber PII');
  if (keys.some(k => typeof input[k] !== 'boolean' && input[k] !== null)) throw Error('Evidence is true, false, or null only');
  const has = k => input[k] === true;
  const needed = xs => xs.filter(k => !has(k));
  const consent = needed(['provider_email_eligibility','provider_confirmed_transition']);
  const fulfillment = needed(['welcome_received','fieldbook_retrieved']);
  const rendering = needed(['native_jetpack_preview','fv_postal_verified','unsubscribe_verified']);
  const merchant = needed(['approved_partner_account','explicit_email_permission','approved_earning_link','live_vetted_warmup_guide','current_product_terms','adjacent_commercial_disclosure']);
  const approval = needed(['founder_final_campaign_approval']);
  let next;
  if(consent.length) next='VERIFY_PROVIDER_CONSENT_ELIGIBILITY';
  else if(fulfillment.length) next='VERIFY_RECEIVED_WELCOME_AND_DOWNLOAD';
  else if(rendering.length) next='VERIFY_REAL_RENDERED_EMAIL_FOOTER';
  else if(merchant.length) next='VERIFY_NAMED_MERCHANT_APPROVAL';
  else if(approval.length) next='REQUEST_FOUNDER_FINAL_CAMPAIGN_APPROVAL';
  else next='MANUAL_RELEASE_WORKFLOW_ONLY';
  return {
    mode:'OFFLINE_REVIEW_ONLY', release:'HOLD_UNSENT', sent:false,
    visitor_subscription_events:[], purchases:[], realized_net_revenue:null,
    email_eligibility_count:null, // aggregate follower count is NOT reachability
    issue_mix:{editorial:[1,2,4,6],commercial_review_pending:[3,5]},
    primary_offer:'Zen12 Premium (hypothesis only)',
    secondary_offer:'Total Focus (independent merchant hold)',
    stages:{consent_missing:consent,fulfillment_missing:fulfillment,rendering_missing:rendering,merchant_missing:merchant,approval_missing:approval},
    ready_for_manual_review: ![consent,fulfillment,rendering,merchant,approval].some(a=>a.length),
    next_action:next
  };
}
module.exports={review,EVIDENCE};
