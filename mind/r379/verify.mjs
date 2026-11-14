#!/usr/bin/env node
// Node 18+ stdlib only. Source-only assertions do NOT certify browser accessibility or commercial authorization.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
const dir=path.dirname(new URL(import.meta.url).pathname);
const read=(name)=>fs.readFileSync(path.join(dir,name),"utf8");
const a=read("ZEN12_A_EVIDENCE_GUIDE.html");
const b=read("ZEN12_B_OPTIONAL_42S_GUIDE.html");
const hub=read("MIND_HUB_WORDPRESS_REVIEW_ONLY.html");
const svg=read("ORIGINAL_AV_POSTER.svg");
const vtt=read("ORIGINAL_42S_CAPTIONS.vtt");
const article=read("THE_WORD_THAT_CHANGED_WHEN_THE_MOUTH_MOVED.md");
const dossier=read("CONVERSION_FIRST_ACCEPTANCE.md");
const matrix=JSON.parse(read("CLAIM_SOURCE_AUTHORIZATION_MATRIX.json"));
let count=0;
const check=(cond,why)=>{assert.ok(cond,why);count++};
for(const [label,html] of [["A",a],["B",b],["hub",hub]]){
 check(/<html lang="en">/.test(html),label+" language");
 check(/name="robots" content="noindex,nofollow,noarchive"/.test(html),label+" noindex");
 check(!/<script\b|<iframe\b|<form\b|<video\b[^>]*autoplay\b|<audio\b[^>]*autoplay\b/i.test(html),label+" no script, iframe, form or autoplay");
 check(!/https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com\/?(?:[^\s"'<>]*)?["']/.test(html),label+" no direct active seller links");
 check(!/<a[^>]+href=["'][^"']*(?:click\.html|\/checkout|affiliat|ref=|partner=)/i.test(html),label+" no affiliate redirect");
 check(/prefers-reduced-motion/.test(html),label+" reduced motion");
}
for(const [label,html] of [["A",a],["B",b]]){
 check(/<button[^>]*\bdisabled\b/.test(html),label+" native disabled");
 check(/may earn a commission/.test(html),label+" adjacent FTC text");
 check(html.indexOf("may earn a commission")<html.indexOf("Merchant checkout withheld"),label+" disclosure before button");
 check(/https:\/\/finalvestige.com\/focus\//.test(html),label+" existing free path");
 check(/not independently established for the product/i.test(html),label+" seller claim boundary");
 check(/12 levels/.test(html)&&/48 MP3/.test(html),label+" verified seller-described format");
}
const panel=/<figure class="film"[\s\S]*?<\/figure>/;
check(!panel.test(a)&&panel.test(b),"single B-only film panel");
check(b.replace(panel,"")===a,"A/B strict parity after B film panel");
check(b.includes("ORIGINAL_AV_POSTER.svg"),"B poster reference");
check(b.includes("ORIGINAL_42S_CAPTIONS.vtt"),"B caption file reference");
check(b.includes("not encoded or hosted"),"B video honest status");
check(svg.includes("<title")&&svg.includes("<desc"),"original poster alt");
check(vtt.startsWith("WEBVTT"),"captions format");
check((vtt.match(/-->/g)||[]).length===6,"six captions");
check(vtt.includes("00:00:42.000"),"42 second duration");
check(article.trim().split(/\s+/).length>=1800,"substantial investigation");
check(article.includes("10.1038/264746a0")&&article.includes("10.1371/journal.pone.0207160"),"primary research");
check(article.includes("puysegurs-animal-magnetism-files/"),"source archive link");
check(!/this product cured|we used zen12|guaranteed wealth/i.test(article+a+b),"no invented endorsement");
check(hub.includes("Perception &amp; Attention")&&hub.includes("History of Suggestion")&&hub.includes("Practice &amp; Reflection")&&hub.includes("Tools Under Review"),"four-stream hub");
check(matrix.claims.length>=30,"claim audit breadth");
check(matrix.release_gates.length>=30,"gating breadth");
check(matrix.release_gates.every(g=>g.status==="HOLD"),"all commercial gates withheld");
check(matrix.actual_commercial_evidence.net_revenue_per_1000_qualified_humans==="NOT_COMPUTABLE","no fake net revenue");
check(dossier.includes("NOT COMPUTABLE")&&dossier.includes("asset_id=UNKNOWN"),"attribution transparency");
check(dossier.includes("Seven- and thirty-day")||dossier.includes("Seven- and thirty-day"),"cohorts");
check(!/href=["']https:\/\/zen12\.com/i.test(a+b+hub),"no seller CTA");
check(!/<input\b/i.test(a+b+hub),"no new input");
console.log("PASS "+count+" structural/source/commerce checks; external WCAG/browser/checkout/permission not tested");
