// R388 offline copy, legal and merchant hard stops; NO WordPress/email/affiliate actions.
export function validateCandidate(v){
 const errors=[];
 if(!v||typeof v!=="object")return {status:"HOLD_COPY",errors:["candidate missing"]};
 if(!["editorial","commercial"].includes(v.kind))errors.push("kind");
 if(typeof v.subject!=="string"||v.subject.trim().length<18||v.subject.trim().length>75||/\n|guarantee|cure|act now|secret sale/i.test(v.subject))errors.push("subject");
 if(typeof v.preheader!=="string"||v.preheader.length<45||v.preheader.length>125||/100%|scientifically proven|limited time/i.test(v.preheader))errors.push("preheader");
 if(!Array.isArray(v.primary_ctas)||v.primary_ctas.length!==1||typeof v.primary_ctas[0]!=="string"||!/^https:\/\/finalvestige\.com\/[a-z0-9/-]+\/$/.test(v.primary_ctas[0]))errors.push("exactly one valid own-site CTA");
 if(!Array.isArray(v.source_urls)||v.source_urls.length<2||v.source_urls.some(x=>typeof x!=="string"||!x.startsWith("https://")))errors.push("two source URLs");
 if(!Array.isArray(v.merchant_urls)||v.merchant_urls.some(x=>typeof x!=="string"||!x.startsWith("https://")))errors.push("merchant URLs");
 if(v.postal_placeholder!==true||v.unsubscribe_placeholder!==true)errors.push("cannot remove legal hold placeholders");
 if(v.kind==="editorial"&&v.merchant_urls.length)errors.push("editorial must not contain merchant URL");
 if(v.kind==="commercial"&&v.merchant_urls.length)errors.push("direct merchant link must not activate inside draft");
 return {status:errors.length?"HOLD_COPY":"OFFLINE_COPY_REVIEW_ONLY",errors};
}
export function reviewProofs(p,kind){
 const shared=["founder_final_campaign_approval","provider_email_eligible_aggregate","provider_consent_attested","actual_welcome_receipt","genuine_native_preview","native_subject_matches","preheader_handling_observed","publisher_postal_rendered","native_unsubscribe_function_verified","sender_identity_verified"];
 const commercial=["named_affiliate_account_accepted","exact_sku_email_permission","approved_merchant_creative","issued_affiliate_link","live_vetted_guide","buyer_terms_rechecked","near_cta_disclosure"];
 const missing=[...shared,...(kind==="commercial"?commercial:[])].filter(k=>p?.[k]!==true);
 return {state:missing.length?"HOLD_UNSENT":"HUMAN_REVIEW_ONLY_NO_SEND",missing,notes:"Only independently observed proof may set a flag; no inferred approvals or automatic sends."};
}
export function classifyMerchantEvidence(v){
 const flags=["named_affiliate_account_accepted","sku_email_permission","issued_earning_url","live_vetted_guide","referred_checkout_verified"];
 const missing=flags.filter(k=>v?.[k]!==true);
 return {status:missing.length?"HOLD_MERCHANT":"STILL_REQUIRES_FOUNDER_APPROVAL",missing,price_validated_for_referral:v?.referred_checkout_verified===true&&v?.price_at_referred_checkout_verified===true};
}
