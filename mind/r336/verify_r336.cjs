"use strict";
/** Run from repo root: node mind/r336/verify_r336.cjs
 * Read-only source checks. Does not prove browser/WP/payment readiness.
 */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const base=__dirname;
const read=n=>fs.readFileSync(path.join(base,n),"utf8");
const A=read("ZEN12_A_REVIEW.html"),B=read("ZEN12_B_FILM_REVIEW.html"),H=read("MIND_HUB_REVIEW.html"),M=JSON.parse(read("CLAIM_SOURCE_GATE_MATRIX.json")),D=read("CONVERSION_ACCEPTANCE.md"),S=read("ZEN12_POSTER.svg"),V=read("ZEN12_42S_CAPTIONS.vtt"),R=read("THE_BRAIN_SCAN_THAT_LEARNED_THE_PERSON.md");
let pass=0;
function check(c,msg){assert.ok(c,msg);pass++}
for(const [label,x] of [["A",A],["B",B],["hub",H]]){
  check(/<!doctype html>/i.test(x),label+" HTML5 doctype");
  check(/<html lang="en">/.test(x),label+" language");
  check(/name="viewport"/.test(x),label+" viewport");
  check(/name="robots" content="noindex,nofollow"/.test(x),label+" preview robots");
  check(!/<script\b|<form\b|<iframe\b|<track\b/i.test(x),label+" no scripts/forms/iframes");
  check(!/href="https?:\/\/(?:www\.)?(?:affiliates\.inspire3\.com|payhip\.com|clickbank\.)/i.test(x),label+" no active merchant earning links");
  check(/may earn a commission/i.test(x),label+" disclosure");
  check(/disabled/.test(x),label+" disabled commerce");
  check(/https:\/\/finalvestige\.com\/focus\//.test(x),label+" existing single Fieldbook path");
  check(/#main/.test(x),label+" skip navigation");
}
check(A.includes("12 levels, 48 MP3s"),"A tiers");check(B.includes("12 levels, 48 MP3s"),"B tiers");
check(A.includes("33-minute"),"A format accurate");check(B.includes("33-minute"),"B format accurate");
check(B.includes("NOT PLAYABLE")&&B.includes("<details>"),"B honest optional transcript");
check(!A.includes("Optional original micro-film"),"A excludes media");
check(B.replace(/<section class="panel" aria-labelledby="film-title">[\s\S]*?<\/section>/,"")===A.replace("<title>Zen12 Independent Text Guide — A","<title>Zen12 Optional Video Guide — B"),"A/B substantive parity");
check(V.startsWith("WEBVTT")&&V.includes("00:00:42.000"),"VTT duration");check(/<svg/.test(S),"original poster");
check(M.claims.length>=18,"claim matrix coverage");
check(M.sources.length>=15,"source ledger coverage");
check(Object.values(M.activation_gates).every(v=>v===false),"all gates remain closed");
check(!/https?:\/\/[^\s"'<>]*(?:ref=|hop=|aff_id=)/i.test(A+B),"no invented affiliate param");
check(R.includes("preprint")&&R.includes("subject-independent"),"science caveats");
check(D.includes("NOT COMPUTABLE")&&D.includes("affiliate_click"),"conversion definitions");
console.log("PASS "+pass+" read-only source checks; no browser/merchant/WP assertions");