'use strict';
/* Final Vestige Dispatch R334. Pure, local, non-sending synthetic-proof auditor.
   This is NOT a subscriber exporter, a link builder, or a sales-reporting system. */
const HOLD = 'HOLD_UNSENT';
const required = Object.freeze([
  'founder_campaign_approval','provider_eligible_recipient_proof',
  'provider_confirmed_opt_in_proof','welcome_receipt_proof',
  'publisher_postal_proof','native_unsubscribe_receipt_proof',
  'jetpack_actual_render_proof','native_subject_and_footer_review',
  'merchant_account_approval','merchant_email_channel_permission',
  'issued_affiliate_link_proof','founder_approved_live_buyer_guide',
  'product_claim_and_checkout_review','independent_settlement_export'
]);
const allowedSources = new Set(['youtube','tiktok','instagram','facebook','pinterest','x','bluesky']);
const types = new Set(['landing','cta_click','signup_attempt','provider_confirmed_signup','welcome_receipt','guide_visit','affiliate_outbound','merchant_paid_order','merchant_refund']);
function assertSanitized(obj){
  const forbidden = /(^|[_-])(email|phone|ip|full_name|first_name|last_name|street|address|recipient|contact|customer_email|raw_user)([_-]|$)/i;
  function walk(v, path='root'){
    if(v===null||v===undefined)return;
    if(Array.isArray(v)){v.forEach((n,i)=>walk(n,path+"["+i+"]"));return;}
    if(typeof v==='object') {for(const [k,val] of Object.entries(v)){if(forbidden.test(k) && !(path==='root.receipts' && required.includes(k)))throw new Error("PII_FIELD_REJECTED:"+path+"."+k);walk(val,path+"."+k)}return;}
    if(typeof v==='string' && (/\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b/i.test(v)||/\b(?:\d{1,3}\.){3}\d{1,3}\b/.test(v)||/[?&](?:email|phone|token)=/i.test(v)))throw new Error("PII_VALUE_REJECTED:"+path);
  }
  walk(obj);
}
function nonempty(v){return typeof v==='string' && /^[A-Za-z0-9_-]{8,120}$/.test(v)}
function auditor(input){
  if(!input || input.synthetic!==true || !Array.isArray(input.events))throw new Error('SYNTHETIC_EVENTS_REQUIRED');
  assertSanitized(input);
  if(input.events.length>5000)throw new Error('TOO_MANY_EVENTS');
  const ids=new Set();const signups=new Set();const sessions=new Set();const settlements=new Map();
  const qa={qualified_session_candidates:0,signup_attempts:0,provider_confirmed_candidates:0,guide_visits:0,outbound_clicks:0,settled_order_candidates:0,refund_candidates:0};
  const warnings=[];
  for(const e of input.events){
    if(!e || !types.has(e.type) || !nonempty(e.event_id) || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(e.at))throw new Error('BAD_EVENT_SCHEMA');
    if(Number.isNaN(Date.parse(e.at)))throw new Error('INVALID_TIME');
    if(ids.has(e.event_id))throw new Error('DUPLICATE_EVENT_ID');ids.add(e.event_id);
    if(e.type==='landing'){
      if(!nonempty(e.session_ref)||!nonempty(e.asset_id)||!allowedSources.has(e.utm_source)||e.utm_medium!=='organic_social'||!/^([a-z0-9]+_){1,6}pilot_2026_11$/.test(e.utm_campaign))throw new Error('INVALID_ACQUISITION_PROVENANCE');
      if(e.quality_status==='provider_human_classified'&&!sessions.has(e.session_ref)){sessions.add(e.session_ref);qa.qualified_session_candidates++}
    } else if(e.type==='signup_attempt')qa.signup_attempts++;
    else if(e.type==='provider_confirmed_signup'){
      if(e.provider!=='jetpack'||e.provider_status!=='confirmed'||e.consent_scope!=='fv_dispatch'||!nonempty(e.subscriber_ref)||!nonempty(e.provider_receipt_ref))throw new Error('UNPROVEN_LEAD');
      if(!signups.has(e.subscriber_ref)){signups.add(e.subscriber_ref);qa.provider_confirmed_candidates++}
    } else if(e.type==='guide_visit')qa.guide_visits++;
    else if(e.type==='affiliate_outbound')qa.outbound_clicks++;
    else if(e.type==='merchant_paid_order'){
      if(e.issuer!=='merchant_settlement_export'||e.state!=='settled'||!nonempty(e.order_ref)||!Number.isSafeInteger(e.commission_cents)||e.commission_cents<0)throw new Error('UNVERIFIED_PAID_ORDER');
      if(settlements.has(e.order_ref))throw new Error('DUPLICATE_ORDER');settlements.set(e.order_ref,e.commission_cents);qa.settled_order_candidates++;
    } else if(e.type==='merchant_refund'){
      if(!nonempty(e.order_ref)||!Number.isSafeInteger(e.refunded_commission_cents)||e.refunded_commission_cents<0)throw new Error('BAD_REFUND');
      if(!settlements.has(e.order_ref))throw new Error('ORPHAN_REFUND');
      if(e.refunded_commission_cents>settlements.get(e.order_ref))throw new Error('REFUND_EXCEEDS_ORDER');
      settlements.set(e.order_ref,settlements.get(e.order_ref)-e.refunded_commission_cents);qa.refund_candidates++;
    }
  }
  const receipts=input.receipts||{};
  const missing=required.filter(k=>!receipts[k] || receipts[k].verified!==true || !nonempty(receipts[k].opaque_proof_ref));
  if(qa.outbound_clicks && !qa.settled_order_candidates)warnings.push('Clicks are not paid sales.');
  if(qa.signup_attempts && !qa.provider_confirmed_candidates)warnings.push('A form submit is not a provider-confirmed subscriber.');
  if(qa.provider_confirmed_candidates)warnings.push('Synthetic provider-looking receipts are not actual double-opt-in evidence.');
  if(qa.settled_order_candidates)warnings.push('Synthetic merchant-looking records are not independently settled orders.');
  return {
    dataset:'SYNTHETIC_QA_ONLY',send_authorized:false,post_publication_authorized:false,affiliate_activation_authorized:false,
    release:HOLD,commercial_offer:'ZEN12_PREMIUM_HYPOTHESIS_ONLY',
    required_receipts:required.length,missing_receipts:missing,qa_candidates:qa,
    actual_paid_orders:null,actual_confirmed_leads:null,actual_qualified_human_sessions:null,
    realized_net_revenue_per_1000:null,monetization_proven:false,warnings
  };
}
module.exports={auditor,assertSanitized,required,HOLD};
