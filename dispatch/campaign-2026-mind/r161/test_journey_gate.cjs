'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {review,EVIDENCE}=require('./journey_gate.cjs');
const full=Object.fromEntries(EVIDENCE.map(k=>[k,true]));
const empty=Object.fromEntries(EVIDENCE.map(k=>[k,false]));
test('all-false observed evidence hard-holds without inventing sales or subscribers',()=>{
 const r=review(empty);assert.equal(r.release,'HOLD_UNSENT');assert.equal(r.next_action,'VERIFY_PROVIDER_CONSENT_ELIGIBILITY');assert.deepEqual(r.visitor_subscription_events,[]);assert.equal(r.realized_net_revenue,null);assert.equal(r.email_eligibility_count,null);assert.deepEqual(r.issue_mix.editorial,[1,2,4,6]);assert.deepEqual(r.issue_mix.commercial_review_pending,[3,5]);
});
test('even perfect hypothetical attestations cannot send mail',()=>{
 const r=review(full);assert.equal(r.sent,false);assert.equal(r.release,'HOLD_UNSENT');assert.equal(r.next_action,'MANUAL_RELEASE_WORKFLOW_ONLY');assert.equal(r.ready_for_manual_review,true);assert.deepEqual(r.purchases,[]);
});
test('no subscriber addresses, arbitrary keys, or made-up trust values',()=>{
 for(const data of [{email:'person@example.com'}, {confirmed:true}, {provider_email_eligibility:'yes'}, {approved_earning_link:1}, {welcome_received:'person@example.com'},null,[]])assert.throws(()=>review(data));
});
test('missing essential proof blocks precisely its dependency stage',()=>{
 const step={provider_email_eligibility:'VERIFY_PROVIDER_CONSENT_ELIGIBILITY',provider_confirmed_transition:'VERIFY_PROVIDER_CONSENT_ELIGIBILITY',welcome_received:'VERIFY_RECEIVED_WELCOME_AND_DOWNLOAD',fieldbook_retrieved:'VERIFY_RECEIVED_WELCOME_AND_DOWNLOAD',native_jetpack_preview:'VERIFY_REAL_RENDERED_EMAIL_FOOTER',fv_postal_verified:'VERIFY_REAL_RENDERED_EMAIL_FOOTER',unsubscribe_verified:'VERIFY_REAL_RENDERED_EMAIL_FOOTER',approved_partner_account:'VERIFY_NAMED_MERCHANT_APPROVAL',explicit_email_permission:'VERIFY_NAMED_MERCHANT_APPROVAL',approved_earning_link:'VERIFY_NAMED_MERCHANT_APPROVAL',live_vetted_warmup_guide:'VERIFY_NAMED_MERCHANT_APPROVAL',current_product_terms:'VERIFY_NAMED_MERCHANT_APPROVAL',adjacent_commercial_disclosure:'VERIFY_NAMED_MERCHANT_APPROVAL',founder_final_campaign_approval:'REQUEST_FOUNDER_FINAL_CAMPAIGN_APPROVAL'};
 for(const k of EVIDENCE){for(const value of [false,null]){const x={...full,[k]:value},r=review(x);assert.equal(r.ready_for_manual_review,false,k);assert.equal(r.next_action,step[k],k);assert.equal(r.sent,false,k);assert.ok(Object.values(r.stages).some(s=>s.includes(k)));}}
});
test('cannot promote unverified seller terms, email rights or non-live guide',()=>{
 const x={...full, current_product_terms:false,explicit_email_permission:false,live_vetted_warmup_guide:false};const r=review(x);assert.equal(r.next_action,'VERIFY_NAMED_MERCHANT_APPROVAL');assert.deepEqual(r.stages.merchant_missing,['explicit_email_permission','live_vetted_warmup_guide','current_product_terms']);
});
test('canonical 4:2 campaign allocation remains reserved',()=>{
 const r=review(full);assert.equal(r.issue_mix.editorial.length,4);assert.equal(r.issue_mix.commercial_review_pending.length,2);assert.equal(r.issue_mix.commercial_review_pending[0],3);
});
test('null is unknown, not affirmation',()=>{
 const r=review({provider_email_eligibility:null,provider_confirmed_transition:null});assert.equal(r.ready_for_manual_review,false);assert.equal(r.stages.consent_missing.length,2);
});
