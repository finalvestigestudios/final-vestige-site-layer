'use strict';
const assert = require('node:assert/strict');
const {inspection}=require('./cohort_audit');
const base=()=>({
 schema:'FV-DISPATCH-COHORT-V1',mode:'synthetic',as_of_day:'2026-11-10',
 attestations:{complete_qualified_sessions:true,jetpack_confirmations_verified:true,merchant_settlements_reconciled:true,cohort_attribution_verified:true,publisher_postal_and_unsubscribe_verified:false,partner_email_permission_verified:false,founder_campaign_approval:false},
 sessions:[{day:'2026-11-06',platform:'youtube',campaign:'cluster_pilot_2026_11',asset_id:'yt_001',qualified_human_sessions:100},
 {day:'2026-10-17',platform:'tiktok',campaign:'cluster_pilot_2026_11',asset_id:'tt_001',qualified_human_sessions:200}],
 confirmations:[{day:'2026-11-07',provider:'jetpack',event_ref:'event_01',status:'confirmed',consent_scope:'fv_dispatch'},
 {day:'2026-11-07',provider:'jetpack',event_ref:'event_01',status:'confirmed',consent_scope:'fv_dispatch'},
 {day:'2026-11-08',provider:'jetpack',event_ref:'event_02',status:'pending',consent_scope:'fv_dispatch'}],
 settlements:[{acquisition_day:'2026-11-06',settled_day:'2026-11-09',merchant:'inspire3',order_ref:'order_01',origin_platform:'youtube',campaign:'cluster_pilot_2026_11',asset_id:'yt_001',status:'settled',gross_commission_cents:1200,refund_cents:100,fee_cents:50},
 {acquisition_day:'2026-10-17',settled_day:'2026-11-01',merchant:'inspire3',order_ref:'order_02',origin_platform:'tiktok',campaign:'cluster_pilot_2026_11',asset_id:'tt_001',status:'settled',gross_commission_cents:2000,refund_cents:200,fee_cents:100}]
});
const cases=[];
function test(name,fn){cases.push([name,fn]);}
const mutate=(f)=>{const x=base();f(x);return inspection(x);};
test('valid synthetic ledger holds send',()=>{const r=inspection(base());assert(r.pass);assert.equal(r.state,'HOLD_UNSENT');assert.equal(r.send_authorized,false);});
test('7d start inclusive',()=>assert.equal(inspection(base()).cohorts['7d'].period_start,'2026-11-04'));
test('30d start inclusive',()=>assert.equal(inspection(base()).cohorts['30d'].period_start,'2026-10-12'));
test('7d human sessions',()=>assert.equal(inspection(base()).cohorts['7d'].qualified_human_sessions,100));
test('30d human sessions',()=>assert.equal(inspection(base()).cohorts['30d'].qualified_human_sessions,300));
test('duplicated confirmation event counts once',()=>assert.equal(inspection(base()).cohorts['7d'].deduped_confirmed_signups,1));
test('pending signup not counted',()=>assert.equal(inspection(base()).cohorts['30d'].deduped_confirmed_signups,1));
test('7d gross',()=>assert.equal(inspection(base()).cohorts['7d'].gross_commission_cents,1200));
test('7d refund and fee',()=>{const r=inspection(base()).cohorts['7d'];assert.equal(r.refund_cents,100);assert.equal(r.fee_cents,50);});
test('7d realized net',()=>assert.equal(inspection(base()).cohorts['7d'].realized_net_commission_cents,1050));
test('7d net per 1000',()=>assert.equal(inspection(base()).cohorts['7d'].net_cents_per_1000_qualified_human_sessions,10500));
test('30d realized net',()=>assert.equal(inspection(base()).cohorts['30d'].realized_net_commission_cents,2750));
test('30d net per 1000',()=>assert.equal(inspection(base()).cohorts['30d'].net_cents_per_1000_qualified_human_sessions,9167));
test('lead-to-customer rate never inferred',()=>assert.equal(inspection(base()).cohorts['7d'].lead_to_customer_rate,null));
test('cannot claim campaign send approval',()=>assert(!mutate(x=>x.attestations.founder_campaign_approval=true).pass));
test('cannot claim partner email rights',()=>assert(!mutate(x=>x.attestations.partner_email_permission_verified=true).pass));
test('cannot claim footer/address proof',()=>assert(!mutate(x=>x.attestations.publisher_postal_and_unsubscribe_verified=true).pass));
test('missing attestation map rejected',()=>assert(!mutate(x=>x.attestations={}).pass));
test('missing mandatory attestation rejected',()=>assert(!mutate(x=>delete x.attestations.cohort_attribution_verified).pass));
test('unknown extra field rejected',()=>assert(!mutate(x=>x.sessions[0].visitor_email='private@example.com').pass));
test('unknown per-user ID rejected',()=>assert(!mutate(x=>x.confirmations[0].email='private@example.com').pass));
test('merchant newsletter cannot be FV confirmed lead',()=>assert(!mutate(x=>x.confirmations[0].provider='zen12').pass));
test('future confirmation rejected',()=>assert(!mutate(x=>x.confirmations[0].day='2026-12-01').pass));
test('invalid calendar date rejected',()=>assert(!mutate(x=>x.sessions[0].day='2026-11-31').pass));
test('negative session counts rejected',()=>assert(!mutate(x=>x.sessions[0].qualified_human_sessions=-1).pass));
test('unapproved platform rejected',()=>assert(!mutate(x=>x.sessions[0].platform='search').pass));
test('PII in asset ID rejected',()=>assert(!mutate(x=>x.sessions[0].asset_id='user@example.com').pass));
test('duplicate daily aggregate rejected',()=>assert(!mutate(x=>x.sessions.push({...x.sessions[0]})).pass));
test('duplicate settlement rejected',()=>assert(!mutate(x=>x.settlements.push({...x.settlements[0]})).pass));
test('negative payout rejected',()=>assert(!mutate(x=>x.settlements[0].gross_commission_cents=-100).pass));
test('refund+fees exceeding gross rejected',()=>assert(!mutate(x=>x.settlements[0].refund_cents=9999).pass));
test('acquisition after settlement rejected',()=>assert(!mutate(x=>x.settlements[0].settled_day='2026-11-05').pass));
test('unmatched merchant sale not falsely attributed',()=>{const r=mutate(x=>x.settlements[0].asset_id='unmatched');assert(r.pass);assert.equal(r.cohorts['7d'].settled_attributed_orders,0);});
test('unreconciled orders are UNKNOWN not zero',()=>{const r=mutate(x=>x.attestations.merchant_settlements_reconciled=false);assert(r.pass);assert.equal(r.cohorts['7d'].settled_attributed_orders,null);assert.equal(r.cohorts['7d'].net_cents_per_1000_qualified_human_sessions,null);});
test('unverified sessions cannot yield revenue per 1000',()=>{const r=mutate(x=>x.attestations.complete_qualified_sessions=false);assert(r.pass);assert.equal(r.cohorts['7d'].qualified_human_sessions,null);assert.equal(r.cohorts['7d'].net_cents_per_1000_qualified_human_sessions,null);});
test('unverified signup provider means unknown leads',()=>{const r=mutate(x=>x.attestations.jetpack_confirmations_verified=false);assert(r.pass);assert.equal(r.cohorts['7d'].deduped_confirmed_signups,null);});
test('zero denominator means no rate',()=>{const r=mutate(x=>x.sessions=[]);assert(r.pass);assert.equal(r.cohorts['7d'].net_cents_per_1000_qualified_human_sessions,null);});
test('empty unverified evidence yields null metrics, not 0',()=>{const r=mutate(x=>{x.sessions=[];x.confirmations=[];x.settlements=[];x.attestations.complete_qualified_sessions=false;x.attestations.jetpack_confirmations_verified=false;x.attestations.merchant_settlements_reconciled=false;x.attestations.cohort_attribution_verified=false;});assert(r.pass);assert.equal(r.cohorts['30d'].qualified_human_sessions,null);assert.equal(r.cohorts['30d'].settled_attributed_orders,null);});
test('hypothetical live attestation does not equal verified source',()=>{const r=mutate(x=>x.mode='external_aggregate');assert(r.pass);assert.equal(r.evidence_class,'UNVERIFIED_EXTERNAL_ATTESTATION');});
test('malformed as-of date fails closed without throwing',()=>{const r=mutate(x=>x.as_of_day='2026-11-31');assert(!r.pass);});
test('missing list fails closed',()=>{const x=base();delete x.sessions;assert(!inspection(x).pass);});
let count=0;for(const [name,fn] of cases){try{fn();console.log('PASS '+name);count++;}catch(e){console.error('FAIL '+name+' '+e.message);process.exitCode=1;}}
console.log('SUMMARY '+count+'/'+cases.length+' passed');
