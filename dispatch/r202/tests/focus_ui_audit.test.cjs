"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const a=require("../focus_ui_audit.cjs");
const src='<div class="wp-block-jetpack-subscriptions"><a href="/">Send me the fieldbook</a></div>'+
'<div id="fvf-gift" hidden>Your fieldbook is ready</div>'+
"<script>var bad=['invalid_email','error','blocked_email','opted_out','blocked'];"+
"var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}"+
"if(q){if(bad.indexOf(q)<0){show();}}"+
"if(/\\bis-subscriber\\b/.test(c.className)){show();}"+
"new MutationObserver(check).observe(c,{attributes:true});</script>";
test("source signals and REST fallback accurately flagged",()=>{
 const o=a.auditFocusMarkup(src);
 assert.equal(o.queryEvidence,true);assert.equal(o.classEvidence,true);
 assert.equal(o.gift,true);assert.equal(o.formFallback,true);
 assert.equal(o.providerConfirmed,false);
 assert.equal(o.actualEmailEligibility,"UNKNOWN");
});
test("no claim that WP runtime subscribe form is broken",()=>{
 assert.match(a.auditFocusMarkup(src).caveat,/not live-browser/);
});
test("no markup query gate => no false detection",()=>{
 const o=a.auditFocusMarkup('<div id="fvf-gift" hidden></div>');
 assert.equal(o.queryEvidence,false);assert.equal(o.classEvidence,false);
});
test("null and empty URL do not show the observed gift",()=>{
 assert.equal(a.reproduceObservedGiftLogic(null),false);
 assert.equal(a.reproduceObservedGiftLogic(""),false);
});
for(const bad of a.BLOCKED) test("negative state "+bad,()=>{
 assert.equal(a.reproduceObservedGiftLogic(bad),false);
});
for(const candidate of ["anything","pending","subscribed","confirmed","true","1"])
 test("query alone shows current gift, not confirmed consent: "+candidate,()=>{
  assert.equal(a.reproduceObservedGiftLogic(candidate),true);
  assert.equal(a.classifyEvidence({query:candidate}).confirmed_signup,false);
 });
test("CSS-only shows gift but cannot prove confirmed consent",()=>{
 assert.equal(a.reproduceObservedGiftLogic(null,true),true);
 assert.equal(a.classifyEvidence({css:"is-subscriber"}).confirmed_signup,false);
});
const proof={provider:"jetpack",filter:"Email subscription = Subscribed",
 consent_basis:"provider_observed_double_opt_in",previous_status:"pending",
 current_status:"subscribed",evidence_access:"restricted_provider_record",
 duplicate:false,suppressed:false,private_proof_ref:"internal:private-check-20261107"};
test("private provider transition meets staged predicate but no auto analytics",()=>{
 const o=a.classifyEvidence(proof);
 assert.equal(o.confirmed_signup,true);assert.equal(o.may_emit_public_analytics,false);
});
for(const [key,value] of Object.entries({
 previous_status:"subscribed",current_status:"pending",provider:"browser",
 filter:"WordPress Reader",consent_basis:"assumed",evidence_access:"public_github",
 duplicate:true,suppressed:true,private_proof_ref:"github:public"
})) test("reject provider mutation "+key,()=>{
 assert.equal(a.classifyEvidence({...proof,[key]:value}).confirmed_signup,false);
});
test("reject account-less proof",()=>{
 assert.equal(a.classifyEvidence({...proof,private_proof_ref:undefined}).confirmed_signup,false);
});
test("safe pre-confirm copy does not assert enrollment",()=>{
 assert.match(a.proposedCopy("unconfirmed"),/confirm your subscription/);
 assert.match(a.proposedCopy("unknown"),/does not by itself subscribe/);
});
