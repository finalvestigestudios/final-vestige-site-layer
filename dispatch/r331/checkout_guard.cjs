"use strict";
const REQUIRED = ["affiliate_acceptance","email_permission","issued_link","guide_live","postal_address","unsubscribe_received","welcome_receipt","founder_final_approval"];
function inspect(record) {
  const failures=[];
  if(!record||typeof record!=="object") return {status:"HOLD_UNSENT",allow_send:false,failures:["invalid_record"]};
  const p=record.proofs||{};
  for(const key of REQUIRED) if(p[key]!==true) failures.push("unverified_"+key);
  const email=String(record.email||"");
  const sub=String(record.subject||"");
  if(!sub||sub.length>70) failures.push("invalid_subject");
  if(!email.includes("Commercial disclosure:")) failures.push("missing_near_offer_disclosure");
  if(!email.includes("may be enrolled")&&!email.includes("may be added")) failures.push("merchant_sms_consent_omitted");
  if(!email.toLowerCase().includes("seller")||!email.includes("12 minutes")) failures.push("claim_framing_omitted");
  if(/(?:12\s*minutes\s*(?:equals|=)|guaranteed\s+(?:result|focus)|clinically\s+proven\s+to\s+reprogram)/i.test(email)) failures.push("unsubstantiated_efficacy_claim");
  if(/(?:getstarted|zen12\.com\/gift|affiliates\.inspire3\.com)[^\s]*\?[^\s]*affiliate/i.test(email)) failures.push("unapproved_merchant_deep_link");
  if(/(?:only\s+\d+\s+minutes\s+left|discount\s+expires|hurry|last\s+chance)/i.test(email)) failures.push("unverified_scarcity");
  if(/\$\s*\d+(?:\.\d\d)?/.test(email)) failures.push("volatile_price_in_email");
  if(/\\[\\[PENDING_FIRST_PARTY_ZEN12_GUIDE\\]\\]/.test(email)) failures.push("unresolved_guide_cta");
  const dest=String(record.cta_url||"");
  if(dest){
    try {const u=new URL(dest);if(u.protocol!=="https:"||u.hostname!=="finalvestige.com") failures.push("unapproved_commercial_destination");}
    catch {failures.push("invalid_commercial_destination");}
    if(p.guide_live!==true) failures.push("unapproved_guide_destination");
  }
  if(/<a\\b[^>]*href\\s*=\\s*["'][^"']*(?:zen12\\.com|inspire3\\.com|hypnosislive\\.com)/i.test(String(record.html||""))) failures.push("direct_merchant_anchor");
  if(record.is_post_live||record.is_scheduled||record.test_mail_sent||record.has_contacted_subscribers) failures.push("forbidden_live_action");
  if(record.metric_claim==="click_is_sale"||record.metric_claim==="free_sample_is_confirmed_signup") failures.push("false_conversion_attribution");
  // No automated code path can authorize campaign sending even if all attestations were supplied.
  return {status:"HOLD_UNSENT",allow_send:false,failures};
}
module.exports={inspect,REQUIRED};
