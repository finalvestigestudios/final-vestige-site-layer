'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {review,resultBase,MASKED_FIELDS,PRIVATE_FIELDS}=require('./proof_gate_v3.js');
const base=()=>({schema:'FV-DISPATCH-COHORT-V2',mode:'external_aggregate',as_of_day:'2026-11-10',
 attestations:{complete_qualified_sessions:true,jetpack_confirmations_verified:true,
 merchant_settlements_reconciled:true,cohort_attribution_verified:true,
 publisher_postal_and_unsubscribe_verified:false,partner_email_permission_verified:false,
 founder_campaign_approval:false},
 sessions:[{day:'2026-11-10',utm_source:'tiktok',utm_medium:'organic_social',
 utm_campaign:'mind_pilot_2026_11',utm_content:'asset_123',attribution_class:'tagged_asset',qualified_human_sessions:100}],
 confirmations:[{day:'2026-11-10',provider:'jetpack',event_ref:'evt_xyz',status:'confirmed',consent_scope:'fv_dispatch'}],
 settlements:[{acquisition_day:'2026-11-10',settled_day:'2026-11-10',merchant:'inspire3',
 order_ref:'order_xyz',utm_source:'tiktok',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',
 utm_content:'asset_123',attribution_class:'tagged_asset',status:'settled',gross_cents:100,refund_cents:100,fee_cents:5}]});
function secure(x){assert.equal(x.release,'HOLD_UNSENT');
 for(const key of ['send_authorized','merchant_link_authorized','campaign_approved','authenticated_merchant_sale','confirmed_signup_verified','realized_net_revenue_verified'])assert.equal(x[key],false);
 assert.equal(x.external_metrics,'NOT_COMPUTABLE');assert.equal(x.eligible_recipient_count,null);
 for(const k of MASKED_FIELDS)assert.equal(Object.hasOwn(x,k),false,k);
 const j=JSON.stringify(x);for(const p of ['order_xyz','evt_xyz','asset_123','@'])assert(!j.includes(p),'PII/reference leaked: '+p);
}
test('synthetic remains hold and labelled, with negative net example',()=>{
 const x=base();x.mode='synthetic';const r=review(x);secure(r);
 assert.equal(r.valid,true);assert.equal(r.reason,'SYNTHETIC_EXAMPLE_ONLY');
 assert.equal(r.demonstration['7d'].all_values_hypothetical,true);
 assert.equal(r.demonstration['7d'].example_net_cents,-5);
 assert.equal(r.demonstration['7d'].example_net_cents_per_1000,-50);
});
test('caller-supplied external attestations never establish real net revenue',()=>{
 const r=review(base());secure(r);assert.equal(r.valid,true);
 assert.equal(r.demonstration,null);assert.equal(r.evidence_type,'CALLER_SUPPLIED_EXTERNAL_DATA_NOT_AUTHENTICATED');
});
test('returns no fake zeros if session denominator is missing',()=>{
 const x=base();x.sessions=[];const r=review(x);secure(r);assert.equal(r.demonstration,null);
});
test('all unsupported modes fail closed',()=>{for(const m of [null,'verified_real','paid','live',''] ){
 const x=base();x.mode=m;const r=review(x);secure(r);assert.equal(r.valid,false);}});
test('invalid schema fails closed',()=>{for(const shape of [null,{},[],{schema:'X'},'external']){
 const r=review(shape);secure(r);assert.equal(r.valid,false);}});
test('disallow unapproved send permissions even under a synthetic sample',()=>{
 for(const k of ['publisher_postal_and_unsubscribe_verified','partner_email_permission_verified','founder_campaign_approval']){
 const x=base();x.mode='synthetic';x.attestations[k]=true;const r=review(x);secure(r);assert.equal(r.valid,false);
 }});
test('refuse fabricated source types and confirmation providers',()=>{
 const variants=[(x)=>x.confirmations[0].provider='zen12',(x)=>x.confirmations[0].consent_scope='zen12',
 (x)=>x.settlements[0].merchant='unverified', (x)=>x.sessions[0].utm_source='unknown',
 (x)=>x.settlements[0].gross_cents=-1, (x)=>x.sessions[0].day='2026-11-32'];
 for(const change of variants){const x=base();change(x);const r=review(x);secure(r);assert.equal(r.valid,false);}
});
test('reject repeated conflicting confirmation references and duplicate sessions',()=>{
 const a=base();a.confirmations.push({...a.confirmations[0],status:'pending'});
 const b=base();b.sessions.push({...b.sessions[0]});
 for(const x of [a,b]){const r=review(x);secure(r);assert.equal(r.valid,false);}
});
test('cannot assert independent merchant sale by changing record status',()=>{
 for(const s of ['settled','refunded','pending']){
 const x=base();x.settlements[0].status=s;const r=review(x);secure(r);
 assert.equal(r.valid,true);assert.equal(r.demonstration,null);
 }});
test('no raw identifiers, emails or subscriber PII in status',()=>{
 const r=review(base());secure(r);for(const k of PRIVATE_FIELDS)assert.equal(Object.hasOwn(r,k),false);
});
test('never authenticate mock provider events even with valid route and attestation booleans',()=>{
 const x=base();x.confirmations[0].status='confirmed';x.attestations.jetpack_confirmations_verified=true;
 const r=review(x);secure(r);assert.equal(r.confirmed_signup_verified,false);
});
test('no proof of email delivery or physical mailing address from data',()=>{
 const r=review(base());secure(r);assert.equal(r.publisher_postal,'NOT_VERIFIED');
 assert.equal(r.unsubscribe_function,'NOT_VERIFIED');assert.equal(r.jetpack_rendering,'NOT_VERIFIED');
});
test('read-only constraints apply even if no data',()=>{const r=resultBase();secure(r);});
