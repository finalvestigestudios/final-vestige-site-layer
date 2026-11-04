"use strict";
/**
 * Offline-only privacy-safe conversion metric. NOT website instrumentation.
 * No network, storage, visitor IDs, email, IP, checkout IDs or partner credentials.
 * This module never equates outbound click, Focus reveal, or subscriber counts with paid orders.
 */
const PRIVATE_FIELDS = new Set([
  "email", "name", "buyer_name", "buyer_email", "ip", "ip_address",
  "address", "phone", "order_id", "customer_id", "session_id",
  "user_agent", "fingerprint", "referrer_url", "full_url", "payment_token"
]);
function noPrivateFields(obj) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) return false;
  return Object.keys(obj).every((key) => !PRIVATE_FIELDS.has(key.toLowerCase()));
}
function verifiedNumber(value) {
  return typeof value === "number" && Number.isSafeInteger(value) && value >= 0;
}
function netRevenuePer1000(cohort) {
  if (!noPrivateFields(cohort)) return {status: "REJECTED_PRIVATE_DATA"};
  const required = ["qualified_human_sessions", "owned_settled_gross_cents",
    "affiliate_settled_commission_cents", "refunds_cents", "fees_cents", "chargebacks_cents",
    "confirmed_paid_orders"];
  if (!required.every(k => verifiedNumber(cohort[k])) || cohort.qualified_human_sessions === 0) {
    return {status: "NOT_COMPUTABLE", reason: "missing_or_invalid_denominator_or_money"};
  }
  if (![7,30].includes(cohort.cohort_days)) return {status: "NOT_COMPUTABLE", reason: "cohort_invalid"};
  if (cohort.qualified_sessions_authoritative !== true) return {status: "NOT_COMPUTABLE", reason: "human_sessions_unverified"};
  if (cohort.merchant_settlement_authoritative !== true) return {status: "NOT_COMPUTABLE", reason: "merchant_record_unverified"};
  if (cohort.refunds_and_fees_reconciled !== true) return {status: "NOT_COMPUTABLE", reason: "adjustments_missing"};
  if (cohort.attribution_verified !== true) return {status: "NOT_COMPUTABLE", reason: "campaign_attribution_unknown"};
  if (cohort.confirmed_paid_orders === 0 && (cohort.owned_settled_gross_cents > 0 || cohort.affiliate_settled_commission_cents > 0)) {
    return {status: "NOT_COMPUTABLE", reason: "money_without_confirmed_paid_orders"};
  }
  const netCents=cohort.owned_settled_gross_cents+cohort.affiliate_settled_commission_cents-
    cohort.refunds_cents-cohort.fees_cents-cohort.chargebacks_cents;
  if (!Number.isSafeInteger(netCents)) return {status: "NOT_COMPUTABLE",reason: "money_overflow"};
  const per1000Dollars=(netCents / 100) * 1000 / cohort.qualified_human_sessions;
  if (!Number.isFinite(per1000Dollars)) return {status:"NOT_COMPUTABLE",reason:"invalid_arithmetic"};
  return {status:"VERIFIED_AGGREGATE_INPUTS_ONLY",cohort_days:cohort.cohort_days,
    net_revenue_cents:netCents,net_revenue_per_1000_qualified_sessions_usd:Number(per1000Dollars.toFixed(2)),
    paid_order_count:cohort.confirmed_paid_orders,
    denominator:cohort.qualified_human_sessions,
    sample_warning:cohort.confirmed_paid_orders<20 || cohort.qualified_human_sessions<1000,
    note:"Aggregate input calculations do NOT independently authenticate records. Operator must retain source-of-truth receipts."};
}
function classifyEvent(name, origin) {
  if (["focus_query_reveal","focus_css_reveal","affiliate_outbound","pdf_download","focus_cta_click"].includes(name)) return "NOT_PAID_CONVERSION";
  if (name==="native_confirmed_signup") return origin==="jetpack_native_verified" ? "CONFIRMED_LEAD_ONLY":"UNVERIFIED";
  if (name==="paid_order") return origin==="merchant_authoritative_aggregate" ? "POTENTIAL_PAID_EVIDENCE":"UNVERIFIED";
  return "UNVERIFIED";
}
module.exports={noPrivateFields,netRevenuePer1000,classifyEvent};
