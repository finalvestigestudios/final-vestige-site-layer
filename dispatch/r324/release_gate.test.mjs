import test from "node:test";import assert from "node:assert/strict";
import {assess,REQUIRED} from "./release_gate.mjs";
test("all empty proofs fail closed",()=>{const r=assess();assert.equal(r.state,"HOLD_UNSENT");assert.equal(r.merchant,"HOLD_MERCHANT");assert.equal(r.maySend,false);assert.equal(r.missing.length,REQUIRED.length)});
for(const name of REQUIRED){
  test("false or absent "+name+" keeps HOLD",()=>{
    const all=Object.fromEntries(REQUIRED.map(x=>[x,true]));
    for(const v of [false,"true",1,null,undefined]){
      const r=assess({...all,[name]:v});assert.equal(r.state,"HOLD_UNSENT");assert.equal(r.maySend,false);assert.ok(r.missing.includes(name));
    }
  });
}
test("even all booleans true returns review only, never send",()=>{const e=Object.fromEntries(REQUIRED.map(x=>[x,true]));const r=assess(e);assert.equal(r.state,"FOUNDER_REVIEW_ONLY");assert.equal(r.maySend,false)});
for(const k of ["affiliateClickAsPaidSale","merchantOptInAsFVLead","pdfDownloadAsConfirmedSignup","browserParamAsConfirmedSignup"]){
  test("reject false conversion "+k,()=>{const all=Object.fromEntries(REQUIRED.map(x=>[x,true]));const r=assess({...all,[k]:true});assert.ok(r.missing.includes("INVALID_CONVERSION_CLASSIFICATION"));assert.equal(r.state,"HOLD_UNSENT");assert.equal(r.maySend,false)});
}
