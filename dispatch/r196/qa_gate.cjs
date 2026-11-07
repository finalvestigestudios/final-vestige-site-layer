"use strict";
/* R196 synthetic read-only eligibility and release policy. No network, sends, subscribers, or telemetry. */
const immutableCampaign={editorial:[1,2,4,6],commercial:[3,5]};
function statusOfConfirmation(record, seen=new Set()){
  if(!record || record.provider!=="wordpress_jetpack" || record.source!=="provider_verified_transition"
    || record.authoritative_evidence_verified!==true || record.email_subscription!=="subscribed"
    || record.consent_for_dispatch!==true || record.current_status!=="subscribed"
    || typeof record.provider_event_id!=="string" || record.provider_event_id.length<8)
      return "NOT_CONFIRMED";
  if(seen.has(record.provider_event_id)) return "DUPLICATE_NOT_NEW";
  seen.add(record.provider_event_id);
  return "PROVIDER_CONFIRMED_TRANSITION";
}
function evaluateRelease(issue,proof={}){
  if(![1,2,3,4,5,6].includes(issue))return "INVALID_ISSUE";
  if(proof.founder_final_send_approval!==true || proof.verified_recipient_consent!==true
    || proof.actual_received_Jetpack_preview!==true || proof.valid_FV_postal_address!==true
    || proof.actual_working_unsubscribe!==true)return "HOLD_UNSENT";
  if(immutableCampaign.commercial.includes(issue) && !(proof.merchant_named_approval===true
     && proof.merchant_email_channel_rights===true && proof.issued_earning_link_verified===true
     && proof.live_mind_guide_verified===true && proof.seller_claims_audited===true
     && proof.adjacent_affiliate_disclosure_verified===true))return "HOLD_MERCHANT";
  return "READY_FOR_FOUNDER_MANUAL_SEND_REVIEW_ONLY";
}
function paidMetric(report){
  if(!report || report.independent_merchant_settlement!==true || report.complete_purchase_reconciliation!==true
     || report.refunds_and_fees_reconciled!==true || report.qualified_human_denominator_verified!==true
     || !Number.isFinite(report.qualified_human_sessions) || report.qualified_human_sessions<=0
     || !Number.isFinite(report.realized_net_revenue))return "NOT_COMPUTABLE";
  return 1000*report.realized_net_revenue/report.qualified_human_sessions;
}
module.exports={immutableCampaign,statusOfConfirmation,evaluateRelease,paidMetric};
