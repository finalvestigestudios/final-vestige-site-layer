"use strict";
// Pure offline control. NEVER reads subscriber identities or production analytics.
const HOLD = 'HOLD_UNSENT';
function reconcileCounters(newsletter, followers) {
  if (!newsletter || !followers) throw Error('BOTH_SNAPSHOTS_REQUIRED');
  for (const n of [newsletter.total, newsletter.confirmed, newsletter.unconfirmed, followers.email, followers.wpcom]) {
    if (!Number.isSafeInteger(n) || n < 0) throw Error('INVALID_COUNTER');
  }
  const findings=[];
  if(newsletter.total!==newsletter.confirmed+newsletter.unconfirmed) findings.push('NOT_ADDITIVE_POSSIBLE_PENDING_REQUEST_OVERLAP');
  if(followers.email===0 && followers.wpcom>0) findings.push('EMAIL_ONLY_ZERO_DOES_NOT_ESTABLISH_ZERO_EMAIL_DELIVERY');
  return Object.freeze({newsletter_total:newsletter.total,newsletter_confirmed:newsletter.confirmed,unconfirmed_requests:newsletter.unconfirmed,
    wpcom_followers:followers.wpcom,email_only_followers:followers.email,email_eligible_recipients:null,
    findings,release_status:HOLD});
}
function confirmedSignup(candidate) {
  if (!candidate || typeof candidate!=='object') return false;
  return candidate.provider_confirmed===true && candidate.email_subscription_status==='Subscribed' &&
    candidate.consent_proof_verified===true && candidate.suppressed!==true && candidate.event_name==='confirmed_signup' &&
    typeof candidate.provider_transition_id==='string' && /^[a-zA-Z0-9_-]{8,96}$/.test(candidate.provider_transition_id) &&
    typeof candidate.confirmed_at==='string' && Number.isFinite(Date.parse(candidate.confirmed_at));
}
function dedupeConfirmed(events) {
  if(!Array.isArray(events)) throw Error('EVENTS_ARRAY_REQUIRED');
  const seen=new Set();let eligible=0;let rejected=0;let duplicate=0;
  for(const e of events){if(!confirmedSignup(e)){rejected++;continue;}
    if(seen.has(e.provider_transition_id)){duplicate++;continue;}
    seen.add(e.provider_transition_id);eligible++;
  }
  return Object.freeze({synthetic_confirmed_transitions:eligible,rejected,duplicate,
    production_confirmed_signups:null, production_email_eligible:null});
}
function validateAttribution(record) {
  const errors=[]; const err=s=>errors.push(s);
  if(!record||typeof record!=='object') return {errors:['RECORD_REQUIRED'],paid_attributed:false};
  if(record.is_synthetic!==false) err('NOT_AUTHENTICATED_PRODUCTION');
  if(record.provider_order_verified!==true || record.commission_settled!==true || record.refund_reconciled!==true || record.fees_reconciled!==true) err('PAID_SETTLEMENT_UNVERIFIED');
  if(typeof record.asset_id!=='string'||!/^grok-[a-z0-9_-]{4,80}$/.test(record.asset_id)) err('ASSET_ID_UNVERIFIED');
  if(!['utm_source=timeline','utm_source=tiktok','utm_source=youtube','utm_source=shorts'].includes(record.utm_source)) err('UTM_SOURCE_INVALID');
  if(record.offer_id!=='zen12') err('SINGLE_OFFER_MISMATCH');
  if(!record.outbound_affiliate_click_verified) err('NO_AUTHENTICATED_AFFILIATE_CLICK');
  const dates=['session_at','cta_at','click_at','order_at','settled_at'];
  const parsed=dates.map(d=>typeof record[d]==='string'?Date.parse(record[d]):NaN);
  if(parsed.some(x=>!Number.isFinite(x)) || parsed.some((x,i)=>i>0&&x<parsed[i-1])) err('CAUSAL_TIMELINE_INVALID');
  if(record.currency!=='USD'||!Number.isSafeInteger(record.net_commission_cents)||record.net_commission_cents<0) err('NET_REVENUE_INVALID');
  // A locally supplied provider-verified boolean is not independent provider attestation.
  // Never turn JSON assertions into actual reported money.
  return Object.freeze({errors,paid_attributed:false,verified_net_revenue_usd:null,
    verified_net_revenue_per_1000_qualified_human_sessions:null});
}
function releaseDecision(packet) {
  const blockers=['founder_final_approval','physical_address_verified','delivered_unsubscribe_verified','native_preview_verified','welcome_received_verified','eligible_audience_verified'];
  const missing=blockers.filter(k=>packet?.[k]!==true);
  for(const k of ['merchant_email_permission','merchant_account_accepted','issued_affiliate_link','approved_live_guide','checkout_terms_verified']) if(packet?.[k]!==true) missing.push(k);
  return Object.freeze({status:HOLD,commercial_issues:[3,5],missing_proofs:missing,can_send:false});
}
module.exports={reconcileCounters,confirmedSignup,dedupeConfirmed,validateAttribution,releaseDecision};
