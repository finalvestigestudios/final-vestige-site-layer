'use strict';
const assert=require('node:assert/strict');
const {evaluateFocusRecord,evaluatePageSignal}=require('./focus_measurement_contract.cjs');
let n=0;
const probes=[{subscribe_query:'success'},{subscribe_query:'unconfirmed',gift_visible:true},{gift_visible:true,pdf_clicked:true},{subscriber_css:true},{pdf_clicked:true},{subscribe_query:'blocked'},{},null];
for(const p of probes){let r=evaluatePageSignal(p);assert.equal(r.confirmed_signup,false);assert.equal(r.paid_customer,false);n++;}
const base={provider_authenticated:true,provider:'jetpack',site:'finalvestige.com',email_subscription_status:'subscribed',dispatch_consent:true,provider_confirmation_time:'2026-11-09T10:00:00Z'};
const records=[base,{...base,provider_authenticated:false},{...base,email_subscription_status:'reader_only'},{...base,email_subscription_status:'not_confirmed'},{...base,email_subscription_status:'bounced'},{...base,email_subscription_status:'emails_paused'},{...base,email_subscription_status:'not_sending'},{...base,dispatch_consent:false},{...base,email:'private@example.com'},{...base,provider_confirmation_time:null},{...base,site:'other.com'},{...base,provider:'anything'},null,{},[],{...base,ip:'192.0.2.3'}];
for(const p of records){assert.equal(evaluateFocusRecord(p).confirmed_signup,false);n++;}
console.log('OFFLINE EVIDENCE CONTRACT: '+n+'/'+n+' passed; no positive signup can be asserted by self-supplied fixtures.');
