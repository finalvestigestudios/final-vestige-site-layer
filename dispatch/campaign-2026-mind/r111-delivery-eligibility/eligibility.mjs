/**
 * R111 — read-only WordPress/Jetpack newsletter evidence interpreter.
 * Pure, offline. Never sends mail, reads recipients, makes requests or sets
 * consent, subscription or financial facts. PRIVATE counts are never publicly
 * projected when a small cohort could reveal subscriber behavior.
 */
const INT = n => Number.isSafeInteger(n) && n >= 0;
const UNKNOWN = null;
const SAFE_DATE = s => typeof s === 'string' && /^20\d{2}-\d{2}-\d{2}T/.test(s) && Number.isFinite(Date.parse(s));

export function reconcileNewsletter({ status, followers } = {}) {
  if (!status || status.origin !== 'connected_wordpress_jetpack_newsletter_status' ||
      !SAFE_DATE(status.as_of)) return { error: 'no_authoritative_jetpack_snapshot', eligibility: UNKNOWN };
  const sub = status.subscribers;
  if (!sub || !['total','confirmed','unconfirmed','suppressed'].every(k => INT(sub[k]))) {
    return { error: 'missing_or_invalid_native_counts', eligibility: UNKNOWN };
  }
  if (sub.confirmed > sub.total || sub.suppressed > sub.total + sub.unconfirmed) {
    return { error: 'counts_require_native_review', eligibility: UNKNOWN };
  }
  const independentFollowers = followers &&
    followers.origin === 'connected_wordpress_follower_summary' &&
    INT(followers.wordpress) && INT(followers.email)
    ? { wordpress_reader: followers.wordpress, email_follower_summary: followers.email } : null;
  // Official WP subscriber docs: unconfirmed excluded from total. Therefore
  // 2 total, 2 confirmed, 2 pending is POSSIBLE (not a four-person audience).
  // Reader following, summary email=0, subscribed, deliverable, and recipients
  // for a particular send are NOT interchangeable.
  return {
    error: null, as_of: status.as_of, newsletter_total: sub.total,
    confirmed_accounts: sub.confirmed, pending_unconfirmed: sub.unconfirmed,
    suppressed_total: sub.suppressed, followers: independentFollowers,
    pending_excluded_from_total: true,
    additive_subscriber_total: null, email_eligible_recipients: UNKNOWN,
    welcome_delivered: UNKNOWN, effective_optout_verified: UNKNOWN,
    ready_to_send: false, state: 'HOLD_UNSENT',
    reason: 'subscriber_count_is_not_verified_email_reachability'
  };
}

const PROOFS = new Set([
  'existing_authorized_received_welcome_mime', 'first_party_pdf_open_verified',
  'actual_received_commercial_footer', 'actual_received_unsubscribe_and_suppression',
  'publisher_postal_address_approved', 'named_partner_email_channel_permission',
  'approved_first_party_offer_guide', 'founder_exact_campaign_approval'
]);

/** Track evidence readiness without allowing a synthetic attestation to SEND. */
export function evidenceReadiness(items = []) {
  if (!Array.isArray(items)) throw new TypeError('items must be array');
  const satisfied = new Set();
  for (const v of items) {
    if (!v || !PROOFS.has(v.proof_kind) || v.verified !== true ||
        typeof v.evidence_ref !== 'string' || !/^evidence_[a-z0-9_-]{6,80}$/.test(v.evidence_ref) ||
        v.source !== 'independent_authorized_review') continue;
    satisfied.add(v.proof_kind);
  }
  const missing = [...PROOFS].filter(x => !satisfied.has(x));
  return { reviewed_proof_kinds: [...satisfied], missing_proof_kinds: missing,
    editorial_state: 'HOLD_UNSENT',
    commercial_state: 'HOLD_MERCHANT_AND_UNSENT',
    sending_authorized: false, production_activated: false };
}

/** Never expose per-person keys, hashes, source asset IDs or exact counts in
 * a public dashboard for this tiny list. A real confirmed_signup must have
 * been counted by R110 using native opt-in evidence, not button or PDF clicks.
 * No qualified-session count, merchant order or revenue is inferred. */
export function publicConsentScorecard(aggregate, cohortSize, k = 20) {
  if (!INT(cohortSize) || !INT(k) || k < 20 || !aggregate ||
      !INT(aggregate.confirmed_signup_events) ||
      !INT(aggregate.attributable_opt_ins) ||
      aggregate.attributable_opt_ins > aggregate.confirmed_signup_events) {
    return { status: 'INVALID_OR_UNVERIFIED', confirmed_signups: null,
      source_linked_signups: null, orders: null, net_revenue: null };
  }
  if (cohortSize < k) return {
    status: 'SMALL_COHORT_SUPPRESSED', confirmed_signups: null,
    source_linked_signups: null, orders: null, net_revenue: null
  };
  return { status: 'COUNTS_ONLY_NOT_DELIVERY_OR_SALES',
    confirmed_signups: aggregate.confirmed_signup_events,
    source_linked_signups: aggregate.attributable_opt_ins,
    orders: null, net_revenue: null };
}
