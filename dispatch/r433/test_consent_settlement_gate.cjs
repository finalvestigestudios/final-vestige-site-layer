"use strict";
const assert=require("node:assert/strict");
const {inspect}=require("./consent_settlement_gate.cjs");
const W={jetpack:{subscriptions:true,email_new_posts_by_default:false,newsletter_categories_enabled:false},subscribers:{dashboard_total:3,confirmed:3,unconfirmed:2,distinct_eligible_inboxes:null,provider_email_subscription_subscribed_aggregate:null},compliance:{sender_postal_verified:false,received_unsubscribe_verified:false,actual_jetpack_email_preview_verified:false,affiliate_email_permission_verified:false}};
let checks=0;
function ok(test){test();checks++;}
const a="2026-10-01T00:00:00Z",b="2026-10-02T00:00:00Z";
const evt=[
 {type:"signup_attempt",event_id:"attempt-01",subscription_key:"opaque-one",at:a},
 {type:"signup_attempt",event_id:"attempt-02",subscription_key:"opaque-one",at:a},
 {type:"provider_confirmed_subscribed",event_id:"provider-confirmation-01",subscription_key:"opaque-one",provider_evidence:true,at:a},
 {type:"provider_confirmed_subscribed",event_id:"provider-confirmation-02",subscription_key:"opaque-one",provider_evidence:true,at:b},
 {type:"qualified_visit",event_id:"visit-01",session_id:"session-one",asset_id:"grok-asset-one",utm_campaign:"attention_pilot_2026_11",human_verified:true,at:a},
 {type:"settled_order",event_id:"order-01",order_id:"order-one",session_id:"session-one",merchant_evidence:true,payment_state:"settled",gross_usd:40,at:b},
 {type:"refund",event_id:"refund-01",order_id:"order-one",provider_evidence:true,amount_usd:5,at:b},
 {type:"fee",event_id:"fee-01",order_id:"order-one",provider_evidence:true,amount_usd:2,at:b}
];
ok(()=>assert.equal(inspect(W,[]).sendAuthorized,false));
ok(()=>assert.equal(inspect(W,[]).status,"HOLD_UNSENT"));
ok(()=>assert.equal(inspect(W,[]).observed.eligible_inboxes,null));
ok(()=>assert.ok(inspect(W,[]).blocked.includes("RECIPIENT_ELIGIBILITY_UNKNOWN")));
ok(()=>assert.ok(inspect(W,[]).blocked.includes("UNSUBSCRIBE_UNWITNESSED")));
ok(()=>assert.ok(inspect(W,[]).blocked.includes("PUBLISHER_POSTAL_UNWITNESSED")));
ok(()=>assert.ok(inspect(W,[]).blocked.includes("NATIVE_PREVIEW_UNWITNESSED")));
ok(()=>assert.ok(inspect(W,[]).blocked.includes("MERCHANT_EMAIL_RIGHTS_UNVERIFIED")));
ok(()=>assert.equal(inspect(W,evt).unique_attempts,1));
ok(()=>assert.equal(inspect(W,evt).unique_confirmed_signups,1));
ok(()=>assert.equal(inspect(W,evt).qualified_sessions,1));
ok(()=>assert.equal(inspect(W,evt).order_record_count,1));
ok(()=>assert.equal(inspect(W,evt).cohorts["7d"].status,"NOT_COMPUTABLE"));
ok(()=>assert.equal(inspect(W,evt).cohorts["30d"].status,"NOT_COMPUTABLE"));
const full={qualified_human_reporting_complete:true,merchant_reporting_complete:true,refund_reporting_complete:true,fee_reporting_complete:true,as_of:"2026-11-15T00:00:00Z"};
ok(()=>assert.equal(inspect(W,evt,full).cohorts["7d"].net_revenue_usd,33));
ok(()=>assert.equal(inspect(W,evt,full).cohorts["7d"].net_per_1000,33000));
ok(()=>assert.equal(inspect(W,evt,full).cohorts["30d"].net_revenue_usd,33));
ok(()=>assert.equal(inspect(W,[...evt,evt[0]],full).unique_attempts,1));
for(const bad of [
 {type:"provider_confirmed_subscribed",event_id:"bad-proof",subscription_key:"opaque-one",at:a},
 {type:"settled_order",event_id:"bad-order",order_id:"order-two",session_id:"session-one",payment_state:"settled",gross_usd:500,at:b},
 {type:"qualified_visit",event_id:"bad-session",session_id:"session-two",asset_id:"a01",utm_campaign:"pilot",human_verified:false,at:a},
 {type:"refund",event_id:"bad-refund",order_id:"order-one",amount_usd:5,at:a},
 {type:"signup_attempt",event_id:"mail-leak",subscription_key:"opaque-one",email:"private@example.com",at:a},
 {type:"signup_attempt",event_id:"ip-leak",subscription_key:"opaque-one",ip_address:"127.0.0.1",at:a},
 {type:"made_up_sale",event_id:"bad-type",at:a},
 {type:"settled_order",event_id:"duplicate-order",order_id:"order-one",session_id:"session-one",merchant_evidence:true,payment_state:"settled",gross_usd:42,at:b}
])ok(()=>assert.throws(()=>inspect(W,[...evt,bad],full)));
ok(()=>assert.equal(inspect({...W,jetpack:{...W.jetpack,email_new_posts_by_default:true}},[]).blocked.includes("AUTO_SEND_DEFAULT_DRIFT"),true));
ok(()=>assert.equal(inspect({...W,jetpack:{...W.jetpack,newsletter_categories_enabled:true}},[]).blocked.includes("CATEGORY_TARGETING_DRIFT"),true));
ok(()=>assert.equal(inspect(W,evt,{...full,merchant_reporting_complete:false}).cohorts["7d"].status,"NOT_COMPUTABLE"));
console.log("PASS "+checks+" R433 offline-native Node assertions; never authorizes sending");
