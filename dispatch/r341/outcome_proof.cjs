'use strict';
// Dispatch R341 — PURE / NO NETWORK / NO SEND / NO PII
const allowed = new Set(['qualified_session','signup_attempt','confirmed_signup','fieldbook_download','email_cta_click','affiliate_settlement','direct_order_settlement']);
const sourceNames = new Set(['youtube','tiktok','instagram','facebook','pinterest','x','bluesky','email','direct']);
function validRef(s){return typeof s==='string'&&/^[a-zA-Z0-9][a-zA-Z0-9:_-]{3,99}$/.test(s);}
function date(s){const ms=Date.parse(s||''); if(!Number.isFinite(ms)||!/^\d{4}-\d{2}-\d{2}T/.test(s))throw Error('INVALID_DATE');return ms;}
function noPrivateData(value){
  const piiKey=/^(email|address|name|phone|ip|user_agent|subscriber_email|recipient|cookie|raw_url|password|token)$/i;
  const scan=(o)=>{
    if(typeof o==='string' && /[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}/.test(o))throw Error('PII_VALUE');
    if(!o||typeof o!=='object')return;
    if(Array.isArray(o)){o.forEach(scan);return;}
    for(const [k,v] of Object.entries(o)){if(piiKey.test(k))throw Error('PII_FIELD');scan(v);}
  };scan(value);
}
function compile(events,attestation,asOf){
  if(!Array.isArray(events)||!attestation||typeof attestation!=='object')throw Error('MISSING_INPUT');
  noPrivateData(events);noPrivateData(attestation);
  const now=date(asOf),past7=now-7*86400000,past30=now-30*86400000;
  const seen=new Set(), sessions=new Map(),confirms=new Map(),settlements=new Map(),counts={signup_attempt:0,fieldbook_download:0,email_cta_click:0};
  for(const e of events){
    if(!e||!allowed.has(e.type)||!validRef(e.event_id))throw Error('INVALID_EVENT');
    if(seen.has(e.event_id))throw Error('DUPLICATE_EVENT_ID');seen.add(e.event_id);
    const t=date(e.at);if(t>now)throw Error('FUTURE_EVENT');
    if(e.type==='qualified_session'){
      if(!validRef(e.session_ref)||!validRef(e.asset_id)||!sourceNames.has(e.utm_source)||e.utm_medium!=='organic_social'&&e.utm_source!=='email'||e.verified_human!==true||!validRef(e.evidence_ref))throw Error('UNVERIFIED_SESSION');
      if(sessions.has(e.session_ref))throw Error('DUPLICATE_SESSION');sessions.set(e.session_ref,{...e,t});
    }else if(e.type==='confirmed_signup'){
      if(e.provider!=='jetpack'||e.status!=='active'||e.consent_scope!=='dispatch'||!validRef(e.provider_ref)||!validRef(e.evidence_ref)||!validRef(e.confirmation_event_ref))throw Error('UNVERIFIED_SIGNUP');
      // Previously verified WordPress.com users may not receive a second confirmation challenge.
      if(!['double_opt_in','existing_verified_wpcom'].includes(e.confirmation_method))throw Error('UNKNOWN_CONFIRMATION_PATH');
      if(confirms.has(e.provider_ref))throw Error('DUPLICATE_CONFIRMED_SUBSCRIBER');confirms.set(e.provider_ref,{...e,t});
    }else if(e.type==='affiliate_settlement'||e.type==='direct_order_settlement'){
      if(e.status!=='settled'||!validRef(e.order_ref)||!validRef(e.evidence_ref)||!validRef(e.session_ref)||!['merchant_statement','own_checkout_ledger'].includes(e.ledger_source)||!['affiliate_settlement','direct_order_settlement'].includes(e.type))throw Error('UNVERIFIED_ORDER');
      if(e.type==='affiliate_settlement'&&e.ledger_source!=='merchant_statement')throw Error('AFFILIATE_NEEDS_MERCHANT_EVIDENCE');
      if(e.type==='direct_order_settlement'&&e.ledger_source!=='own_checkout_ledger')throw Error('DIRECT_NEEDS_LEDGER');
      for(const key of ['gross_revenue_cents','refund_cents','fee_cents'])if(!Number.isSafeInteger(e[key])||e[key]<0)throw Error('MISSING_FINANCIAL_COMPONENT');
      if(e.refund_cents+e.fee_cents>e.gross_revenue_cents)throw Error('UNRECONCILED_FINANCIALS');
      if(settlements.has(e.order_ref))throw Error('DUPLICATE_ORDER');settlements.set(e.order_ref,{...e,t});
    }else{
      if(e.type==='signup_attempt'&&e.provider!=='jetpack')throw Error('MERCHANT_SIGNUP_NOT_FV');
      counts[e.type]=(counts[e.type]||0)+1;
    }
  }
  for(const order of settlements.values())if(!sessions.has(order.session_ref)||order.t<sessions.get(order.session_ref).t)throw Error('ORDER_WITHOUT_QUALIFIED_SOURCE');
  function window(from){
    const ss=[...sessions.values()].filter(s=>s.t>=from);
    const ids=new Set(ss.map(s=>s.session_ref));
    const orders=[...settlements.values()].filter(o=>o.t>=from&&ids.has(o.session_ref));
    const confirmsInWindow=[...confirms.values()].filter(c=>c.t>=from).length;
    const net=orders.reduce((n,o)=>n+o.gross_revenue_cents-o.refund_cents-o.fee_cents,0);
    const complete=attestation.qualified_session_reporting_complete===true&&attestation.settlement_reporting_complete===true&&attestation.source_to_order_reconciliation_complete===true;
    return {qualified_sessions:complete?ss.length:null,confirmed_signups:attestation.provider_confirmation_reconciliation_complete===true?confirmsInWindow:null,settled_orders:complete?orders.length:null,net_revenue_cents:complete?net:null,net_revenue_per_1000_sessions_cents:complete&&ss.length>0?Math.round(net*1000/ss.length):null,reporting_complete:complete,warning:'Synthetic checks are NOT campaign results. No newsletter release or merchant promotion authorization.'};
  }
  return {status:'HOLD_UNSENT',offers:'HOLD_MERCHANT',as_of:asOf,seven_day:window(past7),thirty_day:window(past30),diagnostic_events:counts,raw_subscribers_exported:false,source:'offline_input_only'};
}
module.exports={compile,noPrivateData};