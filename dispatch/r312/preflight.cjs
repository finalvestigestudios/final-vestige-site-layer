"use strict";
/* R312: pure, offline, read-only evidence evaluator. Absolutely no network, CMS, send or signup actions. */
const EDITORIAL = new Set([1, 2, 4, 6]);
const COMMERCIAL = new Set([3, 5]);
const REQUIRED = ["founder_campaign_release", "subscriber_eligibility",
  "received_welcome", "actual_jetpack_preview", "verified_optout"];
function inspect(e) {
  if (!e || e.record_type !== "EDITORIAL_REVIEW_ONLY_NO_SEND") throw Error("invalid evidence scope");
  if (!Array.isArray(e.issues) || e.issues.length !== 6) throw Error("six original issues required");
  const n = e.issues.map(x => x.number);
  if (new Set(n).size !== 6 || n.some(x => !Number.isInteger(x) || x < 1 || x > 6)) throw Error("invalid edition identity");
  if (e.issues.filter(x => x.kind === "editorial").length !== 4 ||
      e.issues.filter(x => x.kind === "commercial-review-pending").length !== 2) throw Error("4:2 mix changed");
  for (const x of e.issues) {
    if (!x.subject || !x.proposed_preheader || !x.source_blob_sha || x.hold !== "HOLD_UNSENT") throw Error("master fidelity lost");
    if (EDITORIAL.has(x.number) !== (x.kind === "editorial")) throw Error("edition misclassified");
    if (COMMERCIAL.has(x.number) && x.commercial_hold !== "HOLD_MERCHANT") throw Error("merchant hold removed");
    if (x.inbox_preheader_verified !== false) throw Error("preheader requires witnessed native inbox");
  }
  const blocker = [];
  for (const k of REQUIRED) if (e.approval?.[k] !== true) blocker.push(k);
  for (const k of ["merchant_email_rights", "issued_earning_link", "live_independent_buyer_guides"])
    if (e.approval?.[k] !== true) blocker.push(k);
  if (!e.site_snapshot || e.site_snapshot.default_email_new_posts !== false) blocker.push("default_sending_not_disabled");
  if (!e.site_snapshot?.email_eligible_count && e.site_snapshot?.email_eligible_count !== 0) blocker.push("eligible_recipient_count_unknown");
  if (e.site_snapshot?.email_eligible_count === 0) blocker.push("no_verified_recipients");
  if (e.preheader_contract?.wordpress_inbox_preview_text_control !== "VERIFIED_BY_RECEIVED_EMAIL")
    blocker.push("native_inbox_preheader_unverified");
  const duplicateCTA = e.issues[0].editorial_cta === e.issues[1].editorial_cta;
  const timingClaim = /\bfourteen seconds\b|\b14 seconds\b/i.test(e.issues[3].subject);
  const repeatedSignup = /\/focus\/?$/.test(e.issues[5].editorial_cta || "");
  const pendingGuides = e.issues.filter(x => COMMERCIAL.has(x.number) && x.editorial_cta === null).map(x => x.number);
  const editorialWarnings = [
    ...(duplicateCTA ? ["01_02_same_destination"] : []),
    ...(timingClaim ? ["04_unverified_time_claim"] : []),
    ...(repeatedSignup ? ["06_existing_subscriber_reoptin"] : [])
  ];
  return Object.freeze({
    six_original_preserved: true, split:"4:2", blocked_editions:[1,2,3,4,5,6],
    commercial_hold:[3,5], blocker, pendingGuides, editorialWarnings,
    native_preview_proved:false, received_email_proved:false,
    realized_net_revenue_per_1000_qualified_sessions:null,
    authorized_to_send:false, // Deliberate non-executable contract, even if every field is spoofed true
    conclusion:"HOLD_UNSENT"
  });
}
module.exports = { inspect, EDITORIAL, COMMERCIAL };
