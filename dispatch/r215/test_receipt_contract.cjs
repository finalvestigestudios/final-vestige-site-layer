'use strict';
const assert=require('node:assert/strict');
const {ISSUE_TYPES,campaignLink,classifyNewsletter,confirmedSignup,evaluateRevenue,editionGate}=require('./receipt_contract.cjs');
let n=0;function check(condition,message){assert.ok(condition,message);n++;}
const cases=Object.entries(ISSUE_TYPES);
check(cases.length===6,'six issues');check(cases.filter(x=>x[1]==='editorial').length===4,'four editorial');check(cases.filter(x=>x[1]==='commercial').length===2,'two held commercial');
for (const [i] of cases){const u=new URL(campaignLink(i,'https://finalvestige.com/2026/11/02/change-blindness/'));check(u.searchParams.get('utm_content')==='issue_'+i,'issue slug');check(u.searchParams.get('utm_source')==='dispatch'&&u.searchParams.get('utm_medium')==='email','email-specific source/medium');check(!u.searchParams.has('email'),'no PII');}
for(const bad of ['https://zen12.com/hnp','http://finalvestige.com/focus/','https://finalvestige.com/focus/?email=x','https://finalvestige.com/subscribe','https://finalvestige.com/path#anchor','https://fakefinalvestige.com/']){assert.throws(()=>campaignLink('01',bad));n++;}
assert.throws(()=>campaignLink('07','https://finalvestige.com/'));n++;
const c=classifyNewsletter({total:3,confirmed:3,unconfirmed:2,suppressed:0,paid:0});check(c.emailEligible==='UNKNOWN','never fabricate recipient eligibility');check(c.nonadditive===true,'nonadditive counters');
const good={provider_confirmed:true,email_subscription_active:true,suppressed:false,pending:false,repeat:false,reader_only:false};check(confirmedSignup(good)===1,'genuine provider active confirmation');
for(const k of Object.keys(good)){const changed={...good,[k]:!good[k]};check(confirmedSignup(changed)===0,'false or duplicate confirmation refused: '+k);}
const goodFin={qualified_human_sessions:100,settled_paid_orders:1,verified_gross:10,verified_fees:2,verified_refunds:0,verified_chargebacks:0,partner_attribution_verified:true};
check(evaluateRevenue(goodFin).net_per_1000===80,'net paid conversion');
check(evaluateRevenue({...goodFin,settled_paid_orders:0,verified_gross:0,verified_fees:0}).net_per_1000===0,'valid realized zero');
check(evaluateRevenue({...goodFin,verified_refunds:20}).net_per_1000===-120,'negative net allowed');
check(evaluateRevenue({...goodFin,partner_attribution_verified:false}).status==='NOT_COMPUTABLE','click != sale');
check(evaluateRevenue({...goodFin,verified_fees:null}).status==='NOT_COMPUTABLE','missing fees != zero');
check(evaluateRevenue({...goodFin,qualified_human_sessions:0}).status==='NOT_COMPUTABLE','no denominator');
check(evaluateRevenue({...goodFin,settled_paid_orders:0}).status==='NOT_COMPUTABLE','gross contradiction');
const g=editionGate('01');check(g.status==='HOLD'&&g.missing.includes('founder_final_send_approval'),'founder gate');
const m=editionGate('03');check(m.missing.includes('email_channel_permission')&&m.missing.includes('published_vetted_guide'),'merchant gates');
const all={founder_final_send_approval:true,provider_eligible_audience_verified:true,received_email_verified:true,publisher_postal_verified:true,unsubscribe_function_verified:true,consent_scope_verified:true,named_partner_acceptance:true,email_channel_permission:true,issued_earning_url:true,published_vetted_guide:true,checkout_terms_verified:true};
check(editionGate('03',all).status==='CANDIDATE_FOR_FINAL_HUMAN_REVIEW','never auto-authorize');check(editionGate('03',all).not_authorization===true,'final human approval not bypassed');
console.log('PASS',n,'native Node R215 offline assertions (NO WORDPRESS OR EMAIL ACTION)');
