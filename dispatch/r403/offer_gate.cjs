"use strict";
// Evidence-structure inspector, NOT an independent verifier and NEVER a send authorizer.
function auditOfferEvidence(input){
 const blocks=[], add=(x)=>blocks.push(x), allowed={"03":"zen12_premium","05":"hypnosislive_total_focus"};
 const e=input&&typeof input==="object"?input:{};
 const p=(x)=>!!(x&&typeof x==="object"&&x.status==="VERIFIED"&&typeof x.evidence_url==="string"&&/^https:\/\//.test(x.evidence_url)&&/^\d{4}-\d{2}-\d{2}/.test(x.checked_at||"")&&typeof x.reviewer==="string"&&x.reviewer.trim().length>=3);
 if(!allowed[e.issue]) add("INVALID_EDITION");
 if(e.product_sku!==allowed[e.issue]) add("SKU_SCOPE_MISMATCH");
 if(e.active_merchant_link||e.active_offer_guide_link) add("ACTIVE_UNAUTHORIZED_CTA");
 if(e.production_write||e.send_requested||e.test_email_requested) add("PRODUCTION_OR_EMAIL_ACTION_FORBIDDEN");
 for(const k of ["named_partner_approval","email_channel_permission","product_specific_permission","approved_creative","issued_earning_url","live_guide_and_disclosure","source_claim_review","referred_checkout_terms","publisher_postal_address","unsubscribe_function","actual_jetpack_preview","confirmed_recipient_consent","founder_final_review"]){if(!p(e.proofs?.[k]))add("MISSING_"+k.toUpperCase());}
 if(e.email_copy?.promises_automatic_reprogramming||e.email_copy?.claims_medical_effect||e.email_copy?.quotes_unverified_vendor_testimonials)add("UNSUPPORTED_EFFECT_CLAIM");
 if(e.email_copy?.price_or_discount_text){if(!p(e.proofs?.exact_referred_price_checked) || !p(e.proofs?.referral_checkout_match))add("PRICE_COPY_UNSUPPORTED");}
 if(e.email_copy?.mentions_specific_refund){if(!p(e.proofs?.referral_refund_policy_checked))add("REFUND_COPY_UNSUPPORTED");}
 if(e.issue==="05" && (e.email_copy?.identifies_total_focus_as_entire_hypnosis_live_catalog||e.email_copy?.substitutes_total_focus_without_founder_approval))add("PRODUCT_IDENTITY_DRIFT");
 if(e.identity?.counted_confirmed_signup_from_url_param||e.identity?.counted_download_as_signup||e.identity?.added_jetpack_follower_categories)add("FALSE_SUBSCRIBER_ATTRIBUTION");
 if(e.identity?.counted_click_as_paid_sale||e.identity?.counted_unsettled_affiliate_value_as_net_revenue)add("FALSE_REVENUE_ATTRIBUTION");
 return {decision:blocks.length?"HOLD":"HUMAN_REVIEW_ONLY",send_authorized:false,blocks};
}
module.exports = {auditOfferEvidence};
