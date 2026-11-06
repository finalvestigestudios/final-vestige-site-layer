"use strict";
const fs=require("node:fs"),assert=require("node:assert/strict"),path=require("node:path");
const dir=__dirname,ledger=JSON.parse(fs.readFileSync(path.join(dir,"r155-release-ledger.json"),"utf8"));
let total=0;
function check(name,fn){fn();total++;process.stdout.write("PASS "+name+"\n")}
for(const id of ["02","06"]){const md=fs.readFileSync(path.join(dir,id+"-OPTIONAL-UNSENT.md"),"utf8"),html=fs.readFileSync(path.join(dir,id+"-reviewer.html"),"utf8"),txt=fs.readFileSync(path.join(dir,id+"-reviewer.txt"),"utf8");
const e=ledger.sources.find(x=>x.issue===id);
check(id+" non-sending and no ad",()=>{assert.match(md,/UNSENT/);assert.doesNotMatch(md,/https:\/\/(?:www\.)?(?:zen12|hypnosislive)\.com/);assert.doesNotMatch(html,/<script|<img|<form/ig)});
check(id+" one primary CTA article destination",()=>{const url=e.cta;assert.ok(md.includes(url)&&html.includes(url)&&txt.includes(url));assert.ok((html.match(/display:inline-block;background:/g)||[]).length===1)});
check(id+" source links in both message variants",()=>{for(const url of e.links){assert.ok(md.includes(url),url);assert.ok(html.includes(url),url);assert.ok(txt.includes(url),url)}});
check(id+" compliance holds visible",()=>{for(const token of ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"]){assert.ok(md.includes(token)&&html.includes(token)&&txt.includes(token))}});
check(id+" accessible email-safe structure",()=>{assert.match(html,/<html lang="en">/);assert.match(html,/<h1/);assert.match(html,/table role="presentation"/);assert.match(html,/name="viewport"/);assert.doesNotMatch(html,/<style|position:absolute|background-image/);assert.match(html,/overflow-wrap:anywhere/)});
check(id+" copy accurate without medical or marketing inflation",()=>{assert.doesNotMatch(md,/guaranteed (results|cure)|impossible map|ancient antarctica proven|magnetism proven/i);assert.ok(md.length>1600)});
check(id+" subject and preheader both formats",()=>{const subs=/\*\*Subject:\*\* (.*)/.exec(md)[1],pre=/\*\*Preheader:\*\* (.*)/.exec(md)[1];assert.ok(subs.length<68&&pre.length<120);for(const x of [html,txt]){assert.ok(x.includes(subs));assert.ok(x.includes(pre))}});
}
check("preserve 4:2 and hard holds",()=>{const i=Object.values(ledger.issues);assert.equal(i.filter(x=>x.type==="editorial").length,4);assert.equal(i.filter(x=>x.type==="affiliate-reserved").length,2);assert.ok(Object.values(ledger.locks).every(x=>x===false))});
check("do not invent subscribers or revenue",()=>{assert.equal(ledger.email_eligible_audience,null);assert.equal(ledger.confirmed_signup_events,null);assert.equal(ledger.net_revenue_per_1000,null);assert.equal(ledger.qualified_human_sessions,null)});
check("no fake source CTA activations",()=>{assert.equal(ledger.issues["03"].cta_status,"HOLD_MERCHANT_UNPUBLISHED");assert.equal(ledger.issues["05"].cta_status,"HOLD_MERCHANT_UNPUBLISHED")});
console.log("R155 source-only tests: "+total+" PASS; no live email/browser/client tests.");
