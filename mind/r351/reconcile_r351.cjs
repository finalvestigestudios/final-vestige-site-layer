'use strict';
// Aggregate, privacy-safe *synthetic* revenue gate for Mind R351.
// Run: node mind/r351/reconcile_r351.cjs
// THIS DOES NOT CONNECT TO PAYMENT PROCESSORS OR REPORT ANY REAL COMMISSION.
const assert=require('node:assert/strict');
function reconcile(x){
  const missing=[];
  if(!x||typeof x!=='object'||Array.isArray(x))return {status:'NOT COMPUTABLE',missing:['valid aggregate input']};
  const banned=/email|name|phone|ip|fingerprint|address|cookie|contact|visitor_id|user_id|transaction_id|payment_token|card/i;
  for(const k of Object.keys(x))if(banned.test(k))throw Error('Privacy field not accepted: '+k);
  if(![7,30].includes(x.cohort_days))missing.push('7/30-day cohort');
  if(!['owned_product','affiliate_commission'].includes(x.payout_type))missing.push('payout type');
  if(x.currency!=='USD')missing.push('same verified USD currency');
  if(x.paid_order_verified!==true)missing.push('merchant-confirmed paid order');
  if(x.merchant_settlement_verified!==true)missing.push('merchant-confirmed settled payout');
  if(x.fee_refund_verified!==true)missing.push('verified fees and refunds');
  if(x.qualified_sessions_verified!==true)missing.push('qualified-human source/denominator');
  if(!Number.isInteger(x.qualified_human_sessions)||x.qualified_human_sessions<=0)missing.push('positive qualified-human session denominator');
  if(!Number.isInteger(x.confirmed_paid_orders)||x.confirmed_paid_orders<=0)missing.push('positive confirmed paid order count');
  for(const name of ['settled_payout_usd','refunds_usd','fees_usd']){
    if(typeof x[name]!=='number'||!Number.isFinite(x[name])||x[name]<0)missing.push('verified nonnegative '+name);
  }
  if(missing.length)return {status:'NOT COMPUTABLE',missing:[...new Set(missing)]};
  const net=x.settled_payout_usd-x.refunds_usd-x.fees_usd;
  return {status:'COMPUTABLE_FROM_VERIFIED_INPUT',cohort_days:x.cohort_days,source:x.payout_type,
    confirmed_paid_orders:x.confirmed_paid_orders,qualified_human_sessions:x.qualified_human_sessions,
    realized_net_usd:Number(net.toFixed(2)),
    realized_net_per_1000_qualified_sessions_usd:Number((net*1000/x.qualified_human_sessions).toFixed(2)),
    paid_conversion_rate:Number((x.confirmed_paid_orders/x.qualified_human_sessions).toFixed(6)),
    note:'Only as reliable as authenticated settlement, refunds, fee and qualified-session evidence; never infer affiliate sales from clicks.'};
}
function runSyntheticTests(){
 const ready={cohort_days:7,payout_type:'owned_product',currency:'USD',paid_order_verified:true,
 merchant_settlement_verified:true,fee_refund_verified:true,qualified_sessions_verified:true,
 qualified_human_sessions:1000,confirmed_paid_orders:2,settled_payout_usd:100,refunds_usd:10,fees_usd:5};
 let n=0;const test=(msg,fn)=>{fn();n++;};
 test('owned settled net',()=>assert.equal(reconcile(ready).realized_net_usd,85));
 test('per 1000',()=>assert.equal(reconcile(ready).realized_net_per_1000_qualified_sessions_usd,85));
 test('paid rate',()=>assert.equal(reconcile(ready).paid_conversion_rate,0.002));
 test('affiliate payout not basket total',()=>assert.equal(reconcile({...ready,payout_type:'affiliate_commission',settled_payout_usd:16,refunds_usd:1,fees_usd:0}).realized_net_usd,15));
 test('30day valid',()=>assert.equal(reconcile({...ready,cohort_days:30}).status,'COMPUTABLE_FROM_VERIFIED_INPUT'));
 test('unverified purchase rejects',()=>assert.equal(reconcile({...ready,paid_order_verified:false}).status,'NOT COMPUTABLE'));
 test('unknown merchant rejects',()=>assert.equal(reconcile({...ready,merchant_settlement_verified:false}).status,'NOT COMPUTABLE'));
 test('refund unknown rejects',()=>assert.equal(reconcile({...ready,fee_refund_verified:false}).status,'NOT COMPUTABLE'));
 test('no qualified provenance rejects',()=>assert.equal(reconcile({...ready,qualified_sessions_verified:false}).status,'NOT COMPUTABLE'));
 test('zero sessions rejects',()=>assert.equal(reconcile({...ready,qualified_human_sessions:0}).status,'NOT COMPUTABLE'));
 test('zero paid orders rejects',()=>assert.equal(reconcile({...ready,confirmed_paid_orders:0}).status,'NOT COMPUTABLE'));
 test('fake unknown fees rejects',()=>assert.equal(reconcile({...ready,fees_usd:null}).status,'NOT COMPUTABLE'));
 test('invalid cohort rejects',()=>assert.equal(reconcile({...ready,cohort_days:8}).status,'NOT COMPUTABLE'));
 test('negative refund rejects',()=>assert.equal(reconcile({...ready,refunds_usd:-20}).status,'NOT COMPUTABLE'));
 test('infinite payout rejects',()=>assert.equal(reconcile({...ready,settled_payout_usd:Infinity}).status,'NOT COMPUTABLE'));
 test('negative net allowed when verified',()=>assert.equal(reconcile({...ready,refunds_usd:200}).realized_net_usd,-105));
 test('email PII rejects',()=>assert.throws(()=>reconcile({...ready,email:'a@b.com'}),/Privacy/));
 test('IP PII rejects',()=>assert.throws(()=>reconcile({...ready,ip:'127.0.0.1'}),/Privacy/));
 test('tracking token PII rejects',()=>assert.throws(()=>reconcile({...ready,transaction_id:'abc'}),/Privacy/));
 test('click only is not settlement',()=>assert.equal(reconcile({affiliate_clicks:10}).status,'NOT COMPUTABLE'));
 console.log('PASS '+n+'/'+n+' deterministic synthetic accounting and privacy tests. NO real merchant evidence.');
}
if(require.main===module)runSyntheticTests();
module.exports={reconcile,runSyntheticTests};
