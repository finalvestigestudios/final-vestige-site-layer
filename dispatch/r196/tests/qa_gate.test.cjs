"use strict";
// Synthetic unit checks. No external data or live calls. To run: node tests/qa_gate.test.cjs
const assert=require("node:assert/strict");
const {immutableCampaign,statusOfConfirmation,evaluateRelease,paidMetric}=require("../qa_gate.cjs");
const seen=new Set();
const good={provider:"wordpress_jetpack",source:"provider_verified_transition",authoritative_evidence_verified:true,email_subscription:"subscribed",consent_for_dispatch:true,current_status:"subscribed",provider_event_id:"provider-event-000001"};
assert.deepEqual(immutableCampaign.editorial,[1,2,4,6]);
assert.deepEqual(immutableCampaign.commercial,[3,5]);
assert.equal(statusOfConfirmation(null,seen),"NOT_CONFIRMED");
for(const k of ["provider","source","authoritative_evidence_verified","email_subscription","consent_for_dispatch","current_status","provider_event_id"]){
 const r={...good}; delete r[k]; assert.equal(statusOfConfirmation(r,new Set()),"NOT_CONFIRMED",k);
}
assert.equal(statusOfConfirmation({...good,source:"browser_success"},new Set()),"NOT_CONFIRMED");
assert.equal(statusOfConfirmation({...good,email_subscription:"pending"},new Set()),"NOT_CONFIRMED");
assert.equal(statusOfConfirmation({...good,current_status:"unsubscribed"},new Set()),"NOT_CONFIRMED");
assert.equal(statusOfConfirmation(good,seen),"PROVIDER_CONFIRMED_TRANSITION");
assert.equal(statusOfConfirmation(good,seen),"DUPLICATE_NOT_NEW");
assert.equal(evaluateRelease(7,{}),"INVALID_ISSUE");
for(let i=1;i<=6;i++)assert.equal(evaluateRelease(i,{}),"HOLD_UNSENT");
const legal={founder_final_send_approval:true,verified_recipient_consent:true,actual_received_Jetpack_preview:true,valid_FV_postal_address:true,actual_working_unsubscribe:true};
assert.equal(evaluateRelease(1,legal),"READY_FOR_FOUNDER_MANUAL_SEND_REVIEW_ONLY");
assert.equal(evaluateRelease(3,legal),"HOLD_MERCHANT");
const merchant={merchant_named_approval:true,merchant_email_channel_rights:true,issued_earning_link_verified:true,live_mind_guide_verified:true,seller_claims_audited:true,adjacent_affiliate_disclosure_verified:true};
for(const k of Object.keys(merchant)){const p={...legal,...merchant};delete p[k];assert.equal(evaluateRelease(3,p),"HOLD_MERCHANT",k);}
assert.equal(evaluateRelease(3,{...legal,...merchant}),"READY_FOR_FOUNDER_MANUAL_SEND_REVIEW_ONLY");
assert.equal(paidMetric({}),"NOT_COMPUTABLE");
assert.equal(paidMetric({qualified_human_sessions:50,realized_net_revenue:0}),"NOT_COMPUTABLE");
const verified={independent_merchant_settlement:true,complete_purchase_reconciliation:true,refunds_and_fees_reconciled:true,qualified_human_denominator_verified:true,qualified_human_sessions:200,realized_net_revenue:25};
assert.equal(paidMetric(verified),125);
assert.equal(paidMetric({...verified,qualified_human_sessions:0}),"NOT_COMPUTABLE");
assert.equal(paidMetric({...verified,complete_purchase_reconciliation:false}),"NOT_COMPUTABLE");
console.log("R196 synthetic gate checks PASS (not live provider, email, or merchant verification)");
