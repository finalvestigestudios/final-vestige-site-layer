'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),{compile,noPrivateData}=require('./outcome_proof.cjs');
const when='2026-11-13T23:30:00Z';
const complete={qualified_session_reporting_complete:true,settlement_reporting_complete:true,source_to_order_reconciliation_complete:true,provider_confirmation_reconciliation_complete:true};
const missing={qualified_session_reporting_complete:false,settlement_reporting_complete:false,source_to_order_reconciliation_complete:false,provider_confirmation_reconciliation_complete:false};
const session={type:'qualified_session',event_id:'evt_001',at:'2026-11-13T15:00:00Z',session_ref:'session_abc12',asset_id:'fv_vid_001',utm_source:'tiktok',utm_medium:'organic_social',verified_human:true,evidence_ref:'server_1234'};
const lead={type:'confirmed_signup',event_id:'evt_002',at:'2026-11-13T15:20:00Z',provider:'jetpack',provider_ref:'anon_sub_1234',status:'active',consent_scope:'dispatch',confirmation_method:'existing_verified_wpcom',confirmation_event_ref:'wp_confirm_111',evidence_ref:'wp_private_789'};
const order={type:'affiliate_settlement',event_id:'evt_003',at:'2026-11-13T18:00:00Z',order_ref:'order_abc12',session_ref:'session_abc12',evidence_ref:'statement_001',ledger_source:'merchant_statement',status:'settled',gross_revenue_cents:1000,refund_cents:100,fee_cents:50};
const clone=o=>JSON.parse(JSON.stringify(o));
test('empty evidence cannot be represented as observed zero revenue',()=>{let r=compile([],missing,when);assert.equal(r.seven_day.net_revenue_cents,null);assert.equal(r.seven_day.qualified_sessions,null);assert.equal(r.status,'HOLD_UNSENT');});
test('mock complete revenue is calculated only for verified settled order',()=>{let r=compile([session,lead,order],complete,when);assert.equal(r.seven_day.net_revenue_cents,850);assert.equal(r.seven_day.settled_orders,1);assert.equal(r.seven_day.confirmed_signups,1);assert.equal(r.seven_day.net_revenue_per_1000_sessions_cents,850000);});
test('partial reporting must suppress sales and conversion KPI',()=>{let r=compile([session,order],missing,when);assert.equal(r.thirty_day.settled_orders,null);assert.equal(r.thirty_day.net_revenue_per_1000_sessions_cents,null);});
test('complete reporting of no orders gives zero, but ratio requires sessions',()=>{let r=compile([session],complete,when);assert.equal(r.seven_day.net_revenue_cents,0);assert.equal(r.seven_day.net_revenue_per_1000_sessions_cents,0);});
test('even complete reporting with no denominator suppresses ratio',()=>{let r=compile([],complete,when);assert.equal(r.seven_day.net_revenue_per_1000_sessions_cents,null);});
test('WordPress SSO confirmation can be valid',()=>{assert.equal(compile([lead],complete,when).thirty_day.confirmed_signups,1);});
test('double opt in can be valid',()=>{let e=clone(lead);e.confirmation_method='double_opt_in';assert.equal(compile([e],complete,when).seven_day.confirmed_signups,1);});
for(const [label,change] of [
  ['unconfirmed status',e=>e.status='unconfirmed'],['incorrect consent scope',e=>e.consent_scope='merchant'],
  ['merchant program',e=>e.provider='inspire3'],['unknown provider proof',e=>delete e.evidence_ref],
  ['unverifiable confirmation',e=>e.confirmation_method='form_submission'],
  ['missing provider ref',e=>delete e.provider_ref],['missing confirmation ref',e=>delete e.confirmation_event_ref]
])test('reject lead: '+label,()=>{let e=clone(lead);change(e);assert.throws(()=>compile([e],complete,when));});
test('deduplicate provider subscriber identities',()=>{let e=clone(lead);e.event_id='evt_004';assert.throws(()=>compile([lead,e],complete,when),/DUPLICATE_CONFIRMED_SUBSCRIBER/);});
test('reject duplicate event id even if type differs',()=>{let e=clone(session);assert.throws(()=>compile([session,e],complete,when),/DUPLICATE_EVENT_ID/);});
test('reject unverified session',()=>{let e=clone(session);e.verified_human=false;assert.throws(()=>compile([e],complete,when),/UNVERIFIED_SESSION/);});
test('reject social source with wrong campaign medium',()=>{let e=clone(session);e.utm_medium='paid_search';assert.throws(()=>compile([e],complete,when));});
test('reject two session events with same ID',()=>{let e=clone(session);e.event_id='evt_dup';assert.throws(()=>compile([session,e],complete,when));});
test('reject unknown social source',()=>{let e=clone(session);e.utm_source='mystery';assert.throws(()=>compile([e],complete,when));});
test('reject unverified affiliate click as a payment',()=>{let e=clone(order);e.status='clicked';assert.throws(()=>compile([session,e],complete,when));});
test('reject unverified merchant network order',()=>{let e=clone(order);e.ledger_source='analytics_event';assert.throws(()=>compile([session,e],complete,when));});
test('reject payment without exact matched qualified session',()=>{assert.throws(()=>compile([order],complete,when),/ORDER_WITHOUT_QUALIFIED_SOURCE/);});
test('reject payment before attributable visit',()=>{let e=clone(order);e.at='2026-11-12T18:00:00Z';assert.throws(()=>compile([session,e],complete,when));});
test('reject duplicate settlements',()=>{let e=clone(order);e.event_id='evt_005';assert.throws(()=>compile([session,order,e],complete,when));});
test('reject missing refund audit',()=>{let e=clone(order);delete e.refund_cents;assert.throws(()=>compile([session,e],complete,when));});
test('reject fee higher than gross',()=>{let e=clone(order);e.fee_cents=1200;assert.throws(()=>compile([session,e],complete,when));});
test('reject raw identifiers including email string',()=>{let e=clone(lead);e.evidence_ref='person@example.com';assert.throws(()=>compile([e],complete,when));});
test('reject PII keys',()=>assert.throws(()=>noPrivateData([{email:'hidden'}]),/PII_FIELD/));
test('reject PII in nested metadata',()=>assert.throws(()=>noPrivateData({extra:{metadata:{phone:'123'}}}),/PII_FIELD/));
test('reject event from future',()=>{let e=clone(session);e.at='2026-11-14T23:00:00Z';assert.throws(()=>compile([e],complete,when));});
test('reject merchant newsletter as FV signup',()=>{let e={type:'signup_attempt',event_id:'evt_x99',at:'2026-11-13T12:00:00Z',provider:'inspire3'};assert.throws(()=>compile([e],complete,when));});
test('a fieldbook download is diagnostic not confirmed lead',()=>{let e={type:'fieldbook_download',event_id:'evt_dl1',at:'2026-11-13T12:00:00Z'};let r=compile([e],complete,when);assert.equal(r.seven_day.confirmed_signups,0);assert.equal(r.diagnostic_events.fieldbook_download,1);});
test('no revenue backfill from lead or click',()=>{let e={type:'email_cta_click',event_id:'evt_c12',at:'2026-11-13T12:00:00Z'};let r=compile([lead,e],complete,when);assert.equal(r.seven_day.net_revenue_cents,0);});
test('reject unsettled order',()=>{let e=clone(order);e.status='pending';assert.throws(()=>compile([session,e],complete,when));});
test('refuse when as-of is invalid',()=>assert.throws(()=>compile([],complete,'tomorrow'),/INVALID_DATE/));
test('reject email traffic mislabeled as organic social',()=>{let e=clone(session);e.utm_source='email';assert.throws(()=>compile([e],complete,when),/UNVERIFIED_SESSION/);});
test('accept email traffic only with matching email medium',()=>{let e=clone(session);e.utm_source='email';e.utm_medium='email';assert.equal(compile([e],complete,when).seven_day.qualified_sessions,1);});
test('reject direct traffic mislabeled as social',()=>{let e=clone(session);e.utm_source='direct';assert.throws(()=>compile([e],complete,when));});
test('reject other PII field names',()=>assert.throws(()=>noPrivateData({customer_email:'redacted'}),/PII_FIELD/));
