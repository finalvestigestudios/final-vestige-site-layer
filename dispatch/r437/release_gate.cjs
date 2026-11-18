"use strict";
/** Fail-closed source-only Dispatch release adjudicator, never a send authorization. */
function adjudicate(snapshot, proof = {}) {
  const stages = ["founder_final_approval","provider_eligible_inboxes_verified","welcome_received_verified","native_jetpack_preview_verified","valid_fv_postal_in_received_mail","working_unsubscribe_in_received_mail"];
  const commercial = ["named_partner_email_permission","current_exact_offer_and_terms","approved_live_warmup_guide","issued_earning_link","seller_checkout_and_settlement_verified"];
  if (!snapshot || snapshot.status !== "HOLD_UNSENT" || !Array.isArray(snapshot.records) || snapshot.records.length !== 6) throw new Error("Incorrect campaign manifest");
  const findings = snapshot.records.map((r) => {
    const extra = r.kind === "commercial-review-pending" ? commercial : [];
    const blocked = [...stages,...extra].filter(key=>proof[key] !== true);
    if (r.flags?.includes("CANONICAL_FOURTEEN_SECONDS_SUBJECT_NEEDS_CORRECTION") || r.flags?.includes("DUPLICATE_FIRST_PARTY_CTA")) blocked.push("founder_copy_selection_and_review");
    return {issue:r.number,kind:r.kind,blocked,review_possible:blocked.length === 0,may_send:false};
  });
  return {status:"HOLD_UNSENT",may_send:false,findings};
}
module.exports={adjudicate};
