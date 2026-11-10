'use strict';
/**
 * Dispatch R265: non-sending, privacy-safe attribution and cohort audit.
 * Input may contain synthetic records or separately attested, aggregate-only
 * source evidence. No live analytics, mail, merchant, or WordPress calls.
 * A PASS means internally consistent HOLD-only evidence, NEVER approval to send.
 */
const SCHEMA = 'FV-DISPATCH-COHORT-V1';
const REFERENCE = '2026-11-10';
const SOURCES = new Set(['youtube','tiktok','instagram','facebook']);
const safeId = v => typeof v === 'string' && /^[a-z0-9][a-z0-9_-]{0,62}$/.test(v);
const keys = (obj, expected) => !!obj && !Array.isArray(obj) && typeof obj === 'object' &&
  JSON.stringify(Object.keys(obj).sort()) === JSON.stringify(expected.slice().sort());
const dateValid = d => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d) &&
  !Number.isNaN(Date.parse(d+'T00:00:00Z')) && new Date(d+'T00:00:00Z').toISOString().slice(0,10) === d;
const dayNumber = d => Date.parse(d+'T00:00:00Z')/86400000;
const cents = v => Number.isSafeInteger(v) && v >= 0;
function inspection(input){
  const errors=[]; const add = x => {if (!errors.includes(x)) errors.push(x);};
  if (!keys(input,['schema','mode','as_of_day','attestations','sessions','confirmations','settlements']))
    return {pass:false,errors:['invalid_top_level'],state:'HOLD_UNSENT',cohorts:null};
  if (input.schema!==SCHEMA || !['synthetic','external_aggregate'].includes(input.mode) || !dateValid(input.as_of_day)) add('schema_mode_or_date');
  const at=input.attestations;
  const required=['complete_qualified_sessions','jetpack_confirmations_verified','merchant_settlements_reconciled','cohort_attribution_verified','publisher_postal_and_unsubscribe_verified','partner_email_permission_verified','founder_campaign_approval'];
  if (!keys(at,required) || required.some(k=>typeof at?.[k]!=='boolean')) add('missing_attestations');
  // This is a non-sending offline audit; attestation is not external proof.
  for (const k of ['publisher_postal_and_unsubscribe_verified','partner_email_permission_verified','founder_campaign_approval'])
    if (at?.[k]!==false) add('improper_release_claim_'+k);
  if (!Array.isArray(input.sessions) || !Array.isArray(input.confirmations) || !Array.isArray(input.settlements))
    return {pass:false,errors:[...errors,'event_lists_required'],state:'HOLD_UNSENT',cohorts:null};
  const sourceKeys=['day','platform','campaign','asset_id','qualified_human_sessions'];
  const confirmationKeys=['day','provider','event_ref','status','consent_scope'];
  const settlementKeys=['acquisition_day','settled_day','merchant','order_ref','origin_platform','campaign','asset_id','status','gross_commission_cents','refund_cents','fee_cents'];
  const sessionSeen=new Set(), confirmSeen=new Set(), orderSeen=new Set();
  const sessions=[]; const confirmations=[]; const orders=[];
  function routeValid(r){return SOURCES.has(r.platform) && safeId(r.campaign) && safeId(r.asset_id) && r.campaign.startsWith('cluster_pilot_');}
  input.sessions.forEach((s,i)=>{
    if(!keys(s,sourceKeys)|| !dateValid(s?.day) || !routeValid(s) || !cents(s.qualified_human_sessions) || s.day>input.as_of_day) return add('invalid_session_'+i);
    const k=[s.day,s.platform,s.campaign,s.asset_id].join(':');
    if(sessionSeen.has(k)) return add('duplicate_daily_aggregate_'+i);
    sessionSeen.add(k); sessions.push(s);
  });
  input.confirmations.forEach((s,i)=>{
    if(!keys(s,confirmationKeys)||!dateValid(s?.day)||s.day>input.as_of_day||s.provider!=='jetpack'||!safeId(s.event_ref)||!['confirmed','pending','suppressed'].includes(s.status)||s.consent_scope!=='fv_dispatch') return add('invalid_confirmation_'+i);
    if(confirmSeen.has(s.event_ref)) return; // Deduplicate repeated provider confirmation, NOT signup attempts.
    confirmSeen.add(s.event_ref);
    if(s.status==='confirmed') confirmations.push(s);
  });
  input.settlements.forEach((s,i)=>{
    if(!keys(s,settlementKeys)||!dateValid(s?.acquisition_day)||!dateValid(s?.settled_day)||s.settled_day>input.as_of_day||s.acquisition_day>s.settled_day||s.merchant!=='inspire3'||!safeId(s.order_ref)||!['settled','pending','refunded'].includes(s.status)||!cents(s.gross_commission_cents)||!cents(s.refund_cents)||!cents(s.fee_cents)||s.refund_cents+s.fee_cents>s.gross_commission_cents||!routeValid({...s,platform:s.origin_platform})) return add('invalid_settlement_'+i);
    if(orderSeen.has(s.order_ref)) return add('duplicate_order_'+i);
    orderSeen.add(s.order_ref);
    if(s.status==='settled') orders.push(s);
  });
  if(errors.length) return {pass:false,errors,state:'HOLD_UNSENT',cohorts:null};
  const complete = at.complete_qualified_sessions && at.jetpack_confirmations_verified && at.merchant_settlements_reconciled && at.cohort_attribution_verified;
  // Even externally asserted completeness is not independent validation; caller must authenticate sources.
  const earliest = n => dayNumber(input.as_of_day)-n+1;
  const cohorts = {};
  for (const window of [7,30]){
    const start=earliest(window);
    const inPeriod = d => dayNumber(d)>=start && dayNumber(d)<=dayNumber(input.as_of_day);
    const visit=sessions.filter(s=>inPeriod(s.day));
    const relevant=new Set(visit.map(s=>[s.platform,s.campaign,s.asset_id].join(':')));
    const countedOrders=orders.filter(o=>inPeriod(o.acquisition_day) && relevant.has([o.origin_platform,o.campaign,o.asset_id].join(':')));
    const human=visit.reduce((sum,x)=>sum+x.qualified_human_sessions,0);
    const gross=countedOrders.reduce((sum,x)=>sum+x.gross_commission_cents,0);
    const refunds=countedOrders.reduce((sum,x)=>sum+x.refund_cents,0);
    const fees=countedOrders.reduce((sum,x)=>sum+x.fee_cents,0);
    const leads=confirmations.filter(x=>inPeriod(x.day)).length;
    const money=complete && human>0;
    cohorts[window+'d']={period_start:new Date(start*86400000).toISOString().slice(0,10),period_end:input.as_of_day,
      qualified_human_sessions:at.complete_qualified_sessions?human:null,
      deduped_confirmed_signups:at.jetpack_confirmations_verified?leads:null,
      settled_attributed_orders:at.merchant_settlements_reconciled&&at.cohort_attribution_verified?countedOrders.length:null,
      gross_commission_cents:at.merchant_settlements_reconciled&&at.cohort_attribution_verified?gross:null,
      refund_cents:at.merchant_settlements_reconciled&&at.cohort_attribution_verified?refunds:null,
      fee_cents:at.merchant_settlements_reconciled&&at.cohort_attribution_verified?fees:null,
      realized_net_commission_cents:at.merchant_settlements_reconciled&&at.cohort_attribution_verified?gross-refunds-fees:null,
      net_cents_per_1000_qualified_human_sessions:money?Math.round((gross-refunds-fees)*1000/human):null,
      lead_to_customer_rate:null,
      caveat:'Period is defined by verified acquisition day; settlement must be reconciled by as_of_day. No person-level lead-to-sale join.'};
  }
  return {pass:true,errors:[],state:'HOLD_UNSENT',evidence_class:input.mode==='synthetic'?'SYNTHETIC_DEMONSTRATION':'UNVERIFIED_EXTERNAL_ATTESTATION',
    cohorts,send_authorized:false,commercial_activation_authorized:false,
    warnings:['No emails, subscriber identifiers, IPs, cookies, or analytics scripts accepted.',
      'Merchant signup is never a Final Vestige confirmed_signup.',
      'External source flags are not independent merchant or provider authentication.',
      'Zero recorded orders is not evidence of zero real sales unless complete source ledgers are attested.']};
}
module.exports={inspection,SCHEMA,REFERENCE};
