"use strict";
// READ-ONLY AGGREGATE ANALYST. No network, mail, subscriber mutation, affiliate activation or send authorization.
function reconcile(s) {
  const d=s.newsletter_diagnostics, f=s.follower_stats, cfg=s.settings;
  const finiteInt=x=>Number.isInteger(x)&&x>=0;
  if(!d||!f||!cfg||!s.as_of)throw Error("missing provenance");
  for(const x of [d.total,d.confirmed,d.unconfirmed,d.suppressed,f.email,f.wpcom])if(!finiteInt(x))throw Error("noninteger aggregate");
  if(typeof cfg.new_posts_auto_email!=="boolean"||typeof cfg.newsletter_enabled!=="boolean")throw Error("invalid configuration");
  if(s.subscriber_emails || s.recipient_ids || s.identified_contacts)throw Error("PII prohibited in aggregate snapshot");
  const reasons=[];
  if(d.confirmed+d.unconfirmed>d.total)reasons.push("DIAGNOSTIC_POPULATIONS_NOT_ADDITIVE");
  if(d.confirmed!==f.email)reasons.push("DIAGNOSTIC_CONFIRMED_DIFFERS_FROM_EMAIL_FOLLOWERS");
  if(f.email===0)reasons.push("EMAIL_FOLLOWER_COUNTER_ZERO");
  if(!s.provider_verified_active_email_recipient_count)reasons.push("ACTIVE_ELIGIBLE_RECIPIENTS_NOT_VERIFIED");
  const holds=["NO_FINAL_FOUNDER_CAMPAIGN_APPROVAL","REAL_JETPACK_RECEIVED_MIME_UNVERIFIED","PUBLISHER_POSTAL_ADDRESS_UNVERIFIED","WORKING_UNSUBSCRIBE_UNVERIFIED"];
  if(!s.welcome_receipt_verified)holds.push("WELCOME_RECEIPT_UNVERIFIED");
  if(!s.provider_confirmed_consent_audited)holds.push("CONSENT_PROVENANCE_UNVERIFIED");
  const issues=[1,2,3,4,5,6].map(n=>({issue:n,kind:(n===3||n===5)?"commercial":"editorial",decision:"HOLD_UNSENT",merchant_hold:n===3||n===5?"HOLD_MERCHANT":null}));
  return {as_of:s.as_of,claimed_unique_recipient_count:null,confirmed_signup_count:null,diagnostic:d,followers:f,newsletter_enabled:cfg.newsletter_enabled,auto_new_post_emails_enabled:cfg.new_posts_auto_email,reason_codes:reasons,release_blockers:holds,issues,commercial_approval:"NOT_VERIFIED",newsletter_delivery:"NOT_VERIFIED",all_sends:"HOLD_UNSENT"};
}
function realizeKpi(e) {
  if(!e||e.settlement_source_authenticated!==true||e.human_sessions_source_authenticated!==true) return null;
  const keys=["qualified_human_sessions","settled_gross","refunds","platform_fees","affiliate_reversals"];
  if(keys.some(k=>!Number.isFinite(e[k])||e[k]<0)||e.qualified_human_sessions<=0)return null;
  if(e.refunds+e.platform_fees+e.affiliate_reversals>e.settled_gross)return null;
  return {net_revenue:e.settled_gross-e.refunds-e.platform_fees-e.affiliate_reversals,per_1000_sessions:1000*(e.settled_gross-e.refunds-e.platform_fees-e.affiliate_reversals)/e.qualified_human_sessions,cohort:e.cohort||null,kind:"RECONCILED_VERIFIED"};
}
module.exports={reconcile,realizeKpi};
