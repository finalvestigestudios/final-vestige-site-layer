// Mind R444 native Node regression gate; not itself evidence of native execution.
// Run at repo root: node --test mind/r444/qa.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {dirname,join} from "node:path";
import {fileURLToPath} from "node:url";
const dir=dirname(fileURLToPath(import.meta.url));
const read=(f)=>readFileSync(join(dir,f),"utf8");
const A=read("ZEN12_A_TEXT_ONLY.html");
const B=read("ZEN12_B_OPTIONAL_42S_CONCEPT.html");
const H=read("MIND_HUB_WP_SOURCE_ONLY.html");
const M=JSON.parse(read("CLAIM_SOURCE_PERMISSION_MATRIX.json"));
const V=read("R444_42S_CAPTIONS.vtt");
const article=read("THE_PARAGRAPH_THAT_WENT_MISSING.md");
const guideCore=(s)=>s.slice(s.indexOf('<section id="decision">'),s.indexOf('<p><small>Variant '));
test("no live merchant links, JS, forms, pixels or tracking in A/B/hub",()=>{
 for(const doc of [A,B,H]){
  assert.match(doc,/<!doctype html>/i);
  assert.match(doc,/<html lang="en">/i);
  assert.match(doc,/<meta name="viewport"/i);
  assert.match(doc,/<meta name="robots" content="noindex,nofollow">/i);
  assert.doesNotMatch(doc,/<script\b|<iframe\b|<form\b|<video\b|onerror\s*=|onclick\s*=|javascript:/i);
  assert.doesNotMatch(doc,/<a[^>]+href=["']https?:\/\/(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i);
  assert.doesNotMatch(doc,/dataLayer\s*=|gtag\(|fbq\(|localStorage|sessionStorage|document\.cookie/i);
  assert.match(doc,/<button type="button" disabled>/);
  assert.match(doc,/@media\(prefers-reduced-motion:reduce\)/);
 }
});
test("A and B have exactly identical substantive guide and hard-hold",()=>{
 assert.ok(guideCore(A).length>2500);
 assert.equal(guideCore(A),guideCore(B));
 for(const doc of [A,B]){
 assert.match(doc,/Prospective affiliate disclosure:/);
 assert.match(doc,/No earning link is active/i);
 assert.match(doc,/If you buy through a future approved earning link/);
 assert.match(doc,/Purchase option unavailable pending approval/);
 assert.match(doc,/five questions/i);
 }
});
test("optional film is appropriately static, accessible, complete",()=>{
 assert.match(B,/<svg[^>]+role="img"/);
 assert.match(B,/<title id="poster-title">/);
 assert.match(B,/<desc id="poster-description">/);
 assert.match(B,/<details>/);
 assert.match(B,/not an encoded or playable film/i);
 assert.match(V,/^WEBVTT/);
 assert.equal((V.match(/ --> /g)||[]).length,6);
 assert.match(V,/00:00:35\.000 --> 00:00:42\.000/);
});
test("hub respects original four streams / one focus funnel",()=>{
 for(const id of ["perception","suggestion","reflection","review"])assert.match(H,new RegExp('id="'+id+'"'));
 assert.match(H,/finalvestige\.com\/focus\//);
 assert.match(H,/puysegurs-animal-magnetism-files/);
});
test("claims hold account permission and revenue uncertainty",()=>{
 assert.equal(M.claim_count,31);
 assert.equal(M.claims.length,31);
 assert.equal(M.release_gates.length,28);
 assert.ok(M.release_gates.every(g=>g.decision==="HOLD"));
 assert.ok(Object.values(M.affiliate_activation).every(x=>x===false));
 for(const id of ["C07","C08","C12","C17","C18","C19","C20","C21","C22","C23","C29","C30","C31"])assert.ok(M.claims.some(c=>c.id===id&&/NOT |UNVERIFIED|FALSE|UNTESTED/.test(c.status)),id);
 assert.equal(M.verified_revenue_per_1000,"NOT_COMPUTABLE");
});
test("original editorial cites research and refuses named SKU efficacy inference",()=>{
 for(const kw of ["self-caught","probe-caught","meta-awareness","Puységur","Mrazek","Zen12"])assert.ok(article.includes(kw),kw);
 assert.match(article,/not a trial of Zen12/i);
 assert.doesNotMatch(article,/I used Zen12|we tested Zen12|guaranteed cure/i);
});
