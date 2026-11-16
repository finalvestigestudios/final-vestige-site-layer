// FV Dispatch R394 — OFFLINE, pure verification helpers. Never sends or records PII.
export const SEND_AUTHORIZED = false;
const fields = [
  "provider_eligible_count","welcome_receipt","native_preview",
  "postal_address","unsubscribe_verified","editorial_sources",
  "founder_final_approval"
];
const commerce = [
  "named_publisher_approval","specific_sku","email_channel_permission",
  "approved_merchant_creative","issued_earning_url","live_vetted_guide",
  "referred_checkout_terms","near_offer_disclosure"
];
export function evaluateIssue(issue, proof = {}) {
  const commercial = issue === 3 || issue === 5;
  if (![1,2,3,4,5,6].includes(issue)) throw Error("Unknown pilot issue");
  const missing = [...fields,...(commercial ? commerce : [])]
    .filter(k => proof[k] !== true);
  if (issue === 4 && proof.apollo_14_second_copy_correction !== true)
    missing.push("apollo_14_second_copy_correction");
  return Object.freeze({
    issue,
    lane: commercial ? "commercial-review-pending" : "editorial",
    eligible_for_human_review: missing.length === 0,
    missing,
    send_authorized: SEND_AUTHORIZED,
    state: "HOLD_UNSENT"
  });
}
export function confirmedSignupCount(events) {
  if (!Array.isArray(events)) throw Error("events must be an array");
  const ids = new Set(), subscribers = new Set(); let count=0;
  for (const e of events) {
    if (!e || e.origin !== "jetpack_provider" ||
        e.kind !== "newly_eligible_transition" ||
        e.prior_status === "Subscribed" ||
        e.new_status !== "Subscribed" ||
        e.consent_recorded !== true ||
        typeof e.provider_event_id !== "string" || !e.provider_event_id ||
        typeof e.opaque_subscriber_key !== "string" || !e.opaque_subscriber_key ||
        typeof e.confirmed_at !== "string" || !/^\d{4}-\d{2}-\d{2}T/.test(e.confirmed_at)) continue;
    if (ids.has(e.provider_event_id) || subscribers.has(e.opaque_subscriber_key)) continue;
    ids.add(e.provider_event_id); subscribers.add(e.opaque_subscriber_key); count++;
  }
  return count;
}
export function settledNetPer1000({qualified_human_sessions, sessions_audited, settlements} = {}) {
  if (sessions_audited !== true || !Number.isSafeInteger(qualified_human_sessions) ||
      qualified_human_sessions <= 0 || !Array.isArray(settlements))
    return Object.freeze({status:"NOT_COMPUTABLE",reason:"audited denominator or ledger missing"});
  const ids = new Set(); let netCents=0;
  for (const s of settlements) {
    if (!s || s.provider_verified !== true || s.status !== "settled" ||
        typeof s.settlement_id !== "string" || !s.settlement_id ||
        !Number.isSafeInteger(s.commission_cents) || s.commission_cents < 0 ||
        !Number.isSafeInteger(s.refund_cents) || s.refund_cents < 0 ||
        !Number.isSafeInteger(s.fee_cents) || s.fee_cents < 0 ||
        !Number.isSafeInteger(s.reversal_cents) || s.reversal_cents < 0)
      return Object.freeze({status:"NOT_COMPUTABLE",reason:"invalid or unverified settlement"});
    if (ids.has(s.settlement_id)) continue;
    ids.add(s.settlement_id);
    netCents += s.commission_cents - s.refund_cents - s.fee_cents - s.reversal_cents;
  }
  if (!Number.isSafeInteger(netCents))
    return Object.freeze({status:"NOT_COMPUTABLE",reason:"integer overflow"});
  return Object.freeze({status:"COMPUTABLE",verified_settlements:ids.size,net_revenue_cents:netCents,
    revenue_per_1000_sessions_usd:Math.round((netCents/100*1000/qualified_human_sessions)*100)/100});
}
