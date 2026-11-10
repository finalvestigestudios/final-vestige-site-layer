"use strict";
// Dispatch R249: privacy-safe received-email intake for FUTURE founder-authorized test.
// Input is redacted by reviewer before invocation; never logs raw mail or addresses.
// A local test NEVER approves dispatch, consent, merchant promotion, or CAN-SPAM compliance.
const validRef=s=>typeof s==="string" && /^evidence\/[a-z0-9][a-z0-9._/-]{5,95}$/i.test(s);
function header(raw,key) {
 const h=String(raw||"").split(/\r?\n\r?\n/,1)[0].replace(/\r?\n[ \t]+/g," ");
 const m=h.match(new RegExp("(?:^|\\n)"+key+":\\s*([^\\n]+)","i"));
 return m?m[1].trim():"";
}
function auditReceivedSpecimen(x={}) {
 const checks={};
 checks.real_receipt_artifact=validRef(x.receiptProofRef) && x.kind==="received_from_provider";
 checks.subject_exact=!!x.expectedSubject&&header(x.rawHeaders,"subject")===x.expectedSubject;
 checks.sender_matches_expected=/donotreply@wordpress\.com\b/i.test(header(x.rawHeaders,"from")) &&
   /Final Vestige Studios/i.test(header(x.rawHeaders,"from"));
 checks.visible_body_evidence=validRef(x.renderProofRef)&&String(x.renderedText||"").length>=90;
 checks.preheader_in_inbox=validRef(x.inboxProofRef) && !!x.expectedPreheader &&
   String(x.observedInboxPreview||"").includes(x.expectedPreheader);
 checks.publisher_postal=!!x.publisherPostal && x.publisherPostal.length>=12 &&
   !/\[\[|automattic|wordpress\.com/i.test(x.publisherPostal) &&
   String(x.renderedText||"").includes(x.publisherPostal);
 checks.unsubscribe_exposed=/(?:unsubscribe|opt out)/i.test(String(x.renderedText||"")) &&
   /<a\b[^>]*href=["']https?:\/\/[^"']+["'][^>]*>[\s\S]*?(?:unsubscribe|opt out)/i.test(String(x.renderedHtml||"")) &&
   !/\[\[|placeholder/i.test(String(x.renderedHtml||""));
 checks.unsubscribe_functional_separate_proof=validRef(x.optoutProofRef)&&x.optoutResult==="PASS";
 checks.no_unresolved_tokens=!/\[\[(?:VALID_POSTAL_ADDRESS_REQUIRED|JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED|APPROVED_)[^\]]*\]\]/i.test(
   String(x.renderedText||"")+" "+String(x.renderedHtml||""));
 checks.no_active_merchant_url=!/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com)/i.test(String(x.renderedHtml||""));
 checks.receipt_alone_not_consented=x.providerConfirmedConsentProofRef===undefined;
 const incomplete=Object.entries(checks).filter(([,v])=>v!==true).map(([k])=>k);
 return Object.freeze({checks,unresolved:incomplete,local_candidate_only:incomplete.length===0,
   authorized_to_send:false,actual_eligible_recipient_count:null,
   double_opt_in_proven:false,welcome_delivered_proven:false,
   independently_settled_revenue:null, released:false});
}
module.exports={auditReceivedSpecimen};
