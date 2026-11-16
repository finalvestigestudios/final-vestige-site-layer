"use strict";
/* Dispatch R407: an OFFLINE reviewer for sanitized evidence only.
   Never place subscriber emails, verification tokens, IPs, or signed provider URLs into these records.
   Structural validity does NOT authenticate a provider event or authorize mailing. */
const SAFE_ID=/^[a-z0-9][a-z0-9_-]{3,63}$/;
const SOURCES=new Set(["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"]);
const PROOFS=["named_affiliate_acceptance","approved_sku","email_marketing_permission","issued_earning_link","guide_live_verified","referred_checkout_verified","merchant_claim_review","publisher_postal_verified","jetpack_preview_verified","operational_unsubscribe","founder_final_approval"];
function reject(reason){return {status:"REJECT",reason};}
function reviewSnapshot(n,f){
  if(!n||!f||["total","confirmed","unconfirmed","suppressed"].some(k=>!Number.isInteger(n[k])||n[k]<0))return reject("missing_or_invalid_provider_counts");
  if(!Number.isInteger(f.wpcom)||!Number.isInteger(f.email))return reject("missing_follower_breakdown");
  return {status:"NONADDITIVE_COUNTS_ONLY",
    newsletter:{total:n.total,confirmed:n.confirmed,unconfirmed:n.unconfirmed,suppressed:n.suppressed},
    followers:{wpcom:f.wpcom,email:f.email},
    recipient_inboxes:null,confirmed_signup_v1:null,
    reason:"overlapping provider categories; no unique email eligibility evidence"};
}
function reviewSource(u){
  if(!u||typeof u!=="object")return reject("missing_utm");
  if(Object.keys(u).some(k=>/(email|recipient|subscriber|user_id|ip|auth|token|name)/i.test(k)))return reject("personal_data_key");
  if(!SOURCES.has(u.utm_source)||u.utm_medium!=="organic_social"||!/^mind_pilot_20[0-9]{2}_[0-9]{2}$/.test(u.utm_campaign||"")||!SAFE_ID.test(u.utm_content||""))return reject("invalid_or_undocumented_asset_tag");
  return {status:"PROVISIONAL_SOURCE_TAG_ONLY",reason:"published asset ID and qualified human visit require independent audits"};
}
function reviewSignup(p){
  if(!p||typeof p!=="object")return reject("not_a_provider_receipt");
  if(Object.keys(p).some(k=>/(email|address|ip|recipient|confirmation_url|token|raw_id)/i.test(k)))return reject("personal_data_or_secret");
  if(p.origin!=="authenticated_provider_export"||p.state!=="confirmed"||p.email_eligible!==true||p.suppressed!==false||!SAFE_ID.test(p.provider_record_ref||"")||!SAFE_ID.test(p.opaque_dedup_key||""))return reject("consent_or_eligibility_unproven");
  return {status:"REVIEW_CANDIDATE_NOT_COUNTED",reason:"independent provider attestation and private dedup remain necessary",confirmed_signup_v1:null};
}
function reviewCommercial(proof){
  const missing=PROOFS.filter(k=>proof?.[k]!==true);
  return {status:"HOLD_UNSENT",missing,possible_human_review:missing.length===0,send_authorized:false};
}
function reviewJourney(s,source,signup,commercial){
  return {snapshot:reviewSnapshot(s.newsletter,s.followers),attribution:reviewSource(source),signup:reviewSignup(signup),commercial:reviewCommercial(commercial),
    confirmed_signup_v1:null,eligible_recipients:null,paid_orders:null,net_revenue_per_1000_qualified_humans:null,release:"HOLD_UNSENT"};
}
if(typeof module!=="undefined"&&module.exports){module.exports={reviewSnapshot,reviewSource,reviewSignup,reviewCommercial,reviewJourney,PROOFS};}
