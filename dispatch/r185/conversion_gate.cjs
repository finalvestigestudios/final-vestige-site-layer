"use strict";
/* Final Vestige Dispatch R185: pure proof evaluator, NO network/WordPress/email writes.
   This is NOT an authoritative Jetpack subscriber API and never activates sending. */
const REQUIRED_PARTNER = ["named_affiliate_approval","email_channel_permission","approved_earning_url",
  "seller_terms_reviewed","approved_live_first_party_guide"];
const REQUIRED_SEND = ["founder_final_campaign_approval","valid_fv_postal_address",
  "native_jetpack_preview_examined","working_unsubscribe_verified","email_eligible_aggregate_verified",
  "welcome_received_authorized_evidence"];
const ALLOWED_SOURCES = new Set(["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"]);
const URL_HAZARDS = /(?:email=|subscriber=|token=|password=|auth=|key=)/i;
const EMAIL_PII = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i;
function safeString(x){return typeof x === "string" && x.length > 0 && !EMAIL_PII.test(x) && !URL_HAZARDS.test(x);}
function requireSafeOpaque(x) { return safeString(x) && /^[A-Za-z0-9_-]{6,96}$/.test(x); }
function safeUtm(u) {
  if (!u || typeof u!=="object" || !ALLOWED_SOURCES.has(u.utm_source)) return false;
  if(u.utm_medium!=="organic_social")return false;
  if(!/^(mind|mysteries|history|preparedness)_pilot_2026_11$/.test(u.utm_campaign||""))return false;
  return requireSafeOpaque(u.utm_content) && u.utm_content!=="unknown" && u.utm_content!=="sample";
}
/* Provider data must be externally verified by an authorized operator.
   Never treat these checks as proof that an invented JSON receipt is authentic. */
function classifyProviderEvent(e) {
  if(!e || typeof e!=="object") return {state:"REJECT",reason:"missing_event"};
  if(e.kind==="client_success"||e.kind==="download_panel"||e.kind==="aggregate_delta"||
     e.kind==="query_parameter")return {state:"REJECT",reason:"client_or_aggregate_not_provider"};
  if(e.kind!=="provider_subscription_status")return {state:"REJECT",reason:"unexpected_kind"};
  if(e.provider!=="jetpack"||e.email_subscription!=="Subscribed"||
     e.confirmed_by_provider!==true||e.consent_source_verified!==true||
     !requireSafeOpaque(e.private_evidence_ref)||!requireSafeOpaque(e.provider_event_id))
    return {state:"HOLD",reason:"provider_or_consent_incomplete"};
  if("subscriber_email" in e||"email" in e||"name" in e||"ip" in e)
    return {state:"REJECT",reason:"pii_fields_forbidden"};
  return {state:"REVIEW_CANDIDATE",reason:"human_must_verify_provider_receipt"};
}
function summarizeConfirmedCandidates(events) {
  const seen=new Set(); let candidates=0,duplicates=0,rejected=0,held=0;
  for(const e of Array.isArray(events)?events:[]){
    const c=classifyProviderEvent(e);
    if(c.state==="REVIEW_CANDIDATE"){
      if(seen.has(e.provider_event_id))duplicates++;else {seen.add(e.provider_event_id); candidates++;}
    }else if(c.state==="REJECT") rejected++; else held++;
  }
  return {human_review_candidates:candidates,duplicate_provider_refs:duplicates,rejected,held,
    confirmed_signup_events_emitted:0,warning:"Not provider authentication; do not count leads until independent verification."};
}
function releaseGate(input,commercial) {
  const e=input&&typeof input==="object"?input:{};
  const missing=REQUIRED_SEND.filter(k=>e[k]!==true);
  if(commercial)missing.push(...REQUIRED_PARTNER.filter(k=>e[k]!==true));
  return {status:"HOLD_UNSENT",merchant_status:commercial?"HOLD_MERCHANT":"NOT_APPLICABLE",
    missing,can_send:false,can_activate_affiliate_links:false,automated_send_capability:false};
}
function validateRevenueRecord(r) {
 if(!r||typeof r!=="object")return false;
 if(!requireSafeOpaque(r.opaque_settlement_ref) || !["first_party_paid","affiliate_settled"].includes(r.type))return false;
 if(r.independently_reported!==true||r.refund_checked!==true||r.fees_checked!==true)return false;
 for(const k of ["gross","refund","fees"])if(!Number.isFinite(r[k])||r[k]<0)return false;
 if(r.refund>r.gross)return false;
 if(["email","customer_email","name","card_number","ip"].some(k=>k in r))return false;
 return true;
}
function safeRevenueScorecard(data){
 const d=data&&typeof data==="object"?data:{};
 const sessions=d.qualified_human_sessions;
 const complete=Number.isSafeInteger(sessions)&&sessions>0&&d.qualified_human_sessions_verified===true&&
    d.settlement_dataset_complete===true&&d.attribution_reconciled===true&&Array.isArray(d.settlements)&&
    d.settlements.every(validateRevenueRecord);
 if(!complete)return {status:"NOT_COMPUTABLE",net_revenue_per_1000_qualified_humans:null,
  verified_paid_orders:null,warning:"Missing authoritative denominators or reconciled paid settlements; clicks are not sales."};
 const unique=new Set(d.settlements.map(s=>s.opaque_settlement_ref));
 if(unique.size!==d.settlements.length)return {status:"NOT_COMPUTABLE",net_revenue_per_1000_qualified_humans:null,
   verified_paid_orders:null,warning:"Duplicate settlement references"};
 const net=d.settlements.reduce((a,x)=>a+x.gross-x.refund-x.fees,0);
 return {status:"SOURCE_ATTESTED_INPUT_ONLY",net_revenue_per_1000_qualified_humans:net*1000/sessions,
   verified_paid_orders:d.settlements.length,net_revenue:net,
   warning:"Offline calculation on provided figures, NOT independent verification of provider records."};
}
module.exports={safeUtm,classifyProviderEvent,summarizeConfirmedCandidates,releaseGate,
 validateRevenueRecord,safeRevenueScorecard,REQUIRED_PARTNER,REQUIRED_SEND};