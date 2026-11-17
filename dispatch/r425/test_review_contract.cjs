/* node unit checks on the review-only contract, never a send-capable implementation */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const g = require("./review_contract.cjs");
function witness(){return {status:"witnessed",owner:"QA Lead",checked_at:"2026-11-17T15:05:29Z",evidence_ref:"https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174"}}
function fullEvidence(){
  const d={controls:{automatic_new_post_emails:false,no_list_import_no_wordpress_write_no_send:true}};
  for(const k of [...g.COMMON,...g.MERCHANT,...Object.values(g.ISSUE_EXTRAS).flat()]){
    const a=k.split("."); d[a[0]] ||= {}; d[a[0]][a[1]]=witness();
  }
  return d;
}
test("six original issues four editorial and two reserved commercial",()=>{
 const r=g.evaluateCampaign({});
 assert.equal(r.slots.length,6); assert.equal(r.editorial,4); assert.equal(r.commercial,2);
 assert.equal(r.slots.filter(s=>s.kind==="commercial").length,2);
});
test("unverified input always holds",()=>{for(const s of g.evaluateCampaign({}).slots){assert.equal(s.state,"HOLD_UNSENT"); assert.equal(s.send_authorized,false); assert(s.blocked.length>2)}});
test("all-synthetic evidence cannot pass source mode",()=>{
 const r=g.evaluateCampaign(fullEvidence());assert(!r.all_ready_for_founder_review);
 assert(r.slots.every(s=>s.blocked.includes("not_authenticated_production_evidence")));
});
test("even all-attested production shaped data cannot authorize sending",()=>{
 const r=g.evaluateCampaign(fullEvidence(),{mode:"production_attestation"});
 assert(r.all_ready_for_founder_review);assert(!r.send_authorized);
 assert(r.slots.every(s=>!s.send_authorized && s.state==="HOLD_UNSENT"));
});
test("each global condition independently blocks editorial",()=>{
 for(const key of g.COMMON){const x=fullEvidence();const [a,b]=key.split(".");delete x[a][b];
 const r=g.evaluate(1,x,{mode:"production_attestation"});assert(r.blocked.includes(key),key);}
});
test("each merchant proof independently blocks slot 03 and 05",()=>{
 for(const key of g.MERCHANT){for(const n of [3,5]){const x=fullEvidence();const [a,b]=key.split(".");x[a][b]={status:"unknown"};
 assert(g.evaluate(n,x,{mode:"production_attestation"}).blocked.includes(key),key+"/"+n);}}
});
test("merchant proof does not block the four editorial slots",()=>{
 const x=fullEvidence(); delete x.merchant;
 for(const n of [1,2,4,6]) assert(g.evaluate(n,x,{mode:"production_attestation"}).can_request_founder_review);
});
test("Apollo wording correction is a mandatory independent gate",()=>{
 const x=fullEvidence();delete x.editorial.apollo1_timestamp_language_corrected;
 assert(g.evaluate(4,x,{mode:"production_attestation"}).blocked.includes("editorial.apollo1_timestamp_language_corrected"));
 assert(!g.evaluate(2,x,{mode:"production_attestation"}).blocked.includes("editorial.apollo1_timestamp_language_corrected"));
});
test("subscriber CTA repetition remains blocked on issue 06",()=>{
 const x=fullEvidence();delete x.editorial.existing_subscriber_cta_not_signup_repeat;
 assert(!g.evaluate(6,x,{mode:"production_attestation"}).can_request_founder_review);
});
test("invalid issue numbers are rejected",()=>{for(const x of [0,7,44,"banana",null])assert.equal(g.evaluate(x,{},{}).state,"INVALID")});
test("client-supplied email address poisons proof packet",()=>{
 const x=fullEvidence();x.person="private-person@example.com";
 assert(g.evaluate(3,x,{mode:"production_attestation"}).blocked.includes("recipient_email_or_PII_in_attestation"));
});
test("don't accept false confirmations",()=>{
 for(const bad of [null,false,true,"verified",{status:"verified"},{status:"witnessed"},
 {status:"witnessed",owner:"A",checked_at:"2026-11-17",evidence_ref:"https://evil.example.com/"},
 {status:"witnessed",owner:"A Team",checked_at:"tomorrow",evidence_ref:"https://github.com/example/test"}
 ])assert.equal(g.proof(bad),false);
});
test("no auto-send control cannot be turned on",()=>{
 const x=fullEvidence();x.controls.automatic_new_post_emails=true;
 assert(g.evaluate(1,x,{mode:"production_attestation"}).blocked.includes("automatic_post_send_not_proven_off"));
});
test("WordPress write/import veto cannot be turned off",()=>{
 const x=fullEvidence();x.controls.no_list_import_no_wordpress_write_no_send=false;
 assert(g.evaluate(1,x,{mode:"production_attestation"}).blocked.includes("non_sending_controls_not_proven"));
});
test("issue 03 is merchant-blocked while 04 stays editorial",()=>{
 const x=fullEvidence();delete x.merchant;
 assert(!g.evaluate(3,x,{mode:"production_attestation"}).can_request_founder_review);
 assert(g.evaluate(4,x,{mode:"production_attestation"}).can_request_founder_review);
});
test("proofs cannot be an empty URL or omitted reviewer",()=>{
 assert(!g.proof({...witness(),evidence_ref:""}));
 assert(!g.proof({...witness(),owner:""}));
});
