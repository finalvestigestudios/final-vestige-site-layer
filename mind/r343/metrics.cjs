'use strict';
// Offline first-party aggregate contract. NOT a deployed analytics script.
// Never ingest visitor email, IP address, customer name, device fingerprint or cookies.
const INVALID='NOT_COMPUTABLE';
const finiteNonNegative=n=>typeof n==='number' && Number.isFinite(n) && n>=0;
function computeVerifiedRevenue(input){
 if(!input||!['7','30'].includes(String(input.period_days))||
    !input.campaign||!input.reconciliation_complete) return {status:INVALID,reason:'period_campaign_or_reconciliation_missing'};
 const s=input.qualified_sessions;
 if(!s||s.provider_attested!==true||!finiteNonNegative(s.human_count)||
    s.human_count===0||s.campaign!==input.campaign||
    s.period_days!==input.period_days) return {status:INVALID,reason:'qualified_human_sessions_unverified'};
 if(!Array.isArray(input.receipts)) return {status:INVALID,reason:'merchant_receipts_missing'};
 const relevant=input.receipts.filter(r=>r.campaign===input.campaign && r.period_days===input.period_days);
 const keys=new Set();let net=0,paid=0;
 for(const r of relevant){
   // Provisional clicks, signups, and checkouts are NEVER purchases.
   if(r.event_type!=='paid_order_verified'&&r.event_type!=='affiliate_commission_settled')continue;
   if(!r.provider_attested||r.settlement_status!=='settled'||!r.transaction_key ||
      !['owned_digital_order','affiliate_commission'].includes(r.receipt_kind)||
      !finiteNonNegative(r.gross_amount)||!finiteNonNegative(r.refund_amount)||
      !finiteNonNegative(r.fee_amount))return {status:INVALID,reason:'receipt_unreconciled'};
   if(keys.has(r.transaction_key))return {status:INVALID,reason:'duplicate_transaction'};
   keys.add(r.transaction_key);paid++;net+=r.gross_amount-r.refund_amount-r.fee_amount;
 }
 const leads=input.confirmed_leads;
 const lead_to_customer=(leads&&leads.provider_attested===true&&finiteNonNegative(leads.count)&&leads.count>0)
   ? paid/leads.count : null;
 return {status:'VERIFIED_INPUTS_ONLY',campaign:input.campaign,period_days:input.period_days,
   qualified_human_sessions:s.human_count,confirmed_paid_receipts:paid,
   net_revenue:Math.round(net*100)/100,net_per_1000_qualified:Math.round(100000*net/s.human_count)/100,
   verified_paid_rate:paid/s.human_count,lead_to_customer_rate:lead_to_customer,
   note:'Synthetic fixture math; not actual Final Vestige financial evidence'};
}
module.exports={computeVerifiedRevenue,INVALID};
