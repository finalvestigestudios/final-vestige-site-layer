"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const {probe,LIVE_SCRIPT}=require("./focus_gate_probe.cjs");
for(const v of ["yes","unconfirmed","pending","anything","12345","true"]){
  test("query "+v+" can reveal gift, but not a confirmed lead",()=>{
    const r=probe("?subscribe="+v);
    assert.equal(r.gift_visible,true); assert.equal(r.confirmed_signup,null);assert.equal(r.consent_verified,false);
  });
}
for(const v of ["invalid_email","error","blocked_email","opted_out","blocked"]){
  test("excluded error "+v,()=>assert.equal(probe("?subscribe="+v).gift_visible,false));
}
test("no query hidden",()=>assert.equal(probe("").gift_visible,false));
test("client CSS class does not establish actual consent",()=>{
  const r=probe("","is-subscriber");assert.equal(r.confirmed_signup,null);});
test("source snippet holds observed query gate",()=>{
  assert.match(LIVE_SCRIPT,/URLSearchParams/); assert.match(LIVE_SCRIPT,/bad.indexOf\(q\)<0/);
});
test("suite and probe are read only",()=>{
  const s=fs.readFileSync(__dirname+"/focus_gate_probe.cjs","utf8");
  assert.doesNotMatch(s,/fetch\(|XMLHttpRequest|\.submit\(|sendMail|wp\.api/);
});
test("no merchant URL, one approved editorial destination, and source",()=>{
  const m=fs.readFileSync(__dirname+"/01_OPTIONAL_CHANGE_BLINDNESS.md","utf8");
  assert.match(m,/only half/);assert.match(m,/10.3758\/BF03208840/);
  assert.match(m,/finalvestige.com\/2026\/11\/02\/change-blindness/);
  assert.doesNotMatch(m,/awin1.com|clickbank.net|affiliate\.inspire3/);
});
test("static reviewers never become approved send",()=>{
  for(const name of ["01_OPTIONAL_CHANGE_BLINDNESS.md","01_PLAINTEXT.txt","01_REVIEW_ONLY.html"]){
   const c=fs.readFileSync(__dirname+"/"+name,"utf8");
   assert.match(c,/UNSENT/);assert.match(c,/VALID_FV_POSTAL_ADDRESS_REQUIRED/);assert.match(c,/JETPACK_UNSUBSCRIBE_RENDER_AND_FUNCTION_REQUIRED/);
  }
});
test("fail-closed 4:2 merchant allocation",()=>{
 const l=JSON.parse(fs.readFileSync(__dirname+"/RELEASE_EVIDENCE.json","utf8"));
 assert.deepEqual(l.issue_mix,{editorial:4,commercial_drafts:2});
 assert.equal(l.actual_email_eligible,null);
 assert.equal(l.verified_net_revenue_per_1000,null);
 assert.equal(l.all_sends,"HOLD_UNSENT");
 assert.equal(l.affiliate_drafts,"HOLD_MERCHANT");
 assert.ok(Object.values(l.proofs).every(v=>v===false));
});
