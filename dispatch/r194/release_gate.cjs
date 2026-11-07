'use strict';
function inspect(e){
 const h=[],w=e.newsletter||{},o=e.offer||{};
 if(!Number.isInteger(w.authoritative_unique_email_eligible)||w.authoritative_unique_email_eligible<1)h.push('provider_email_eligible_not_verified');
 if(w.welcome_received_verified!==true)h.push('fieldbook_welcome_receipt_missing');
 if(w.actual_jetpack_email_preview_verified!==true)h.push('actual_email_preview_missing');
 if(w.valid_fv_postal_footer_verified!==true||w.functional_unsubscribe_verified!==true)h.push('postal_or_unsubscribe_unverified');
 if(o.partner_accepted_for_fv!==true||o.permitted_email_marketing!==true||!o.issued_earning_link||!o.published_guide||o.verified_checkout_refund_terms!==true)h.push('merchant_rights_and_guide_missing');
 if(JSON.stringify(e.allocation)!==JSON.stringify(['editorial','editorial','commercial','editorial','commercial','editorial']))h.push('canonical_four_to_two_drift');
 if(e.founder_send_approval!==true)h.push('no_final_founder_send_approval');
 return {release_allowed:h.length===0,holds:h};
}
function kpi(v){if(v==null||v.reconciled!==true||!Number.isSafeInteger(v.sessions)||v.sessions<1||typeof v.net!=='number'||!Number.isFinite(v.net))return null;return v.net*1000/v.sessions}
if(typeof module!=='undefined')module.exports={inspect,kpi};