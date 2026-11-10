"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {evaluateProbe,evaluateMatrix,canonicalUrl}=require("./browser_evidence_gate.cjs");
function good(page="focus",viewport_width=390){
 return {record_source:"UNAUTHENTICATED_PLAYWRIGHT_BROWSER",url:"https://finalvestige.com/"+page+"/",
 viewport_width,observed_at_utc:"2026-11-10T06:40:00.000Z",unauthenticated_context:true,
 blocked_non_get_requests:true,user_data_typed:false,form_submitted:false,received_email_sent:false,
 visible_email_inputs:1,accessible_visible_email_inputs:1,visible_submit_controls:1,
 safe_openers_clicked:0,self_navigation_count:0,browser_errors:0,keyboard_reached_subscribe:true};
}
test("canonical URLs limited to two exact site pages",()=>{
 assert.equal(canonicalUrl("https://finalvestige.com/focus"),"https://finalvestige.com/focus/");
 for(const bad of ["https://evil.example/focus/","http://finalvestige.com/focus/","https://finalvestige.com/focus/?token=x","javascript:alert(1)",null])
  assert.equal(canonicalUrl(bad),null);
});
test("valid browser observation remains visual-only",()=>{
 const x=evaluateProbe(good()); assert.equal(x.classification,"VISUAL_ENTRY_PRESENT_UNSUBMITTED");
 assert.equal(x.visual_entry_pass,true);assert.equal(x.subscription_verified,false);assert.equal(x.release_authorized,false);
});
for(const [name,modify] of [
 ["external destination",o=>o.url="https://elsewhere.com/focus/"],
 ["unapproved viewport",o=>o.viewport_width=800],
 ["logged in",o=>o.unauthenticated_context=false],
 ["no HTTP method guard",o=>o.blocked_non_get_requests=false],
 ["typed email",o=>o.user_data_typed=true],
 ["form submitted",o=>o.form_submitted=true],
 ["email sent",o=>o.received_email_sent=true],
 ["fake browser source",o=>o.record_source="API_ONLY"],
 ["no date",o=>o.observed_at_utc=""],
 ["bad count",o=>o.visible_email_inputs=-2],
])test("invalid evidence rejected: "+name,()=>{let o=good();modify(o);let x=evaluateProbe(o);
 assert.equal(x.classification,"INVALID_PROOF");assert.equal(x.release_authorized,false);});
test("visible email with missing accessible name is not pass",()=>{
 const o=good();o.accessible_visible_email_inputs=0;
 assert.equal(evaluateProbe(o).classification,"VISIBLE_FIELD_INCOMPLETE_ACCESSIBILITY");
});
test("self-navigation without input is flagged, not declared broken",()=>{
 const o=good();o.visible_email_inputs=0;o.accessible_visible_email_inputs=0;o.visible_submit_controls=0;o.safe_openers_clicked=1;o.self_navigation_count=1;
 assert.equal(evaluateProbe(o).classification,"SELF_NAVIGATION_WITHOUT_VISIBLE_FIELD");
});
test("missing input without opener is an unknown frontend state",()=>{
 const o=good();o.visible_email_inputs=0;o.accessible_visible_email_inputs=0;o.visible_submit_controls=0;
 assert.equal(evaluateProbe(o).classification,"NO_VISIBLE_INPUT_FOUND");
});
test("browser exception blocks aggregate pass",()=>{
 let o=good();o.browser_errors=1;
 assert.equal(evaluateProbe(o).js_errors_reported,true);
});
test("keyboard unreachable blocks aggregate visual pass",()=>{
 let o=good();o.keyboard_reached_subscribe=false;assert.equal(evaluateProbe(o).visual_entry_pass,false);
});
test("empty/malformed observations never ready",()=>{
 assert.equal(evaluateMatrix(null).status,"INVALID");assert.equal(evaluateMatrix([]).status,"NEEDS_REVIEW");
});
test("complete four-slot matrix passes VISUAL ONLY without claiming paid results",()=>{
 const a=[good("focus",390),good("focus",1440),good("dispatch",390),good("dispatch",1440)];
 const x=evaluateMatrix(a);assert.equal(x.status,"VISUAL_ONLY_COMPLETE");
 assert.equal(x.release_authorized,false);assert.equal(x.confirmed_signup,null);assert.equal(x.net_revenue_per_1000,null);
});
test("missing viewport blocks completion",()=>{
 const a=[good("focus",390),good("dispatch",390)];
 const x=evaluateMatrix(a);assert.equal(x.status,"NEEDS_REVIEW");assert.equal(x.missing.length,2);
});
test("duplicate slot blocks completion",()=>{
 const a=[good("focus",390),good("focus",390),good("dispatch",390),good("dispatch",1440)];
 assert.equal(evaluateMatrix(a).status,"NEEDS_REVIEW");
});
test("one JS error blocks completion",()=>{
 const a=[good("focus",390),good("focus",1440),good("dispatch",390),good("dispatch",1440)];a[3].browser_errors=1;
 assert.equal(evaluateMatrix(a).status,"NEEDS_REVIEW");
});
