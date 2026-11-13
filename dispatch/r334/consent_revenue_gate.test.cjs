'use strict';
const test=require('node:test');const assert=require('node:assert/strict');const {auditor,required,HOLD}=require('./consent_revenue_gate.cjs');
const when='2026-11-13T17:30:00Z';
const landing={type:'landing',event_id:'event_landing_001',at:when,session_ref:'sess_example_001',asset_id:'yt_change_001',utm_source:'youtube',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',quality_status:'provider_human_classified'};
const signup={type:'provider_confirmed_signup',event_id:'event_signup_001',at:when,provider:'jetpack',provider_status:'confirmed',consent_scope:'fv_dispatch',subscriber_ref:'opaque_sub_001',provider_receipt_ref:'opaque_proof_001'};
const sale={type:'merchant_paid_order',event_id:'event_order_001',at:when,issuer:'merchant_settlement_export',state:'settled',order_ref:'opaque_order_001',commission_cents:850};
const E=(events=[],receipts={})=>({synthetic:true,events,receipts});
function bad(events,err){assert.throws(()=>auditor(E(events)),new RegExp(err))}
const tests=[
 ['empty is hard hold',()=>{const r=auditor(E());assert.equal(r.release,HOLD);assert.equal(r.missing_receipts.length,14)}],
 ['all presumed receipts cannot enable sends',()=>{const x=Object.fromEntries(required.map(k=>[k,{verified:true,opaque_proof_ref:'proof_synthetic_001'}]));const r=auditor(E([landing,signup,sale],x));assert.equal(r.missing_receipts.length,0);assert.equal(r.send_authorized,false);assert.equal(r.monetization_proven,false)}],
 ['all real KPIs remain null',()=>{const r=auditor(E([landing,signup,sale]));assert.equal(r.actual_paid_orders,null);assert.equal(r.realized_net_revenue_per_1000,null);assert.equal(r.actual_confirmed_leads,null)}],
 ['qualified session candidate',()=>assert.equal(auditor(E([landing])).qa_candidates.qualified_session_candidates,1)],
 ['dedupe session candidates',()=>assert.equal(auditor(E([landing,{...landing,event_id:'event_landing_002'}])).qa_candidates.qualified_session_candidates,1)],
 ['duplicate event rejected',()=>bad([landing,landing],'DUPLICATE_EVENT_ID')],
 ['missing asset rejected',()=>bad([{...landing,asset_id:''}],'INVALID_ACQUISITION')],
 ['bad source rejected',()=>bad([{...landing,utm_source:'adbot'}],'INVALID_ACQUISITION')],
 ['bad medium rejected',()=>bad([{...landing,utm_medium:'paid_social'}],'INVALID_ACQUISITION')],
 ['bad campaign rejected',()=>bad([{...landing,utm_campaign:'random'}],'INVALID_ACQUISITION')],
 ['no human proof is not qualified',()=>assert.equal(auditor(E([{...landing,quality_status:'unknown'}])).qa_candidates.qualified_session_candidates,0)],
 ['form attempt does not confirm',()=>{const r=auditor(E([{type:'signup_attempt',event_id:'form_attempt_001',at:when}]));assert.equal(r.qa_candidates.provider_confirmed_candidates,0);assert.match(r.warnings.join(' '),/form submit/i)}],
 ['provider signup candidate',()=>assert.equal(auditor(E([signup])).qa_candidates.provider_confirmed_candidates,1)],
 ['duplicate provider subscriber deduped',()=>assert.equal(auditor(E([signup,{...signup,event_id:'event_signup_002'}])).qa_candidates.provider_confirmed_candidates,1)],
 ['wrong consent scope rejected',()=>bad([{...signup,consent_scope:'zen12_merchant'}],'UNPROVEN_LEAD')],
 ['pending is not confirmed',()=>bad([{...signup,provider_status:'pending'}],'UNPROVEN_LEAD')],
 ['wrong provider rejected',()=>bad([{...signup,provider:'inspire3'}],'UNPROVEN_LEAD')],
 ['missing provider proof rejected',()=>bad([{...signup,provider_receipt_ref:''}],'UNPROVEN_LEAD')],
 ['click never becomes sale',()=>{const r=auditor(E([{type:'affiliate_outbound',event_id:'event_click_001',at:when}]));assert.equal(r.qa_candidates.settled_order_candidates,0);assert.equal(r.monetization_proven,false)}],
 ['merchant candidate never real revenue',()=>{const r=auditor(E([sale]));assert.equal(r.qa_candidates.settled_order_candidates,1);assert.equal(r.actual_paid_orders,null)}],
 ['click proof not sufficient',()=>bad([{...sale,issuer:'web_analytics'}],'UNVERIFIED_PAID_ORDER')],
 ['pending order rejected',()=>bad([{...sale,state:'pending'}],'UNVERIFIED_PAID_ORDER')],
 ['untrusted decimal currency rejected',()=>bad([{...sale,commission_cents:8.5}],'UNVERIFIED_PAID_ORDER')],
 ['negative commission rejected',()=>bad([{...sale,commission_cents:-1}],'UNVERIFIED_PAID_ORDER')],
 ['duplicate order rejected',()=>bad([sale,{...sale,event_id:'event_order_002'}],'DUPLICATE_ORDER')],
 ['orphan refund rejected',()=>bad([{type:'merchant_refund',event_id:'event_refund_001',at:when,order_ref:'fake_order_001',refunded_commission_cents:5}],'ORPHAN_REFUND')],
 ['refund above order rejected',()=>bad([sale,{type:'merchant_refund',event_id:'event_refund_001',at:when,order_ref:'opaque_order_001',refunded_commission_cents:851}],'REFUND_EXCEEDS_ORDER')],
 ['normal refund candidate',()=>{const r=auditor(E([sale,{type:'merchant_refund',event_id:'event_refund_001',at:when,order_ref:'opaque_order_001',refunded_commission_cents:850}]));assert.equal(r.qa_candidates.refund_candidates,1);assert.equal(r.realized_net_revenue_per_1000,null)}],
 ['email field rejected',()=>assert.throws(()=>auditor(E([{...landing,recipient_email:'hidden@example.com'}])),/PII_FIELD/)],
 ['email value rejected',()=>assert.throws(()=>auditor(E([{...landing,asset_id:'foo@example.com'}])),/PII_VALUE/)],
 ['IP field rejected',()=>assert.throws(()=>auditor(E([{...landing,ip:'192.0.2.1'}])),/PII_FIELD/)],
 ['tracking URL PII rejected',()=>assert.throws(()=>auditor(E([{...landing,href:'https://example.com/?email=test'}])),/PII_VALUE/)],
 ['bad timestamp rejected',()=>bad([{...landing,at:'2026-11-13'}],'BAD_EVENT_SCHEMA')],
 ['invalid time rejected',()=>bad([{...landing,at:'2026-99-99T00:00:00Z'}],'INVALID_TIME')],
 ['non-synthetic forbidden',()=>assert.throws(()=>auditor({synthetic:false,events:[]}),/SYNTHETIC_EVENTS/)],
 ['receipt booleans alone not evidence',()=>{const r=auditor(E([],{founder_campaign_approval:{verified:true}}));assert.ok(r.missing_receipts.includes('founder_campaign_approval'))}],
 ['no active link or send decision anywhere',()=>{const r=auditor(E([landing,signup,sale]));assert.equal(r.affiliate_activation_authorized,false);assert.equal(r.post_publication_authorized,false)}]
];
for(const [name,fn] of tests)test(name,fn);
