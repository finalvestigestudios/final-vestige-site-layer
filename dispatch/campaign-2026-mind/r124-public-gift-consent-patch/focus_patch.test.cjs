"use strict";
const {test} = require("node:test");
const assert=require("node:assert/strict");
const p=require("./focus_patch.cjs");
function fixture(){
  const scripts='<script id="fvf-gift-v2">(function(){var g=document.getElementById(\'fvf-gift\');if(!g){return;}\nvar bad=[\'invalid_email\',\'error\',\'blocked_email\',\'opted_out\',\'blocked\'];\nfunction show(){g.hidden=false;}\nvar q=null;try{q=new URLSearchParams(window.location.search).get(\'subscribe\');}catch(e){}\nif(q){if(bad.indexOf(q)<0){show();}}\nvar c=document.querySelector(\'.wp-block-jetpack-subscriptions__container\');\nfunction check(){if(c){if(/\\\\bis-subscriber\\\\b/.test(c.className)){show();}}}\ncheck();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:[\'class\']});}}})();</script>';
  const locations=["after_why","after_routine","after_inside","after_limits","close"];
  const ctas=locations.map((k,i)=>'<a class="fvf-btn" href="#subscribe-blog" data-fv-event="focus_signup_click" data-fv-location="'+k+'">'+(i%2?"Send me the fieldbook":"Get the free fieldbook")+'</a>').join("\n");
  return '<main class="fv-focus">'+p.GIFT_OPEN+'<a href="'+p.PDF+'" data-fv-event="focus_pdf_click" data-fv-location="after_signup">Download the Seven Day Focus Fieldbook</a><p>'+p.GIFT_INFO+'</p></div><div class="wp-block-jetpack-subscriptions__container"></div><section>'+ctas+'</section><p>'+p.FAQ_OPEN+'</p><p>'+p.FAQ_MOBILE+'</p>'+scripts+'<p>'+'reader research '.repeat(1400)+'</p></main>';
}
test("source controls and available public PDF preserved",()=>{
  const old=fixture(), a=p.inspect(old), result=p.proposePatch(old), n=result.html;
  assert.equal(a.signup_ctas,5);assert.equal(a.gift_count,1);
  assert.equal(result.status,"DRAFT_ONLY_NOT_PUBLISHED");
  assert.ok(n.includes(p.GIFT_REPLACE));
  assert.equal(n.includes('id="fvf-gift-v2"'),false);
  assert.equal(n.includes("new URLSearchParams("),false);
  assert.equal(n.includes("is-subscriber"),false);
  assert.equal(n.includes(p.PDF),true);
  assert.equal(n.includes('data-fv-event="focus_pdf_click"'),true);
  assert.equal(n.includes('data-fv-location="public_pdf"'),true);
  assert.equal(n.includes('wp-block-jetpack-subscriptions__container'),true);
  assert.equal(n.match(/Join The Dispatch \(free\)/g).length,5);
  assert.ok(n.includes("Downloading it does not subscribe you"));
  assert.ok(n.includes("You do not need to enter your email address again"));
  assert.ok(result.proof.signup_clicks_not_confirmed_signups);
  assert.ok(result.proof.separate_final_founder_approval_required);
});
test("missing or changed source signatures reject patch",()=>{
  const s=fixture();
  for(const x of [p.GIFT_OPEN,p.GIFT_INFO,p.FAQ_OPEN,p.FAQ_MOBILE,'data-fv-location="after_signup"','focus_signup_click','wp-block-jetpack-subscriptions','id="fvf-gift-v2"']) {
    assert.throws(()=>p.proposePatch(s.replace(x,"BROKEN")),/HOLD_SOURCE_DRIFT/);
  }
});
test("additional surprise script and duplicate gift are closed",()=>{
 const s=fixture();
 assert.throws(()=>p.proposePatch(s+s.slice(s.indexOf('<script id="fvf-gift-v2">'),s.indexOf('</script>')+9)),/HOLD_SOURCE_DRIFT/);
 assert.throws(()=>p.proposePatch(s+p.GIFT_OPEN),/HOLD_SOURCE_DRIFT/);
});
test("short or invalid source rejected",()=>{
  for(const x of ["",null,{},42,"a".repeat(15999)])assert.throws(()=>p.proposePatch(x));
});
test("not a mail or purchase workflow",()=>{
 const n=p.proposePatch(fixture()).html;
 for(const bad of ["mailto:","affiliates.inspire3.com","zen12.com/hnp","<form action=","fake_confirmed_signup"])assert.equal(n.includes(bad),false);
 assert.ok(n.includes("data-fv-event=\"focus_signup_click\""));
 assert.ok(!/\b(function|const|let)\s+sendEmail\b/.test(n));
});
test("reapplying patch refuses silent edit of already revised source",()=>{
  assert.throws(()=>p.proposePatch(p.proposePatch(fixture()).html),/HOLD_SOURCE_DRIFT/);
});
test("no additional tracking or network resources",()=>{
  const old=fixture(), next=p.proposePatch(old).html;
  assert.equal((old.match(/https?:\/\//g)||[]).length,(next.match(/https?:\/\//g)||[]).length);
  assert.ok(!next.includes("fetch(")&&!next.includes("XMLHttpRequest"));
});
