"use strict";
/*
 * R121 offline ONLY: aggregate, privacy-minimizing cohort validation.
 * This does not collect data, create cookies, emit HTTP requests, or run on WP.
 * Not a checkout integration. No claim that revenue/sessions exist.
 * Expected usage: Node.js import by test script (or future approved isolated QA).
 */
const ALLOWED = new Set([
  "cohort","utm_source","utm_medium","utm_campaign","asset_id",
  "window_days","qualified_human_sessions","confirmed_paid_orders",
  "settled_income_cents","refunds_reversals_cents","fees_cents",
  "merchant_verified","qualified_sessions_verified","attribution_verified",
  "refund_fee_reconciled","source_kind"
]);
const forbiddenHints=/email|phone|name|address|ip(?:_|$)|cookie|fingerprint|token|password|secret|order_id|customer_id|session_id|device_id|raw_referrer|referrer_url/i;

function validateAggregate(record) {
  if (!record || typeof record !== "object" || Array.isArray(record)) return ["not an aggregate object"];
  const errors=[];
  for(const key of Object.keys(record)){
    if(forbiddenHints.test(key))errors.push("PII or sensitive key refused: "+key);
    else if(!ALLOWED.has(key))errors.push("unexpected field refused: "+key);
  }
  for(const k of ["qualified_human_sessions","confirmed_paid_orders","settled_income_cents","refunds_reversals_cents","fees_cents"]){
    if(record[k] !== null && record[k] !== undefined && (!Number.isSafeInteger(record[k]) || record[k]<0)) errors.push("invalid nonnegative integer: "+k);
  }
  if(record.window_days!==undefined && ![7,30].includes(record.window_days)) errors.push("window must be 7 or 30 days");
  if(record.source_kind!==undefined && !["fv_owned","affiliate"].includes(record.source_kind)) errors.push("source kind must be fv_owned or affiliate");
  if(record.asset_id!==undefined && !/^[a-zA-Z0-9_-]{1,70}$/.test(record.asset_id)) errors.push("invalid asset id");
  if(record.utm_source!==undefined && !/^[a-z0-9_]{2,40}$/.test(record.utm_source)) errors.push("invalid source");
  if(record.utm_medium!==undefined && record.utm_medium!=="organic_social") errors.push("invalid medium");
  if(record.utm_campaign!==undefined && !/^mind_pilot_\d{4}_\d{2}$/.test(record.utm_campaign)) errors.push("invalid campaign");
  if(record.cohort!==undefined && !/^\d{4}-\d{2}-\d{2}$/.test(record.cohort)) errors.push("invalid date cohort");
  return errors;
}
function calculateRevenue(record){
  const errors=validateAggregate(record);
  if(errors.length) return {status:"INVALID",errors};
  const needs={
    qualified_human_sessions:"qualified human landing-session denominator",
    confirmed_paid_orders:"merchant-confirmed paid order count",
    settled_income_cents:"settled merchant gross or affiliate commission income",
    refunds_reversals_cents:"merchant-reconciled refunds/reversals",
    fees_cents:"fees",
    merchant_verified:"merchant-origin record",
    qualified_sessions_verified:"qualified-session record",
    attribution_verified:"cross-channel attributable cohort",
    refund_fee_reconciled:"refund/fee settlement reconciliation",
    window_days:"7 or 30 day window",
    source_kind:"owned sale or affiliate commission"
  };
  const missing=Object.entries(needs).filter(([k])=>(["merchant_verified","qualified_sessions_verified","attribution_verified","refund_fee_reconciled"].includes(k) ? record[k]!==true : record[k]===undefined||record[k]===null)).map(([,reason])=>reason);
  if(record.qualified_human_sessions===0)missing.push("nonzero qualified-human denominator");
  if(missing.length)return {status:"NOT_COMPUTABLE",missing};
  const net_cents=record.settled_income_cents-record.refunds_reversals_cents-record.fees_cents;
  return {
    status:"COMPUTABLE_FROM_VERIFIED_AGGREGATES",
    net_revenue_cents:net_cents,
    net_revenue_per_1000_qualified_humans_cents:net_cents*1000/record.qualified_human_sessions,
    paid_conversion_rate:record.confirmed_paid_orders/record.qualified_human_sessions,
    warning:record.confirmed_paid_orders<10||record.qualified_human_sessions<200 ? "SMALL_SAMPLE_DESCRIPTIVE_ONLY" : null,
    note:"Result only as reliable as the externally confirmed merchant, attribution and qualification evidence."
  };
}
module.exports={validateAggregate,calculateRevenue};
