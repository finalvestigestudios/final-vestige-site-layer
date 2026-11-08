"use strict";
// Source-only gate: no WordPress/email/network write APIs. Synthetic success never authorizes sending.
function audit(m,e={}) {
 let issues=m?.issues||[], blockers=[];
 if(m?.status!=="UNSENT_REVIEW_ONLY"||m?.send_permitted!==false)blockers.push("UNSENT_LOCK");
 if(issues.length!==6||issues.filter(x=>x.kind==="editorial").length!==4||issues.filter(x=>x.kind==="commercial-review-pending").length!==2)blockers.push("FOUR_TWO_MIX");
 if(new Set(issues.map(x=>x.number)).size!==6)blockers.push("ISSUE_IDS");
 for(const x of issues){
  if(x.status!=="HOLD_UNSENT"||x.post_id!==null)blockers.push("PRODUCTION_STATE_"+x.number);
  if(x.kind==="commercial-review-pending"&&!String(x.destination).startsWith("[[APPROVED_"))blockers.push("MERCHANT_LINK_"+x.number);
 }
 if(e.actual_jetpack_preview!==true)blockers.push("NATIVE_PREVIEW_UNKNOWN");
 if(e.received_compliant_email!==true)blockers.push("ACTUAL_DELIVERY_UNKNOWN");
 if(e.publisher_address_verified!==true||e.unsubscribe_verified!==true)blockers.push("FOOTER_UNVERIFIED");
 if(e.provider_eligible_audience!==true)blockers.push("RECIPIENTS_UNVERIFIED");
 if(e.founder_final_approval!==true)blockers.push("FOUNDER_APPROVAL_MISSING");
 if(e.named_partner_email_rights!==true||e.issued_affiliate_url!==true||e.live_vetted_guide!==true)blockers.push("MERCHANT_APPROVAL_MISSING");
 return Object.freeze({result:"HOLD_UNSENT",can_send:false,blockers});
}
function audienceCount(o){return o&&o.source==="provider-deliverable-count"&&Number.isSafeInteger(o.count)&&o.count>=0?o.count:null;}
function previewClass(x){return ({offline:"SOURCE_ONLY",wordpress_preview:"VISUAL_ONLY",authorized_received:"RECEIVED_REQUIRES_QA"})[x]||"UNKNOWN";}
module.exports={audit,audienceCount,previewClass};
