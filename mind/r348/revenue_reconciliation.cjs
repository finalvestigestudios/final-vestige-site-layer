// Final Vestige Mind R348 — synthetic, aggregate-only commercial scorecard.
// This module does NOT collect events, call merchants, set cookies, or report actual revenue.
// Run: node mind/r348/revenue_reconciliation.cjs
'use strict';
const FIELDS=['windowDays','qualifiedHumanSessions','settledOwnedReceipts','settledAffiliateCommissions','refunds','fees','confirmedPaidOrders','confirmedPaidCustomers','confirmedLeads','affiliateOutboundClicks','humanEvidence','settlementEvidence','adjustmentEvidence'];
const CERT='PROVIDER_VERIFIED';
function reconcile(input){
 if(!input || typeof input!=='object' || Array.isArray(input))throw Error('Aggregate cohort object required');
 for(const key of Object.keys(input))if(!FIELDS.includes(key))throw Error('Disallowed field in privacy-safe aggregate: '+key);
 if(![7,30].includes(input.windowDays))throw Error('Only 7 or 30 day cohorts supported');
 const nums=['qualifiedHumanSessions','settledOwnedReceipts','settledAffiliateCommissions','refunds','fees','confirmedPaidOrders','confirmedPaidCustomers','confirmedLeads','affiliateOutboundClicks'];
 for(const k of nums)if(input[k]!=null && (!Number.isFinite(input[k])||input[k]<0))throw Error('Invalid nonnegative aggregate '+k);
 for(const k of ['qualifiedHumanSessions','confirmedPaidOrders','confirmedPaidCustomers','confirmedLeads','affiliateOutboundClicks'])if(input[k]!=null && !Number.isInteger(input[k]))throw Error('Count must be integer '+k);
 const complete=['qualifiedHumanSessions','settledOwnedReceipts','settledAffiliateCommissions','refunds','fees','confirmedPaidOrders','confirmedPaidCustomers'].every(k=>input[k]!=null);
 const verified=input.humanEvidence===CERT && input.settlementEvidence===CERT && input.adjustmentEvidence===CERT;
 const reason=!verified?'MISSING_PROVIDER_VERIFICATION':!complete?'MISSING_INPUT':input.qualifiedHumanSessions===0?'NO_QUALIFIED_HUMAN_DENOMINATOR':null;
 if(reason)return {windowDays:input.windowDays,status:'NOT_COMPUTABLE',reason,realizedNetRevenue:null,netRevenuePer1000QualifiedHumanSessions:null,paidConversionRate:null,leadToCustomerConversion:null};
 const net=input.settledOwnedReceipts+input.settledAffiliateCommissions-input.refunds-input.fees;
 return {
  windowDays:input.windowDays,status:'COMPUTABLE',reason:null,realizedNetRevenue:net,
  netRevenuePer1000QualifiedHumanSessions:1000*net/input.qualifiedHumanSessions,
  paidConversionRate:input.confirmedPaidOrders/input.qualifiedHumanSessions,
  leadToCustomerConversion:input.confirmedLeads>0?input.confirmedPaidCustomers/input.confirmedLeads:null,
  affiliateOutboundClicks:input.affiliateOutboundClicks??null,
  confirmation:'SYNTHETIC_ONLY_UNLESS_REAL_PROVIDER_REPORTS_SUPPLIED'
 };
}
function selftest(){
 let n=0;const assert=(c,m)=>{n++;if(!c)throw Error('FAIL '+m)};
 const base={windowDays:7,qualifiedHumanSessions:200,settledOwnedReceipts:50,settledAffiliateCommissions:20,refunds:10,fees:5,confirmedPaidOrders:4,confirmedPaidCustomers:3,confirmedLeads:20,affiliateOutboundClicks:100,humanEvidence:CERT,settlementEvidence:CERT,adjustmentEvidence:CERT};
 let x=reconcile(base);
 assert(x.realizedNetRevenue===55,'refund-adjusted realized net');
 assert(x.netRevenuePer1000QualifiedHumanSessions===275,'net/1000');
 assert(x.paidConversionRate===.02,'orders vs clicks');
 assert(x.leadToCustomerConversion===.15,'confirmed leads only');
 assert(reconcile({...base,affiliateOutboundClicks:19999}).netRevenuePer1000QualifiedHumanSessions===275,'outbound clicks excluded');
 assert(reconcile({...base,settlementEvidence:'SELF_REPORTED'}).status==='NOT_COMPUTABLE','unverified sales blocked');
 assert(reconcile({...base,fees:null}).status==='NOT_COMPUTABLE','missing fees blocked');
 assert(reconcile({...base,qualifiedHumanSessions:0}).status==='NOT_COMPUTABLE','no denominator');
 assert(reconcile({...base,refunds:90}).realizedNetRevenue===-25,'losses not hidden');
 assert(reconcile({...base,windowDays:30}).windowDays===30,'30-day cohort');
 assert(reconcile({...base,confirmedLeads:0}).leadToCustomerConversion===null,'no lead denominator');
 try{reconcile({...base,email:'visitor@example.com'});throw Error('Privacy guard escaped')}catch(e){assert(/Disallowed field/.test(String(e)),'PII key rejected')}
 try{reconcile({...base,confirmedPaidOrders:-1});throw Error('Negative count escaped')}catch(e){assert(/Invalid nonnegative/.test(String(e)),'negative aggregate rejected')}
 assert(reconcile({...base,humanEvidence:null}).status==='NOT_COMPUTABLE','unverified humans blocked');
 return n;
}
module.exports={reconcile,selftest};
if(require.main===module)console.log('PASS R348 aggregate-only synthetic metrics '+selftest()+' checks; no real receipts or clients accessed.');
