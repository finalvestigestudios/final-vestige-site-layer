#!/usr/bin/env node
// Run: node mind/r349/verify_r349.cjs from repository root. No network, CMS writes, or paid calls.
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const root = __dirname;
const read = n => fs.readFileSync(path.join(root,n),"utf8");
const a = read("ZEN12_A_TEXT_GUIDE.html");
const b = read("ZEN12_B_OPTIONAL_FILM.html");
const hub = read("MIND_HUB_WORDPRESS_SOURCE_REVIEW.html");
const vtt = read("OPTIONAL_42S_CAPTIONS.vtt");
const svg = read("OPTIONAL_42S_POSTER.svg");
const research = read("THE_LOAD_THAT_LET_THE_UNEXPECTED_THROUGH.md");
const rev = read("CONVERSION_REVENUE_ACCEPTANCE.md");
const matrix = JSON.parse(read("CLAIM_SOURCE_AUTHORIZATION_MATRIX.json"));
let checks=0;const ok=(cond,msg)=>{assert.ok(cond,msg);checks++};

function checkOffer(html){
 ok(/<button\b[^>]*\bdisabled\b[^>]*\baria-disabled="true"/i.test(html),"purchase button disabled");
 ok(!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(html),"no clickable merchant link");
 ok(!/<script\b|<form\b|<iframe\b|<video\b/i.test(html),"no script/form/iframe/video");
 ok(!/on(?:click|load|error|submit)\s*=|javascript:|<meta[^>]*http-equiv=["']refresh/i.test(html),"no inline handlers or redirects");
 ok(/Affiliate disclosure:[\s\S]{0,700}<button[^>]*disabled/i.test(html),"earning disclosure near disabled CTA");
 ok(/https:\/\/finalvestige\.com\/focus\//.test(html),"existing Focus path preserved");
 ok(/<html lang="en">/.test(html)&&/name="viewport"/.test(html),"language and viewport");
 ok(/prefers-reduced-motion/.test(html)&&/focus-visible/.test(html),"keyboard/reduced-motion styles");
 ok(/<th scope="col">/.test(html)&&/<th scope="row">/.test(html),"semantic table");
 ok(/one-year|one year/i.test(html)&&/not independently verified final checkout totals/i.test(html),"price/refund caveats");
 ok(/Zen12's own newsletter/.test(html)&&/Final Vestige/.test(html),"distinct consent");
 ok(/not a first-person listening review/i.test(html),"no fabricated trial");
}
checkOffer(a);checkOffer(b);
const extractCore = s=>s.match(/<article id="buyer-guide">([\s\S]*?)<\/article>/)?.[1];
ok(extractCore(a)===extractCore(b),"identical substantive A/B buyer copy");
ok(/<details>/.test(b)&&/<summary>/.test(b)&&/42-second transcript/.test(b),"optional readable film transcript");
ok(!/<details>/.test(a),"A truly text-only");
ok(/loading="lazy"/.test(b)&&/OPTIONAL_42S_POSTER\.svg/.test(b),"B lazy original poster");
ok(vtt.startsWith("WEBVTT")&&vtt.includes("00:00:42.000"),"42-second caption concept");
ok((vtt.match(/--> /g)||[]).length===6,"six caption segments");
ok(svg.includes("<title")&&svg.includes("<desc")&&svg.includes("viewBox"),"accessible original SVG");
ok(/Mind|Perception/i.test(hub)&&/Perception &amp; Attention/.test(hub)&&/History of Suggestion/.test(hub)&&/Practice &amp; Reflection/.test(hub)&&/Tools Under Review/.test(hub),"four streams");
ok(!/<form\b|<script\b/i.test(hub),"hub no forms/scripts");
ok(!/href=["']https?:\/\/(?:www\.)?zen12\./.test(hub),"hub no active merchant");
ok(/pubmed\.ncbi\.nlm\.nih\.gov\/21937032/.test(research),"primary study linked");
ok(research.trim().split(/\s+/).length >= 1500,"substantive original research");
ok(matrix.sources.length>=12&&matrix.claims.length>=24,"source/claim records");
ok(matrix.sources.every(s=>/^https:\/\//.test(s.url)&&s.id),"grounded source URLs");
const idSet = new Set(matrix.sources.map(s=>s.id));
ok(matrix.claims.every(c=>c.source_ids.every(id=>idSet.has(id))),"claim refs valid");
ok(matrix.gates.length>=25&&matrix.gates.every(g=>g.status==="HOLD"),"all release gates closed");
ok(matrix.affiliate_status==="NOT VERIFIED","authorization unverified");
ok(/NOT COMPUTABLE/.test(rev)&&/qualified_human_sessions/.test(rev),"revenue spec refuses invented denominator");
ok(/asset_id \*\*NULL\*\*/.test(rev),"no invented Grok IDs");

function verifyAdversarial(){
 const unsafe=[
   a.replace("disabled aria-disabled", 'aria-disabled'),
   a.replace("If you purchase through an authorized affiliate link in the future, Final Vestige may earn a commission at no additional cost to you.","No commissions are earned."),
   a.replace("https://finalvestige.com/focus/","https://zen12.com/buy-now"),
   a.replace("<article id=\"buyer-guide\">","<script>alert(1)</script><article id=\"buyer-guide\">"),
   b.replace("loading=\"lazy\"","loading=\"eager\""),
   b.replace("42-second transcript","short video"),
 ];
 ok(!/<button\b[^>]*\bdisabled\b[^>]*\baria-disabled="true"/.test(unsafe[0]),"reject enabled CTA");
 ok(!/Affiliate disclosure:[\s\S]{0,700}<button[^>]*disabled/i.test(unsafe[1]),"reject removed disclosure");
 ok(/href="https:\/\/zen12\.com/.test(unsafe[2]),"reject active merchant URL");
 ok(/<script\b/.test(unsafe[3]),"reject inline script");
 ok(!/loading="lazy"/.test(unsafe[4]),"reject eager poster");
 ok(!/42-second transcript/.test(unsafe[5]),"reject omitted video transcript");
}
verifyAdversarial();
console.log("PASS",checks,"isolated source/structure assertions; no browser, WordPress or merchant transaction QA");
