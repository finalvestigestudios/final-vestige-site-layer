'use strict';
/**
 * R207 SOURCE-ONLY release and realized-revenue guard.
 * NOT connected to WordPress, an ESP, an affiliate account, or a checkout.
 * This module cannot send emails, change live configuration, or approve release.
 */
const REQUIRED_SHARED = Object.freeze({
  publisher_postal: 'publisher_attestation',
  sender_identity: 'received_message',
  provider_eligible_audience: 'provider_subscription_report',
  welcome_received: 'received_message',
  native_jetpack_received_email: 'received_message',
  unsubscribe_functional: 'observed_functional_test',
  founder_final_approval: 'founder_decision'
});
const REQUIRED_MERCHANT = Object.freeze({
  named_partner_acceptance: 'partner_account',
  email_channel_permission: 'partner_account',
  issued_earning_link: 'partner_account',
  current_claims_and_terms: 'merchant_page_and_checkout',
  approved_live_buyer_guide: 'authenticated_cms',
  separate_commercial_approval: 'founder_decision'
});
const ISSUE_TYPES = Object.freeze({
  '01': 'editorial', '02': 'editorial', '03': 'merchant',
  '04': 'editorial', '05': 'merchant', '06': 'editorial'
});
const BAD_REF = /^(?:unverified|pending|hold|none|null|tbd|todo|test|sample|placeholder)$/i;
function verified(p, sourceClass) {
  return !!p && p.status === 'VERIFIED' &&
    p.source_class === sourceClass &&
    typeof p.evidence_ref === 'string' &&
    p.evidence_ref.trim().length >= 8 &&
    !BAD_REF.test(p.evidence_ref.trim()) &&
    typeof p.reviewed_at === 'string' &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(p.reviewed_at);
}
function gate(issueId, attestations = {}) {
  const issueType = ISSUE_TYPES[issueId];
  if (!issueType) throw new Error('unknown canonical issue');
  const checks = {...REQUIRED_SHARED, ...(issueType === 'merchant' ? REQUIRED_MERCHANT : {})};
  const missing = Object.entries(checks)
    .filter(([name,source])=>!verified(attestations[name],source)).map(([name])=>name);
  return Object.freeze({
    issue_id: issueId,
    type: issueType,
    status: missing.length ? (issueType==='merchant' ? 'HOLD_MERCHANT_AND_SEND' : 'HOLD_UNSENT') : 'FOUNDER_REVIEW_ONLY',
    missing,
    is_send_authorized: false // never a release engine
  });
}
function reconcileSubscribers(data) {
  const n = data || {};
  for (const key of ['total','confirmed','unconfirmed','wpcom_followers','email_only_followers']) {
    if (!Number.isInteger(n[key]) || n[key] < 0) throw new Error('invalid aggregate counter '+key);
  }
  // Counters are NOT additive or disjoint. WP.com followers can receive email.
  return Object.freeze({
    diagnostic: { ...n },
    counted_total: n.total,
    authoritative_eligible: null,
    warning: 'Nonadditive counts; use deduplicated provider-filtered Email subscription=Subscribed. Email-only=0 is not eligible=0.'
  });
}
function cohortRevenue(report) {
  // A blank ledger MUST NOT be represented as $0 revenue.
  if (!report || report.reconciled !== true ||
      report.source_class !== 'merchant_settlement_or_owned_checkout' ||
      report.complete_order_population !== true ||
      report.refunds_complete !== true ||
      report.fees_complete !== true ||
      !Number.isInteger(report.unique_qualified_human_sessions) ||
      report.unique_qualified_human_sessions <= 0 ||
      !Number.isInteger(report.confirmed_paid_orders) ||
      report.confirmed_paid_orders < 0 ||
      !['7_day','30_day'].includes(report.cohort) ||
      ![report.gross,report.refunds,report.fees].every(Number.isFinite) ||
      report.gross<0 || report.refunds<0 || report.fees<0) return null;
  const net = report.gross - report.refunds - report.fees;
  return Object.freeze({net_revenue:net, net_per_1000_qualified_sessions:1000*net/report.unique_qualified_human_sessions, cohort:report.cohort, confirmed_paid_orders:report.confirmed_paid_orders});
}
module.exports = {ISSUE_TYPES, REQUIRED_SHARED, REQUIRED_MERCHANT, verified, gate, reconcileSubscribers, cohortRevenue};