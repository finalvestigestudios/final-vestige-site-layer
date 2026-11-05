"use strict";
/** Synthetic test cases ONLY. They are NOT actual confirmations, delivery, or sales. */
const assert=require("node:assert/strict");
const m=require("./native_confirmation_gate.cjs");
let passed=0;function run(name,fn){fn();passed++;console.log("PASS "+name);}
const agg={provider:"wordpress_jetpack_newsletter",counts:{total:3,confirmed:3,unconfirmed:2,suppressed:0,paid:0}};
const event={provider:"wordpress_native_subscriber_transition",native_record_verified:true,confirmation_path:"existing_wpcom_account",previous_email_status:"Not subscribed",current_email_status:"Subscribed",explicit_site_subscription_consent:true,unique_transition_attested:true,anonymous_transition_key:"c9kN6yPn_Native001",observed_at:"2026-11-05T02:34:13Z"};
function change(x,fn){const r=JSON.parse(JSON.stringify(x));fn(r);return r;}
function throws(fn){assert.throws(fn);}
run("reports 3 total",()=>assert.equal(m.aggregates(agg).reported_total,3));
run("pending non-additive",()=>assert.equal(m.aggregates(agg).combined_total,null));
run("unverified email eligibility",()=>assert.equal(m.aggregates(agg).independently_verified_email_eligible,null));
run("confirmed aggregate not an event",()=>assert.equal(m.aggregates(agg).confirmed_signup_events,null));
run("bad total rejected",()=>throws(()=>m.aggregates(change(agg,x=>x.counts.total=-1))));
run("wrong provider rejected",()=>throws(()=>m.aggregates(change(agg,x=>x.provider="social"))));
run("out-of-range confirmed rejected",()=>throws(()=>m.aggregates(change(agg,x=>x.counts.confirmed=4))));
run("native eligibility unknown without source",()=>assert.equal(m.nativeEligibility(null).eligible,null));
run("native eligibility source authenticated",()=>assert.equal(m.nativeEligibility({provider:"wordpress_subscribers_email_status_filters",verified_read_only:true,status_counts:Object.fromEntries(m.STATUSES.map(s=>[s,s==="Subscribed"?2:0]))}).eligible,2));
run("follower total cannot be reachability",()=>assert.equal(m.nativeEligibility({provider:"jetpack_follower_stats",email:0,total:3}).eligible,null));
run("native overlapping status rejected",()=>throws(()=>m.nativeEligibility({provider:"wordpress_subscribers_email_status_filters",verified_read_only:true,status_counts:{...Object.fromEntries(m.STATUSES.map(s=>[s,0])),"Not sending (any reason)":3}})));
run("existing WordPress account valid confirmation path",()=>assert.equal(m.confirmSignup(event).countable,true));
run("email-link confirmation path also valid",()=>assert.equal(m.confirmSignup(change(event,x=>x.confirmation_path="email_link")).countable,true));
run("existing user without new transition rejected",()=>throws(()=>m.confirmSignup(change(event,x=>x.previous_email_status="Subscribed"))));
run("no explicit consent rejected",()=>throws(()=>m.confirmSignup(change(event,x=>x.explicit_site_subscription_consent=false))));
run("not confirmed not countable",()=>throws(()=>m.confirmSignup(change(event,x=>x.current_email_status="Not confirmed"))));
run("duplicate event deduplicated",()=>assert.equal(m.aggregateTransitions([event,event]),1));
run("two distinct transitions",()=>assert.equal(m.aggregateTransitions([event,change(event,x=>x.anonymous_transition_key="c9kN6yPn_Native002")]),2));
run("unverified native record ignored",()=>assert.equal(m.confirmSignup(change(event,x=>x.native_record_verified=false)).countable,false));
run("PII key rejected",()=>throws(()=>m.confirmSignup({...event,email:"hidden"})));
run("nested PII rejected",()=>throws(()=>m.aggregates({...agg,more:{nested:{subscriber_email:"secret"}}})));
run("email pattern rejected",()=>throws(()=>m.confirmSignup({...event,note:"someone@example.com"})));
run("malformed opaque key rejected",()=>throws(()=>m.confirmSignup(change(event,x=>x.anonymous_transition_key="x"))));
run("absent welcome not verified",()=>assert.equal(m.welcomeEvidence(null).verified,false));
run("synthetic specimen not verified welcome",()=>assert.equal(m.welcomeEvidence({provider:"offline_mime_preview",received_mailbox_message_verified:true}).verified,false));
run("welcome requires PDF opened",()=>assert.equal(m.welcomeEvidence({provider:"authenticated_received_message_audit",received_mailbox_message_verified:true}).verified,false));
run("merchant default hold",()=>assert.equal(m.merchant(null).ready,false));
run("merchant demands email rights",()=>assert.ok(m.merchant({named_affiliate_acceptance:true}).missing.includes("email_marketing_permission")));
run("commercial sends ALWAYS hold",()=>assert.equal(m.commercialRelease({merchant:{},legal:{},consent:{}}).release,"HOLD_UNSENT_FOUNDER_APPROVAL_REQUIRED"));
run("missing address flagged",()=>assert.ok(m.commercialRelease({}).missing.includes("legal:publisher_address")));
run("missing real unsub flagged",()=>assert.ok(m.commercialRelease({}).missing.includes("legal:unsubscribe")));
run("revenue unknown without authoritative source",()=>assert.equal(m.netRevenuePerThousand({qualified_sessions:2,gross_cents:500}),null));
run("zero denominator not zero revenue",()=>assert.equal(m.netRevenuePerThousand({source:"reconciled_merchant_payments",qualified_sessions_source_verified:true,settled_orders_source_verified:true,refunds_and_fees_verified:true,qualified_sessions:0,gross_cents:0,refunds_cents:0,fees_cents:0,affiliate_commission_cents:0}),null));
run("synthetic revenue arithmetic",()=>{const r=m.netRevenuePerThousand({source:"reconciled_merchant_payments",qualified_sessions_source_verified:true,settled_orders_source_verified:true,refunds_and_fees_verified:true,qualified_sessions:100,gross_cents:2000,refunds_cents:500,fees_cents:200,affiliate_commission_cents:400,paid_orders:2});assert.equal(r.net_cents,1700);assert.equal(r.net_revenue_cents_per_1000_qualified_sessions,17000);});
console.log("PASSED "+passed);
