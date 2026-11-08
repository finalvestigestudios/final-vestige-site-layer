"use strict";
/* Isolated read-only source audit. No WordPress, email, subscriber or analytics I/O.
 * This module inspects supplied markup, NOT a user's live browser state.
 */
const BLOCKED = Object.freeze(["invalid_email","error","blocked_email","opted_out","blocked"]);
function reproduceObservedGiftLogic(subscribeParam, subscriberCss=false) {
  const q = typeof subscribeParam==="string" ? subscribeParam : null;
  return (!!q && !BLOCKED.includes(q)) || subscriberCss===true;
}
function auditFocusMarkup(html) {
  if(typeof html!=="string") throw new TypeError("html source required");
  const queryEvidence = html.includes("new URLSearchParams(window.location.search).get('subscribe')") &&
                        html.includes("bad.indexOf(q)<0") && html.includes("show();");
  const classEvidence = html.includes("is-subscriber") && html.includes("MutationObserver(check)");
  const gift = html.includes('id="fvf-gift"') && html.includes("hidden");
  const jetpack = html.includes("wp-block-jetpack-subscriptions");
  const formFallback = jetpack && /<a\b[^>]*>Send me the fieldbook<\/a>/i.test(html);
  const findings = [];
  if(queryEvidence) findings.push("URL_PARAMETER_SHOWS_DOWNLOAD_WITHOUT_PROVIDER_CONFIRMATION");
  if(classEvidence) findings.push("CLIENT_CSS_CLASS_NOT_PROVIDER_CONFIRMED_CONSENT");
  if(gift) findings.push("DOWNLOAD_PANEL_EXISTS_BUT_ITS_VISIBILITY_IS_NOT_CONSENT");
  if(formFallback) findings.push("REST_RENDER_CONTAINS_SUBSCRIBE_ANCHOR_RUNTIME_FORM_NOT_TESTED");
  return Object.freeze({
    queryEvidence, classEvidence, gift, jetpack, formFallback,
    findings, providerConfirmed:false,
    actualEmailEligibility:"UNKNOWN",
    action:queryEvidence||classEvidence?"ENGINEERING_REVIEW_OF_SUCCESS_STATE":"NO_SOURCE_GATED_SUCCESS_DETECTED",
    caveat:"REST markup is not live-browser Jetpack widget rendering; do not infer that subscriptions cannot be submitted."
  });
}
function isAuthoritativeConfirmation(record) {
  return !!record && typeof record==="object" &&
    record.provider==="jetpack" &&
    record.filter==="Email subscription = Subscribed" &&
    record.consent_basis==="provider_observed_double_opt_in" &&
    record.previous_status==="pending" &&
    record.current_status==="subscribed" &&
    record.evidence_access==="restricted_provider_record" &&
    record.duplicate===false && record.suppressed===false &&
    typeof record.private_proof_ref==="string" &&
    /^internal:[A-Za-z0-9/_-]{12,}$/.test(record.private_proof_ref);
}
function classifyEvidence(record) {
  if(!isAuthoritativeConfirmation(record)) return Object.freeze({
    confirmed_signup:false, reason:"NO_AUTHORITATIVE_PROVIDER_TRANSITION",
    may_emit_public_analytics:false
  });
  return Object.freeze({confirmed_signup:true,
    reason:"RESTRICTED_PROVIDER_RECORD_MEETS_SPEC",
    may_emit_public_analytics:false,
    caveat:"This predicate is not a live integration: a trusted provider adapter and idempotent private journal remain required."
  });
}
function proposedCopy(status) {
  if(status==="unconfirmed") return "Your Fieldbook is available to download. To join The Dispatch, check your inbox and confirm your subscription if prompted.";
  if(status==="provider_confirmed") return "Your email subscription is confirmed. Your welcome email includes the same Fieldbook link.";
  return "Your Fieldbook is available. Downloading it does not by itself subscribe you to The Dispatch.";
}
module.exports={BLOCKED,reproduceObservedGiftLogic,auditFocusMarkup,
  isAuthoritativeConfirmation,classifyEvidence,proposedCopy};
