"use strict";
/** Read-only R13 source audits. REST markup does NOT establish a browser signup or a received email. */
function inspectSignupMarkup(input,pageId=523){
 const html=String(input??"").replace(/<!--[\s\S]*?-->/g,"").replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi,"").replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi,"");
 const forms=[...html.matchAll(/<form\b[^>]*>[\s\S]*?<\/form\s*>/gi)].map(x=>x[0]);
 const formSkeleton=forms.some(f=>(/<input\b[^>]*\btype\s*=\s*["']?email\b/i.test(f) && /(?:<button\b|<input\b[^>]*\btype\s*=\s*["']?submit\b)/i.test(f)));
 const anchors=[...html.matchAll(/<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']/gi)].map(x=>x[1].replace(/&(?:amp|#0?38|#x0?26);/gi,"&"));
 const selfLink=anchors.some(href=>{const h=href.toLowerCase();const q=(h.split("?")[1]||"").split("&");return /^(https?:\/\/finalvestige\.com\/|\/)$/.test(h.split("?")[0]) && q.includes("post_type=page") && q.includes("p="+String(pageId));});
 const disposition=formSkeleton?"FORM_SKELETON_IN_REST_UNVERIFIED":selfLink?"SELF_LINK_FALLBACK_IN_REST_REQUIRES_BROWSER_PROOF":"NO_FORM_IN_REST_REQUIRES_BROWSER_PROOF";
 return {source:"WORDPRESS_MCP_RENDERED_CONTENT_NOT_BROWSER",disposition,form_skeleton_present:formSkeleton,self_link_fallback_present:selfLink,subscriber_conversion_proven:false,actual_dom_verified:false,actual_submit_verified:false,send_authorized:false};
}
function auditCommercialDrafts(issue03,issue05){
 const zen=String(issue03??""), focus=String(issue05??"");const flags=[];
 if(/\b14[\s-]+days\b/i.test(focus)||/\bfive\s+sessions\s+per\s+year\b/i.test(focus))flags.push("ISSUE05_VOLATILE_REFUND_NUMBERS_IN_DRAFT");
 if(/\bmore\s+than\s+200\b/i.test(focus)||/\bmost\s+individual\s+sessions\s+are\s+about\s+40\s+minutes\b/i.test(focus))flags.push("ISSUE05_CATALOG_VS_TOTAL_FOCUS_SKU_MISMATCH");
 if(!/\btotal\s+focus\b/i.test(focus))flags.push("ISSUE05_NO_TOTAL_FOCUS_SKU_SPECIFIC_COMPARISON");
 if(!/\bzen12\b/i.test(zen))flags.push("ISSUE03_NO_EXACT_ZEN12_SKU");
 if(!/commercial disclosure:/i.test(zen)||!/commercial disclosure:/i.test(focus))flags.push("MISSING_NEAR_OFFER_DISCLOSURE");
 if(!/\[\[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED\]\]/.test(zen)||!/\[\[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED\]\]/.test(focus))flags.push("MISSING_INACTIVE_GUIDE_URL_HARD_STOP");
 return {flags,merchant_approval_inferred:false,copy_approved:false,guide_links_live:false,send_authorized:false,release:"HOLD_UNSENT"};
}
function assessReadiness(snapshot,markupAudit,copyAudit){
 const w=snapshot?.wordpress||{},p=snapshot?.pages||{},rights=snapshot?.rights||{},counts=w.subscriber_aggregates||{},anomalies=[];
 if(Number.isFinite(counts.total)&&Number.isFinite(counts.confirmed)&&Number.isFinite(counts.unconfirmed)&&counts.confirmed+counts.unconfirmed>counts.total)anomalies.push("SUBSCRIBER_AGGREGATE_CONFLICT");
 if(!p.dispatch?.published||!p.focus?.published)anomalies.push("FIRST_PARTY_SIGNUP_OR_FIELDBOOK_NOT_PUBLISHED");
 if(!p.zen12_guide?.published||!p.total_focus_guide?.published)anomalies.push("BOTH_OFFER_GUIDES_NOT_LIVE");
 // A form skeleton in REST is still not a completed browser, consent or delivery proof.
 anomalies.push("SIGNUP_RENDERING_BROWSER_PROOF_MISSING");
 if(!w.native_received_email_proven)anomalies.push("RECEIVED_JETPACK_MIME_MISSING");
 if(!w.fv_postal_verified||!w.unsubscribe_rendered_verified)anomalies.push("VALID_POSTAL_AND_UNSUBSCRIBE_PROOF_MISSING");
 if(!w.unique_permissioned_deliverable_verified)anomalies.push("PERMISSIONED_AUDIENCE_UNKNOWN");
 if(!rights.zen12_email_allowed||!rights.total_focus_email_allowed)anomalies.push("ACCOUNT_SPECIFIC_SKU_EMAIL_RIGHTS_UNVERIFIED");
 if(copyAudit.flags.length)anomalies.push("COMMERCIAL_DRAFT_COPY_REDLINE_REVIEW_REQUIRED");
 return {anomalies,source_only:true,release:"HOLD_UNSENT",send_authorized:false,affiliate_links_authorized:false,real_subscriber_addresses_in_report:false};
}
function inspectSavedSubscribeBlock(raw){
 const text=String(raw??"");
 const matched=text.match(/<!--\s*wp:jetpack\/subscriptions(?:\s+(\{[^\n]*?\}))?\s*\/-->/i);
 if(!matched)return {block_present:false,attributes_parsed:false,button_on_new_line:null,explicit_button_only_style:false,browser_opt_in_verified:false};
 let attributes={};try{attributes=matched[1]?JSON.parse(matched[1]):{}}catch{return {block_present:true,attributes_parsed:false,button_on_new_line:null,explicit_button_only_style:false,browser_opt_in_verified:false}};
 const classes=String(attributes.className??"").split(/\s+/);
 return {block_present:true,attributes_parsed:true,button_on_new_line:attributes.buttonOnNewLine===true,explicit_button_only_style:classes.includes("is-style-button-only"),saved_button_label:attributes.submitButtonText??null,email_placeholder_configured:typeof attributes.subscribePlaceholder==="string",browser_opt_in_verified:false};
}
module.exports={inspectSignupMarkup,inspectSavedSubscribeBlock,auditCommercialDrafts,assessReadiness};
