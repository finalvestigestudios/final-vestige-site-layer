// Run: cd mind/r476 && node --test QA_REGRESSION.test.cjs
// Static-source scope ONLY; no browser/WordPress/merchant/Jetpack proof.
"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const read=f=>fs.readFileSync(path.join(__dirname,f),"utf8");
const A=read("ZEN12_A_TEXT_EVIDENCE_GUIDE.html"),B=read("ZEN12_B_OPTIONAL_FILM_EVIDENCE_GUIDE.html"),hub=read("MIND_ARCHIVE_SOURCE_ONLY.html"),article=read("THE_VOICE_YOU_HEARD_WITH_YOUR_EYES.md"),vtt=read("ZEN12_OPTIONAL_42S_CAPTIONS.vtt"),m=JSON.parse(read("CLAIM_PERMISSION_MERCHANT_MATRIX.json"));
for(const [i,h] of [A,B].entries()){
 test("variant "+i+" disabled merchant control",()=>assert.match(h,/<button[^>]*disabled[^>]*aria-disabled="true"/));
 test("variant "+i+" adjacent FTC disclosure",()=>{const d=h.indexOf('class="disclosure"'),b=h.indexOf("<button");assert(d>0&&b>d&&b-d<950);assert.match(h.slice(d,b),/may earn a commission/i)});
 test("variant "+i+" no affiliate URL",()=>assert.doesNotMatch(h,/<a[^>]+href=["'][^"']*(?:affiliate_id=|affid=|refersion)/i));
 test("variant "+i+" no form or tracker",()=>assert.doesNotMatch(h,/<form\b|<script\b|<iframe\b/i));
 test("variant "+i+" no forced video",()=>assert.doesNotMatch(h,/\bautoplay\b|<video\b[^>]+src=/i));
 test("variant "+i+" no price/coupon",()=>assert.doesNotMatch(h,/\$\s*\d|coupon\s+code|VZ54YTD6/i));
 test("variant "+i+" original sources",()=>{assert.match(h,/zen12\.com\/about/);assert.match(h,/10\.1371\/journal\.pone\.0286023/);});
 test("variant "+i+" accessible landmarks",()=>{assert.match(h,/<main>/);assert.match(h,/<h1>/);assert.match(h,/name="viewport"/);});
}
test("identical substance A and B",()=>{const body=x=>x.slice(x.indexOf('<p class="intro">'),x.indexOf("<footer>"));assert.equal(body(A),body(B));});
test("B adds optional poster/transcript and A does not",()=>{assert.match(B,/Read the complete 42-second transcript/);assert.match(B,/class="poster"/);assert.doesNotMatch(A,/Read the complete 42-second transcript/);});
test("six contiguous VTT cues exactly 42 sec",()=>{let xs=[...vtt.matchAll(/00:00:(\d{2})\.000 --> 00:00:(\d{2})\.000/g)].map(x=>[+x[1],+x[2]]);assert.deepEqual(xs,[[0,7],[7,14],[14,21],[21,28],[28,35],[35,42]]);});
test("hub preserves Focus, Dispatch and Puységur",()=>{assert.match(hub,/finalvestige\.com\/focus\//);assert.match(hub,/finalvestige\.com\/dispatch\//);assert.match(hub,/puysegurs-animal-magnetism-files/);assert.doesNotMatch(hub,/<form\b|<script\b/i);});
test("article includes primary experiment, counterexample, review, archive",()=>{for(const s of ["10.1038/264746a0","1960275","10.1371/journal.pone.0286023","puysegurs-animal-magnetism-files"])assert(article.includes(s));});
test("permission remains HARD HOLD",()=>{assert.equal(m.partner_verification.named_FV_approval,false);assert.equal(m.partner_verification.issued_authorized_affiliate_url,false);assert.equal(m.partner_verification.merchant_link,"WITHHELD");assert.equal(m.partner_verification.revenue_per_1000,"NOT_COMPUTABLE");});
test("claim matrix has substantiated omissions and source urls",()=>{assert(m.decisions.filter(d=>d.use.startsWith("OMIT")||d.use.startsWith("REJECT")).length>=5);assert(m.release_gates.length>=15);assert(Object.keys(m.sources).length>=10);});
test("no dynamic HTML injection attributes",()=>{for(const h of [A,B,hub])assert.doesNotMatch(h,/\bonclick\s*=|\bonerror\s*=|javascript:/i);});
test("six unsafe synthetic mutations detected",()=>{const mutated=[A.replace('disabled aria-disabled="true"','aria-disabled="false"'),A.replace('class="disclosure"','class="deleted"'),A+"<script>alert(1)</script>",A+"<form></form>",A+'<a href="https://example.invalid/?affiliate_id=bad">Buy</a>',A.replace('may earn a commission','no material relationship')];const bad=h=>!/<button[^>]*disabled[^>]*aria-disabled="true"/.test(h)||!h.includes('class="disclosure"')||/<script|<form|affiliate_id=/i.test(h)||!h.includes('may earn a commission');for(const s of mutated)assert(bad(s));});
