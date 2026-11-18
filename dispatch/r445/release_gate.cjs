"use strict";
// Offline pure QA rules only; this file cannot send, publish, or contact subscribers.
const isDocId = x => typeof x === "string" && /^[A-Za-z0-9._:/#-]{12,256}$/.test(x);
function newConfirmedSignup(e, seen = new Set()) {
  if (!e || typeof e !== "object") return {counted:false,reason:"missing_event"};
  if (e.provider !== "wordpress_jetpack" ||
      e.transition !== "new_confirmed_email_subscribed" ||
      e.email_status !== "subscribed" || e.previous_email_status === "subscribed")
    return {counted:false,reason:"no_authoritative_new_transition"};
  if (e.consent_scope !== "dispatch_updates" || e.was_existing !== false)
    return {counted:false,reason:"missing_consent_or_existing"};
  if (!/^hmac-sha256:[0-9a-f]{64}$/.test(e.private_subject_key||"") ||
      !isDocId(e.provider_transition_id))
    return {counted:false,reason:"private_dedup_evidence_missing"};
  if (!e.confirmed_at || !Number.isFinite(Date.parse(e.confirmed_at)))
    return {counted:false,reason:"confirmation_time_missing"};
  const key=e.provider+":"+e.provider_transition_id;
  if (seen.has(key)) return {counted:false,reason:"duplicate"};
  seen.add(key); return {counted:true,reason:"provider_confirmed_new_transition"};
}
function editionGate(e={}) {
  const holds=[];
  if (![1,2,3,4,5,6].includes(e.issue)) holds.push("bad_issue");
  const commercial=[3,5].includes(e.issue);
  if (e.publisher_postal_witness!==true || !isDocId(e.publisher_postal_witness_ref)) holds.push("publisher_postal");
  if (e.rendered_unsubscribe_witness!==true || !isDocId(e.unsubscribe_witness_ref)) holds.push("rendered_unsubscribe");
  if (e.native_jetpack_preview_witness!==true || !isDocId(e.preview_witness_ref)) holds.push("real_native_preview");
  if (e.consent_and_audience_witness!==true || !isDocId(e.audience_witness_ref)) holds.push("audience");
  if (e.founder_final_approval!==true || !isDocId(e.founder_approval_ref)) holds.push("final_founder_approval");
  if (commercial) {
    const expected=e.issue===3?"Zen12":"Hypnosis Live";
    if (e.exact_product!==expected) holds.push("product_identity");
    if (e.named_partner_approved!==true || !isDocId(e.partner_account_evidence_ref)) holds.push("named_partner_approval");
    if (e.email_marketing_authorized!==true || !isDocId(e.email_rights_evidence_ref)) holds.push("email_channel_rights");
    if (e.exact_sku_terms_checked!==true || !isDocId(e.checkout_terms_evidence_ref)) holds.push("sku_price_refund_claims");
    if (e.vetted_guide_live!==true || !/^https:\/\/finalvestige\.com\//.test(e.approved_guide_url||"")) holds.push("live_approved_guide");
    if (e.merchant_earning_url_verified!==true || !isDocId(e.issued_affiliate_link_evidence_ref)) holds.push("earning_link");
    if (e.proximate_disclosure_witness!==true || !isDocId(e.disclosure_evidence_ref)) holds.push("near_offer_disclosure");
  }
  return {issue:e.issue,commercial,ready:holds.length===0,holds};
}
function realizedRevenueMetric(data) {
  if (!data || data.qualified_human_sessions_verified!==true ||
      !Number.isInteger(data.qualified_human_sessions) || data.qualified_human_sessions<=0)
    return {computable:false,reason:"verified_qualified_sessions_missing"};
  if (data.settlement_export_verified!==true || !Array.isArray(data.orders))
    return {computable:false,reason:"independent_paid_settlements_missing"};
  if (!data.cohort || !["7d","30d"].includes(data.cohort))
    return {computable:false,reason:"invalid_cohort"};
  if (data.orders.some(o=>!isDocId(o.provider_receipt_ref)||o.status!=="settled" ||
      ![o.gross,o.fees,o.refunds].every(n=>typeof n==="number"&&Number.isFinite(n)&&n>=0)))
    return {computable:false,reason:"unverified_or_invalid_transaction"};
  const sum=(k)=>data.orders.reduce((s,o)=>s+o[k],0);
  const gross=sum("gross"),fees=sum("fees"),refunds=sum("refunds");
  const net=gross-fees-refunds;
  return {computable:true,cohort:data.cohort,confirmed_settled_orders:data.orders.length,
    gross,fees,refunds,net,net_per_1000_qualified_sessions:net*1000/data.qualified_human_sessions};
}
module.exports={newConfirmedSignup,editionGate,realizedRevenueMetric};
