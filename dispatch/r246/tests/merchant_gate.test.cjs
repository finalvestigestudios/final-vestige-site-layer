"use strict";
const {evaluateEvidence}=require("../merchant_gate.cjs");
const assert=require("node:assert/strict");
const test=require("node:test");
const base=()=>({
 original_campaign_ref:"d57ccdba3aee8f065e143e101c2945f4f3d01647",
 pilot_mix:{editorial:4,commercial:2},
 current_state:{all_sends_hold:true,wp_new_post_auto_send_off:true},
 documents:{},
 seller_pages:[
 {product:"Zen12",page_url:"https://zen12.com/hnp",price_usd:87.99},
 {product:"Zen12",page_url:"https://zen12.com/secret/",price_usd:37}
 ],
 authorized_earning_destination_verified:false,
 consent:{confirmed_signup_provider_transition_verified:false},
 revenue:{independent_settled_orders_verified:false}
});
test("unverified baseline retains all campaign holds",()=>{const r=evaluateEvidence(base());assert.equal(r.status,"HOLD_UNSENT");assert.equal(r.verified_paid_orders,null);assert.ok(r.blockers.includes("ZEN12_PAGE_PRICE_VARIANCE_REQUIRES_EXACT_CHECKOUT_MATCH"));});
test("every missing authority gate is separately explained",()=>{const r=evaluateEvidence(base());for(const k of ["partner_named_acceptance","partner_email_channel_permission","issued_earning_link","specific_seller_checkout_price","specific_seller_refund_terms","approved_live_warmup_guide","provider_eligible_status_aggregate","welcome_received_independently","publisher_postal_address","real_jetpack_preview","unsubscribe_in_received_email","founder_campaign_release"])assert.ok(r.blockers.some(x=>x.endsWith(":"+k)),k);});
test("invented approval booleans cannot cause release",()=>{const p=base();p.authorized_earning_destination_verified=true;p.consent.confirmed_signup_provider_transition_verified=true;p.revenue.independent_settled_orders_verified=true;assert.equal(evaluateEvidence(p).status,"HOLD_UNSENT");assert.equal(evaluateEvidence(p).verified_paid_orders,null);});
test("even forged documentary records cannot cause release",()=>{const p=base();const names={partner_named_acceptance:"merchant_account",partner_email_channel_permission:"merchant_account",issued_earning_link:"merchant_account",specific_seller_checkout_price:"merchant_checkout",specific_seller_refund_terms:"merchant_checkout",approved_live_warmup_guide:"site_owner",provider_eligible_status_aggregate:"wp_subscriber_status",welcome_received_independently:"received_inbox",publisher_postal_address:"publisher",real_jetpack_preview:"wp_native_preview",unsubscribe_in_received_email:"received_inbox",founder_campaign_release:"founder"};for(const [k,issuer] of Object.entries(names))p.documents[k]={state:"verified",ref:"FAKE-REVIEW-00001",issuer,observed_utc:"2026-11-09T00:00:00Z"};assert.equal(evaluateEvidence(p).status,"HOLD_UNSENT");assert.ok(evaluateEvidence(p).blockers.includes("NON_SENDING_DOC_REVIEW_ONLY"));});
test("unexpected pilot ratio is rejected",()=>{const p=base();p.pilot_mix.commercial=3;assert.ok(evaluateEvidence(p).blockers.includes("PILOT_4_2_CHANGED"));});
test("original source SHA drift is rejected",()=>{const p=base();p.original_campaign_ref="FAKE";assert.ok(evaluateEvidence(p).blockers.includes("ORIGINAL_SOURCE_IDENTITY_NOT_LOCKED"));});
test("auto-send cannot be marked on",()=>{const p=base();p.current_state.wp_new_post_auto_send_off=false;assert.ok(evaluateEvidence(p).blockers.includes("POST_AUTO_SEND_NOT_CONFIRMED_OFF"));});
test("missing two distinct seller pages is rejected",()=>{const p=base();p.seller_pages.pop();assert.ok(evaluateEvidence(p).blockers.includes("SELLER_PAGE_DIFFERENCE_NOT_DOCUMENTED"));});
test("nonmatching merchant domain is rejected",()=>{const p=base();p.seller_pages[1].page_url="https://example.com/secret/";assert.ok(evaluateEvidence(p).blockers.includes("SELLER_PAGE_DIFFERENCE_NOT_DOCUMENTED"));});
test("non-numeric price is rejected",()=>{const p=base();p.seller_pages[1].price_usd="37";assert.ok(evaluateEvidence(p).blockers.includes("SELLER_PAGE_DIFFERENCE_NOT_DOCUMENTED"));});
test("no invented zero net revenue",()=>{const r=evaluateEvidence(base());assert.equal(r.verified_net_revenue_usd,null);assert.equal(r.realized_net_revenue_per_1000_human_sessions,null);});
test("does not accept malformed input",()=>{assert.throws(()=>evaluateEvidence(null));assert.throws(()=>evaluateEvidence([]));});
