"use strict";
/* Read-only Focus page source analysis. No browser, network, mail or WP write. */
const BAD = Object.freeze(["invalid_email","error","blocked_email","opted_out","blocked"]);
const EVIDENCE=Object.freeze({
  query:"new URLSearchParams(window.location.search).get('subscribe')",
  broadReveal:"if(q){if(bad.indexOf(q)<0){show();}}",
  subscriberClass:"if(/\\bis-subscriber\\b/.test(c.className)){show();}",
  confirmationHelp:"Tap the download button after you confirm your email.",
  duplicateAdvice:"open this page in Safari or Chrome and sign up again.",
  giftCopy:"Please confirm your email to join The Dispatch."
});
function auditSource(pageBody){
  if(typeof pageBody!=="string"||pageBody.length<1000)throw TypeError("Full read-only page body required");
  const match=Object.fromEntries(Object.entries(EVIDENCE).map(([key,value])=>[key,pageBody.includes(value)]));
  return {proof:match,
    unknown_query_reveals_gift:match.query&&match.broadReveal,
    duplicate_signup_advice_present:match.duplicateAdvice,
    confirmation_help_conflicts_with_reveal:match.confirmationHelp&&match.query&&match.broadReveal,
    original_source_changed_or_incomplete:Object.values(match).some(v=>!v),
    ui_reveal_is_not_confirmed_signup:true, release:"HOLD_UNSENT"};
}
function classifyUi(input={}){
  if(!input||typeof input!=="object"||Array.isArray(input))throw TypeError("Synthetic object required");
  const q=typeof input.subscribeParam==="string"?input.subscribeParam:"";
  const cls=typeof input.containerClass==="string"?input.containerClass:"";
  const fromQuery=!!q&&!BAD.includes(q);
  const fromClass=/\bis-subscriber\b/.test(cls);
  return {gift_visible_in_source_logic:fromQuery||fromClass,
    reason:fromQuery?"NON_BLOCKLIST_QUERY":fromClass?"CSS_CLASS":"NO_REVEAL",
    confirmed_signup:false,email_reachable:null,welcome_received:null,
    paid_customer:false,client_confirmed_signup_permitted:false};
}
function classifyNativeConfirmation(evidence){
  // A source classifier, not a real native event. Never mint identity or emit analytics.
  if(!evidence||typeof evidence!=="object"||Array.isArray(evidence))return "NOT_VERIFIED";
  const allowed=["source","confirmed","consent","nativeEventId","opaqueId","occurredAt","optedOut"];
  if(Object.keys(evidence).some(k=>!allowed.includes(k)))return "REJECT_PII_OR_UNKNOWN_FIELDS";
  if(evidence.source!=="AUTHENTICATED_WORDPRESS_CONFIRMATION"||
     evidence.confirmed!==true||evidence.consent!==true||evidence.optedOut!==false)
    return "NOT_VERIFIED";
  if(!/^[a-f0-9]{64}$/.test(evidence.opaqueId||"")||
     !/^[A-Za-z0-9_-]{8,100}$/.test(evidence.nativeEventId||""))return "NOT_VERIFIED";
  if(typeof evidence.occurredAt!=="string"||
     !/(?:Z|[+-]\d\d:\d\d)$/.test(evidence.occurredAt)||
     !Number.isFinite(Date.parse(evidence.occurredAt)))return "NOT_VERIFIED";
  return "SYNTHETICALLY_ELIGIBLE_FOR_NATIVE_DEDUP_REVIEW_ONLY";
}
function classifyCounters(c){
  if(!c||typeof c!=="object"||
    !["total","confirmed","unconfirmed"].every(k=>Number.isInteger(c[k])&&c[k]>=0))
      throw TypeError("Authenticated aggregate snapshot required");
  return {observed:{total:c.total,confirmed:c.confirmed,unconfirmed:c.unconfirmed},
    is_new_confirmed_signup_proof:false,confirmed_plus_pending_is_total:false,
    import_is_consent_proof:false,actual_reachable:null,welcome_received:null,
    paid_orders:null,release:"HOLD_UNSENT"};
}
module.exports={BAD,EVIDENCE,auditSource,classifyUi,classifyNativeConfirmation,classifyCounters};
