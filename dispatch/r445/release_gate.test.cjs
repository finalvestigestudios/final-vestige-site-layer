"use strict";
const test=require("node:test"); const assert=require("node:assert/strict");
const {newConfirmedSignup,editionGate,realizedRevenueMetric}=require("./release_gate.cjs");
const key="hmac-sha256:"+"c".repeat(64);
const validEvent={provider:"wordpress_jetpack",transition:"new_confirmed_email_subscribed",
  email_status:"subscribed",previous_email_status:"unconfirmed",consent_scope:"dispatch_updates",
  was_existing:false,private_subject_key:key,provider_transition_id:"jetpack-transition-001",
  confirmed_at:"2026-11-18T10:00:00Z"};
test("new provider-confirmed unique transition counts exactly once",()=>{
 const seen=new Set(); assert.equal(newConfirmedSignup(validEvent,seen).counted,true);
 assert.equal(newConfirmedSignup(validEvent,seen).reason,"duplicate")});
for(const [name,change] of [
 ["click instead of provider transition",{transition:"focus_signup_click"}],
 ["pdf access",{transition:"focus_pdf_click"}],
 ["reader follow",{transition:"reader_follow",email_status:"reader"}],
 ["previous subscriber",{previous_email_status:"subscribed",was_existing:true}],
 ["consent not scoped",{consent_scope:"unspecified"}],
 ["existing account",{was_existing:true}],
 ["private key absent",{private_subject_key:"unsafe@example.com"}],
 ["provider receipt absent",{provider_transition_id:"x"}],
 ["confirmation timestamp absent",{confirmed_at:""}]
])test("reject "+name,()=>assert.equal(newConfirmedSignup({...validEvent,...change}).counted,false));
test("empty release entirely held",()=>{let x=editionGate({issue:6});assert.equal(x.ready,false);assert.ok(x.holds.includes("publisher_postal"));assert.ok(x.holds.includes("real_native_preview"));});
test("commercial issue 03 requires Zen12 not Total Focus",()=>{const x=editionGate({issue:3,exact_product:"Total Focus"});assert.ok(x.holds.includes("product_identity"));assert.ok(x.holds.includes("email_channel_rights"));});
test("commercial issue 05 requires Hypnosis Live",()=>assert.ok(editionGate({issue:5,exact_product:"Zen12"}).holds.includes("product_identity")));
test("four editorial slots bypass ONLY merchant-specific gate",()=>{for(const n of [1,2,4,6]){let x=editionGate({issue:n});assert.equal(x.commercial,false);assert.equal(x.ready,false);assert.equal(x.holds.includes("email_channel_rights"),false);}});
test("manually claimed approvals without evidence never release",()=>{const x=editionGate({issue:3,publisher_postal_witness:true,rendered_unsubscribe_witness:true,
native_jetpack_preview_witness:true,consent_and_audience_witness:true,founder_final_approval:true,
named_partner_approved:true,email_marketing_authorized:true,exact_sku_terms_checked:true,
vetted_guide_live:true,merchant_earning_url_verified:true,proximate_disclosure_witness:true,
exact_product:"Zen12",approved_guide_url:"https://finalvestige.com/not-verified/"});
assert.equal(x.ready,false);assert.ok(x.holds.includes("named_partner_approval"));});
test("revenue requires real sessions",()=>assert.equal(realizedRevenueMetric({orders:[]}).computable,false));
test("revenue requires settlement data",()=>assert.equal(realizedRevenueMetric({qualified_human_sessions_verified:true,qualified_human_sessions:10}).computable,false));
test("revenue never counts affiliate click",()=>assert.equal(realizedRevenueMetric({qualified_human_sessions_verified:true,qualified_human_sessions:10,
settlement_export_verified:true,cohort:"7d",orders:[{status:"clicked",gross:1,fees:0,refunds:0,provider_receipt_ref:"merchant-receipt-01"}]}).computable,false));
test("synthetic settled economics only",()=>{let r=realizedRevenueMetric({qualified_human_sessions_verified:true,qualified_human_sessions:200,
settlement_export_verified:true,cohort:"30d",orders:[{status:"settled",gross:17,fees:2,refunds:5,provider_receipt_ref:"mock-provider-receipt-01"}]});
assert.equal(r.computable,true);assert.equal(r.net,10);assert.equal(r.net_per_1000_qualified_sessions,50);});
test("unknown cohort rejected",()=>assert.equal(realizedRevenueMetric({qualified_human_sessions_verified:true,qualified_human_sessions:1,settlement_export_verified:true,cohort:"1d",orders:[]}).computable,false));
test("zero denominators never become fake conversion rates",()=>assert.equal(realizedRevenueMetric({qualified_human_sessions_verified:true,qualified_human_sessions:0,settlement_export_verified:true,cohort:"7d",orders:[]}).computable,false));
