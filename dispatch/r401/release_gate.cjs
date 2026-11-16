"use strict";
const COMMON={consent_provider_eligible:"provider",unique_confirmed_recipient_count:"provider",received_fieldbook_welcome:"received_mail",reviewed_post_title_subject:"native_preview",native_jetpack_preview:"native_preview",actual_inbox_preheader:"received_mail",verified_fv_postal:"legal",functional_unsubscribe:"legal",one_live_cta:"site",editorial_source_check:"editorial",founder_final_email_approval:"founder"};
const MERCHANT={merchant_named_fv_acceptance:"merchant",named_product_email_permission:"merchant",issued_earning_url:"merchant",approved_published_warmup:"site",merchant_checkout_and_refund_verified:"merchant",near_link_disclosure_verified:"legal"};
function evidenceValid(e,source){return !!e&&typeof e==="object"&&!Array.isArray(e)&&e.source===source&&typeof e.ref==="string"&&/^https:\/\/[^@\s]{12,}$/.test(e.ref)&&typeof e.reviewer==="string"&&e.reviewer.trim().length>=3&&typeof e.checked_at==="string"&&/^20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(e.checked_at);}
function assessIssue(n,proof={}){
const kinds={1:"editorial",2:"editorial",3:"commercial",4:"editorial",5:"commercial",6:"editorial"};
if(!Number.isInteger(n)||!Object.hasOwn(kinds,n))return {issue_number:n,review_state:"HOLD_BAD_ISSUE",send_authorized:false,blockers:["invalid_issue"]};
const requirements={...COMMON,...(kinds[n]==="commercial"?MERCHANT:{}),...(n===4?{issue04_clock_correction_adopted:"founder"}:{})};
const blockers=Object.entries(requirements).filter(([k,kind])=>!evidenceValid(proof?.[k],kind)).map(([k])=>k);
return {issue_number:n,kind:kinds[n],review_state:blockers.length?"HOLD_EVIDENCE":"HUMAN_REVIEW_CANDIDATE_ONLY",send_authorized:false,blockers,proofs_structurally_present:Object.keys(requirements).length-blockers.length,note:"References are structurally checked, never independently authenticated; sending always forbidden."};
}
function auditCampaignManifest(m){
if(!m||!Array.isArray(m.issues))return {status:"HOLD_BAD_MANIFEST",reasons:["missing_issues"],send_authorized:false};
const reasons=[];
if(m.status!=="DRAFT_UNSENT_NO_SCHEDULING")reasons.push("manifest_status_changed");
if(m.issues.length!==6)reasons.push("issue_count_changed");
if(m.mix?.editorial!==4||m.mix?.commercial_review_pending!==2)reasons.push("mix_changed");
for(let n=1;n<=6;n++){const found=m.issues.filter(x=>x.number===n);
if(found.length!==1){reasons.push("duplicate_or_missing_"+n);continue;}
const x=found[0],comm=n===3||n===5;
if(x.kind!==(comm?"commercial-review-pending":"editorial"))reasons.push("kind_"+n);
if(x.merchant_affiliate_url!==null)reasons.push("merchant_link_"+n);
if(x.publish_state!=="hold")reasons.push("publish_state_"+n);
if(!x.subject||!x.preheader)reasons.push("subject_preheader_"+n);
if(comm&&!/^\[\[APPROVED_/.test(x.editorial_cta||""))reasons.push("offer_cta_"+n);
}
return {status:reasons.length?"HOLD_MANIFEST_DRIFT":"MANIFEST_UNCHANGED_AS_DESCRIBED",reasons,send_authorized:false};
}
module.exports={COMMON,MERCHANT,evidenceValid,assessIssue,auditCampaignManifest};
