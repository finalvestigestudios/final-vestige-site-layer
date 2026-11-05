"use strict";
/** Dispatch R127: read-only data contracts. NO sending, network, subscriber writes, or purchases. */
const STATUSES=["Subscribed","Not subscribed","Not confirmed","Bounced","Emails paused","Not sending"];
const CONFIRM=["email_link","existing_wpcom_account"];
const BLOCK=["address","email","phone","ip","cookie","token","subscriber_id","subscriber_name","subscriber_email","user_id","user_name"];
function demand(ok,msg){if(!ok)throw Error(msg);}
function safe(x,path="root"){
 if(!x||typeof x!=="object")return;
 for(const [k,v] of Object.entries(x)){
  demand(!BLOCK.some(p=>k.toLowerCase()===p) || (k.toLowerCase()==="email" && Number.isSafeInteger(v) && v>=0), "PII key rejected at "+path);
  if(typeof v==="string")demand(!/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(v),"PII value rejected");
  if(v&&typeof v==="object")safe(v,path+"."+k);
 }
}
function natural(n){return Number.isSafeInteger(n)&&n>=0}
function aggregates(s){
 safe(s);demand(s&&s.provider==="wordpress_jetpack_newsletter","wrong aggregate source");
 demand(s.counts&&["total","confirmed","unconfirmed","suppressed","paid"].every(k=>natural(s.counts[k])),"bad counts");
 demand(s.counts.confirmed<=s.counts.total,"confirmed exceeds total");
 // WordPress.com documents Not confirmed is excluded from its subscriber total.
 // Diagnostics' unconfirmed semantics must still be independently checked, not simply added.
 return Object.freeze({reported_total:s.counts.total,reported_confirmed:s.counts.confirmed,
  reported_unconfirmed:s.counts.unconfirmed,combined_total:null,
  independently_verified_email_eligible:null,confirmed_signup_events:null,
  reconciliation:"WordPress.com documents Not confirmed excluded from subscriber total; native-status mapping still required",
  legacy_email_followers_do_not_imply_eligibility:true});
}
function nativeEligibility(s){
 safe(s);
 if(!s||s.provider!=="wordpress_subscribers_email_status_filters"||s.verified_read_only!==true)
  return {eligible:null,reason:"No authoritative filtered subscribers view"};
 demand(s.status_counts&&typeof s.status_counts==="object","missing native statuses");
 demand(Object.keys(s.status_counts).every(k=>STATUSES.includes(k)),"unknown or overlapping status filter");
 demand(STATUSES.every(k=>natural(s.status_counts[k])),"missing/bad status");
 demand(s.status_counts["Not confirmed"]>=0,"not confirmed missing");
 return {eligible:s.status_counts.Subscribed,reason:"Native filtered status aggregate, not confirmation or delivery evidence"};
}
function confirmSignup(e){
 safe(e);
 if(!e||e.native_record_verified!==true||e.provider!=="wordpress_native_subscriber_transition")
  return {countable:false,reason:"No verified native transition"};
 demand(CONFIRM.includes(e.confirmation_path),"unknown confirmation path");
 demand(e.previous_email_status!=="Subscribed","duplicate or preexisting subscriber");
 demand(e.current_email_status==="Subscribed","not currently email-subscribed");
 demand(e.explicit_site_subscription_consent===true,"consent unverified");
 demand(e.unique_transition_attested===true,"dedup evidence missing");
 demand(typeof e.anonymous_transition_key==="string" && /^[a-zA-Z0-9_-]{12,100}$/.test(e.anonymous_transition_key),"opaque key required");
 demand(typeof e.observed_at==="string"&&!Number.isNaN(Date.parse(e.observed_at)),"timestamp missing");
 return {countable:true,reason:"Structurally valid native consent transition; authenticity requires independent source review",
 confirmation_path:e.confirmation_path,anonymous_transition_key:e.anonymous_transition_key};
}
function aggregateTransitions(events){
 demand(Array.isArray(events),"array required");const seen=new Set();let count=0;
 for(const e of events){const r=confirmSignup(e);if(!r.countable)continue;
  if(!seen.has(r.anonymous_transition_key)){seen.add(r.anonymous_transition_key);count++;}}
 return count;
}
function welcomeEvidence(e){
 safe(e);
 const required=["received_mailbox_message_verified","actual_jetpack_sender_verified","full_fieldbook_link_present","full_fieldbook_pdf_opened","unsubscribe_link_rendered","publisher_postal_address_verified"];
 return {verified:!!e&&e.provider==="authenticated_received_message_audit"&&required.every(k=>e[k]===true),
 missing:required.filter(k=>!e||e[k]!==true)};
}
function merchant(e){
 safe(e);
 const required=["named_affiliate_acceptance","email_marketing_permission","authorized_link_format","first_party_guide_live","current_buyer_terms_reviewed","refund_and_price_checked_at_checkout","near_offer_disclosure","claim_evidence_reviewed"];
 return {ready:!!e&&required.every(k=>e[k]===true),missing:required.filter(k=>!e||e[k]!==true)};
}
function commercialRelease(x){
 safe(x);const a=merchant(x?.merchant||null);
 const legal=x?.legal||{},consent=x?.consent||{};
 const missing=[...a.missing.map(k=>"merchant:"+k)];
 if(legal.publisher_physical_postal_address_verified!==true)missing.push("legal:publisher_address");
 if(legal.actual_jetpack_unsubscribe_rendered_verified!==true)missing.push("legal:unsubscribe");
 if(consent.authoritative_email_reachability_verified!==true)missing.push("consent:reachability");
 if(consent.authorized_received_email_preview_verified!==true)missing.push("consent:received_email");
 // Never authorize dispatch via this offline evaluator, even in synthetic all-true data.
 return {draft_readiness:missing.length===0,release:"HOLD_UNSENT_FOUNDER_APPROVAL_REQUIRED",missing};
}
function netRevenuePerThousand(x){
 safe(x);
 if(!x||x.source!=="reconciled_merchant_payments"||x.qualified_sessions_source_verified!==true||
 x.settled_orders_source_verified!==true||x.refunds_and_fees_verified!==true)return null;
 for(const k of ["qualified_sessions","gross_cents","refunds_cents","fees_cents","affiliate_commission_cents"])
  demand(natural(x[k]),"bad economic value "+k);
 if(x.qualified_sessions===0)return null;
 return {net_cents:x.gross_cents+x.affiliate_commission_cents-x.refunds_cents-x.fees_cents,
 net_revenue_cents_per_1000_qualified_sessions:1000*(x.gross_cents+x.affiliate_commission_cents-x.refunds_cents-x.fees_cents)/x.qualified_sessions,
 paid_orders:x.paid_orders??null,small_sample_warning:x.qualified_sessions<1000};
}
module.exports={STATUSES,aggregates,nativeEligibility,confirmSignup,aggregateTransitions,welcomeEvidence,merchant,commercialRelease,netRevenuePerThousand};
