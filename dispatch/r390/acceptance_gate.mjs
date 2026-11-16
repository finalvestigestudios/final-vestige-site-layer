/**
 * R390 non-sending read-only evidence gate.
 * Proof input is a redacted JSON snapshot; never accepts subscriber addresses.
 */
export const COMMERCIAL = new Set([3,5]);
const COMMON = [
  "founder_final_campaign_approved",
  "founder_audience_and_schedule_approved",
  "actual_native_jetpack_preview_verified",
  "publisher_physical_address_verified",
  "operational_unsubscribe_verified",
  "truthful_subject_checked_in_native_preview",
  "provider_consent_and_welcome_verified",
  "source_link_client_open_verified"
];
const MERCHANT = [
  "approved_partner_account",
  "exact_sku_affiliate_acceptance",
  "email_channel_permission",
  "creative_permission",
  "issued_earning_url_verified",
  "approved_live_guide_verified",
  "referred_checkout_price_and_refund_verified",
  "proximity_disclosure_verified",
  "offer_claim_support_verified"
];
export function validateLedger(s) {
  if (!s || !Array.isArray(s.editions) || s.editions.length !== 6) throw new Error("Exactly six editions required");
  const ids=s.editions.map(x=>x.edition);
  if (ids.some((x,i)=>x!==i+1)) throw new Error("Edition ordering or IDs changed");
  const commercial=s.editions.filter(x=>x.kind==="commercial").map(x=>x.edition);
  if (JSON.stringify(commercial)!=="[3,5]") throw new Error("Original 4:2 campaign changed");
  if(s.newsletter?.email_new_posts_by_default!==false) throw new Error("Automatic emailing must stay disabled");
  if(s.editions.some(x=>!x.subject || (x.kind==="editorial" && !x.destination) || (x.kind==="commercial" && x.destination))) throw new Error("Unsupported CTA activation or missing editorial CTA");
  if(s.editions.some(x=>x.destination && !x.destination.startsWith("https://finalvestige.com/"))) throw new Error("Editorial CTA must remain on published FV site");
  return true;
}
export function assessEdition(s,n) {
  validateLedger(s);
  const e=s.editions[n-1];
  if(!e)throw new Error("Unknown edition");
  const missing=COMMON.filter(k=>s.attestation?.[k]!==true);
  if(s.newsletter?.enabled!==true) missing.push("newsletter_enabled");
  if(s.newsletter?.private_recipient_filter_verified!==true || !Number.isInteger(s.newsletter?.recipient_email_eligible_count) || s.newsletter.recipient_email_eligible_count<=0) missing.push("recipient_eligibility_verified");
  if(!e.copy_approval) missing.push("edition_copy_approved");
  if(COMMERCIAL.has(n)){
    const p=s.merchant?.[n===3?"zen12":"total_focus"];
    for(const k of MERCHANT) if(p?.[k]!==true)missing.push("merchant."+k);
  }
  return {edition:n,status:missing.length?"HOLD_UNSENT":"READY_FOR_FOUNDER_REVIEW_ONLY",missing,commercial:COMMERCIAL.has(n)};
}
export function assessCampaign(s) { validateLedger(s); return s.editions.map(e=>assessEdition(s,e.edition)); }
export function verifiedRevenuePer1000({human_sessions,settled_commission_net,authoritative_sessions,authoritative_ledger}={}) {
  if(!authoritative_sessions || !authoritative_ledger || !Number.isInteger(human_sessions) || human_sessions<=0 || !Number.isFinite(settled_commission_net)) return {status:"NOT_COMPUTABLE"};
  return {status:"VERIFIED_INPUTS",value:1000*settled_commission_net/human_sessions};
}
