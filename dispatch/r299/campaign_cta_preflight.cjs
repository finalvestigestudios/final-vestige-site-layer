"use strict";
/* R299: source-only, privacy-safe reader-journey preflight. Cannot authorize sending. */
const PDF="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf";
function auditCampaign(manifest, manuscripts, evidence={}) {
  if (!manifest || !Array.isArray(manifest.issues) || !Array.isArray(manuscripts)) throw Error("Six manuscript inputs required");
  const issues=manifest.issues.map((item,index)=>{
    const body=String(manuscripts[index]||"");
    const findings=[];
    const has=s=>body.includes(s);
    if (!has(item.subject)) findings.push("SUBJECT_SOURCE_MISMATCH");
    if (!has(item.preheader)) findings.push("PREHEADER_SOURCE_MISMATCH");
    if (!has("UNSENT DRAFT")) findings.push("DRAFT_WARNING_MISSING");
    if (!has("[[VALID_POSTAL_ADDRESS_REQUIRED]]")) findings.push("POSTAL_HOLD_MISSING");
    if (!has("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")) findings.push("UNSUBSCRIBE_HOLD_MISSING");
    if (item.merchant_affiliate_url!==null) findings.push("UNAUTHORIZED_MERCHANT_URL");
    if (item.kind==="commercial-review-pending") {
      if (!String(item.editorial_cta).startsWith("[[APPROVED_")) findings.push("UNVERIFIED_COMMERCIAL_CTA");
      if (!has("Commercial disclosure:")) findings.push("DISCLOSURE_MISSING");
      findings.push("MERCHANT_EMAIL_PERMISSION_UNVERIFIED","GUIDE_NOT_LIVE");
    }
    if (index===3 && /Fourteen seconds/i.test(item.subject)) findings.push("APOLLO_CLOCK_CONTEXT_NEEDS_REVIEW");
    if (index===5 && item.editorial_cta==="https://finalvestige.com/focus/") findings.push("EXISTING_SUBSCRIBER_REENTERS_SIGNUP_LANDING");
    if (index>0 && item.editorial_cta===manifest.issues[index-1].editorial_cta && item.kind==="editorial") findings.push("ADJACENT_EMAILS_SHARE_CTA_DESTINATION");
    findings.push("PREHEADER_NATIVE_JETPACK_RENDER_UNVERIFIED");
    return {number:item.number,kind:item.kind,subject:item.subject,cta:item.editorial_cta,findings,decision:"HOLD_UNSENT"};
  });
  const editorial=issues.filter(x=>x.kind==="editorial").length, commercial=issues.filter(x=>x.kind==="commercial-review-pending").length;
  const systemic=[];
  if (issues.length!==6 || editorial!==4 || commercial!==2) systemic.push("FOUR_TWO_ALLOCATION_BROKEN");
  if (manifest.status!=="DRAFT_UNSENT_NO_SCHEDULING") systemic.push("MASTER_NOT_UNSENT");
  if (!evidence.providerEligibleCountVerified) systemic.push("ELIGIBLE_EMAIL_AUDIENCE_UNKNOWN");
  if (!evidence.receivedWelcomeVerified) systemic.push("FIELD_BOOK_WELCOME_RECEIPT_UNKNOWN");
  if (!evidence.jetpackNativePreviewVerified) systemic.push("NATIVE_PREVIEW_MISSING");
  if (!evidence.validPublisherPostalAddressInReceivedEmail) systemic.push("LEGAL_POSTAL_FOOTER_UNVERIFIED");
  if (!evidence.functionalUnsubscribeInReceivedEmail) systemic.push("UNSUBSCRIBE_RENDER_UNVERIFIED");
  if (!evidence.founderFinalCampaignApproval) systemic.push("FOUNDER_SEND_APPROVAL_ABSENT");
  return {status:"HOLD_UNSENT",count:issues.length,allocation:{editorial,commercial},
    issues,systemic,netRevenuePerThousandQualifiedSessions:null,
    buyerJourney:"Grok asset → /focus/ → provider verified consent → editorial mail → authorized live guide → independently settled order",
    canonicalPdf:PDF,notice:"Offline hypothetical review only. No send, publication, consent event or revenue is inferred."};
}
module.exports={auditCampaign,PDF};