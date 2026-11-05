'use strict';
/** Mind R132: offline aggregate reconciliation only. NO visitor PII or live tracking. */
const SENSITIVE=/(name|email|phone|ip_address|address|customer|person|cookie|fingerprint|token|password)/i;
const ALLOWED=new Set(['cohort_days','qualified_human_sessions','attribution_evidence','merchant_report_complete','merchant_settlement_verified','attributable_orders','gross_commission_cents','refunds_cents','fees_cents','report_period','data_handling_approved']);
function parseAggregate(x){
  if(!x||typeof x!=='object'||Array.isArray(x))return {status:'INVALID',reason:'Object required'};
  const keys=Object.keys(x);
  if(keys.some(k=>SENSITIVE.test(k)||!ALLOWED.has(k)))return {status:'INVALID',reason:'Unexpected field or possible identifying data'};
  if(![7,30].includes(x.cohort_days))return {status:'INVALID',reason:'Cohort must be 7 or 30 days'};
  if(x.data_handling_approved!==true||x.merchant_report_complete!==true||x.merchant_settlement_verified!==true)return {status:'NOT_COMPUTABLE',reason:'Merchant eligibility or complete settlement unavailable'};
  if(x.attribution_evidence!=='verified')return {status:'NOT_COMPUTABLE',reason:'First-party to merchant attribution unavailable'};
  if(typeof x.report_period!=='string'||!/^20\d\d-\d\d-\d\d\/20\d\d-\d\d-\d\d$/.test(x.report_period))return {status:'NOT_COMPUTABLE',reason:'Bounded reconciliation period missing'};
  for(const k of ['qualified_human_sessions','attributable_orders','gross_commission_cents','refunds_cents','fees_cents'])
   if(!Number.isSafeInteger(x[k])||x[k]<0)return {status:'NOT_COMPUTABLE',reason:'Missing or invalid verified '+k};
  if(x.qualified_human_sessions===0)return {status:'NOT_COMPUTABLE',reason:'Zero qualified-human denominator'};
  if(x.refunds_cents>x.gross_commission_cents) return {status:'INVALID',reason:'Refunds exceed gross without adjustment evidence'};
  const net=x.gross_commission_cents-x.refunds_cents-x.fees_cents;
  return {status:'VERIFIED_AGGREGATE',cohort_days:x.cohort_days,attributable_orders:x.attributable_orders,net_revenue_cents:net,net_per_1000_qualified_human_sessions_cents:Math.round(net*1000/x.qualified_human_sessions),paid_order_rate:x.attributable_orders/x.qualified_human_sessions,warning:x.qualified_human_sessions<1000||x.attributable_orders<30?'TINY_SAMPLE_DO_NOT_INFER_CAUSALITY':null};
}
module.exports={parseAggregate};
