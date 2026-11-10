import test from 'node:test';
import assert from 'node:assert/strict';
import {queryWouldShowGift,assessFocusEvidence,releaseBoundary} from './gift_signal_gate.mjs';
const H='https://finalvestige.com/focus/';
const cases=[['',false],['subscribe=',false],['subscribe=invalid_email',false],
 ['subscribe=error',false],['subscribe=blocked_email',false],
 ['subscribe=opted_out',false],['subscribe=blocked',false],
 ['subscribe=unconfirmed',true],['subscribe=pending',true],['subscribe=1',true],
 ['subscribe=false',true],['subscribe=ERROR',true],['subscribe=blocked%20',true],
 ['subscribe=unrecognized-state',true],['subscribe=success',true]];
for(const [query,expected] of cases) test('exact published query-logic '+(query||'<no query>'),()=>{
 assert.equal(queryWouldShowGift(H+(query?'?'+query:'')),expected);
 const a=assessFocusEvidence({url:H+(query?'?'+query:''),giftVisible:expected});
 assert.equal(a.confirmed_signup,false);assert.equal(a.mayCountLead,false);
});
for(const status of ['Not confirmed','Not subscribed','Bounced','Emails paused','Not sending',''])
 test('non-deliverable or pending '+(status||'<empty>')+' never qualifies',()=>{
  const r=assessFocusEvidence({providerTransitionVerified:true,emailConsentVerified:true,dedupeVerified:true,providerStatus:status});
  assert.equal(r.confirmed_signup,false);
});
test('a historical class is-subscriber alone is UI not new consent',()=>{
 const a=assessFocusEvidence({jetpackClass:'abc is-subscriber xyz',giftVisible:true});
 assert.equal(a.classWouldShowGift,true);assert.equal(a.confirmed_signup,false);
});
test('all three provider controls are independently required',()=>{
 for(const missing of ['providerTransitionVerified','emailConsentVerified','dedupeVerified']){
  const a={providerTransitionVerified:true,emailConsentVerified:true,dedupeVerified:true,providerStatus:'Subscribed'};
  a[missing]=false;assert.equal(assessFocusEvidence(a).mayCountLead,false);
 }
});
test('provider-verified subscribed transition can count lead only',()=>{
 const a=assessFocusEvidence({providerTransitionVerified:true,emailConsentVerified:true,dedupeVerified:true,providerStatus:'Subscribed'});
 assert.equal(a.confirmed_signup,true);assert.equal(a.verifiedPaidOrder,false);assert.equal(a.maySendCampaign,false);assert.equal(a.netRevenue,null);
});
test('even all mocked gates do not authorize a send',()=>{
 const all=Object.fromEntries(['emailAffiliatePermission','merchantEarningURL','approvedBuyerGuide','actualEmailEligibleAggregate',
  'welcomeReceived','postalAddressReceived','unsubscribeReceivedAndWorking','finalFounderSendApproval'].map(k=>[k,true]));
 const s=releaseBoundary(all);assert.equal(s.status,'HOLD_UNSENT');assert.equal(s.sendAuthorized,false);
});
test('unknown gates produce named unmet conditions, no synthetic metrics',()=>{
 const s=releaseBoundary({});assert.equal(s.unmet.length,8);assert.equal(s.sendAuthorized,false);
});
