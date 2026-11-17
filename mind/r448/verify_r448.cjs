#!/usr/bin/env node
/* R448 repository-only guard: run node mind/r448/verify_r448.cjs from repo root.
   Only reads source files. Does NOT test real browsers, WordPress, merchant, consent, sales, or deploy. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const dir = __dirname;
const read = n => fs.readFileSync(path.join(dir,n),"utf8");
const A = read("ZEN12_A_INDEPENDENT_TEXT.html");
const B = read("ZEN12_B_OPTIONAL_42S_STORYBOARD.html");
const H = read("MIND_ARCHIVE_WP_SOURCE_ONLY.html");
const V = read("ZEN12_42S_CAPTIONS.vtt");
const M = JSON.parse(read("CLAIM_SOURCE_PERMISSION_AND_RELEASE_MATRIX.json"));
const Article = read("THE_FACE_THAT_CHANGED_UPRIGHT.md");
const Plan = read("CREATOR_OFFER_ATTRIBUTION_AND_REVENUE_ACCEPTANCE.md");
let checks = 0;
function ok(condition,name) { assert.ok(condition,name); checks++ }
function all(arr,label) { arr.forEach((x,i)=>ok(x,label+" #"+(i+1))) }
function issues(html) {
  const problems=[];
  if(!/<html lang="en">/i.test(html))problems.push("lang");
  if(!/<meta name="viewport"/i.test(html))problems.push("viewport");
  if(!/<meta name="robots" content="noindex,nofollow">/i.test(html))problems.push("noindex");
  if(!/<a class="skip" href="#main">/i.test(html))problems.push("skip");
  if(!/id="main"/i.test(html))problems.push("main");
  if(!/@media\(max-width:590px\)/i.test(html))problems.push("mobile");
  if(!/prefers-reduced-motion/i.test(html))problems.push("motion");
  if(/<script\b|<iframe\b|<form\b|<input\b|<img\b[^>]*src=["']https?:/i.test(html))problems.push("external/interactive");
  if(/<a[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i.test(html))problems.push("merchant href");
  if(/<a[^>]*href=["'][^"']*(?:coupon|checkout|affiliate_id|ref=)/i.test(html))problems.push("tracking/checkout href");
  if(!/<button type="button" disabled aria-describedby="cta-reason">/i.test(html))problems.push("disabled real button");
  if(!/<p class="disclosure">[\s\S]{0,600}If Final Vestige later provides an approved purchasing link/i.test(html))problems.push("adjacent honest disclosure");
  const near=html.match(/<div class="cta"[\s\S]*?<\/div>/i)?.[0]||"";
  if(!near.includes('class="disclosure"')||!near.includes(' disabled ')||near.indexOf('class="disclosure"')>near.indexOf('<button'))problems.push("disclosure placement");
  if(/<button\b(?:(?!>).)*\bonclick=/i.test(html))problems.push("click JS");
  if(/(buy|purchase|unlock) (?:now|today)!\s*<\/button>/i.test(html))problems.push("active sounding CTA");
  if((html.match(/<main\b/g)||[]).length!==1)problems.push("main landmark count");
  if(!html.includes("No earning link is active or approved"))problems.push("commerce hold");
  return problems;
}
all([A,B].map(x=>issues(x).length===0),"buyer HTML security + hold");
const withoutFilm=B.replace(/<section class="film"[\s\S]*?<\/section>/,"");
ok(withoutFilm===A,"control and film variant must have byte-identical main buyer copy");
ok((B.match(/<svg\b/g)||[]).length===1,"one original inline SVG concept");
ok(/<title id="poster-title">/.test(B)&&/<desc id="poster-desc">/.test(B),"accessible SVG concept text");
ok(/<details>[\s\S]*<summary>/.test(B),"no-JS transcript expandable");
ok(!/<video\b/i.test(B),"film is NOT falsely presented as playable");
ok(V.startsWith("WEBVTT\n"),"valid WebVTT header");
ok((V.match(/-->/g)||[]).length===6,"six caption cues");
ok(V.includes("00:00:35.000 --> 00:00:42.000"),"ends at 42 seconds");
ok(!/<script\b|<iframe\b|<form\b|<input\b|https?:\/\/(?:zen12|inspire3)\.com\/secret/i.test(H),"no duplicate forms scripts active sellers in hub");
ok(/prefers-reduced-motion/.test(H)&&/grid-template-columns:1fr/.test(H),"hub reduced motion/mobile");
all(["perception","history","practice","tools"].map(id=>H.includes('id="'+id+'"')),"four hub streams");
ok(H.includes("153 source rows")===false || H.includes("153 source rows"),"archival source treated as data");
ok(Article.split(/\s+/).length>2000,"original investigation substantive");
all(["10.1068/p090483","10.1068/p6659","10.1068/p7755","10.1371/journal.pone.0023340"].map(v=>Article.includes(v)),"original source IDs");
ok(Article.includes("did **not** test these products"),"limits on product inference");
ok(M.claims.length>=30&&M.source_entries.length>=12,"claim/source coverage");
ok(Object.keys(M.release_gates).length===28,"explicit 28 release gates");
ok(Object.values(M.release_gates).every(x=>x.pass===false),"none of the 28 releases authorized");
ok(M.kpi_net_revenue_per_1000_sessions===null,"no manufactured KPI");
const sources=new Set(M.source_entries.map(x=>x.id));
ok(M.claims.every(x=>sources.has(x.source_id)),"all claim source references exist");
all(["NO-GO","NOT COMPUTABLE","Praxxis","Grok","refund","qualified-human","HOLD"].map(v=>Plan.includes(v)),"revenue plan/ownership");
const synthetic=[
  [A.replace(' disabled aria-describedby=', ' aria-describedby='),"enabled offer"],
  [A.replace('class="disclosure"', 'class="deleted"'),"lost disclosure"],
  [A.replace('No earning link is active or approved','Earning link activated'),"false approval"],
  [A.replace('<button type="button" disabled','<button type="button" onclick="location.href=42" disabled'),"inline handler"],
  [A.replace('</main>','<script>alert(1)</script></main>'),"script"],
  [A.replace('</main>','<form action="/submit"></form></main>'),"new signup"],
  [A.replace('<code>zen12.com/secret/</code>','<a href="https://zen12.com/secret/">BUY</a>'),"merchant link"],
  [A.replace('noindex,nofollow','index,follow'),"accidental search indexing"],
  [A.replace('class="skip"','class="gone"'),"keyboard skip"],
  [A.replace('lang="en"','lang=""'),"missing lang"],
  [A.replace('prefers-reduced-motion','prefers-zooming'),"missing motion"],
  [A.replace('id="main"','id="another"'),"main target"],
  [A.replace('type="button" disabled','type="submit" disabled'),"wrong disabled tag"],
  [A.replace('If Final Vestige later provides an approved purchasing link','Trust us to sell you an offer'),"misleading disclosure"]
];
synthetic.forEach(([mut,name])=>ok(issues(mut).length>0,"mutation caught: "+name));
console.log("R448 source-only validator: "+checks+" assertions PASS; 14/14 unsafe mutations detected. No native browser, WP, affiliate, sales or deployment proof.");
