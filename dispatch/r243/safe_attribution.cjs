"use strict";
// Source-controlled, read-only calculation; never sends mail, activates offers, or claims production reconciliation.
const scoreLedger = function scoreLedger(input) {
  const must=(ok,msg)=>{if(!ok)throw Error(msg)};
  must(input&&typeof input==="object"&&!Array.isArray(input),"ledger_required");
  must(input.schema==="fv.dispatch.revenue_evidence.v1","schema_mismatch");
  must(["SYNTHETIC_ONLY","PRODUCTION_READONLY_EXPORT"].includes(input.mode),"mode_invalid");
  must(Number.isFinite(Date.parse(input.as_of_utc)),"as_of_invalid");
  for(const k of ["sessions","confirmations","actions","orders"])must(Array.isArray(input[k]),"invalid_"+k);
  const raw=JSON.stringify(input);
  must(!/"(?:email|email_address|phone|ip_address|full_name|first_name|last_name|street_address|recipient_address)"\s*:/.test(raw),"pii_key_forbidden");
  must(!/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/.test(raw),"email_value_forbidden");
  const now=Date.parse(input.as_of_utc), uniq=(xs,fn)=>[...new Map(xs.map(x=>[fn(x),x])).values()];
  const proofs=input.reconciliations||{}, safeRef=x=>typeof x==="string"&&/^[A-Za-z0-9._:-]{6,120}$/.test(x);
  for(const s of input.sessions)must(safeRef(s.session_id)&&Number.isFinite(Date.parse(s.at_utc)),"bad_session");
  for(const c of input.confirmations)must(safeRef(c.opaque_subscriber_ref)&&safeRef(c.provider_transition_ref)&&Number.isFinite(Date.parse(c.at_utc)),"bad_confirmation");
  for(const o of input.orders)must(safeRef(o.transaction_ref)&&Number.isFinite(Date.parse(o.at_utc)),"bad_order");
  const status=[];
  if(proofs.qualified_sessions_verified!==true)status.push("QUALIFIED_HUMAN_SESSIONS_UNVERIFIED");
  if(proofs.email_provider_status_reconciled!==true)status.push("ELIGIBLE_EMAIL_AUDIENCE_UNVERIFIED");
  if(proofs.merchant_paid_reporting_reconciled!==true)status.push("PAID_ORDER_SOURCE_UNVERIFIED");
  if(proofs.campaign_linkage_reconciled!==true)status.push("CROSS_PLATFORM_ATTRIBUTION_UNVERIFIED");
  const windows={};
  for(const days of [7,30]){
    const start=now-days*86400000;
    const inWindow=at=>{const t=Date.parse(at);return t>=start&&t<=now};
    const qs=uniq(input.sessions.filter(s=>inWindow(s.at_utc)&&s.human_review==="verified_qualified_human"&&safeRef(s.asset_id)&&s.utm_medium==="organic_social"&&s.utm_content===s.asset_id&&s.provider_ref&&safeRef(s.provider_ref)),s=>s.session_id);
    const ids=new Set(qs.map(s=>s.session_id));
    const cs=uniq(input.confirmations.filter(c=>inWindow(c.at_utc)&&c.provider==="jetpack"&&c.status==="Subscribed"&&c.transition==="confirmed"&&c.verification==="provider_verified"&&ids.has(c.attributed_session_id)),c=>c.opaque_subscriber_ref);
    const rawOrders=input.orders.filter(o=>inWindow(o.at_utc)&&o.status==="settled"&&o.verification==="independently_reported_paid"&&o.provider==="affiliate_network"&&safeRef(o.proof_reference)&&safeRef(o.attribution_proof)&&ids.has(o.attributed_session_id)&&Number.isSafeInteger(o.commission_minor)&&o.commission_minor>=0&&Number.isSafeInteger(o.fees_minor)&&o.fees_minor>=0&&Number.isSafeInteger(o.refunds_minor)&&o.refunds_minor>=0);
    const txSeen=new Map();
    for(const o of rawOrders){
      if(txSeen.has(o.transaction_ref)){
        const prior=txSeen.get(o.transaction_ref);
        must(JSON.stringify(prior)===JSON.stringify(o),"conflicting_duplicate_paid_order");
      } else txSeen.set(o.transaction_ref,o);
    }
    const paid=[...txSeen.values()], net=paid.reduce((n,o)=>n+o.commission_minor-o.fees_minor-o.refunds_minor,0);
    const denominatorsOk=proofs.qualified_sessions_verified===true;
    const revenueOk=denominatorsOk&&proofs.merchant_paid_reporting_reconciled===true&&proofs.campaign_linkage_reconciled===true;
    const eligibleLeadsOk=denominatorsOk&&proofs.email_provider_status_reconciled===true;
    windows[days+"d"]={
      qualified_sessions:denominatorsOk?qs.length:null,
      confirmed_leads:eligibleLeadsOk?cs.length:null,
      independently_reported_paid_orders:revenueOk?paid.length:null,
      reported_net_commission_minor:revenueOk?net:null,
      reported_net_per_1000_sessions_minor:revenueOk&&qs.length>0?Math.round(net*1000/qs.length):null,
      low_sample_warning:denominatorsOk&&qs.length<100,
      source_classification:input.mode==="SYNTHETIC_ONLY"?"SIMULATED_NOT_REAL":"SOURCE_LEDGER_NOT_EXTERNALLY_AUDITED",
      orders_not_in_cohort_or_unverified:input.orders.length-paid.length
    };
  }
  return {release:"HOLD_UNSENT",affiliate_email_permission:"NOT_VERIFIED",data_scope:input.mode,blockers:status,windows};
};
module.exports={scoreLedger};
