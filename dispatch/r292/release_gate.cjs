"use strict";
/* Offline-only auditor: never sends mail, creates posts or handles subscriber data. */
const SELLERS=/\b(?:https?:\/\/)?(?:www\.)?(?:zen12\.com|hypnosislive\.com|inspire3\.com|brainwaveshots\.com)(?:\/|[?#\s]|$)/i;
const PII=/(?:[?&](?:email|subscriber(?:_id)?|recipient|token|auth|user_id)=)|(?:[?&]utm_(?:content|term)=[^&\s]*(?:%40|@))/i;
const BANNED=/\[\[(?:VALID_POSTAL_ADDRESS_REQUIRED|JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED|APPROVED_[A-Z_]+)\]\]/;
const VALID_KIND=new Set(["native_editor_preview","received_mime"]);
const REQUIRED_APPROVALS=["founder_final_send_approval","provider_confirmed_eligible_audience","publisher_postal_address_verified","unsubscribe_function_verified","genuine_jetpack_render_verified","issue_specific_copy_approved","send_toggle_off_during_review"];
const MERCHANT_APPROVALS=["publisher_partner_accepted","email_channel_authorized","earning_url_issued","offer_guide_published_and_vetted","seller_terms_current","independent_claim_review_complete"];
function audit(evidence,html="",plain=""){
 const blockers=[],put=(cond,msg)=>{if(!cond)blockers.push(msg)};
 const e=evidence||{},a=e.attestations||{},src=e.source||{};
 put(e.campaign==="fv-dispatch-six-issue-draft","campaign_id_unverified");
 put(e.issue_number>=1&&e.issue_number<=6,"issue_number_invalid");
 put(e.campaign_mix?.editorial===4&&e.campaign_mix?.commercial===2,"4_2_campaign_mix_invalid");
 put(e.issue_number!==3&&e.issue_number!==5||e.kind==="commercial-review-pending","commercial_slot_mislabeled");
 put(e.evidence_class!=="real"||e.capture_kind!=="none","real_capture_missing");
 put(e.capture_kind==="none"||VALID_KIND.has(e.capture_kind),"capture_kind_invalid");
 put(e.capture_kind==="none"||Boolean(src.provider_artifact_ref&&src.captured_utc&&src.source_sha256),"capture_provenance_missing");
 if(e.capture_kind!=="none"){
   put(Boolean(html.trim()&&plain.trim()),"mime_parts_missing");
   put(!BANNED.test(html+plain),"unresolved_release_placeholders");
   put(!PII.test(html+plain),"personal_tracking_parameters_found");
   put(/unsubscribe/i.test(html)&&/unsubscribe/i.test(plain),"unsubscribe_not_in_both_versions");
   put(/postal address/i.test(html)&&/postal address/i.test(plain),"physical_address_label_missing");
   put(/Final Vestige/i.test(html)&&/Final Vestige/i.test(plain),"publisher_identity_missing");
   put(/https:\/\/finalvestige\.com\//i.test(html)&&/https:\/\/finalvestige\.com\//i.test(plain),"first_party_cta_missing");
   put(!/<script\b|<iframe\b|onerror\s*=|onclick\s*=/i.test(html),"email_unsafe_active_markup");
 }
 for(const key of REQUIRED_APPROVALS)put(a[key]===true,"missing_"+key);
 if(e.kind==="commercial-review-pending")for(const key of MERCHANT_APPROVALS)put(a[key]===true,"missing_"+key);
 if((SELLERS.test(html)||SELLERS.test(plain))&&!MERCHANT_APPROVALS.every(k=>a[k]===true))blockers.push("unapproved_seller_url_in_email");
 if(e.evidence_class!=="real")blockers.push("non_real_capture_cannot_authorize");
 if(e.capture_kind!=="received_mime")blockers.push("real_received_mime_not_verified");
 if(!e.approval_record?.founder_signature_ref||!e.approval_record?.approved_version_sha)blockers.push("specific_founder_release_record_missing");
 if(e.capture_kind!=="none"&&!e.postal_proof_ref)blockers.push("publisher_address_evidence_missing");
 if(e.capture_kind!=="none"&&!e.optout_proof_ref)blockers.push("unsubscribe_test_evidence_missing");
 return {state:"HOLD_UNSENT",structural_findings:blockers.length,blockers:[...new Set(blockers)],sale_claim:"NOT_ESTABLISHED",net_revenue_per_1000:"NOT_COMPUTABLE",send_authorized:false};
}
module.exports={audit,REQUIRED_APPROVALS,MERCHANT_APPROVALS};
/* A structurally clean MIME is only reviewer input, never send authorization. */
