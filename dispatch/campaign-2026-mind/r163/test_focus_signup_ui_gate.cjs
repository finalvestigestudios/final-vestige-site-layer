'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {evaluateSignupUI} = require('./focus_signup_ui_gate.cjs');

const unsafe = [
  {postSignupUrl:'?subscribe=1'},
  {postSignupUrl:'?subscribe=confirmed'},
  {postSignupUrl:'?subscribe=anything'},
  {postSignupUrl:'?subscribe=invalid_email'},
  {hasSubscriberCssClass:true},
  {clickObserved:true},
  {postSignupUrl:'?subscribe=1',hasSubscriberCssClass:true,clickObserved:true},
  {providerEmailStatus:'pending'},
  {providerEmailStatus:'reader_only'},
  {providerEmailStatus:'bounced'},
  {providerEmailStatus:'unsubscribed'},
  {providerEmailStatus:'paused'},
  {providerEmailStatus:'subscribed',providerConsentVerified:false},
  {providerEmailStatus:'subscribed',providerConsentVerified:true,currentlySuppressed:true},
];
unsafe.forEach((input,i)=>test('rejects unsupported confirmation '+i,()=>{
  const r=evaluateSignupUI(input);
  assert.equal(r.canRecordConfirmedSignup,false);
  assert.equal(r.display,'CHECK_YOUR_EMAIL');
  assert.equal(r.release,'HOLD_UNSENT');
}));
test('accepts independent provider confirmed email status only for bookkeeping',()=>{
  const r=evaluateSignupUI({providerEmailStatus:'subscribed',providerConsentVerified:true});
  assert.equal(r.canRecordConfirmedSignup,true);
  assert.equal(r.canRecordDeliveredWelcome,false);
  assert.equal(r.canClaimEmailReachable,false);
  assert.equal(r.release,'HOLD_UNSENT');
});
test('received welcome requires separate evidence',()=>{
 const a=evaluateSignupUI({providerEmailStatus:'subscribed',providerConsentVerified:true,welcomeReceiptVerified:true});
 assert.equal(a.canRecordDeliveredWelcome,true);
 assert.equal(a.canClaimEmailReachable,false);
});
test('fabricated welcome alone is insufficient',()=>{
 const a=evaluateSignupUI({providerEmailStatus:'pending',welcomeReceiptVerified:true});
 assert.equal(a.canRecordDeliveredWelcome,false);
});
test('reject unknown provider status',()=>assert.throws(()=>evaluateSignupUI({providerEmailStatus:'approved'}),TypeError));
test('client-only signals ignored even when status true',()=>{
 const r=evaluateSignupUI({providerEmailStatus:'subscribed',providerConsentVerified:true,postSignupUrl:'?subscribe=anything'});
 assert.equal(r.clientSignalsIgnored,true);
 assert.equal(r.emailPreviewValidated,false);
});
