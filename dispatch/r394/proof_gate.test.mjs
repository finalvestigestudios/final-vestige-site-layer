import test from "node:test";
import assert from "node:assert/strict";
import {evaluateIssue,confirmedSignupCount,settledNetPer1000,SEND_AUTHORIZED} from "./proof_gate.mjs";
const fields=["provider_eligible_count","welcome_receipt","native_preview","postal_address",
"unsubscribe_verified","editorial_sources","founder_final_approval"];
const commerce=["named_publisher_approval","specific_sku","email_channel_permission",
"approved_merchant_creative","issued_earning_url","live_vetted_guide",
"referred_checkout_terms","near_offer_disclosure"];
const good=Object.fromEntries([...fields,...commerce,"apollo_14_second_copy_correction"].map(x=>[x,true]));
test("SENDING NEVER AUTHORIZED",()=>assert.equal(SEND_AUTHORIZED,false));
for(let i=1;i<=6;i++){
 test("pilot issue "+i+" defaults to hard HOLD",()=>{
  const x=evaluateIssue(i,{});
  assert.equal(x.state,"HOLD_UNSENT");assert.equal(x.send_authorized,false);
  assert.ok(x.missing.length>=fields.length);
 });
 test("pilot issue "+i+" all proof still cannot send",()=>{
  const x=evaluateIssue(i,good);
  assert.equal(x.send_authorized,false);
  assert.equal(x.eligible_for_human_review,true);
 });
}
test("commercial isolated from editorial",()=>{
 assert.equal(evaluateIssue(2,Object.fromEntries(fields.map(x=>[x,true]))).eligible_for_human_review,true);
 assert.equal(evaluateIssue(3,Object.fromEntries(fields.map(x=>[x,true]))).eligible_for_human_review,false);
});
test("Apollo chronology requires dedicated correction",()=>{
 const p={...good,apollo_14_second_copy_correction:false};
 assert.ok(evaluateIssue(4,p).missing.includes("apollo_14_second_copy_correction"));
});
for(const f of [...fields,...commerce]){
 test("removing proof "+f+" blocks eligible-for-review",()=>{
  const e=evaluateIssue(3,{...good,[f]:false});
  assert.ok(e.missing.includes(f));
  assert.equal(e.eligible_for_human_review,false);
 });
}
test("invalid issue is rejected",()=>assert.throws(()=>evaluateIssue(7,good)));
const event={origin:"jetpack_provider",kind:"newly_eligible_transition",prior_status:"Not confirmed",
 new_status:"Subscribed",consent_recorded:true,provider_event_id:"evt_opaque_a",
 opaque_subscriber_key:"sub_opaque_a",confirmed_at:"2026-11-15T19:00:00Z"};
test("new eligible provider transition counted",()=>assert.equal(confirmedSignupCount([event]),1));
test("duplicates deduplicated by event and opaque subscriber",()=>{
 assert.equal(confirmedSignupCount([event,event,{...event,provider_event_id:"evt_opaque_b"}]),1);
});
for(const key of ["origin","kind","new_status","consent_recorded","provider_event_id",
"opaque_subscriber_key","confirmed_at"]){
 test("invalid signup "+key+" discarded",()=>assert.equal(confirmedSignupCount([
  {...event,[key]:key==="consent_recorded"?false:""}]),0));
}
test("known previous subscribed user not a new lead",()=>assert.equal(
 confirmedSignupCount([{...event,prior_status:"Subscribed"}]),0));
test("form click/download not confirmation",()=>assert.equal(confirmedSignupCount([
 {...event,kind:"pdf_download"}]),0));
test("empty provider list is zero confirmed transitions, not subscriber stock",()=>assert.equal(confirmedSignupCount([]),0));
test("missing ledger is NOT_COMPUTABLE",()=>assert.equal(settledNetPer1000({
 qualified_human_sessions:100,sessions_audited:true}).status,"NOT_COMPUTABLE"));
test("unknown sessions is NOT_COMPUTABLE",()=>assert.equal(settledNetPer1000({
 qualified_human_sessions:0,sessions_audited:true,settlements:[]}).status,"NOT_COMPUTABLE"));
test("unverified settlement cannot become sales",()=>assert.equal(settledNetPer1000({
 qualified_human_sessions:100,sessions_audited:true,settlements:[{
 provider_verified:false,status:"settled",settlement_id:"s",commission_cents:500,
 refund_cents:0,fee_cents:0,reversal_cents:0}]}).status,"NOT_COMPUTABLE"));
test("verified paid net subtracts reversals and fees, dedupes IDs",()=>{
 const s={provider_verified:true,status:"settled",settlement_id:"one",commission_cents:1000,
 refund_cents:100,fee_cents:50,reversal_cents:250};
 const r=settledNetPer1000({qualified_human_sessions:200,sessions_audited:true,settlements:[s,s]});
 assert.equal(r.status,"COMPUTABLE");assert.equal(r.net_revenue_cents,600);
 assert.equal(r.revenue_per_1000_sessions_usd,30);assert.equal(r.verified_settlements,1);
});
