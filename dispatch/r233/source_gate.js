"use strict";
/* Research-only release gate. Input is manifest and already retrieved manuscripts. */
const VENDOR={3:"https://zen12.com/hnp",5:"https://hypnosislive.com/mental-skills/total-focus"};
function auditCampaign(manifest, manuscript) {
  let blockers=[], issues=[];
  let entries=Array.isArray(manifest?.issues)?manifest.issues:[];
  if(manifest?.status!=="DRAFT_UNSENT_NO_SCHEDULING")blockers.push("CAMPAIGN_NOT_HELD");
  if(entries.length!==6)blockers.push("ISSUE_COUNT_NOT_SIX");
  if(entries.filter(e=>e.kind==="editorial").length!==4||entries.filter(e=>e.kind==="commercial-review-pending").length!==2)blockers.push("MIX_NOT_4_2");
  for(const e of entries) {
    const body=String(manuscript?.[e.number]||"");let b=[];
    if(!body)b.push("MANUSCRIPT_MISSING");
    if(!body.includes("UNSENT DRAFT")||e.publish_state!=="hold")b.push("RELEASE_HOLD_MISSING");
    if(e.merchant_affiliate_url!==null)b.push("AFFILIATE_LINK_NOT_AUTHORIZED");
    if(!body.includes(e.subject)||!body.includes(e.preheader))b.push("SUBJECT_PREHEADER_MISMATCH");
    if(!body.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")||!body.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))b.push("FOOTER_PROOF_INCOMPLETE");
    if(/guaranteed income|cures anxiety|wealth magnets|100% razor.sharp concentration|money started showing up/i.test(body))b.push("UNSUPPORTED_CLAIM_REVIEW");
    if(e.kind==="commercial-review-pending") {
      if(!body.includes("Commercial disclosure:"))b.push("DISCLOSURE_MISSING");
      if(!body.includes(VENDOR[e.number]))b.push("EXACT_PRODUCT_SALES_SOURCE_MISSING");
      if(!/^\[\[APPROVED_[A-Z0-9_]+\]\]$/.test(String(e.editorial_cta)))b.push("GUIDE_CTA_NOT_HELD");
      b.push("MERCHANT_EMAIL_RIGHTS_NOT_VERIFIED","PUBLISHED_VETTED_GUIDE_NOT_VERIFIED");
    }
    if(e.number===6&&e.editorial_cta==="https://finalvestige.com/focus/")b.push("EXISTING_SUBSCRIBER_REPEAT_SIGNUP_RISK");
    issues.push({number:e.number,kind:e.kind,blockers:b});
  }
  return {release:"HOLD_UNSENT",send_authorized:false,proof:"SOURCE_ONLY",campaign_blockers:blockers,issues,paid_orders:null,net_revenue_per_1000_qualified_sessions:null};
}
