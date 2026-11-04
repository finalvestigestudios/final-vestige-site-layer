/*
 * FV Mind R126 — OFFLINE aggregate-only settlement contract.
 * DRAFT. No browser/network/WordPress hooks. Not a live analytics script.
 * Input must come from independently authorized FIRST-PARTY and MERCHANT aggregate exports.
 * Never pass personal records. Never infer sales from affiliate_outbound or CTA clicks.
 */
"use strict";

const ALLOWED = new Set([
 "cohort_days","utm_campaign","asset_id","qualified_human_sessions","human_qualification_verified",
 "sessions_source","merchant_ledger_source","settlement_coverage_verified",
 "verified_paid_orders","gross_revenue_cents","refunds_cents","fees_cents",
 "chargebacks_cents","currency","confirmed_leads","lead_count_verified",
 "affiliate_outbound_clicks","asset_attribution_verified","synthetic_fixture"
]);
function isInt(x) { return Number.isSafeInteger(x) && x >= 0; }
function validateInput(input) {
 if (!input || typeof input !== "object" || Array.isArray(input)) throw Error("invalid_input");
 for (const key of Object.keys(input)) if (!ALLOWED.has(key)) throw Error("non_whitelisted_field:" + key);
 for (const key of Object.keys(input)) if (/(?:email|phone|customer|postal|address|ip_address|purchase_id|visitor_id)/i.test(key)) throw Error("pii_rejected");
 if (input.cohort_days !== 7 && input.cohort_days !== 30) throw Error("invalid_cohort");
 if (!/^[a-z][a-z0-9_]{2,64}$/.test(input.utm_campaign||"")) throw Error("invalid_campaign");
 if (input.asset_id != null && !/^[A-Za-z0-9_-]{3,80}$/.test(input.asset_id)) throw Error("invalid_asset_id");
 if (input.currency !== "USD") throw Error("unsupported_currency");
 const measures=["qualified_human_sessions","verified_paid_orders","gross_revenue_cents","refunds_cents","fees_cents","chargebacks_cents"];
 for (const m of measures) if (input[m] != null && !isInt(input[m])) throw Error("invalid_measure:"+m);
 if (input.confirmed_leads != null && !isInt(input.confirmed_leads)) throw Error("invalid_measure:confirmed_leads");
 if (input.affiliate_outbound_clicks != null && !isInt(input.affiliate_outbound_clicks)) throw Error("invalid_clicks");
 if (input.synthetic_fixture != null && typeof input.synthetic_fixture !== "boolean") throw Error("invalid_synthetic_flag");
 return true;
}
function measure(input) {
 validateInput(input);
 const missing=[];
 if (input.sessions_source !== "first_party_verified" || input.human_qualification_verified !== true || !isInt(input.qualified_human_sessions) || input.qualified_human_sessions===0)
   missing.push("qualified_human_session_denominator");
 if (input.merchant_ledger_source !== "approved_merchant_reconciliation" || input.settlement_coverage_verified !== true)
   missing.push("merchant_authoritative_settlement_coverage");
 for(const key of ["verified_paid_orders","gross_revenue_cents","refunds_cents","fees_cents","chargebacks_cents"]) if(!isInt(input[key])) missing.push(key);
 if(input.asset_id && input.asset_attribution_verified !== true) missing.push("asset_level_merchant_attribution");
 if (missing.length) return {status:"NOT_COMPUTABLE",reasons:missing,paid_conversion_rate:null,net_revenue_cents:null,net_revenue_per_1000_qualified_sessions_cents:null,affiliate_outbound_clicks:input.affiliate_outbound_clicks ?? null,synthetic_fixture:input.synthetic_fixture===true};
 if (input.verified_paid_orders > input.qualified_human_sessions) throw Error("orders_exceed_sessions_verify_definition");
 const deductions=input.refunds_cents+input.fees_cents+input.chargebacks_cents;
 if(!Number.isSafeInteger(deductions)) throw Error("amount_overflow");
 const net=input.gross_revenue_cents-deductions;
 if(!Number.isSafeInteger(net)) throw Error("amount_overflow");
 const per1000=Math.round(net*1000/input.qualified_human_sessions);
 if(!Number.isSafeInteger(per1000)) throw Error("amount_overflow");
 const leads_ok=input.lead_count_verified === true && isInt(input.confirmed_leads);
 return {
  status:"COMPUTED_FROM_VERIFIED_INPUT_ONLY",
  campaign:input.utm_campaign,
  asset_id:input.asset_id ?? null,
  cohort_days:input.cohort_days,
  currency:input.currency,
  qualified_human_sessions:input.qualified_human_sessions,
  verified_paid_orders:input.verified_paid_orders,
  paid_conversion_rate:input.verified_paid_orders/input.qualified_human_sessions,
  gross_revenue_cents:input.gross_revenue_cents,
  refunds_cents:input.refunds_cents,
  fees_cents:input.fees_cents,
  chargebacks_cents:input.chargebacks_cents,
  net_revenue_cents:net,
  net_revenue_per_1000_qualified_sessions_cents:per1000,
  confirmed_leads:leads_ok?input.confirmed_leads:null,
  lead_to_paid_order_rate:leads_ok && input.confirmed_leads>0 ? input.verified_paid_orders/input.confirmed_leads : null,
  affiliate_outbound_clicks:input.affiliate_outbound_clicks ?? null,
  sample_caution:input.qualified_human_sessions<100 ? "TINY_SAMPLE" : input.verified_paid_orders<10?"LOW_ORDER_COUNT":"NORMAL_REVIEW",
  synthetic_fixture:input.synthetic_fixture===true,
  attribution_note:"This function cannot validate the source claims; only authoritative documented inputs make a real-world result verified."
 };
}
module.exports={measure,validateInput};
