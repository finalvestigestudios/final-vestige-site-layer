'use strict';
/** Aggregated, consent-aware financial reconciler. All currency is integer cents.
 * Pass only verified nonpersonal aggregate counts and provider-settled transaction totals.
 * For an affiliate, gross_cents means settled commission, NOT order value.
 * Never count outbound clicks as paid orders. Do not subtract fees already netted.
 */
const calculateCohort=function calculateCohort(data){
 const allowed=["cohort_days","qualified_human_sessions","session_evidence","settlements"];
 if(!data||typeof data!=="object"||Object.keys(data).some(k=>!allowed.includes(k)))throw new Error("Unknown field / possible personal data");
 if(![7,30].includes(data.cohort_days))throw new Error("Cohort must be 7 or 30 days");
 if(!Number.isSafeInteger(data.qualified_human_sessions)||data.qualified_human_sessions<=0||data.session_evidence!=="verified")return {status:"NOT_COMPUTABLE",reason:"qualified human sessions unverified"};
 if(!Array.isArray(data.settlements)||data.settlements.length===0)return {status:"NOT_COMPUTABLE",reason:"no verified settled order or commission records"};
 let gross=0,refunds=0,fees=0,costs=0;
 for(const s of data.settlements){
  const keys=["channel","verified","settled","gross_cents","refund_cents","fee_cents","variable_cost_cents"];
  if(!s||typeof s!=="object"||Object.keys(s).some(k=>!keys.includes(k)))throw new Error("Unexpected settlement field; no PII allowed");
  if(!["owned_product","affiliate_commission"].includes(s.channel)||s.verified!==true||s.settled!==true)return {status:"NOT_COMPUTABLE",reason:"unverified or unsettled records"};
  for(const k of ["gross_cents","refund_cents","fee_cents","variable_cost_cents"]){if(!Number.isSafeInteger(s[k])||s[k]<0)throw new Error("Amounts must be non-negative integer cents")}
  gross+=s.gross_cents;refunds+=s.refund_cents;fees+=s.fee_cents;costs+=s.variable_cost_cents;
 }
 const net=gross-refunds-fees-costs;
 return {status:"CALCULATED_FROM_VERIFIED_INPUTS",cohort_days:data.cohort_days,qualified_human_sessions:data.qualified_human_sessions,gross_cents:gross,refund_cents:refunds,fee_cents:fees,variable_cost_cents:costs,net_cents:net,net_revenue_per_1000_human_sessions_cents:Math.round(1000*net/data.qualified_human_sessions),note:"Requires provider evidence, consent and independent audit; synthetic examples do not establish actual revenue."};
};
module.exports={calculateCohort};
