"use strict";
/* R430: PURE, OFFLINE, FAIL-CLOSED evidence gate; no network, email, WordPress or checkout calls. */
const MISSING="NOT_COMPUTABLE";
const requiredProofs=["qualified_human_sessions_complete","source_campaign_join_audited","merchant_reporting_complete","refunds_and_fees_complete","settlement_and_referral_verified"];
function safeId(s){return typeof s==="string"&&/^[a-z0-9][a-z0-9_-]{2,79}$/.test(s)}
function utc(x){const n=Date.parse(x);if(!Number.isFinite(n)||!/\d{4}-\d\d-\d\dT/.test(String(x)))throw Error("valid ISO UTC timestamp required");return n}
function inWindow(time,now,days){const t=utc(time);return t<=now&&t>=now-days*86400000}
function rejectPII(record){const j=JSON.stringify(record);if(/(?:[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})/i.test(j)||/"(?:email|recipient_email|ip|phone|full_name|postal_address)"\s*:/i.test(j))throw Error("PERSONAL_DATA_PROHIBITED_IN_AGGREGATE_FIXTURES")}
function cents(n,field){if(!Number.isSafeInteger(n)||n<0)throw Error(field+" must be nonnegative integer cents");return n}
function audit(input){
  rejectPII(input);
  const now=utc(input.as_of_utc);
  const days=input.cohort_days;
  if(![7,30].includes(days))throw Error("cohort_days must be 7 or 30");
  if(!Array.isArray(input.sessions)||!Array.isArray(input.leads)||!Array.isArray(input.orders))throw Error("all three evidence arrays required");
  const proof=input.proofs||{};
  const missing=requiredProofs.filter(k=>proof[k]!==true);
  const seenSessions=new Map(), qualified=new Map(), unknown=[];
  for(const s of input.sessions){
    if(!safeId(s.session_id)||!safeId(s.asset_id))throw Error("opaque asset/session ID required");
    if(seenSessions.has(s.session_id)){
      if(JSON.stringify(seenSessions.get(s.session_id))!==JSON.stringify(s))throw Error("conflicting session duplicate");
      continue;
    }
    seenSessions.set(s.session_id,s);
    if(!inWindow(s.at_utc,now,days))continue;
    if(s.human_verified===true&&s.qualified===true&&
       typeof s.utm_campaign==="string"&&s.utm_campaign.length>3&&
       typeof s.utm_source==="string"&&s.utm_source.length>1){
      qualified.set(s.session_id,s);
    }
  }
  const leadIds=new Set();const leadSessions=new Set();
  for(const lead of input.leads){
    if(!safeId(lead.provider_id)||!safeId(lead.session_id))throw Error("opaque provider/session ID required");
    if(!inWindow(lead.at_utc,now,days))continue;
    if(lead.provider_confirmed===true&&lead.consent_eligible===true&&
       lead.suppressed!==true&&lead.opted_out!==true&&qualified.has(lead.session_id)){
      leadIds.add(lead.provider_id);leadSessions.add(lead.session_id);
    }
  }
  const orders=new Map();let attributedNet=0,settledOrders=0,unmatched=0;
  const orderSessionIds=new Set();
  for(const o of input.orders){
    if(!safeId(o.order_id))throw Error("opaque order ID required");
    if(orders.has(o.order_id)){
      if(JSON.stringify(orders.get(o.order_id))!==JSON.stringify(o))throw Error("conflicting order duplicate");
      continue;
    }
    orders.set(o.order_id,o);
    if(!inWindow(o.at_utc,now,days)||o.status!=="settled")continue;
    if(!["affiliate_commission","owned_gross"].includes(o.revenue_type))throw Error("revenue type unverified");
    cents(o.amount_cents,"amount");cents(o.refund_cents,"refund");cents(o.fee_cents,"fee");
    if(o.merchant_confirmed!==true||o.settlement_confirmed!==true){unknown.push("unverified_order");continue}
    if(!safeId(o.session_id)||!qualified.has(o.session_id)){unmatched++;continue}
    settledOrders++;attributedNet+=o.amount_cents-o.refund_cents-o.fee_cents;orderSessionIds.add(o.session_id);
  }
  if(unmatched)unknown.push("unmatched_settled_order_attribution");
  if(qualified.size===0)unknown.push("no_audited_qualified_human_sessions");
  if(unknown.length)missing.push(...unknown);
  const canCalculate=missing.length===0;
  const leadProof=proof.provider_consent_ledger_complete===true;
  const ret={
    status:"HOLD_UNSENT",cohort_days:days,qualified_human_sessions:canCalculate?qualified.size:null,
    deduplicated_provider_confirmed_leads:leadProof?leadIds.size:null,
    matched_settled_orders:canCalculate?settledOrders:null,
    attributed_net_cents:canCalculate?attributedNet:null,
    net_revenue_per_1000_human_sessions:canCalculate?Math.round((attributedNet/100)*1000/qualified.size*100)/100:MISSING,
    paid_conversion_rate:canCalculate?Math.round(orderSessionIds.size/qualified.size*100000)/1000:MISSING,
    lead_to_customer_rate:canCalculate&&leadProof&&leadSessions.size>0?
      Math.round([...orderSessionIds].filter(id=>leadSessions.has(id)).length/leadSessions.size*100000)/1000:MISSING,
    missing_evidence:[...new Set(missing)]
  };
  return ret;
}
function taggedEditorialCta(issue,href){
  if(![1,2,4,6].includes(issue))return {status:"HOLD_COMMERCIAL_GUIDE_NOT_APPROVED",url:null};
  if(typeof href!=="string"||href.includes("[["))throw Error("real source URL required");
  const u=new URL(href);
  if(u.protocol!=="https:"||u.hostname!=="finalvestige.com"||u.username||u.password)throw Error("first-party HTTPS only");
  if([...u.searchParams.keys()].some(k=>/(email|phone|subscriber|recipient|aff|ref|token)/i.test(k)))throw Error("sensitive or affiliate parameter");
  u.searchParams.set("utm_source","dispatch");u.searchParams.set("utm_medium","email");
  u.searchParams.set("utm_campaign","fv_dispatch_pilot_2026");
  u.searchParams.set("utm_content","issue_"+String(issue).padStart(2,"0"));
  return {status:"CANDIDATE_URL_NOT_LIVE",url:u.toString()};
}
function inspectTransport(issue,postTitle,preheader,blockSource){
  if(!Number.isInteger(issue)||issue<1||issue>6)throw Error("invalid issue");
  if(!postTitle||!preheader||typeof blockSource!=="string")throw Error("missing metadata/source");
  const first=blockSource.match(/<p[^>]*>([\s\S]*?)<\/p>/i)?.[1]||"";
  return {issue,status:"HOLD_NATIVE_PREVIEW_UNWITNESSED",
    subject_input:"WordPress post title; actual delivered subject unverified",
    intended_subject:postTitle,intended_preheader:preheader,
    actual_email_preheader:"UNVERIFIED_JETPACK_RENDER",
    first_editor_paragraph_has_hold_banner:/EDITORIAL HOLD/.test(first),
    false_preheader_risk:/EDITORIAL HOLD/.test(first)?"HOLD_BANNER_MAY_DOMINATE_EMAIL_SNIPPET":"MAPPING_UNKNOWN",
    commercial_link_authorized:false,valid_postal_and_unsubscribe_witness:false};
}
function releaseDecision(evidence){
 const gates=["founder_final_send_approval","actual_native_jetpack_preview_witness","receiving_eligibility_verified",
  "welcome_receipt_witness","publisher_postal_verified","unsubscribe_render_and_function_witness",
  "approved_final_copy","source_link_integrity_verified"];
 if(evidence.commercial===true)gates.push("named_merchant_email_promotion_permission","issued_approved_earning_link","live_warmup_guide_verified","exact_checkout_refund_terms_verified");
 return {status:"HOLD_UNSENT",ready_for_review:gates.every(k=>evidence[k]===true),
   missing:gates.filter(k=>evidence[k]!==true),founder_release_required:true};
}
module.exports={audit,taggedEditorialCta,inspectTransport,releaseDecision,MISSING};