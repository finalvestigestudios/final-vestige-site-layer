'use strict';
// R323 — synthetic, read-only and non-sending. Input flags are NOT provider authentication.
const FV = 'finalvestige.com';
function hasProof(e) {
  return !!e && e.origin === 'authenticated_jetpack_provider'
    && e.site === FV && typeof e.event_id === 'string'
    && e.event_id.trim().length >= 12
    && typeof e.subscriber_key === 'string'
    && e.subscriber_key.trim().length >= 12
    && typeof e.observed_at === 'string'
    && !Number.isNaN(Date.parse(e.observed_at))
    && e.dispatch_consent === true && e.email_eligible === true
    && e.new_site_enrollment === true && e.was_preexisting === false
    && e.suppressed !== true;
}
function countConfirmedSignup(events) {
  if (!Array.isArray(events)) return { count: null, reason: 'provider_events_missing' };
  const identities = new Set(), ids = new Set();
  let count = 0, rejected = 0;
  for (const e of events) {
    if (!hasProof(e) || !['confirmed_email_link', 'wpcom_immediate_active'].includes(e.route)) {
      rejected++; continue;
    }
    if (identities.has(e.subscriber_key) || ids.has(e.event_id)) { rejected++; continue; }
    identities.add(e.subscriber_key); ids.add(e.event_id); count++;
  }
  return { count, rejected, reason: 'synthetic_event_classification_only_not_live_measurement' };
}
function classifyVisitorSignal(e) {
  if (!e || typeof e !== 'object') return 'UNKNOWN';
  if (e.origin === 'zen12.com' || e.origin === 'inspire3.com' || e.origin === 'merchant') return 'MERCHANT_SEPARATE_LIST';
  if (e.kind === 'download' || e.kind === 'signup_attempt' || e.kind === 'query_parameter') return 'NOT_CONFIRMED';
  if (e.kind === 'reader_follow') return 'NOT_EMAIL_ELIGIBILITY';
  if (hasProof(e) && ['confirmed_email_link','wpcom_immediate_active'].includes(e.route)) return 'FV_CONFIRMED_CANDIDATE_ONLY';
  return 'UNKNOWN';
}
function merchantRelease(proofs) {
  const required = [
    'account_approved', 'email_channel_permission', 'earning_url_issued',
    'guide_live_and_approved', 'final_terms_checked', 'adjacent_disclosure_checked',
    'fv_postal_address_verified', 'native_unsubscribe_verified',
    'native_received_preview_verified', 'final_founder_campaign_approval'
  ];
  const missing = required.filter(k => !proofs || !proofs[k]
     || proofs[k].verified !== true || typeof proofs[k].evidence_ref !== 'string'
     || proofs[k].evidence_ref.trim().length < 8
     || proofs[k].independent_reviewer !== true);
  return { state:'HOLD_UNSENT', merchant_state:missing.length?'HOLD_MERCHANT':'HOLD_PENDING_MANUAL_SEND_AUTHORIZATION', missing };
}
function netPerThousand(report) {
  if (!report || report.reconciled !== true || report.sessions_origin_verified !== true
    || report.settlements_origin_verified !== true) return null;
  const n = report.qualified_human_sessions, gross=report.settled_gross,
    refunds=report.refunds, fees=report.fees;
  if (![n,gross,refunds,fees].every(v=>Number.isFinite(v)) || n<=0
    || gross<0 || refunds<0 || fees<0 || refunds+fees>gross) return null;
  return 1000*(gross-refunds-fees)/n;
}
module.exports = { countConfirmedSignup, classifyVisitorSignal, merchantRelease, netPerThousand };
