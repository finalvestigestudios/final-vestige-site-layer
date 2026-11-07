'use strict';
/** Dispatch R174: a strictly offline, PII-free read-only measurement gate. No send method. */
const EDITORIAL = [1, 2, 4, 6], COMMERCIAL = [3, 5];
const forbidPrivate = (input) => {
  const serialized = JSON.stringify(input);
  if (!serialized || serialized.length > 200000) throw new Error('invalid evidence bundle');
  const forbidden = /"(?:email|email_address|recipient|ip_address|full_name|phone|cookie|password|api_key|auth_token|subscriber_id|hashed_email)"\s*:/i;
  if (forbidden.test(serialized)) throw new Error('private or identifying field prohibited');
};
function uniqueRefs(rows) {
  const seen = new Set();
  for (const x of rows) {
    if (!x.evidence_ref || typeof x.evidence_ref !== 'string' || seen.has(x.evidence_ref)) throw new Error('missing or duplicate proof reference');
    seen.add(x.evidence_ref);
  }
}
function isIntegerNonnegative(n) { return Number.isSafeInteger(n) && n >= 0; }
function evaluate(bundle) {
  forbidPrivate(bundle);
  if (![7,30].includes(bundle.cohort_days)) throw new Error('cohort must be seven or thirty days');
  if (bundle.issue_mix?.editorial?.join(',') !== EDITORIAL.join(',') || bundle.issue_mix?.commercial?.join(',') !== COMMERCIAL.join(',')) throw new Error('founder-approved 4:2 mix may not be changed');
  if (bundle.active_affiliate_url != null || bundle.sending_enabled !== false || bundle.founder_send_approval !== false) throw new Error('no affiliate activation or sends permitted');
  const snapshot = bundle.newsletter || {};
  const blockers = [];
  if (snapshot.enabled !== true) blockers.push('NEWSLETTER_DISABLED');
  if (snapshot.new_post_auto_send !== false) blockers.push('AUTO_SEND_NOT_OFF');
  if (snapshot.confirmed_count == null || snapshot.unconfirmed_count == null) blockers.push('NATIVE_COUNTS_MISSING');
  if (snapshot.confirmed_count != null && !isIntegerNonnegative(snapshot.confirmed_count)) throw new Error('bad confirmed count');
  if (snapshot.unconfirmed_count != null && !isIntegerNonnegative(snapshot.unconfirmed_count)) throw new Error('bad pending count');
  if (!isIntegerNonnegative(snapshot.total_count)) throw new Error('bad subscriber total');
  if (snapshot.eligible_recipients == null) blockers.push('EMAIL_ELIGIBILITY_UNKNOWN');
  if (snapshot.actual_welcome_received !== true) blockers.push('WELCOME_RECEIPT_NOT_VERIFIED');
  if (snapshot.native_jetpack_preview !== true) blockers.push('NATIVE_EMAIL_RENDER_UNVERIFIED');
  if (snapshot.valid_fv_postal_address !== true) blockers.push('FV_POSTAL_ADDRESS_UNVERIFIED');
  if (snapshot.functional_opt_out !== true) blockers.push('OPTOUT_UNVERIFIED');
  if (bundle.merchant?.approved_for_publisher_email !== true) blockers.push('PARTNER_EMAIL_PERMISSION_UNKNOWN');
  if (bundle.merchant?.live_approved_guide !== true) blockers.push('VETTED_GUIDE_NOT_LIVE');
  if (bundle.merchant?.earning_url_approved !== true) blockers.push('EARNING_URL_UNVERIFIED');
  if (bundle.merchant?.price_and_refund_terms_checked !== true) blockers.push('CHECKOUT_TERMS_UNVERIFIED');
  const sessions = bundle.sessions || [], orders = bundle.orders || [];
  uniqueRefs(sessions); uniqueRefs(orders);
  let qualified = 0;
  for (const s of sessions) {
    if (!isIntegerNonnegative(s.human_qualified_sessions)) throw new Error('invalid session count');
    if (!/^(youtube|tiktok|instagram|facebook|pinterest|x|bluesky)$/.test(s.utm_source)) throw new Error('unsupported source');
    if (s.utm_medium !== 'organic_social') throw new Error('medium must preserve creator-led source');
    if (!/^[a-z0-9_-]{3,100}$/.test(s.utm_campaign || '') || !/^[a-z0-9_-]{3,100}$/.test(s.asset_id || '')) throw new Error('missing canonical campaign/asset');
    if (s.is_provider_qualified !== true) throw new Error('no unsupported human-session counts');
    qualified += s.human_qualified_sessions;
  }
  if (!Number.isSafeInteger(qualified)) throw new Error('session sum overflow');
  let netCents = 0, settledOrders = 0, attributedOrders = 0, unattributedOrders = 0;
  for (const o of orders) {
    if (o.source !== 'independent_merchant_report' && o.source !== 'owned_checkout_settlement') throw new Error('sales require independent settlement evidence');
    if (o.status !== 'settled' && o.status !== 'refunded') throw new Error('clicks/pending orders are not sales');
    for (const key of ['gross_commission_cents','refund_cents','fees_cents']) if (!isIntegerNonnegative(o[key])) throw new Error('amounts must be integer nonnegative cents');
    settledOrders++;
    const value = o.gross_commission_cents - o.refund_cents - o.fees_cents;
    if (o.campaign_attribution_verified === true && o.asset_attribution_verified === true && sessions.some(s => s.utm_campaign === o.utm_campaign && s.asset_id === o.asset_id)) {
      attributedOrders++; netCents += value;
    } else {
      unattributedOrders++;
    }
  }
  const completeReports = bundle.settlement_report_complete === true && bundle.session_report_complete === true;
  const isAttributionComplete = completeReports && unattributedOrders === 0;
  const revenuePer1k = qualified > 0 && isAttributionComplete ? Math.round(netCents * 1000 / qualified) / 100 : null;
  return Object.freeze({
    gate:'HOLD_UNSENT', commercial_gate:'HOLD_MERCHANT',
    counted_subscribers:snapshot.total_count, confirmed_count:snapshot.confirmed_count, unconfirmed_separate:snapshot.unconfirmed_count,
    actual_email_eligible:snapshot.eligible_recipients ?? null,
    blockers, qualified_human_sessions: qualified,
    merchant_settled_orders: settledOrders, attributed_settled_orders: attributedOrders,
    unattributed_settled_orders:unattributedOrders,
    attributable_net_cents:isAttributionComplete ? netCents : null,
    net_per_1000_qualified_sessions_usd:revenuePer1k,
    missing_attribution: !isAttributionComplete,
    caveat:'Synthetic fixtures are NOT Final Vestige sales. Event/CTA clicks and signups do not prove paid orders.'
  });
}
module.exports={ evaluate, EDITORIAL, COMMERCIAL };
