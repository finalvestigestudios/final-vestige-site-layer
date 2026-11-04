"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const {BAD,EVIDENCE,auditSource,classifyUi,classifyNativeConfirmation,classifyCounters}=require("./focus_state_gate.cjs");
const page="<section>".padEnd(1200,"x")+Object.values(EVIDENCE).join("\n");
test("actual source signature: broad query branch and mobile instruction",()=>{
 const s=auditSource(page);
 assert.equal(s.unknown_query_reveals_gift,true);
 assert.equal(s.duplicate_signup_advice_present,true);
 assert.equal(s.confirmation_help_conflicts_with_reveal,true);
 assert.equal(s.release,"HOLD_UNSENT");
});
test("source drift is detected, not interpreted as a clean pass",()=>{
 const s=auditSource(page.replace(EVIDENCE.broadReveal,"REMOVED_BY_OTHER_AGENT"));
 assert.equal(s.original_source_changed_or_incomplete,true);
 assert.equal(s.unknown_query_reveals_gift,false);
});
test("short or missing source rejected",()=>{
 assert.throws(()=>auditSource("short"),TypeError);
 assert.throws(()=>auditSource(undefined),TypeError);
});
for(const q of ["foo","thanks","success","confirmed","0"]) {
 test("arbitrary query " + q + " reveals gift but not consent",()=>{
  const s=classifyUi({subscribeParam:q});
  assert.equal(s.gift_visible_in_source_logic,true);
  assert.equal(s.reason,"NON_BLOCKLIST_QUERY");
  assert.equal(s.confirmed_signup,false);
  assert.equal(s.client_confirmed_signup_permitted,false);
 });
}
for(const q of BAD.concat([""])) {
 test("blocked or empty query " + (q||"(empty)") + " no reveal",()=>{
  assert.equal(classifyUi({subscribeParam:q}).gift_visible_in_source_logic,false);
 });
}
test("CSS class shows panel, not a new confirmed signup",()=>{
 const s=classifyUi({containerClass:"widget is-subscriber"});
 assert.equal(s.gift_visible_in_source_logic,true);
 assert.equal(s.confirmed_signup,false);
});
test("actual WordPress CSS word boundary also matches not-is-subscriber (not a consent proof)",()=>{
 const s=classifyUi({containerClass:"not-is-subscriber"});
 assert.equal(s.gift_visible_in_source_logic,true);
 assert.equal(s.confirmed_signup,false);
});
test("non-matching CSS remains no gift reveal",()=>{
 assert.equal(classifyUi({containerClass:"unrelated-block"}).gift_visible_in_source_logic,false);
});
test("blocking query + subscriber class still cannot prove confirmation",()=>{
 const s=classifyUi({subscribeParam:"error",containerClass:"is-subscriber"});
 assert.equal(s.gift_visible_in_source_logic,true);
 assert.equal(s.confirmed_signup,false);
});
test("malformed UI state rejected",()=>{
 assert.throws(()=>classifyUi(null),TypeError);
 assert.equal(classifyUi({subscribeParam:["confirmed"]}).confirmed_signup,false);
});
test("only synthetic authoritative proof may enter dedup review",()=>{
 const r=classifyNativeConfirmation({
  source:"AUTHENTICATED_WORDPRESS_CONFIRMATION",confirmed:true,consent:true,
  optedOut:false,nativeEventId:"native_test_2026",opaqueId:"a".repeat(64),
  occurredAt:"2026-11-04T22:00:00Z"});
 assert.equal(r,"SYNTHETICALLY_ELIGIBLE_FOR_NATIVE_DEDUP_REVIEW_ONLY");
});
for(const field of ["source","confirmed","consent","optedOut","opaqueId","nativeEventId","occurredAt"]) {
 test("proof mutation "+field+" fails closed",()=>{
  const a={source:"AUTHENTICATED_WORDPRESS_CONFIRMATION",confirmed:true,consent:true,
   optedOut:false,nativeEventId:"native_test_2026",opaqueId:"a".repeat(64),occurredAt:"2026-11-04T22:00:00Z"};
  a[field]=field==="occurredAt"?"2026-11-04 22:00":null;
  assert.equal(classifyNativeConfirmation(a),"NOT_VERIFIED");
 });
}
test("email address in proof rejected as PII",()=>{
 const a={source:"AUTHENTICATED_WORDPRESS_CONFIRMATION",confirmed:true,consent:true,
  optedOut:false,nativeEventId:"native_test_2026",opaqueId:"a".repeat(64),occurredAt:"2026-11-04T22:00:00Z",
  email:"redacted@example.invalid"};
 assert.equal(classifyNativeConfirmation(a),"REJECT_PII_OR_UNKNOWN_FIELDS");
});
test("WordPress 3/3/2 counters remain nonadditive",()=>{
 const s=classifyCounters({total:3,confirmed:3,unconfirmed:2,imported_last_24h:1});
 assert.equal(s.confirmed_plus_pending_is_total,false);
 assert.equal(s.is_new_confirmed_signup_proof,false);
 assert.equal(s.actual_reachable,null);
 assert.equal(s.paid_orders,null);
});
test("invalid aggregate counters rejected",()=>{
 assert.throws(()=>classifyCounters({total:3,confirmed:-1,unconfirmed:2}),TypeError);
 assert.throws(()=>classifyCounters({total:3,confirmed:"3",unconfirmed:2}),TypeError);
});
