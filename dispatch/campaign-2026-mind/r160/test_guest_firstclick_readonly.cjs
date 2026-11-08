"use strict";
/* R160 offline read-only browser policy checks (no live navigation). */
const assert=require("node:assert/strict");
const {test}=require("node:test");
const fs=require("node:fs");
const path=require("node:path");
const text=fs.readFileSync(path.join(__dirname,"guest_firstclick_readonly.cjs"),"utf8");
const {isSafeCandidate,redactOnly}=require("./guest_firstclick_readonly.cjs");
const dispatch={label:"dispatch",id:523,url:"https://finalvestige.com/dispatch/"};
const focus={label:"focus",id:1579,url:"https://finalvestige.com/focus/"};
test("only known no-submit WordPress self anchors may be clicked",()=>{
  assert.equal(isSafeCandidate("https://finalvestige.com/?post_type=page&p=523",dispatch),true);
  assert.equal(isSafeCandidate("https://finalvestige.com/?p=1579&post_type=page",focus),true);
  for(const href of ["https://evil.example/?post_type=page&p=523",
    "https://finalvestige.com/wp-admin/", "https://finalvestige.com/?post_type=page&p=1579",
    "https://finalvestige.com/?post_type=page&p=523&email=someone",
    "https://finalvestige.com/?post_type=page&p=523#confirmation",
    "/?post_type=post&p=523","/?post_type=page&p=523&send=true"]){
      assert.equal(isSafeCandidate(href,dispatch),false,href);
    }
});
test("screenshot and dashboard output excludes subscribers and raw DOM",()=>{
  const x=redactOnly({page:"focus",viewport:390,url_before:"https://finalvestige.com/focus/",
    url_after:"https://finalvestige.com/focus/",inputs_before:0,inputs_after:0,
    visible_inputs_before:0,visible_inputs_after:0,subscribe_links:1,
    safe_link_clicked:false,blocked_non_get:0,console_error_count:0,
    status:"NO_VISIBLE_EMAIL_INPUT_BROWSER_REVIEW_REQUIRED",screen_file:"focus-390.png",
    subscriber_email:"private@hidden.example",cookie:"secret",outerHTML:"<script>secret</script>"});
  assert.equal(x.subscriber_email,undefined);assert.equal(x.cookie,undefined);assert.equal(x.outerHTML,undefined);
});
test("non-GET network requests MUST be actively aborted",()=>{
  assert.ok(text.includes('route.request().method().toUpperCase()!=="GET"'));
  assert.ok(text.includes('route.abort("blockedbyclient")'));
});
test("no form submission, typing, stored cookies, client-side injection or send helpers",()=>{
  for(const banned of [".fill(", "page.keyboard.type(", "locator.type(", ".press(", ".submit(", "fetch(", "axios", "postData", "localStorage.setItem", "send_email", "newsletter_subscribers_add"]){
    assert.ok(!text.includes(banned),banned);
  }
  assert.ok(text.includes("storageState:{cookies:[],origins:[]}"));
});
test("probe is opt-in to execution, no automatic network on import",()=>{
  assert.ok(text.includes('process.argv.includes("--run")'));
  assert.ok(text.includes("if(require.main===module)main()"));
});
test("output is explicitly non-conversion and privacy preserving",()=>{
  for(const fragment of ["confirmed_signups:null","merchant_orders:null","delivered_welcomes:null",
    "email_submissions:0","NO_VISIBLE_EMAIL_INPUT_BROWSER_REVIEW_REQUIRED",
    "UNKNOWN_NON_GET_NETWORK_BLOCKED_DURING_READONLY_TEST"]){
      assert.ok(text.includes(fragment),fragment);
    }
});
test("captures both known published pages at four responsive widths",()=>{
  for(const fragment of ['id:523,url:"https://finalvestige.com/dispatch/"',
    'id:1579,url:"https://finalvestige.com/focus/"', "const viewports=[320,390,768,1440]"]){
    assert.ok(text.includes(fragment));
  }
});
