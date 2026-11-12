"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { inspect } = require("./preflight.cjs");
const fixture = require("./release-evidence.json");
function sample() { return JSON.parse(JSON.stringify(fixture)); }
test("master source fidelity and 4:2 split", () => {
  let x=inspect(sample()); assert.equal(x.six_original_preserved,true);
  assert.equal(x.split,"4:2"); assert.deepEqual(x.blocked_editions,[1,2,3,4,5,6]);
  assert.deepEqual(x.commercial_hold,[3,5]);
});
test("fully held, sender and consent evidence NOT substituted", () => {
  const x=inspect(sample()); assert.equal(x.authorized_to_send,false);
  assert.equal(x.realized_net_revenue_per_1000_qualified_sessions,null);
  assert.equal(x.native_preview_proved,false);
  assert.equal(x.received_email_proved,false);
});
test("correctly flags three copy conversion flaws", () => {
  assert.deepEqual(inspect(sample()).editorialWarnings,
    ["01_02_same_destination","04_unverified_time_claim","06_existing_subscriber_reoptin"]);
});
test("two missing commercial guide destinations", () => {
  assert.deepEqual(inspect(sample()).pendingGuides,[3,5]);
});
test("all truthy authorization booleans cannot turn on sending", () => {
  let e=sample(); for(const k of Object.keys(e.approval)) e.approval[k]=true;
  e.site_snapshot.email_eligible_count=5; e.preheader_contract.wordpress_inbox_preview_text_control="VERIFIED_BY_RECEIVED_EMAIL";
  assert.equal(inspect(e).authorized_to_send,false);
});
test("unconfirmed totals cannot become eligible recipients", () => {
  const x=inspect(sample()); assert.ok(x.blocker.includes("eligible_recipient_count_unknown"));
});
test("zero recipients still blocks",()=> {
  let e=sample();e.site_snapshot.email_eligible_count=0;
  assert.ok(inspect(e).blocker.includes("no_verified_recipients"));
});
test("default sending unexpectedly on is a blocker",()=> {
  let e=sample(); e.site_snapshot.default_email_new_posts=true;
  assert.ok(inspect(e).blocker.includes("default_sending_not_disabled"));
});
test("no preheader mapping is never passed",()=>{
  assert.ok(inspect(sample()).blocker.includes("native_inbox_preheader_unverified"));
});
for(const n of [0,1,2,3,4,5]) {
  test("no edition can lose required HOLD: "+(n+1),()=> {
    let e=sample();e.issues[n].hold="READY";assert.throws(()=>inspect(e),/fidelity/);
  });
}
for(const n of [2,4]) {
  test("no merchant edition can lose merchant HOLD: "+(n+1),()=> {
    let e=sample();e.issues[n].commercial_hold=null;assert.throws(()=>inspect(e),/merchant hold/);
  });
}
for(const n of [0,1,2,3,4,5]) {
  test("no unverified inbox preheader can be claimed: "+(n+1),()=> {
    let e=sample();e.issues[n].inbox_preheader_verified=true;assert.throws(()=>inspect(e),/preheader/);
  });
}
test("prevents wrong edition role",()=> {
  let e=sample();e.issues[2].kind="editorial";assert.throws(()=>inspect(e));
});
test("rejects fabricated seventh edition",()=> {
  let e=sample();e.issues.push({...e.issues[0],number:7});assert.throws(()=>inspect(e));
});
test("rejects duplicate issue identity",()=> {
  let e=sample();e.issues[1].number=1;assert.throws(()=>inspect(e));
});
test("rejects identity outside 1-6",()=> {
  let e=sample();e.issues[4].number=0;assert.throws(()=>inspect(e));
});
test("rejects unknown evidence scope",()=> {
  let e=sample();e.record_type="READY_TO_SEND";assert.throws(()=>inspect(e));
});
test("never outputs recipient PII",()=> {
  let output=JSON.stringify(inspect(sample()));
  assert.ok(!/@/.test(output));assert.ok(!/customer_email|subscriber_email/.test(output));
});
