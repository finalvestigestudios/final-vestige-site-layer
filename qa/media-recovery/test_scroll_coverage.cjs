'use strict';
/** Synthetic geometry only: never labels site images healthy or broken. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {STEP_PX,MAX_STEPS,MAX_HEIGHT_PX,nextScrollTarget,evaluateCoverage}=require('./scroll_coverage_core.cjs');
const at=(pageHeight,viewportHeight,scrollY,steps)=>({pageHeight,viewportHeight,scrollY,steps});
test('short document needs no scrolling and is complete',()=>{
 assert.equal(nextScrollTarget(at(500,844,0,0)),null);
 assert.equal(evaluateCoverage(at(500,844,0,0)).complete,true);
});
test('first meaningful scroll is 720 px, not a redundant scroll to top',()=>{
 assert.equal(nextScrollTarget(at(30000,844,0,0)),STEP_PX);
});
test('last scroll stops precisely at document bottom',()=>{
 assert.equal(nextScrollTarget(at(2000,844,720,1)),1156);
 assert.equal(evaluateCoverage(at(2000,844,1156,2)).complete,true);
});
test('30000-pixel article is not falsely complete after old 36-step limit',()=>{
 const v=evaluateCoverage(at(30000,844,25920,36));
 assert.equal(v.complete,false);assert.equal(v.state,'incomplete_scan');
 assert.equal(nextScrollTarget(at(30000,844,25920,36)),26640);
});
test('full 80000-pixel article fits inside 120 steps',()=>{
 let y=0,steps=0,target;
 while((target=nextScrollTarget(at(MAX_HEIGHT_PX,844,y,steps)))!==null){y=target;steps++}
 assert.equal(evaluateCoverage(at(MAX_HEIGHT_PX,844,y,steps)).complete,true);
 assert.ok(steps<=MAX_STEPS);assert.equal(y,MAX_HEIGHT_PX-844);
});
test('height growth while scrolling must be reevaluated from current height',()=>{
 assert.equal(evaluateCoverage(at(2000,844,1156,2)).complete,true);
 assert.equal(evaluateCoverage(at(3000,844,1156,2)).complete,false);
 assert.equal(nextScrollTarget(at(3000,844,1156,2)),1876);
});
test('pages above height cap never claim complete',()=>{
 assert.equal(nextScrollTarget(at(80001,844,0,0)),null);
 assert.equal(evaluateCoverage(at(80001,844,80000,10)).state,'height_cap');
});
test('step exhaustion cannot claim completion if bottom was not reached',()=>{
 const v=evaluateCoverage(at(50000,844,10000,MAX_STEPS));
 assert.equal(v.complete,false);assert.equal(v.reason,'step_budget_exhausted');
 assert.equal(nextScrollTarget(at(50000,844,10000,MAX_STEPS)),null);
});
test('scan exceptions always fail closed',()=>{
 const v=evaluateCoverage({...at(2000,844,1156,2),scanError:'CDP timeout'});
 assert.equal(v.complete,false);assert.equal(v.state,'scan_error');
});
test('nonsensical browser metrics fail closed',()=>{
 for(const row of [at(NaN,844,0,0),at(2000,0,0,0),at(2000,844,-1,0),at(2000,844,0,1.5)]){
  assert.equal(evaluateCoverage(row).complete,false);
  assert.equal(nextScrollTarget(row),null);
 }
});
test('a valid zero-image short document is eligible for scroll completion, not image pass',()=>{
 assert.equal(evaluateCoverage(at(700,844,0,0)).state,'full_height_scanned');
});
