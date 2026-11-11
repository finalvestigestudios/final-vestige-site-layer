'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {evaluate,SCHEMA}=require('./consent_category_gate.cjs');
const at1='2026-11-07T01:00:00Z',at2='2026-11-09T02:00:00Z',at3='2026-11-10T20:00:00Z';
const E=(id,event,status,at=at1,categories=[])=>({
  source:'jetpack',scope:'fv_dispatch',subject_ref:id,event_ref:event,
  at_utc:at,status,consent_origin:'fv_first_party',categories});
const R=(events,opts={})=>({schema:SCHEMA,mode:'synthetic',as_of_utc:'2026-11-11T06:30:00Z',
  newsletter_categories_enabled:false,campaign_category:'dispatch',events,...opts});
const checkHold=r=>{
  assert.equal(r.release,'HOLD_UNSENT');assert.equal(r.send_authorized,false);
  assert.equal(r.verified_confirmed_signups,null);assert.equal(r.verified_current_recipients,null);
  assert.equal(r.net_revenue_per_1000,'NOT_COMPUTABLE');
  assert.equal(r.affiliate_email_permission,'NOT_VERIFIED');
};
test('pending attempt not confirmation',()=>{const x=evaluate(R([E('test_1','evt_1','pending')]));checkHold(x);assert.equal(x.illustration.first_signups,0);});
test('first provider state subscribed demonstrates first signup without a confirmation click field',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed')]));checkHold(x);assert.equal(x.illustration.first_signups,1);});
test('categories disabled allows a subscribed state regardless of list of topic categories',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed')]));assert.equal(x.illustration.current_subscribed_to_campaign,1);});
test('categories enabled blocks subscribed state with no matching category',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed')],{newsletter_categories_enabled:true}));assert.equal(x.illustration.current_subscribed_to_campaign,0);assert.equal(x.illustration.subscribed_but_category_excluded,1);});
test('categories enabled and selected qualifies only in synthetic example',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed',at1,['dispatch'])],{newsletter_categories_enabled:true}));checkHold(x);assert.equal(x.illustration.current_subscribed_to_campaign,1);});
test('other topic category cannot authorize dispatch',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed',at1,['history'])],{newsletter_categories_enabled:true}));assert.equal(x.illustration.current_subscribed_to_campaign,0);});
test('category preference update without subscription event does not fabricate a reactivation',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed'),E('test_1','evt_2','subscribed',at2,['dispatch'])],{newsletter_categories_enabled:true}));assert.equal(x.illustration.reactivations,0);assert.equal(x.illustration.current_subscribed_to_campaign,1);});
test('category removal from an otherwise subscribed state blocks eligibility',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed',at1,['dispatch']),E('test_1','evt_2','subscribed',at2,[])],{newsletter_categories_enabled:true}));assert.equal(x.illustration.first_signups,1);assert.equal(x.illustration.current_subscribed_to_campaign,0);});
test('unsubscribe and return is reactivation not new lead',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed',at1,['dispatch']),E('test_1','evt_2','unsubscribed',at2),E('test_1','evt_3','subscribed',at3,['dispatch'])],{newsletter_categories_enabled:true}));assert.equal(x.illustration.first_signups,1);assert.equal(x.illustration.reactivations,1);});
for(const state of ['pending','not_confirmed','reader_only','emails_paused','bounced','suppressed','unsubscribed','not_sending']){
 test('latest '+state+' cannot receive synthetic dispatch',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed'),E('test_1','evt_2',state,at2,['dispatch'])],{newsletter_categories_enabled:true}));assert.equal(x.illustration.current_subscribed_to_campaign,0);});
}
test('duplicate identical events count once',()=>{const e=E('test_1','evt_1','subscribed');assert.equal(evaluate(R([e,e])).illustration.first_signups,1);});
test('conflicting duplicate event reference rejected',()=>{const e=E('test_1','evt_1','subscribed');assert.equal(evaluate(R([e,{...e,status:'pending'}])).reason,'CONFLICTING_EVENT_REF');});
test('simultaneous different states rejected',()=>{assert.equal(evaluate(R([E('test_1','evt_1','pending'),E('test_1','evt_2','subscribed')])).reason,'AMBIGUOUS_SAME_TIME_STATE');});
test('simultaneous different category choices rejected',()=>{assert.equal(evaluate(R([E('test_1','evt_1','subscribed',at1,[]),E('test_1','evt_2','subscribed',at1,['dispatch'])])).reason,'AMBIGUOUS_SAME_TIME_STATE');});
test('external records cannot claim any eligible recipients or synthetic metrics',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed')],{mode:'unverified_external'}));checkHold(x);assert.equal(x.illustration,null);});
test('merchant source is not first-party subscription consent',()=>{const e=E('test_1','evt_1','subscribed');assert.equal(evaluate(R([{...e,source:'zen12'}])).reason,'INVALID_EVENT');});
test('merchant origin is not first-party subscription consent',()=>{const e=E('test_1','evt_1','subscribed');assert.equal(evaluate(R([{...e,consent_origin:'merchant_newsletter'}])).reason,'INVALID_EVENT');});
for(const field of ['email','name','ip','provider_verified','merchant_approved','send_authorized']){
 test('privacy/injected assurance field '+field+' rejects',()=>{const e=E('test_1','evt_1','subscribed');assert.equal(evaluate(R([{...e,[field]:'anything'}])).reason,'INVALID_EVENT');});
}
test('forged root release field rejects',()=>{assert.equal(evaluate({...R([]),send_authorized:true}).reason,'INVALID_ROOT');});
test('future event rejects',()=>{assert.equal(evaluate(R([E('test_1','evt_1','subscribed','2026-11-12T00:00:00Z')])).reason,'INVALID_EVENT');});
test('invalid timestamp rejects',()=>{assert.equal(evaluate(R([E('test_1','evt_1','subscribed','2026-11-31T00:00:00Z')])).reason,'INVALID_EVENT');});
test('duplicate category selection rejects',()=>{assert.equal(evaluate(R([E('test_1','evt_1','subscribed',at1,['dispatch','dispatch'])])).reason,'INVALID_EVENT');});
test('original source cannot become a live provider proof simply by setting a flag',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed')],{mode:'unverified_external'}));checkHold(x);assert.equal(x.verified_confirmed_signups,null);});
test('window boundary keeps distinct first opt-in and later reactivation',()=>{const x=evaluate(R([E('test_1','evt_1','subscribed','2026-09-01T01:00:00Z'),E('test_1','evt_2','unsubscribed',at2),E('test_1','evt_3','subscribed',at3)]));assert.equal(x.illustration.windows['30d'].hypothetical_first_signups,0);assert.equal(x.illustration.windows['7d'].hypothetical_reactivations,1);});
