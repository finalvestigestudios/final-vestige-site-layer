// R243 source-only regression. Execute from repository root: node mind/r243/test_r243.cjs
// Scope: local source invariants and historical R242 plan lock; not a browser, checkout, or efficacy test.
"use strict";
const fs=require("node:fs"),crypto=require("node:crypto"),assert=require("node:assert/strict");
const at=p=>fs.readFileSync(p,"utf8");
const prefix="mind/r243/";
function gitBlob(s){const b=Buffer.from(s,"utf8");return crypto.createHash("sha1").update(Buffer.from("blob "+b.length+"\\0","utf8")).update(b).digest("hex")}
function verify(data){
 const {html,article,plan,matrix,previous}=data;
 assert.equal(gitBlob(previous),"338a6dff709ef76c53b8d667bca79235ee4ff576","Inherited R242 acceptance contract must match exact pinned Git blob");
 for(const token of ["OFFER → FUNNEL STEP","NOT COMPUTABLE","HARD_HOLD","Three candidate creator-topic"]){assert.ok(previous.includes(token),"R242 contract missing "+token)}
 assert.equal(matrix.milestone,243);assert.equal(matrix.commercial.enabled,false);assert.equal(matrix.commercial.affiliate_url,null);
 assert.equal(matrix.gate_count,16);assert.equal(matrix.gates.length,16);
 assert.ok(matrix.gates.every(x=>x.status==="HARD_HOLD"));
 assert.ok(matrix.sources.length>=14&&matrix.claims.length>=27);
 assert.ok(matrix.claims.some(x=>x.claim.includes("isochronic")));
 assert.ok(matrix.claims.some(x=>x.claim.includes("one refund per six months")));
 assert.ok(matrix.claims.some(x=>x.claim.includes("five refunded")));
 assert.ok(matrix.claims.some(x=>x.claim.includes("PLOS ONE")));
 assert.ok(article.includes("PLOS ONE"));assert.ok(article.includes("one refund in any six-month period"));
 assert.ok(article.includes("Five")||article.includes("five"));
 assert.ok(article.includes("UNPUBLISHED"));assert.ok(plan.includes("NOT_COMPUTABLE"));
 const activeButton=html.match(/<button\\b[^>]*>/gi)||[];
 assert.equal(activeButton.length,1,"Exactly one source-preview commercial button");
 assert.ok(/\\sdisabled(?:\\s|>|=)/.test(activeButton[0]),"disabled attribute mandatory, aria-disabled alone inadequate");
 assert.ok(!/<a\\b[^>]*\\bhref\\s*=\\s*["']https?:\\/\\/(?:zen12|brainwaveshots|hypnosislive|inspire3|affiliates\\.inspire3)/i.test(html),"merchant link in active page");
 for(const bad of [/<script\\b/i,/<iframe\\b/i,/<form\\b/i,/\\son\\w+\\s*=/i,/<audio\\b/i,/<video\\b/i,/javascript\\s*:/i,/<div[^>]*\\/\\s*>/i])assert.ok(!bad.test(html),"Prohibited HTML injection/scheme");
 const p=html.indexOf("Prospective affiliate disclosure"),b=html.indexOf("<button");assert.ok(p>=0&&b>p&&b-p<1000,"disclosure must precede and be close to offer");
 assert.ok(html.includes("No commission link is active here."));
 assert.ok(html.includes('https://finalvestige.com/focus/'));
 assert.ok(html.includes("prefers-reduced-motion"));
 assert.ok(html.includes("noindex,nofollow"));
 assert.ok(!/\\$\\d+.*(?:checkout|buy now)/i.test(html),"no purchasable price CTA");
}
function readAll(){return{html:at(prefix+"zen12-canonical-decision-PREVIEW-UNPUBLISHED.html"),article:at(prefix+"THE-PROMISE-BENEATH-THE-PLAY-BUTTON-UNPUBLISHED.md"),plan:at(prefix+"CONVERSION-AND-QA-ACCEPTANCE.md"),matrix:JSON.parse(at(prefix+"CLAIM-PROOF-AND-AUTHORIZATION.json")),previous:at("mind/r242/OFFER-FUNNEL-BLOCKER-REVENUE-ACCEPTANCE.md")}}
const base=readAll();verify(base);
let negative=0;function reject(label,change){const v=readAll();change(v);assert.throws(()=>verify(v),undefined,label);negative++}
reject("unauthorized merchant",v=>v.html=v.html.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/hnp"'));
reject("enabled commerce",v=>v.html=v.html.replace('type="button" disabled','type="button"'));
reject("hidden disclosure",v=>v.html=v.html.replace("Prospective affiliate disclosure","Unspecified relationship"));
reject("extra signup",v=>v.html+='<form><input type="email"></form>');
reject("added pixel",v=>v.html+='<script src="https://tracker.example/pixel.js"></script>');
reject("javascript scheme",v=>v.html+='<a href="javascript:alert(1)">x</a>');
reject("false revenue",v=>v.matrix.commercial.net_revenue_per_1000="500");
reject("permission forgery",v=>v.matrix.gates[0].status="PASS");
reject("policy deletion",v=>v.matrix.claims=v.matrix.claims.filter(x=>!x.claim.includes("one refund per six months")));
reject("previous acceptance changed",v=>v.previous+="\\nCommercial activation allowed");
reject("no risk limit",v=>v.article=v.article.replace("one refund in any six-month period","unlimited refunds"));
reject("bad journal",v=>v.article=v.article.replace(/PLOS ONE/g,"Frontiers in Psychiatry"));
reject("bad contrast bypass",v=>v.html+='<div hidden/>');
console.log("PASS R243 baseline; "+negative+"/"+negative+" deliberately unsafe modifications rejected. Scope static source only. No browser, CI, merchant, payout or CMS test performed.");