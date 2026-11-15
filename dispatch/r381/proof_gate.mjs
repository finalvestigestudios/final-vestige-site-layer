// Dispatch R381: pure offline verification reference, NOT instrumentation or a live authorization system.
// A passing synthetic object only means it merits independent human review; it NEVER sends or publishes.
function hasProof(x){return !!x&&x.verified===true&&typeof x.sourceRef==="string"&&x.sourceRef.trim().length>=8&&typeof x.checkedAt==="string"&&/^\d{4}-\d\d-\d\d/.test(x.checkedAt)}
function editionDecision(edition,gates){
 const required=["founder_final_send_approval","eligible_recipient_consent","actual_welcome_receipt","native_jetpack_preview","subject_and_transport_qa","fv_legal_postal_address","functional_unsubscribe","approved_live_cta","privacy_review"];
 if(edition.number===4)required.push("apollo_1_source_correction");
 if(edition.kind==="commercial")required.push("named_affiliate_acceptance","sku_email_permission","approved_creatives_and_link_format","issued_earning_url","live_independent_guide","referred_checkout_terms","near_offer_disclosure");
 const failed=required.filter(k=>!hasProof(gates[k]));
 return {number:edition.number,kind:edition.kind,state:failed.length?"HOLD_UNSENT":"HUMAN_RELEASE_CANDIDATE_ONLY",merchant_hold:edition.kind==="commercial"&&failed.some(k=>["named_affiliate_acceptance","sku_email_permission","approved_creatives_and_link_format","issued_earning_url","live_independent_guide","referred_checkout_terms"].includes(k)),failed};
}
function confirmedSignup(records){
 if(!Array.isArray(records))return null;
 const valid=records.filter(r=>r&&r.origin==="jetpack_email_subscription"&&r.provider_status==="confirmed"&&r.email_eligible===true&&r.confirmation_authoritative===true&&r.provenance_verified===true&&typeof r.opaque_subscription_id==="string"&&/^[A-Za-z0-9_-]{10,128}$/.test(r.opaque_subscription_id));
 const ids=new Set(valid.map(r=>r.opaque_subscription_id));
 return {confirmed_unique:ids.size,invalid_or_unproven:records.length-valid.length,provenance:"provider-only",does_not_validate_delivery:true};
}
function realizedNetPer1000(qualifiedSessions,orders){
 if(!Number.isInteger(qualifiedSessions)||qualifiedSessions<=0||!Array.isArray(orders))return null;
 const used=new Set();let net=0;
 for(const r of orders){
   if(!r||r.status!=="paid_settled"||r.source!=="independent_merchant_report"||r.proof_verified!==true||typeof r.opaque_order_id!=="string"||r.opaque_order_id.length<10||used.has(r.opaque_order_id))return null;
   used.add(r.opaque_order_id);
   if(!["gross_paid","refunds","fees"].every(k=>typeof r[k]==="number"&&Number.isFinite(r[k])&&r[k]>=0)||typeof r.currency!=="string"||r.currency!=="USD"||r.refund_window_finalized!==true)return null;
   net+=r.gross_paid-r.refunds-r.fees;
 }
 if(!orders.length)return null;
 return Math.round((net*1000/qualifiedSessions)*100)/100;
}
export {hasProof,editionDecision,confirmedSignup,realizedNetPer1000};
