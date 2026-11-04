'use strict';
/**
 * Final Vestige Studios / Mind R125.
 * Offline, PURE arithmetic validation. NOT an analytics collector and NOT production code.
 * This does not certify a merchant order; only authenticated merchant evidence can.
 * No external network, cookies, email, buyer identifiers or browser storage.
 */
const FORBIDDEN_KEYS=/^(?:email|e_mail|first_name|last_name|full_name|customer_name|phone|phone_number|ip|ip_address|address|postal_address|device_id|cookie_id|user_agent|customer_id|buyer_id|order_id|transaction_id)$/i;
function noPersonalData(value){
  if(value && typeof value === 'object'){
    for(const [k,v] of Object.entries(value)){
      if(FORBIDDEN_KEYS.test(k)) throw new Error('PII_FIELD_PROHIBITED');
      noPersonalData(v);
    }
  }
}
function safeInteger(v,field){
  if(!Number.isSafeInteger(v)||v<0) throw new Error('INVALID_'+field.toUpperCase());
}
function evaluateSettledAffiliateCohort(cohort){
  if(!cohort || typeof cohort !== 'object' || Array.isArray(cohort)) throw new Error('INVALID_COHORT');
  noPersonalData(cohort);
  if (![7,30].includes(cohort.window_days)) throw new Error('INVALID_WINDOW');
  if (typeof cohort.asset_id !== 'string'||!/^[a-zA-Z0-9_-]{3,80}$/.test(cohort.asset_id)) throw new Error('MISSING_OR_INVALID_REAL_ASSET_ID');
  if (cohort.affiliate_clicks!==undefined) safeInteger(cohort.affiliate_clicks,'affiliate_clicks');
  if (cohort.confirmed_leads!==undefined) safeInteger(cohort.confirmed_leads,'confirmed_leads');
  if (cohort.qualified_human_sessions == null || cohort.settled_commission_cents == null ||
      cohort.refunded_commission_cents == null || cohort.fees_cents == null ||
      cohort.confirmed_paid_orders == null || cohort.merchant_settlement_verified !== true ||
      cohort.media_provenance_verified !== true || cohort.campaign_attribution_verified !== true) {
    return {status:'NOT_COMPUTABLE',reason:'Missing independently verified qualified session / media attribution / merchant settlement fields',net_revenue_per_1000_qualified_sessions_usd:null,confirmed_paid_conversion_rate:null};
  }
  for(const key of ['qualified_human_sessions','settled_commission_cents','refunded_commission_cents','fees_cents','confirmed_paid_orders'])
    safeInteger(cohort[key],key);
  if (cohort.qualified_human_sessions===0) {
    return {status:'NOT_COMPUTABLE',reason:'No qualified sessions in the denominator',net_revenue_per_1000_qualified_sessions_usd:null,confirmed_paid_conversion_rate:null};
  }
  if(cohort.confirmed_paid_orders>cohort.qualified_human_sessions) throw new Error('INCONSISTENT_ORDER_DENOMINATOR');
  if(cohort.refunded_commission_cents>cohort.settled_commission_cents) throw new Error('REFUNDS_EXCEED_GROSS');
  const netCents=cohort.settled_commission_cents-cohort.refunded_commission_cents-cohort.fees_cents;
  const rate=Math.round((cohort.confirmed_paid_orders/cohort.qualified_human_sessions)*10000)/10000;
  const perThousand=Math.round(((netCents*10)/cohort.qualified_human_sessions)*100)/100;
  return {status:'COMPUTABLE_FROM_VERIFIED_INPUT',window_days:cohort.window_days,
    net_revenue_usd:Math.round(netCents)/100,
    net_revenue_per_1000_qualified_sessions_usd:perThousand,
    confirmed_paid_conversion_rate:rate,
    confirmed_paid_orders:cohort.confirmed_paid_orders,
    qualified_human_sessions:cohort.qualified_human_sessions,
    tiny_sample_warning:cohort.qualified_human_sessions<250||cohort.confirmed_paid_orders<20,
    note:'Calculates supplied verified aggregate inputs; does NOT independently prove authenticity of the merchant ledger.'};
}
module.exports={evaluateSettledAffiliateCohort,noPersonalData};
