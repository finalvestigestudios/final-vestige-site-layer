"use strict";
/* Run offline: node mind/r354/verify_r354.cjs
   No network, no writes, no production credentials. Tests draft-source invariants only. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const get=x=>fs.readFileSync(path.join(__dirname,x),"utf8");
const a=get("ZEN12_A_GUIDE.html"),b=get("ZEN12_B_OPTIONAL_FILM.html"),h=get("MIND_HUB_WP_REVIEW.html");
const v=get("ORIGINAL_42S_CAPTIONS.vtt"),d=get("CONVERSION_ACCEPTANCE.md"),m=JSON.parse(get("CLAIM_SOURCE_MATRIX.json"));
let n=0;function test(ok,msg){assert.ok(ok,msg);n++}
for(const [id,html] of [["A",a],["B",b],["hub",h]]){
 test(html.includes('<html lang="en">'),id+" lang");
 test(html.includes('name="viewport"'),id+" viewport");
 test(html.includes('noindex,nofollow'),id+" noindex");
 test(html.includes("prefers-reduced-motion"),id+" motion");
 test(!/<script\b/i.test(html),id+" scripts");
 test(!/<form\b/i.test(html),id+" extra forms");
 test(!/<iframe\b/i.test(html),id+" iframes");
 test(!/<video\b/i.test(html),id+" no fake playable video");
}
for(const html of [a,b]){
 test(html.includes('disabled aria-disabled="true"'),"disabled purchase control");
 test(html.includes("Prospective affiliate disclosure:"),"disclosure wording");
 test(html.indexOf("Prospective affiliate disclosure:")<html.indexOf("Merchant offer unavailable"),"disclosure next to CTA");
 test(!/href=["'][^"']*(?:aff_id=|hop=|affiliate_id=|ref=)/i.test(html),"no affiliate earning URL");
 test(html.includes("https://finalvestige.com/focus/"),"existing free fieldbook only");
 test(html.includes("unsubstantiated seller claim"),"seller limitation");
}
const stripFilm=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,"");
test(stripFilm(a)===stripFilm(b),"A/B substantive HTML identical except film");
test(b.includes('<svg')&&b.includes('aria-label='),"original accessible static poster");
test(b.includes("Read the 42-second narration transcript"),"text transcript accessible");
test(!a.includes('class="film"'),"A text only");
test((v.match(/-->/g)||[]).length===6&&v.includes("00:00:42.000"),"six captions 42 seconds");
test(m.claims.length>=30,"claim coverage");
test(m.releaseGates.length>=30&&m.releaseGates.every(x=>x.status==="HOLD"),"all release gates hold");
test(m.claims.some(x=>x.classification==="affiliate_private"&&x.verification==="unverified"),"partner status unverified");
test(d.includes("NOT COMPUTABLE"),"net revenue no guess");
test(d.includes("no queue/task rewriting"),"creator custody");
test(h.includes("puysegurs-animal-magnetism-files"),"valid historical route");
test(h.includes("2026/11/02/change-blindness"),"live change blindness route");
console.log("R354 PASS "+n+" source-only checks. Real browser/WordPress/merchant NOT tested.");
