// R352 pure functions; no integrations and no tracking. Run: node mind/r352/revenue_contract.test.cjs
'use strict';const assert=require('node:assert/strict');
function netPerThousand(x){
  const required=['qualifiedHumanSessions','settledGross','processorFees','refundedAmount','confirmedMerchantOrders','sourceVerified','periodDays'];
  if(!x||required.some(k=>!Object.hasOwn(x,k)))return null;
  if(x.sourceVerified!==true||![7,30].includes(x.periodDays))return null;
  if(Object.keys(x).some(k=>/email|ip_address|phone|customer_name|device_fingerprint|token|password/i.test(k)))return null;
  for(const k of ['qualifiedHumanSessions','settledGross','processorFees','refundedAmount','confirmedMerchantOrders'])
    if(typeof x[k]!=='number'||!Number.isFinite(x[k])||x[k]<0)return null;
  if(!Number.isInteger(x.qualifiedHumanSessions)||!Number.isInteger(x.confirmedMerchantOrders))return null;
  if(x.qualifiedHumanSessions===0||x.processorFees+x.refundedAmount>x.settledGross)return null;
  if(x.confirmedMerchantOrders===0&&x.settledGross!==0)return null;
  return Math.round((x.settledGross-x.processorFees-x.refundedAmount)*1000/x.qualifiedHumanSessions*100)/100;
}
if(require.main===module){
const valid={qualifiedHumanSessions:1000,settledGross:100,processorFees:5,refundedAmount:10,confirmedMerchantOrders:2,sourceVerified:true,periodDays:7};
const cases=[
[valid,85],[{...valid,qualifiedHumanSessions:500},170],[{...valid,periodDays:30},85],
[{...valid,sourceVerified:false},null],[{...valid,qualifiedHumanSessions:0},null],
[{...valid,processorFees:undefined},null],[{...valid,processorFees:120},null],
[{...valid,confirmedMerchantOrders:0},null],[{...valid,email:'customer@example.com'},null],
[{...valid,affiliate_click:100,settledGross:0,processorFees:0,refundedAmount:0,confirmedMerchantOrders:0},0],
[{...valid,periodDays:1},null],[{...valid,qualifiedHumanSessions:1.5},null],
];
cases.forEach(([input,expected],i)=>assert.equal(netPerThousand(input),expected,'case '+i));
console.log('R352 settlement/privacy fixtures passed:',cases.length);
}
module.exports={netPerThousand};