// Final Vestige Dispatch R395. Offline, pure functions: no PII, network, writes or sends.
// This does NOT establish that production analytics or merchant settlement are verified.
export const SEND_ENABLED = false;
const isId = x => typeof x === 'string' && /^[a-z0-9][a-z0-9_:-]{2,79}$/i.test(x);
const isCents = x => Number.isSafeInteger(x) && x >= 0;
const isUTC = x => typeof x === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(x) && !Number.isNaN(Date.parse(x)) && new Date(x).toISOString() === x;
const dangerous = x => x && typeof x === 'object' && ['email','ip','ip_address','phone','customer_name','subscriber_email','full_name'].some(k => Object.hasOwn(x,k));
const result = (status, reason, extra={}) => Object.freeze({status,reason,send_enabled:SEND_ENABLED,...extra});

// This deliberately requires first-party QUALIFIED sessions and a provider-settled
// affiliate ledger joined by a real Grok asset ID, NOT site views or outbound clicks.
export function assessAttributableCohort(input={}) {
  if (!input || typeof input !== 'object' || dangerous(input)) return result('NOT_COMPUTABLE','invalid or private input');
  const {issue,window_start_utc:start,window_end_utc:end,window_days:days,campaign_id:campaign,sessions,ledger} = input;
  if (![3,5].includes(issue) || !isId(campaign) || ![7,30].includes(days) || !isUTC(start) || !isUTC(end) || Date.parse(end)-Date.parse(start)!==days*86400000)
    return result('NOT_COMPUTABLE','invalid commercial cohort identity/window');
  if (!Array.isArray(sessions) || sessions.length===0) return result('NOT_COMPUTABLE','missing audited qualified-human sessions');
  let denominator=0;const assetIds=new Set(), reportIds=new Set();
  for(const s of sessions) {
    if (dangerous(s) || !s || !isId(s.asset_id) || !isId(s.report_id) || s.campaign_id!==campaign ||
        s.source_system!=='first_party_analytics' || s.provider_audited!==true ||
        !Number.isSafeInteger(s.qualified_human_sessions) || s.qualified_human_sessions<0 ||
        assetIds.has(s.asset_id) || reportIds.has(s.report_id))
      return result('NOT_COMPUTABLE','invalid, duplicate or unaudited session-source row');
    assetIds.add(s.asset_id);reportIds.add(s.report_id);denominator+=s.qualified_human_sessions;
  }
  if (!Number.isSafeInteger(denominator) || denominator<=0) return result('NOT_COMPUTABLE','no audited qualified-human-session denominator');
  if (!ledger || dangerous(ledger) || ledger.source_system!=='merchant_affiliate_dashboard' ||
      ledger.publisher_account_verified!==true || ledger.email_channel_authorized!==true ||
      ledger.exact_sku_authorized!==true || ledger.referred_guide_live_verified!==true ||
      ledger.report_reconciled!==true || ledger.complete_for_cohort!==true ||
      !isId(ledger.merchant_report_id) || ledger.currency!=='USD' ||
      !isUTC(ledger.settlement_as_of_utc) || Date.parse(ledger.settlement_as_of_utc)<Date.parse(end) ||
      !Array.isArray(ledger.records))
    return result('NOT_COMPUTABLE','SKU/EMAIL authorization or independently reconciled settlement ledger missing');
  let netCents=0; const seenSettlements=new Map(); const seenOrders=new Map();
  for(const p of ledger.records){
    if (!p || dangerous(p) || p.evidence!=='merchant_settled_commission' || p.provider_verified!==true ||
        !isId(p.settlement_id) || !isId(p.opaque_order_key) || !isId(p.asset_id) ||
        !assetIds.has(p.asset_id) || p.campaign_id!==campaign ||
        !isUTC(p.session_at_utc) || Date.parse(p.session_at_utc)<Date.parse(start) || Date.parse(p.session_at_utc)>=Date.parse(end) ||
        !isUTC(p.settled_at_utc) || Date.parse(p.settled_at_utc)>Date.parse(ledger.settlement_as_of_utc) ||
        !['settled','reversed'].includes(p.status) ||
        !['commission_cents','refund_cents','fee_cents','reversal_cents'].every(k=>isCents(p[k])))
      return result('NOT_COMPUTABLE','unattributed, private, unpaid or malformed commission record');
    const fingerprint=JSON.stringify(p);
    if(seenSettlements.has(p.settlement_id)){
      if(seenSettlements.get(p.settlement_id)!==fingerprint)
        return result('NOT_COMPUTABLE','conflicting duplicate settlement identifier');
      continue;
    }
    // One purchase may have later adjustment rows, but those need distinct settlement IDs.
    // The order key is intentionally opaque; count it once in the paid-order figure.
    seenSettlements.set(p.settlement_id,fingerprint);
    if (!seenOrders.has(p.opaque_order_key)) seenOrders.set(p.opaque_order_key,p.asset_id);
    else if(seenOrders.get(p.opaque_order_key)!==p.asset_id)
      return result('NOT_COMPUTABLE','one paid order is assigned to conflicting social assets');
    netCents+=p.commission_cents-p.refund_cents-p.fee_cents-p.reversal_cents;
  }
  if(!Number.isSafeInteger(netCents)) return result('NOT_COMPUTABLE','currency arithmetic overflow');
  return result('COMPUTABLE','audited first-party sessions joined to reconciled merchant settlement',{
    issue,campaign_id:campaign,window_days:days,qualified_human_sessions:denominator,
    verified_settlement_rows:seenSettlements.size,unique_paid_orders:seenOrders.size,net_revenue_cents:netCents,
    net_revenue_usd_per_1000_qualified_sessions:Math.round(netCents*1000/denominator)/100,
    disclaimer:'Not evidence of Final Vestige revenue unless sourced from real audited provider reports'
  });
}
