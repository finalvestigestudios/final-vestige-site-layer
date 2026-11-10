"use strict";
/* R266: no-network, non-sending, privacy-preserving configuration parity audit.
   A PASS certifies only matching public configuration. It cannot authorize delivery. */
const HOLD="HOLD_UNSENT";
const evidenceKeys=["public_http","pdf_inspection","received_welcome","provider_subscribed_aggregate","postal_address_render","unsubscribe_function","merchant_email_permission","merchant_earning_link","founder_final_send_approval"];
const roots=["observed_at","sources","newsletter","media","focus","dispatch","followers","diagnostics","evidence"];
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const isObj=x=>x!==null&&typeof x==="object"&&!Array.isArray(x);
function canonicalPDF(x){
  if(typeof x!=="string") return false;
  try{const u=new URL(x);return u.protocol==="https:"&&u.hostname==="finalvestige.com"&&
    !u.username&&!u.password&&!u.search&&!u.hash&&
    u.pathname.startsWith("/wp-content/uploads/")&&u.pathname.toLowerCase().endsWith(".pdf");}
  catch(e){return false;}
}
function exactEvidence(e){
  return isObj(e)&&Object.keys(e).length===2&&own(e,"status")&&own(e,"proof_id")&&
    (e.status==="UNKNOWN"&&e.proof_id===null||
     e.status==="VERIFIED"&&typeof e.proof_id==="string"&&/^fvproof-[a-z0-9-]{8,64}$/.test(e.proof_id));
}
function audit(s){
 const errors=[],stages={};
 if(!isObj(s))return {pass:false,status:HOLD,errors:["not_an_object"],stages};
 for(const k of Object.keys(s))if(!roots.includes(k))errors.push("unexpected_root:"+k);
 for(const k of roots)if(!own(s,k))errors.push("missing_root:"+k);
 if(typeof s.observed_at!=="string"||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s.observed_at))errors.push("invalid_timestamp");
 if(!isObj(s.sources)||!Array.isArray(s.sources.references)||s.sources.references.length<2||
    s.sources.references.some(v=>typeof v!=="string"||!/^https:\/\/(finalvestige\.com|wordpress\.com)\//.test(v)))errors.push("invalid_sources");
 const n=isObj(s.newsletter)?s.newsletter:{},m=isObj(s.media)?s.media:{},f=isObj(s.focus)?s.focus:{},d=isObj(s.dispatch)?s.dispatch:{};
 if(n.subscriptions!==true||n.email_new_posts_by_default!==false||n.email_content_format!=="full"||
    n.reply_to!=="no-reply"||n.from_name!=="Final Vestige Studios")errors.push("newsletter_configuration_changed");
 const urls=[n.welcome_pdf_url,m.source_url,f.download_url];
 if(!urls.every(canonicalPDF))errors.push("invalid_pdf_destination");
 if(!urls.every(v=>v===urls[0]))errors.push("url_parity_failed");
 if(m.id!==1737||m.mime_type!=="application/pdf"||m.bytes!==599946)errors.push("media_identity_changed");
 if(n.welcome_configured!==true||n.welcome_pdf_label!=="52-page Complete Edition")errors.push("welcome_identity_changed");
 if(f.published!==true||d.published!==true||f.page_id!==1579||d.page_id!==523)errors.push("published_page_identity_changed");
 if(f.discloses_possible_commissions!==true||d.discloses_possible_commissions!==false)
    errors.push("reported_consent_promise_diff_changed");
 if(f.troubleshooting_says_sign_up_again!==true)errors.push("repeat_signup_copy_not_acknowledged");
 const a=isObj(s.diagnostics)?s.diagnostics:{},b=isObj(s.followers)?s.followers:{};
 for(const [k,v] of Object.entries({total:a.total,confirmed:a.confirmed,unconfirmed:a.unconfirmed,suppressed:a.suppressed,email:b.email,wpcom:b.wpcom}))
   if(!Number.isInteger(v)||v<0)errors.push("invalid_diagnostic:"+k);
 if(b.partial!==false)errors.push("follower_read_partial_or_missing");
 if(!isObj(s.evidence))errors.push("evidence_missing");
 else{
   for(const k of Object.keys(s.evidence))if(!evidenceKeys.includes(k))errors.push("unexpected_evidence:"+k);
   for(const k of evidenceKeys)if(!own(s.evidence,k)||!exactEvidence(s.evidence[k]))
       errors.push("bad_or_missing_evidence:"+k);
 }
 stages.media_registered=m.id===1737&&m.mime_type==="application/pdf"&&m.bytes===599946?"OBSERVED":"UNKNOWN";
 stages.three_links_match=urls.every(canonicalPDF)&&urls.every(v=>v===urls[0])?"OBSERVED":"UNKNOWN";
 for(const k of evidenceKeys)stages[k]=isObj(s.evidence)&&exactEvidence(s.evidence[k])&&
  s.evidence[k].status==="VERIFIED"?"ATTESTED_NOT_INDEPENDENTLY_VALIDATED":"UNKNOWN";
 return {status:HOLD,pass:errors.length===0,errors,stages,
  evidence_status:errors.length?"INVALID_SNAPSHOT":"CONFIGURATION_PARITY_ONLY",
  actual_eligible_recipients:null,actually_received_welcome:null,independently_paid_orders:null,realized_net_revenue:null,
  notes:["Registered media is not an end-user PDF fetch or 52-page inspection.",
    "Configured welcome is not receipt, subscriber consent or postal/unsubscribe proof.",
    "Email, Reader and diagnostic counts are separate nonadditive populations.",
    "Free vendor-audio email signup is not FV consent or a paid order.",
    "All issues remain HOLD_UNSENT even if an external proof is attested."]};
}
if(typeof module!=="undefined"&&module.exports)module.exports={audit,canonicalPDF};
