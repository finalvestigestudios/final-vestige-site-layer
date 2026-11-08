"use strict";
/* R197 draft-only non-sending preflight. This module never calls a network API
 * and must NEVER be interpreted as production Jetpack/merchant evidence. */
const REQUIRED_COMMON = [
  "founder.approved_exact_creative", "founder.approved_audience", "founder.approved_schedule",
  "consent.provider_subscribed_aggregate_verified", "consent.opt_out_suppression_verified",
  "delivery.authentic_welcome_received", "delivery.fieldbook_reachable_from_welcome",
  "render.received_jetpack_email_verified", "render.subject_preheader_match",
  "render.publisher_postal_address_verified", "render.unsubscribe_action_verified",
  "render.no_placeholder_tokens"
];
const REQUIRED_MERCHANT = [
  "merchant.named_publisher_accepted", "merchant.email_channel_permission_verified",
  "merchant.issued_earning_url_verified", "merchant.live_guide_passed_independent_qa",
  "merchant.current_checkout_refund_terms_checked", "merchant.product_claims_checked",
  "merchant.disclosure_adjacent_to_guide_and_offer"
];
function readPath(object, path) {
  return path.split(".").reduce((cur,key)=>cur && typeof cur==="object" ? cur[key] : undefined,object);
}
function attest(evidence, id) {
  // Only TRUE with a contemporaneous, identified source is an attestation.
  const entry=readPath(evidence,id);
  return !!(entry && entry.verified===true
    && typeof entry.source==="string" && entry.source.trim().length>7
    && typeof entry.checked_at==="string" && /^20\d\d-\d\d-\d\d/.test(entry.checked_at));
}
function releaseAssessment(evidence, issue) {
  if (![1,2,3,4,5,6].includes(issue)) throw Error("Invalid edition");
  const commercial=issue===3||issue===5;
  const missing=REQUIRED_COMMON.concat(commercial?REQUIRED_MERCHANT:[]).filter(id=>!attest(evidence,id));
  return Object.freeze({issue,kind:commercial?"commercial":"editorial",
    status:missing.length?"HOLD_UNSENT":"READY_FOR_FOUNDER_RECHECK_NOT_AUTHORIZATION",
    missing,mail_sent:false});
}
function confirmedSignup(record, seen) {
  // Use private provider-side identity key; no public analytics email or hash.
  if (!record || record.provider_status!=="SUBSCRIBED" || record.confirmation_method!=="provider_double_opt_in"
      || !record.provider_confirmation_at || !record.private_dedup_key
      || record.suppressed===true || record.unsubscribed===true) return false;
  if (!(seen instanceof Set)) throw Error("Private dedup Set required");
  if (seen.has(record.private_dedup_key)) return false;
  seen.add(record.private_dedup_key);
  return true;
}
function revenuePerThousand(record) {
  // Empty orders are UNKNOWN until independent coverage attests zero.
  if (!record || record.order_ledger_reconciled!==true
      || record.refunds_fees_reconciled!==true
      || record.qualified_human_sessions_verified!==true
      || !Number.isSafeInteger(record.qualified_human_sessions)
      || record.qualified_human_sessions<=0
      || !Array.isArray(record.orders)
      || !record.orders.every(o=>o && typeof o.settled_net_usd==="number"
          && Number.isFinite(o.settled_net_usd) && o.independently_verified===true)) return null;
  if (record.orders.length===0 && record.zero_orders_independently_verified!==true) return null;
  const net=record.orders.reduce((sum,o)=>sum+o.settled_net_usd,0);
  return {net_revenue_usd:Math.round(net*100)/100,
    revenue_per_1000_qualified_human_sessions_usd:Math.round((net*1000/record.qualified_human_sessions)*100)/100,
    denominator:record.qualified_human_sessions,cohort_days:record.cohort_days===30?30:record.cohort_days===7?7:null};
}
module.exports={REQUIRED_COMMON,REQUIRED_MERCHANT,releaseAssessment,confirmedSignup,revenuePerThousand};
