'use strict';
const assert=require('node:assert/strict');
const {computeVerifiedRevenue,INVALID}=require('./metrics.cjs');
const base=()=>({period_days:7,campaign:'grok_asset_verified_01',reconciliation_complete:true,
 qualified_sessions:{provider_attested:true,human_count:1000,campaign:'grok_asset_verified_01',period_days:7},
 confirmed_leads:{provider_attested:true,count:100},
 receipts:[{event_type:'paid_order_verified',receipt_kind:'owned_digital_order',provider_attested:true,
 settlement_status:'settled',transaction_key:'SYNTHETIC_01',campaign:'grok_asset_verified_01',period_days:7,
 gross_amount:20,refund_amount:0,fee_amount:2}]});
let count=0;function eq(a,b){assert.deepEqual(a,b);count++}
let x=computeVerifiedRevenue(base());
eq(x.status,'VERIFIED_INPUTS_ONLY');eq(x.confirmed_paid_receipts,1);eq(x.net_revenue,18);
eq(x.net_per_1000_qualified,18);eq(x.verified_paid_rate,.001);eq(x.lead_to_customer_rate,.01);
let y=base();y.qualified_sessions.human_count=0;eq(computeVerifiedRevenue(y).status,INVALID);
y=base();y.qualified_sessions.provider_attested=false;eq(computeVerifiedRevenue(y).status,INVALID);
y=base();y.reconciliation_complete=false;eq(computeVerifiedRevenue(y).status,INVALID);
y=base();y.receipts[0].provider_attested=false;eq(computeVerifiedRevenue(y).status,INVALID);
y=base();y.receipts[0].refund_amount=null;eq(computeVerifiedRevenue(y).status,INVALID);
y=base();y.receipts.push({...y.receipts[0]});eq(computeVerifiedRevenue(y).status,INVALID);
y=base();y.receipts[0].refund_amount=25;eq(computeVerifiedRevenue(y).net_revenue,-7);
y=base();y.receipts=[{event_type:'affiliate_click',campaign:y.campaign,period_days:7,clicks:200}];
eq(computeVerifiedRevenue(y).confirmed_paid_receipts,0);eq(computeVerifiedRevenue(y).net_revenue,0);
y=base();y.receipts[0].event_type='affiliate_commission_settled';y.receipts[0].receipt_kind='affiliate_commission';
eq(computeVerifiedRevenue(y).net_revenue,18);
y=base();y.confirmed_leads=null;eq(computeVerifiedRevenue(y).lead_to_customer_rate,null);
y=base();y.period_days=30;eq(computeVerifiedRevenue(y).status,INVALID);
console.log('PASS '+count+' synthetic tests; NO live metrics or order verification performed');
