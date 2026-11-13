'use strict';
const test=require('node:test'); const assert=require('node:assert/strict');
const {checkEvent,signupDecision,evaluateSynthetic}=require('./signup_boundary.cjs');
const valid={kind:'provider_signup',synthetic_key:'synthetic-person1',origin:'authenticated_wp_provider',newsletter_consent:true,
  email_subscription_status:'Subscribed',confirmation_mode:'email_link_verified',wp_account_preverified:false,
  source_surface:'focus',proof_id:'synthetic-proof-1'};
function caseOf(change){return {...valid,...change};}
const wp=caseOf({synthetic_key:'synthetic-person2',proof_id:'synthetic-proof-2',confirmation_mode:'preverified_wp_account',wp_account_preverified:true});
test('1 synthetic provider-linked confirmation is accepted',()=>assert.equal(signupDecision(valid).accepted,true));
test('2 preverified WordPress.com account path is accepted without a new email challenge',()=>assert.equal(signupDecision(wp).accepted,true));
test('3 preverified account unsupported without account verification',()=>assert.equal(signupDecision(caseOf({confirmation_mode:'preverified_wp_account'})).accepted,false));
test('4 conflicting account/email challenge modes rejected',()=>assert.equal(signupDecision(caseOf({wp_account_preverified:true})).accepted,false));
test('5 mere signup click not provider confirmation',()=>assert.equal(signupDecision(caseOf({kind:'signup_attempt'})).accepted,false));
test('6 no authenticated provider origin',()=>assert.equal(signupDecision(caseOf({origin:'unverified_browser'})).accepted,false));
test('7 unconfirmed status not recipient',()=>assert.equal(signupDecision(caseOf({email_subscription_status:'Not confirmed'})).accepted,false));
test('8 bounced status not recipient',()=>assert.equal(signupDecision(caseOf({email_subscription_status:'Bounced'})).accepted,false));
test('9 paused email status not recipient',()=>assert.equal(signupDecision(caseOf({email_subscription_status:'Emails paused'})).accepted,false));
test('10 consent unproved',()=>assert.equal(signupDecision(caseOf({newsletter_consent:false})).accepted,false));
test('11 consent missing',()=>assert.equal(signupDecision(caseOf({newsletter_consent:undefined})).accepted,false));
test('12 proof absent',()=>assert.equal(signupDecision(caseOf({proof_id:undefined})).accepted,false));
test('13 unknown surface excluded',()=>assert.equal(signupDecision(caseOf({source_surface:'merchant'})).accepted,false));
test('14 valid surface dispatch',()=>assert.equal(signupDecision(caseOf({source_surface:'dispatch'})).accepted,true));
test('15 direct PDF download is not signup',()=>assert.equal(signupDecision(caseOf({kind:'fieldbook_download'})).accepted,false));
test('16 merchant newsletter opt in is not signup',()=>assert.equal(signupDecision(caseOf({kind:'merchant_optin'})).accepted,false));
test('17 WP.com follower is not automatically email subscribed',()=>assert.equal(signupDecision(caseOf({kind:'wpcom_follower'})).accepted,false));
test('18 email address key excluded',()=>assert.equal(checkEvent(caseOf({email:'private@example.org'})),'PII_OR_UNKNOWN_FIELD'));
test('19 email hash excluded',()=>assert.equal(checkEvent(caseOf({email_hash:'0'.repeat(64)})),'PII_OR_UNKNOWN_FIELD'));
test('20 phone excluded',()=>assert.equal(checkEvent(caseOf({phone:'+1123'})),'PII_OR_UNKNOWN_FIELD'));
test('21 recipient key excluded',()=>assert.equal(checkEvent(caseOf({recipient:'x'})),'PII_OR_UNKNOWN_FIELD'));
test('22 nested payload excluded',()=>assert.equal(checkEvent(caseOf({proof_id:{id:'synthetic-proof-1'}})),'NESTED_PAYLOAD_REJECTED'));
test('23 non synthetic actual IDs excluded',()=>assert.equal(checkEvent(caseOf({synthetic_key:'1234567'})),'NOT_SYNTHETIC'));
test('24 duplicate provider key counts once',()=>assert.equal(evaluateSynthetic([valid,caseOf({proof_id:'synthetic-proof-3'})]).synthetic_confirmed_signup_events,1));
test('25 duplicate proof with new key counts once',()=>assert.equal(evaluateSynthetic([valid,caseOf({synthetic_key:'synthetic-person3'})]).synthetic_confirmed_signup_events,1));
test('26 different modes each count once with distinct synthetic identities',()=>assert.equal(evaluateSynthetic([valid,wp]).synthetic_confirmed_signup_events,2));
test('27 PDF and merchant signup do not increment confirmed',()=>{
 const r=evaluateSynthetic([{kind:'fieldbook_download',synthetic_key:'synthetic-file'}, {kind:'merchant_optin',synthetic_key:'synthetic-merchant'}]);
 assert.equal(r.synthetic_confirmed_signup_events,0); assert.equal(r.synthetic_downloads,1);assert.equal(r.synthetic_merchant_optins,1);
});
test('28 welcome alone is not provider-confirmed consent',()=>{
 const r=evaluateSynthetic([{kind:'welcome_received',synthetic_key:'synthetic-welcome',origin:'independent_recipient_witness',proof_id:'synthetic-proof-welcome'}]);
 assert.equal(r.synthetic_confirmed_signup_events,0);assert.equal(r.synthetic_welcome_receipts,1);
});
test('29 ambiguous 3/3/2 total is not eligible-recipients estimate',()=>{
 const r=evaluateSynthetic([], {total:3,confirmed:3,unconfirmed:2});assert.equal(r.overlapping_counts_observed,true);
 assert.equal(r.actually_eligible_email_recipients,null);
});
test('30 even all synthetic proof leaves actual revenue null and send disabled',()=>{
 const r=evaluateSynthetic([valid,wp]);assert.equal(r.net_revenue,null);assert.equal(r.sender_authorized,false);
 assert.equal(r.revenue_per_1000_qualified_humans,null);
});
test('31 no producer events implies no real-world zero claim',()=>assert.equal(evaluateSynthetic([]).actual_confirmed_signups,null));
test('32 oversized synthetic batch refused',()=>assert.throws(()=>evaluateSynthetic(Array(1001).fill(valid))));
test('33 rejects unknown external paid order state',()=>assert.equal(evaluateSynthetic([caseOf({kind:'paid_order'})]).verified_paid_orders,null));
test('34 output excludes PII and actual identities',()=>{
 const r=evaluateSynthetic([valid]); assert.equal(JSON.stringify(r).includes('person1'),false);
});
test('35 empty no confirmation mode rejected',()=>assert.equal(signupDecision(caseOf({confirmation_mode:undefined})).accepted,false));
test('36 wordpress.com account verification cannot replace subscription consent',()=>assert.equal(signupDecision({...wp,newsletter_consent:false}).accepted,false));
