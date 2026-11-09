"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {audit}=require("../../tools/experience-2/audit_live_optin_context.cjs");
function mock(){
 const jet='<!-- wp:jetpack/subscriptions {"submitButtonText":"Subscribe"} /-->';
 const link='https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf';
 const margins=Array.from({length:72},(_,i)=>'<span class="fv-margin-strip__item">'+i+'</span>').join("");
 const edit={
  home:{id:6,status:"publish",content:margins+'<a href="/focus/">Focus</a>'+jet},
  focus:{id:1579,status:"publish",content:'<p>The Dispatch</p><a href="/privacy-policy/">Privacy</a><a href="'+link+'">Download</a>'+jet},
  dispatch:{id:523,status:"publish",content:'<a href="/focus/">Focus</a>'+jet}
 };
 const view=id=>({id,status:"publish",content:'<div class="wp-block-jetpack-subscriptions"><a href="https://finalvestige.com/?post_type=page&#038;p='+id+'">Subscribe</a></div>'});
 return {homeEdit:edit.home,homeView:view(6),focusEdit:edit.focus,focusView:view(1579),dispatchEdit:edit.dispatch,dispatchView:view(523)};
}
function mutate(p,fn){const c=JSON.parse(JSON.stringify(p));fn(c);return audit(c);}
test("source-verified baseline is blocked without guest browser",()=>{
 const r=audit(mock());assert.equal(r.decision,"HOLD");assert.equal(r.checks.length,15);
 assert.equal(r.checks.filter(x=>x.pass).length,15);assert.deepEqual(r.restFallbackObserved,[6,1579,523]);
 assert.ok(r.blocked.includes("HOSTED_BROWSER_FORM_NOT_VERIFIED"));assert.equal(r.productionWrites,0);
});
test("synthetic guest receipt does not establish independent browser certification",()=>{
 const p=mock();p.hostedAnonymousBrowser={claimed:true};assert.ok(audit(p).blocked.includes("INDEPENDENT_BROWSER_RECEIPT_REVIEW_REQUIRED"));
});
const checks=[
 ["missing native Jetpack block",x=>x.homeEdit.content=x.homeEdit.content.replace("wp:jetpack/subscriptions","wp:html"),"home:editor_native_jetpack"],
 ["two native blocks",x=>x.focusEdit.content+="<!-- wp:jetpack/subscriptions /-->","focus:editor_native_jetpack"],
 ["draft page",x=>x.dispatchEdit.status="draft","dispatch:identity"],
 ["wrong page ID",x=>x.homeView.id=99,"home:identity"],
 ["missing Margin record",x=>x.homeEdit.content=x.homeEdit.content.replace('class="fv-margin-strip__item"','class="lost-record"'),"home:72_margins"],
 ["missing home Focus link",x=>x.homeEdit.content=x.homeEdit.content.replace('href="/focus/"','href="/broken/"'),"home:focus_entry"],
 ["missing Dispatch bridge",x=>x.dispatchEdit.content=x.dispatchEdit.content.replace('href="/focus/"','href="/broken/"'),"dispatch:focus_entry"],
 ["missing PDF link",x=>x.focusEdit.content=x.focusEdit.content.replace("Fieldbook_Complete_Edition.pdf","missing.pdf"),"focus:pdf_link"],
 ["missing privacy context",x=>x.focusEdit.content=x.focusEdit.content.replace("privacy-policy","missing"),"focus:consent"],
 ["REST self link changed",x=>x.homeView.content=x.homeView.content.replace("post_type=page","post_type=other"),"home:rest_fallback_documented"],
 ["REST rendered form rather than link",x=>x.focusView.content='<form><input type="email"></form>',"focus:rest_fallback_documented"],
 ["missing public rendered block",x=>x.dispatchView.content="", "dispatch:rest_fallback_documented"],
 ["gift fabricated by query",x=>x.focusEdit.content+='new URLSearchParams(window.location.search);if(q){if(bad.indexOf(q)<0){show();}}',"focus:no_query_based_gift_success"]
];
for(const [name,change,expected] of checks){test(name,()=>{const r=mutate(mock(),change);assert.ok(r.blocked.includes(expected),JSON.stringify(r.blocked));});}
