"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { classifyFocusClient } = require("./focus_client_truth.cjs");
const u = (query, classes) => classifyFocusClient(query, classes);
test("baseline is a freely available resource without claiming a signup", () => {
  const x = u(); assert.equal(x.state, "public_free_resource"); assert.equal(x.show_free_download, true);
  assert.equal(x.confirmed_signup, false); assert.equal(x.emit_confirmed_signup, false);
});
for (const x of ["unconfirmed", "pending", "success", "subscribed", "confirmed", "true", "1", "arbitrary"]) {
  test("untrusted client success-like status cannot confirm: " + x, () => {
    const a = u("?subscribe="+x); assert.equal(a.state,"await_provider_confirmation");
    assert.equal(a.confirmed_signup,false);assert.equal(a.emit_confirmed_signup,false);
    assert.match(a.copy,/If you requested/);
  });
}
for (const x of ["invalid_email","error","failed","blocked_email","opted_out","blocked","ERROR"," Failed "]) {
  test("problem status remains unconfirmed: " + x, () => {
    const a = u("?subscribe="+encodeURIComponent(x)); assert.equal(a.state,"subscription_not_verified");
    assert.equal(a.show_free_download,true);assert.equal(a.emit_confirmed_signup,false);
  });
}
test("multiple contradictory states fail neutral",()=>assert.equal(u("?subscribe=success&subscribe=failed").state,"ambiguous_client_signal"));
test("empty query does not imply a signup",()=>assert.equal(u("?subscribe=").state,"public_free_resource"));
test("is-subscriber CSS class cannot imply inbox eligibility",()=>{
  const a=u("", "wp-block is-subscriber active"); assert.equal(a.state,"reader_ui_signal_only"); assert.equal(a.confirmed_signup,false);
});
test("lookalike CSS class cannot imply inbox eligibility",()=>assert.equal(u("", "is-not-subscriber").state,"public_free_resource"));
test("query problems trump class styling",()=>assert.equal(u("?subscribe=failed","is-subscriber").state,"subscription_not_verified"));
test("no tracking, network calls, or email exposed in patch",()=>{
  const src=fs.readFileSync(require.resolve("./focus_client_truth.cjs"),"utf8");
  assert.doesNotMatch(src,/fetch\s*\(|XMLHttpRequest|sendBeacon|document\.cookie|localStorage|mailto:|\.email\s*=|analytics\s*\(/i);
});
test("all states have accessible non-sensational status copy",()=>{
  for(const q of ["","?subscribe=failed","?subscribe=success","?subscribe=unknown","?subscribe=success&subscribe=failed"]){
    const a=u(q); assert.ok(a.copy.length>60); assert.doesNotMatch(a.copy,/confirmed subscriber|successfully subscribed|guaranteed/i);
  }
});
test("result is frozen to prevent mutation by caller",()=>assert.equal(Object.isFrozen(u()),true));
