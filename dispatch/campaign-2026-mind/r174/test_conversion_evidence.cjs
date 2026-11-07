'use strict';
const assert=require('node:assert/strict');
const {evaluate}=require('./conversion_evidence.cjs');
const base=()=>({ cohort_days:7,issue_mix:{editorial:[1,2,4,6],commercial:[3,5]},active_affiliate_url:null,sending_enabled:false,founder_send_approval:false,
  newsletter:{enabled:true,new_post_auto_send:false,total_count:3,confirmed_count:3,unconfirmed_count:2,eligible_recipients:null,actual_welcome_received:false,native_jetpack_preview:false,valid_fv_postal_address:false,functional_opt_out:false},
  merchant:{approved_for_publisher_email:false,live_approved_guide:false,earning_url_approved:false,price_and_refund_terms_checked:false},
  sessions:[],orders:[],session_report_complete:false,settlement_report_complete:false});
const s={evidence_ref:'source-001',utm_source:'youtube',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',asset_id:'yt_mind_001',human_qualified_sessions:200,is_provider_qualified:true};
const o={evidence_ref:'order-001',source:'independent_merchant_report',status:'settled',gross_commission_cents:2000,refund_cents:2500,fees_cents:200,campaign_attribution_verified:true,asset_attribution_verified:true,asset_id:'yt_mind_001',utm_campaign:'mind_pilot_2026_11'};
let tests=0;function t(name,fn){fn();tests++;console.log('PASS '+name)}
t('no SEND ever',()=>assert.equal(evaluate(base()).gate,'HOLD_UNSENT'));
t('hold merchant even if permissions appear positive',()=>{let b=base();Object.keys(b.merchant).forEach(k=>b.merchant[k]=true);assert.equal(evaluate(b).commercial_gate,'HOLD_MERCHANT')});
t('counted and pending not added',()=>{let r=evaluate(base());assert.equal(r.counted_subscribers,3);assert.equal(r.unconfirmed_separate,2)});
t('unverified eligible is null, not 3',()=>assert.equal(evaluate(base()).actual_email_eligible,null));
t('welcome not inferred',()=>assert.ok(evaluate(base()).blockers.includes('WELCOME_RECEIPT_NOT_VERIFIED')));
t('real footer remains unverified',()=>assert.ok(evaluate(base()).blockers.includes('FV_POSTAL_ADDRESS_UNVERIFIED')));
t('no invented zero-revenue on missing reports',()=>assert.equal(evaluate(base()).net_per_1000_qualified_sessions_usd,null));
t('strict proof for earned sales',()=>{let b=base();b.orders=[{...o,source:'affiliate_click'}];assert.throws(()=>evaluate(b),/settlement/)});
t('no pending sale',()=>{let b=base();b.orders=[{...o,status:'pending'}];assert.throws(()=>evaluate(b),/sales/)});
t('no direct affiliate link',()=>{let b=base();b.active_affiliate_url='https://example.org/?aff=1';assert.throws(()=>evaluate(b),/sends permitted/)});
t('no auto-send',()=>{let b=base();b.sending_enabled=true;assert.throws(()=>evaluate(b),/sends permitted/)});
t('no fake founder approval',()=>{let b=base();b.founder_send_approval=true;assert.throws(()=>evaluate(b),/sends permitted/)});
t('reject altered campaign mix',()=>{let b=base();b.issue_mix.editorial=[1,2,4];assert.throws(()=>evaluate(b),/4:2/)});
t('reject PII in evidence',()=>{let b=base();b.email='person@example.org';assert.throws(()=>evaluate(b),/private/)});
t('reject duplicate sessions',()=>{let b=base();b.sessions=[s,s];assert.throws(()=>evaluate(b),/duplicate/)});
t('reject duplicate paid orders',()=>{let b=base();b.orders=[o,o];assert.throws(()=>evaluate(b),/duplicate/)});
t('reject invalid source',()=>{let b=base();b.sessions=[{...s,utm_source:'linkedin'}];assert.throws(()=>evaluate(b),/source/)});
t('reject fake human classification',()=>{let b=base();b.sessions=[{...s,is_provider_qualified:false}];assert.throws(()=>evaluate(b),/unsupported/)});
t('reject inflationary negative counts',()=>{let b=base();b.sessions=[{...s,human_qualified_sessions:-1}];assert.throws(()=>evaluate(b),/invalid session/)});
t('refund losses preserved',()=>{let b=base();b.sessions=[s];b.orders=[o];b.session_report_complete=true;b.settlement_report_complete=true;let r=evaluate(b);assert.equal(r.attributable_net_cents,-700);assert.equal(r.net_per_1000_qualified_sessions_usd,-35)});
t('unattributed settlement counted but never assigned to campaign',()=>{let b=base();b.sessions=[s];b.orders=[{...o,campaign_attribution_verified:false}];b.session_report_complete=true;b.settlement_report_complete=true;let r=evaluate(b);assert.equal(r.unattributed_settled_orders,1);assert.equal(r.net_per_1000_qualified_sessions_usd,null)});
t('incomplete report makes revenue unknowable',()=>{let b=base();b.sessions=[s];b.orders=[o];assert.equal(evaluate(b).net_per_1000_qualified_sessions_usd,null)});
t('no denominator, no rate',()=>{let b=base();b.orders=[o];b.session_report_complete=true;b.settlement_report_complete=true;assert.equal(evaluate(b).net_per_1000_qualified_sessions_usd,null)});
t('zero is allowed only for complete reporting with real sessions',()=>{let b=base();b.sessions=[s];b.session_report_complete=true;b.settlement_report_complete=true;assert.equal(evaluate(b).net_per_1000_qualified_sessions_usd,0)});
t('invalid cent values rejected',()=>{let b=base();b.orders=[{...o,fees_cents:0.1}];assert.throws(()=>evaluate(b),/integer/)});
t('30-day cohorts supported',()=>{let b=base();b.cohort_days=30;assert.equal(evaluate(b).gate,'HOLD_UNSENT')});
t('other cohorts prohibited',()=>{let b=base();b.cohort_days=10;assert.throws(()=>evaluate(b),/cohort/)});
t('no false cross-asset sales attribution',()=>{let b=base();b.sessions=[s];b.orders=[{...o,asset_id:'yt_mind_OTHER'}];b.session_report_complete=true;b.settlement_report_complete=true;assert.equal(evaluate(b).net_per_1000_qualified_sessions_usd,null)});
t('no browser-inferred asset attribution',()=>{let b=base();b.sessions=[s];b.orders=[{...o,asset_attribution_verified:false}];b.session_report_complete=true;b.settlement_report_complete=true;assert.equal(evaluate(b).attributed_settled_orders,0)});
t('reject disguised email inside notes',()=>{let b=base();b.note='contact someone@example.com';assert.throws(()=>evaluate(b),/private/)});
t('reject one proof reused across sessions and orders',()=>{let b=base();b.sessions=[s];b.orders=[{...o,evidence_ref:s.evidence_ref}];assert.throws(()=>evaluate(b),/duplicate/)});
console.log(tests+' native Node assertions PASS');
