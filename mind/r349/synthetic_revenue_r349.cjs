#!/usr/bin/env node
// Privacy-safe synthetic net-revenue test; all values deliberately invented for test only.
"use strict";
const assert=require("node:assert/strict");
function score({qualifiedHumanSessions,settlements}={}){
  if(!Number.isSafeInteger(qualifiedHumanSessions)||qualifiedHumanSessions<=0) return {status:"NOT COMPUTABLE",reason:"denominator missing"};
  if(!Array.isArray(settlements)||!settlements.length) return {status:"NOT COMPUTABLE",reason:"no settled purchases"};
  const allowed=["confirmed","gross","fees","refunds","cohort"];
  for(const r of settlements){
    if(Object.keys(r).some(k=>!allowed.includes(k)))return {status:"NOT COMPUTABLE",reason:"unapproved field/PII"};
    if(r.confirmed!==true || !["7d","30d"].includes(r.cohort))return {status:"NOT COMPUTABLE",reason:"unconfirmed settlement/cohort"};
    if([r.gross,r.fees,r.refunds].some(v=>!Number.isFinite(v)||v<0))return {status:"NOT COMPUTABLE",reason:"incomplete financial fields"};
    if(r.fees+r.refunds>r.gross)return {status:"NOT COMPUTABLE",reason:"inconsistent settlement"};
  }
  const gross=settlements.reduce((s,v)=>s+v.gross,0);
  const fees=settlements.reduce((s,v)=>s+v.fees,0);
  const refunds=settlements.reduce((s,v)=>s+v.refunds,0);
  return {status:"CALCULATED SYNTHETIC",gross,fees,refunds,net:gross-fees-refunds,per1000:1000*(gross-fees-refunds)/qualifiedHumanSessions};
}
let n=0;const eq=(v,w)=>{assert.deepEqual(v,w);n++};
eq(score().status,"NOT COMPUTABLE");
eq(score({qualifiedHumanSessions:0,settlements:[]}).status,"NOT COMPUTABLE");
eq(score({qualifiedHumanSessions:100,settlements:[]}).status,"NOT COMPUTABLE");
eq(score({qualifiedHumanSessions:100,settlements:[{confirmed:false,gross:40,fees:3,refunds:2,cohort:"7d"}]}).status,"NOT COMPUTABLE");
eq(score({qualifiedHumanSessions:100,settlements:[{confirmed:true,gross:40,fees:undefined,refunds:2,cohort:"7d"}]}).status,"NOT COMPUTABLE");
eq(score({qualifiedHumanSessions:100,settlements:[{confirmed:true,gross:40,fees:3,refunds:2,cohort:"7d",email:"private"}]}).status,"NOT COMPUTABLE");
eq(score({qualifiedHumanSessions:100,settlements:[{confirmed:true,gross:40,fees:3,refunds:2,cohort:"7d"}]}).net,35);
eq(score({qualifiedHumanSessions:100,settlements:[{confirmed:true,gross:40,fees:3,refunds:2,cohort:"7d"}]}).per1000,350);
eq(score({qualifiedHumanSessions:100,settlements:[{confirmed:true,gross:1,fees:2,refunds:0,cohort:"7d"}]}).status,"NOT COMPUTABLE");
console.log("PASS",n,"synthetic settlement checks; no real merchant evidence");
module.exports={score};
