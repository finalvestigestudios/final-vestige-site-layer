"use strict";
/**
 * OFFLINE / READ-ONLY reporting contract, NOT a live signup detector.
 * This module never queries Jetpack, creates a contact, or emits analytics.
 * Aggregate counters and client-facing signals cannot prove a confirmed signup.
 */
const TOKEN = /^[A-Za-z0-9_-]{12,96}$/;
function nonnegative(value) { return Number.isSafeInteger(value) && value >= 0; }
function reconcileCounts(newsletter, followers) {
  const n = newsletter || {}, f = followers || {};
  for (const key of ["total","confirmed","unconfirmed","suppressed","paid"]) {
    if (!nonnegative(n[key])) throw Error("Invalid newsletter counter: "+key);
  }
  for (const key of ["email","wpcom"]) {
    if (!nonnegative(f[key])) throw Error("Invalid follower counter: "+key);
  }
  if(n.confirmed > n.total) throw Error("Confirmed exceeds counted total; do not infer audience");
  // WordPress identifies not-confirmed requests as NOT counted subscribers.
  // WordPress.com Reader follows do not imply email opted-in.
  return Object.freeze({
    counted_subscribers:n.total,
    confirmed_subscriptions_reported:n.confirmed,
    pending_unconfirmed_requests:n.unconfirmed,
    follower_email_only:f.email,
    follower_wordpress_com:f.wpcom,
    unconfirmed_additive_to_total:false,
    email_eligible_recipients:null,
    successful_welcome_receipts:null,
    confirmed_signup_events:null,
    reason:"Counts are separate provider categories, not distinct people to add. Only a filtered email-subscription status and authoritative recipient evidence can establish send eligibility."
  });
}
function containsSensitiveValue(value) {
  return typeof value!=="string" || /@|https?:\/\/|\s|[?&#=/]/.test(value);
}
function checkLeadCandidate(input) {
  const x = input || {};
  // No browser flag, query string, CSS class, download click, aggregate delta,
  // or manually asserted 'confirmed' state can create a trusted lead.
  if (x.origin !== "authenticated-provider-export")
    return Object.freeze({candidate:false,reason:"NO_AUTHORITATIVE_PROVIDER_EVIDENCE"});
  if (x.status !== "subscribed" || x.email_permission !== true)
    return Object.freeze({candidate:false,reason:"NO_CURRENT_EMAIL_PERMISSION"});
  if (!TOKEN.test(x.proof_ref || "") || containsSensitiveValue(x.proof_ref))
    return Object.freeze({candidate:false,reason:"INVALID_PRIVACY_SAFE_PROOF_REFERENCE"});
  if (!TOKEN.test(x.event_ref || "") || containsSensitiveValue(x.event_ref))
    return Object.freeze({candidate:false,reason:"INVALID_PRIVACY_SAFE_EVENT_REFERENCE"});
  if (x.opted_out === true || x.paused === true || x.bounced === true)
    return Object.freeze({candidate:false,reason:"RECIPIENT_NOT_EMAIL_ELIGIBLE"});
  // This is a review candidate only. The adapter must independently verify
  // provenance, one-person identity/consent and the event's timestamp.
  return Object.freeze({candidate:true,reason:"PROVIDER_PROOF_REQUIRES_INDEPENDENT_VERIFICATION",
    public_event_name:null,send_authorized:false});
}
function dedupeCandidates(items) {
  const seen = new Set(), accepted = [], rejected = [];
  for (const item of items) {
    const decision=checkLeadCandidate(item);
    if(!decision.candidate) {rejected.push(decision.reason);continue;}
    if(seen.has(item.event_ref)){rejected.push("DUPLICATE_EVENT_REFERENCE");continue;}
    seen.add(item.event_ref);
    // Never export names, email addresses, URLs, referral tokens or raw provider records.
    accepted.push(Object.freeze({event_ref:item.event_ref,state:"REVIEW_CANDIDATE_ONLY"}));
  }
  return Object.freeze({accepted,rejected,confirmed_signup_events:null});
}
function releaseGate(proof) {
  const p=proof || {};
  const fields=["founder_final_send_approval","email_eligibility_verified","received_welcome_verified",
    "native_email_footer_verified","publisher_postal_verified","unsubscribe_verified"];
  const all=fields.every(k=>p[k]===true);
  const merchant=all && ["merchant_email_permission_verified","merchant_link_authorized",
    "live_warmup_guide_verified","checkout_terms_verified"].every(k=>p[k]===true);
  // Even a completed planning checklist is not a command to send.
  return Object.freeze({editorial:all?"HUMAN_FINAL_REVIEW_ONLY":"HOLD_UNSENT",
    commercial:merchant?"HUMAN_FINAL_REVIEW_ONLY":"HOLD_MERCHANT",send_authorized:false});
}
module.exports={reconcileCounts,checkLeadCandidate,dedupeCandidates,releaseGate};
