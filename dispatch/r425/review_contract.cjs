/* Final Vestige Dispatch R425 — review-only proof contract.
 * Reads redacted attestations; NEVER sends, schedules, publishes, imports or approves.
 * An 'accepted' synthetic attestation is not independently verified evidence.
 */
"use strict";
const SLOTS = Object.freeze({
  "01": {kind:"editorial",subject:"The mind is not a camera"},
  "02": {kind:"editorial",subject:"Before hypnosis had a name"},
  "03": {kind:"commercial",subject:"The twelve-minute meditation question"},
  "04": {kind:"editorial",subject:"Fourteen seconds. A much longer explanation."},
  "05": {kind:"commercial",subject:"Before you press play on a hypnosis audio"},
  "06": {kind:"editorial",subject:"What did seven days of attention reveal?"}
});
const COMMON = Object.freeze([
  "provider.verified_unique_eligible_recipients",
  "provider.permission_scope_for_dispatch",
  "provider.confirmed_signup_deduplicated",
  "provider.welcome_receipt_witness",
  "transport.native_jetpack_preview_exact_issue",
  "transport.received_email_html_plaintext_witness",
  "transport.publisher_owned_valid_postal_address",
  "transport.operational_unsubscribe_and_suppression",
  "transport.jetpack_manual_post_send_path_documented",
  "editorial.historical_claims_checked",
  "editorial.single_primary_cta_and_sources",
  "editorial.accessibility_email_client_qa",
  "founder.final_creative_audience_date_approval"
]);
const MERCHANT = Object.freeze([
  "merchant.named_final_vestige_partner_acceptance",
  "merchant.exact_product_and_email_channel_authorized",
  "merchant.issued_product_earning_link_redacted_attested",
  "merchant.approved_vetted_guide_live_and_link_checked",
  "merchant.referral_checkout_price_refund_terms_checked",
  "merchant.independent_merchant_claim_review",
  "merchant.near_offer_email_and_guide_disclosure"
]);
const ISSUE_EXTRAS = Object.freeze({
  "01":["editorial.distinct_change_blindness_destination"],
  "02":["editorial.no_consecutive_duplicate_cta"],
  "04":["editorial.apollo1_timestamp_language_corrected"],
  "06":["editorial.existing_subscriber_cta_not_signup_repeat"]
});
function get(o,path) {return path.split(".").reduce((x,k)=> x&&typeof x==="object"? x[k]:undefined,o);}
function proof(x) {
  return !!(x && typeof x==="object" && !Array.isArray(x) &&
    x.status==="witnessed" && typeof x.owner==="string" && x.owner.length>=3 &&
    typeof x.evidence_ref==="string" && /^https:\/\/(github\.com|finalvestige\.com|wordpress\.com)\//i.test(x.evidence_ref) &&
    /^2026-\d\d-\d\d(T\d\d:\d\d:\d\dZ)?$/.test(x.checked_at||""));
}
function evaluate(issue, attestation, options={}) {
  const id=String(issue).padStart(2,"0"), slot=SLOTS[id];
  if(!slot) return {issue:id,state:"INVALID",blocked:["invalid_issue_number"],can_request_founder_review:false,send_authorized:false};
  const blocked=[], data=attestation||{};
  if(options.mode!=="production_attestation") blocked.push("not_authenticated_production_evidence");
  if(/(?:[a-z0-9._%+-]+)@(?:[a-z0-9.-]+)\.[a-z]{2,}/i.test(JSON.stringify(data))) blocked.push("recipient_email_or_PII_in_attestation");
  if(get(data,"controls.automatic_new_post_emails")!==false) blocked.push("automatic_post_send_not_proven_off");
  if(get(data,"controls.no_list_import_no_wordpress_write_no_send")!==true) blocked.push("non_sending_controls_not_proven");
  const required=[...COMMON,...(slot.kind==="commercial"?MERCHANT:[]),...(ISSUE_EXTRAS[id]||[])];
  for(const path of required) if(!proof(get(data,path))) blocked.push(path);
  // A review gate NEVER grants sending authorization; founder approval is a separate manual act.
  return {issue:id,kind:slot.kind,subject:slot.subject,state:"HOLD_UNSENT",
          blocked,can_request_founder_review:blocked.length===0,send_authorized:false};
}
function evaluateCampaign(attestation,options={}) {
  const slots=Object.keys(SLOTS).map(i=>evaluate(i,attestation,options));
  return {status:"HOLD_UNSENT",slots,editorial:4,commercial:2,
          send_authorized:false,all_ready_for_founder_review:slots.every(s=>s.can_request_founder_review)};
}
module.exports={SLOTS,COMMON,MERCHANT,ISSUE_EXTRAS,proof,evaluate,evaluateCampaign};
