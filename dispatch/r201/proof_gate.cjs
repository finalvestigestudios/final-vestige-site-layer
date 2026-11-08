"use strict";
/** Source-only Dispatch R201 gate; no WordPress, mailing or analytics I/O.
 * Evidence values are private references, NOT email addresses or buyer identifiers.
 * REVIEW_CANDIDATE_ONLY is never authorization to send.
 */
const REQUIRED_SHARED = [
 "eligible_subscriber_aggregate", "provider_consent_policy", "received_welcome",
 "jetpack_mime_review", "publisher_postal", "visible_unsubscribe",
 "unsub_functional_evidence", "founder_issue_approval"
];
const REQUIRED_COMMERCIAL = [
 "named_inspire3_account_acceptance", "express_email_channel_rights",
 "issued_account_earning_link", "link_and_creative_format_permitted",
 "approved_live_independent_guide", "current_checkout_refund_review",
 "merchant_claims_checked"
];
const PILOT_TYPES = Object.freeze(["editorial","editorial","commercial","editorial","commercial","editorial"]);
function isProof(value) {
 return !!value && typeof value==="object" && value.verified === true &&
 typeof value.reference==="string" && /^(internal|github):[a-zA-Z0-9._/#-]{6,}$/.test(value.reference) &&
 typeof value.verified_at==="string" && /^20\d{2}-\d{2}-\d{2}T/.test(value.verified_at);
}
function issueReview(number, attestations={}) {
 if(!Number.isInteger(number)||number<1||number>6) throw new Error("edition 1..6 required");
 const commercial=PILOT_TYPES[number-1]==="commercial";
 const needed=commercial?REQUIRED_SHARED.concat(REQUIRED_COMMERCIAL):REQUIRED_SHARED;
 const missing=needed.filter(k=>!isProof(attestations[k]));
 return Object.freeze({edition:number,category:PILOT_TYPES[number-1],
   decision:missing.length?"HOLD_UNSENT":"HUMAN_REVIEW_CANDIDATE_ONLY",
   missing, may_send:false, merchant_active:false});
}
/** This function accepts *private* provider state evidence, never page UI evidence.
 * Event key is an HMAC-derived 64-character token; it must never be published.
 * Returns a non-identifying event outcome, not a subscriber record.
 */
function confirmedSignup(event, seen=new Set()) {
 if(!event||event.provider!=="jetpack"||
    event.previous_status!=="pending"||
    event.current_email_subscription!=="subscribed"||
    event.consumer_consent!=="affirmative"||
    !isProof(event.provider_transition_proof)||
    !/^[a-f0-9]{64}$/.test(event.private_hmac_key||"")||
    seen.has(event.private_hmac_key)) return {event:null,reason:"PROVIDER_CONFIRMATION_NOT_PROVEN"};
 seen.add(event.private_hmac_key);
 return {event:"confirmed_signup",reason:"PROVIDER_TRANSITION_VERIFIED"};
}
/** Only reconciled merchant-reported paid orders support economic results.
 * A verified complete empty settlement report can prove zero purchases; an absent
 * report cannot. Clicks and checkout starts are never orders.
 */
function revenueEvidence(cohort) {
 if(!cohort||!isProof(cohort.qualified_human_sessions_proof)||
    !Number.isSafeInteger(cohort.qualified_human_sessions)||cohort.qualified_human_sessions<=0||
    !isProof(cohort.complete_merchant_settlement_report)||
    !Array.isArray(cohort.orders)) return {status:"NOT_COMPUTABLE"};
 let gross=0,refunds=0,fees=0;
 const ids=new Set();
 for(const o of cohort.orders){
   if(!o||typeof o.private_order_token!=="string"||
      !/^[a-f0-9]{64}$/.test(o.private_order_token)||ids.has(o.private_order_token)||
      !isProof(o.merchant_paid_order_proof)||
      ![o.gross,o.refunds,o.fees].every(v=>Number.isFinite(v)&&v>=0)) return {status:"NOT_COMPUTABLE"};
   ids.add(o.private_order_token);gross+=o.gross;refunds+=o.refunds;fees+=o.fees;
 }
 if(!cohort.report_is_complete) return {status:"NOT_COMPUTABLE"};
 const net=gross-refunds-fees;
 return {status:"RECONCILED_EVIDENCE_ONLY",orders:cohort.orders.length,net_revenue:net,
   net_per_1000_qualified_humans:1000*net/cohort.qualified_human_sessions};
}
module.exports={PILOT_TYPES,REQUIRED_SHARED,REQUIRED_COMMERCIAL,isProof,issueReview,confirmedSignup,revenueEvidence};
