"use strict";
// Review-only, fail-closed QA of current evidence. It CANNOT authorize a send.
function auditReceipt(receipt, manifest){
 const errors=[];if(!receipt||!manifest||!Array.isArray(manifest.issues)||manifest.issues.length!==6)errors.push("SIX_ISSUES_REQUIRED");
 const rows=Array.isArray(manifest?.issues)?manifest.issues:[];
 if(rows.map(x=>x.issue).join(",")!=="1,2,3,4,5,6")errors.push("ORDER_OR_NUMBER");
 if(rows.filter(x=>x.kind==="editorial").length!==4||rows.filter(x=>x.kind==="commercial_draft").length!==2)errors.push("EDITORIAL_4_COMMERCIAL_2");
 for(const i of rows){
   if(i.kind==="commercial_draft"&&(![3,5].includes(i.issue)||i.cta!==null||i.cta_status!=="PENDING_MIND_APPROVAL_NOT_LIVE"||i.disclosure_beside_offer!==true))errors.push("COMMERCIAL_LINK_OR_DISCLOSURE_"+i.issue);
   if(i.kind==="editorial"&&(!/^https:\/\/finalvestige\.com\//.test(i.cta||"")||i.offer===true))errors.push("EDITORIAL_LINK_OR_OFFER_"+i.issue);
 }
 const p=receipt?.commercial_restrictions??{};
 for(const key of ["affiliate_account_approved","email_channel_permission_verified","earning_link_issued","qualifying_offer_terms_verified","approved_guide_live","founder_final_campaign_approval"])if(p[key]!==false)errors.push("UNAUTHENTICATED_PARTNER_ASSERTION_"+key);
 const g=receipt?.legal_inbox??{};
 for(const key of ["final_vestige_valid_physical_mailing_address_verified","received_jetpack_unsubscribe_verified","actual_jetpack_html_plain_mime_verified","eligible_recipients_verified"])if(g[key]!==false)errors.push("UNVERIFIED_INBOX_PROOF_"+key);
 const a=receipt?.platform??{}; if(a.newsletter_enabled!==true||a.email_new_posts_by_default!==false)errors.push("NEWSLETTER_STATE_MISMATCH");
 if(a.provider_filtered_current_eligible!==null)errors.push("UNKNOWN_ELIGIBLE_MUST_BE_NULL");
 if(a.subscriber_diagnostic_total!==3||a.subscriber_diagnostic_confirmed!==3||a.subscriber_diagnostic_unconfirmed!==2)errors.push("DIAGNOSTIC_SNAPSHOT_CHANGED");
 const rev=receipt?.revenue??{};for(const key of ["real_paid_orders","realized_net_revenue_usd","qualified_human_sessions","net_revenue_per_1000"])if(rev[key]!==null)errors.push("UNVERIFIED_FINANCIAL_AMOUNT_"+key);
 if(rev.merchant_settlement_evidence!==false)errors.push("MERCHANT_SETTLEMENT_NOT_ESTABLISHED");
 if(receipt?.offers?.length!==2||receipt.offers.map(x=>x.issue).join(",")!=="3,5")errors.push("TWO_VENDOR_ROWS_REQUIRED");
 for(const v of receipt?.offers??[]){if(v.price_is_authorized_earning_checkout!==false||v.claim_independently_product_proven!==false||v.cta_state!=="PENDING_MIND_APPROVAL_NOT_LIVE")errors.push("SELLER_CLAIM_OR_PRICE_ELEVATED_"+v.issue);}
 return {structural_pass:errors.length===0,errors,release_decision:"HOLD_UNSENT",commercial_decision:"HOLD_MERCHANT",publisher_mail_decision:"HOLD_INBOX_PROOF",paid_revenue_per_1000:null,notes:"This static QA contract cannot authenticate evidence or grant send permission; approval lives outside the test."};
}
module.exports={auditReceipt};
if(require.main===module){const fs=require("node:fs");const path=require("node:path");const root=__dirname;const snapshot=JSON.parse(fs.readFileSync(path.join(root,"merchant_source_snapshot_2026-11-11.json"),"utf8"));const manifest=JSON.parse(fs.readFileSync(path.join(root,"campaign_cta_ledger_2026-11-11.json"),"utf8"));const result=auditReceipt(snapshot,manifest);process.stdout.write(JSON.stringify(result,null,2)+"\n");if(!result.structural_pass)process.exitCode=1;}
