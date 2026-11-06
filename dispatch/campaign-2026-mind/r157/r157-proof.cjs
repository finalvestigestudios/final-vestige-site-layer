'use strict';
// Offline R157 inspection only; no data writes/sends and never authorizes dispatch.
const REQUIRED = ['founder_final_approval','provider_email_eligibility','received_fieldbook_welcome','native_received_email_render','publisher_valid_postal_address','functioning_unsubscribe','exact_partner_approval','affiliate_email_permission','authorized_earning_link','published_buyer_guide','verified_product_terms','verified_public_guide_cta'];
function safeEvidence(x){
 return !!x && typeof x === 'object' && x.verified === true &&
 typeof x.source_ref === 'string' && /^https:\/\/(github\.com\/finalvestigestudios\/final-vestige-site-layer\/|wordpress\.com\/support\/|www\.ftc\.gov\/|zen12\.com\/|hypnosislive\.com\/)/.test(x.source_ref) &&
 typeof x.reviewer_role === 'string' && /^role:[a-z_-]{3,30}$/.test(x.reviewer_role) &&
 x.source_type === 'specific_fv_operational_proof';
}
function decision(issue, proofs={}){
 const allowed=[1,2,3,4,5,6];
 if(!allowed.includes(issue)) return {status:'INVALID_ISSUE',missing:REQUIRED.slice()};
 const keys=issue===3||issue===5?REQUIRED:REQUIRED.slice(0,6);
 const missing=keys.filter(x=>!safeEvidence(proofs[x]));
 return {status:'HOLD_UNSENT',candidate_only:missing.length===0,missing,issue,
  note:'Evidence checker is not provider proof and NEVER authorizes sending.'};
}
function reportedSubscribers(v){
 if(!v||v.site!=='finalvestige.com') return null;
 const s=v.newsletter||{};
 if (![s.reported_total,s.reported_confirmed,s.reported_unconfirmed].every(x=>Number.isInteger(x)&&x>=0)) return null;
 return {reported_total:s.reported_total,reported_confirmed:s.reported_confirmed,reported_unconfirmed:s.reported_unconfirmed,overlap_possible:true,
 email_eligible:null,confirmed_signup_events:null,paid_orders:null,realized_net_revenue:null};
}
module.exports={REQUIRED,safeEvidence,decision,reportedSubscribers};
