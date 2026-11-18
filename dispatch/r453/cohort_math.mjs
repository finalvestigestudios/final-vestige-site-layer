/** Dispatch R453: read-only CLOSED acquisition cohort evaluator (7/30d).
 * SYNTHETIC unit test fixtures, NOT the site's actual metrics. No IO or personal data.
 */
export function timestamp(v) {const d=typeof v==="string"?new Date(v):new Date(NaN);return /^\d{4}-\d{2}-\d{2}T.*Z$/.test(v||"")&&Number.isFinite(d.getTime())?d.getTime():null}

export function measureClosedCohort(v) {
  const proved = p => p?.verified === true && typeof p?.source_ref === "string"
    && /^(https:\/\/|provider:|sha256:)/.test(p.source_ref)
    && typeof p?.checked_at === "string" && /^\d{4}-\d{2}-\d{2}T/.test(p.checked_at);
  const missing=(reason)=>({status:"UNCOMPUTABLE",reason,net_revenue_per_1000_cents:null});
  if(!v||![7,30].includes(v.horizon_days))return missing("unsupported_horizon");
  const start=timestamp(v.cohort_start),end=timestamp(v.cohort_end),asof=timestamp(v.as_of);
  if(start===null||end===null||asof===null||start>=end)return missing("invalid_window");
  if(asof<end+v.horizon_days*86400000)return missing("cohort_not_mature");
  if(!v.complete_sessions||!v.complete_orders||!proved(v.sessions_proof)||!proved(v.orders_proof))return missing("incomplete_verification");
  if(!Array.isArray(v.sessions)||!Array.isArray(v.orders))return missing("event_ledger_missing");
  const sessionMap=new Map();
  for(const s of v.sessions){
    const t=timestamp(s?.seen_at);
    if(t===null||typeof s.id!=="string"||s.id.length<3)return missing("invalid_session");
    if(t<start||t>=end)continue;
    if(s.kind!=="qualified_human"||s.bot===true)continue;
    if(!proved(s.proof)||!s.utm||!["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"].includes(s.utm.source)||s.utm.medium!=="organic_social"||typeof s.utm.asset_id!=="string"||s.utm.asset_id.length<3)return missing("unproven_qualified_session");
    const sig=JSON.stringify([s.seen_at,s.utm]);
    if(sessionMap.has(s.id)&&sessionMap.get(s.id).sig!==sig)return missing("conflicting_duplicate_session");
    sessionMap.set(s.id,{s,t,sig});
  }
  const orderMap=new Map();let net=0,gross=0,fees=0,refunds=0,paid=0;
  for(const o of v.orders){
    if(o?.currency!=="USD"||typeof o?.id!=="string"||o.id.length<3||o.state!=="settled"||!proved(o.settlement_proof)||!["direct","affiliate"].includes(o.sale_type))return missing("unverified_or_invalid_settlement");
    if([o.gross_cents,o.fees_cents,o.refunds_cents].some(n=>!Number.isSafeInteger(n)||n<0)||o.fees_cents+o.refunds_cents>o.gross_cents)return missing("invalid_order_amount");
    const sig=JSON.stringify([o.sale_type,o.gross_cents,o.fees_cents,o.refunds_cents,o.settled_at,o.session_id]);
    if(orderMap.has(o.id)&&orderMap.get(o.id)!==sig)return missing("conflicting_duplicate_order");
    if(orderMap.has(o.id))continue;
    orderMap.set(o.id,sig);
    const session=sessionMap.get(o.session_id);
    if(!session||!proved(o.attribution_proof))continue;
    const settled=timestamp(o.settled_at);
    if(settled===null)return missing("invalid_settlement_time");
    if(settled<session.t||settled>=session.t+v.horizon_days*86400000)continue;
    gross+=o.gross_cents;fees+=o.fees_cents;refunds+=o.refunds_cents;paid++;
  }
  net=gross-fees-refunds;
  if(sessionMap.size===0)return missing("zero_verified_human_sessions");
  return {status:"COMPUTABLE",kind:"closed_acquisition_cohort",horizon_days:v.horizon_days,verified_qualified_sessions:sessionMap.size,independently_attributed_paid_orders:paid,gross_cents:gross,fees_cents:fees,refunds_cents:refunds,net_cents:net,net_revenue_per_1000_cents:Math.round(net*1000/sessionMap.size),warning:"Only mature source-attributed sessions and independently settled paid orders are counted. This is observational attribution, not causal lift."};
}
