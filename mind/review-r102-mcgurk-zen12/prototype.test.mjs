/* Native Node tests: node --test mind/review-r102-mcgurk-zen12/*.test.mjs
 * No network, CMS changes or browser telemetry.
 */
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {ACTIVATION,aggregateSynthetic,recordLiveEvent,trackPurchase} from "./synthetic-attribution.mjs";
const read=name=>readFileSync(new URL("./"+name,import.meta.url),"utf8");
const A=read("pilot-A-text.blocks.html"),B=read("pilot-B-optional-film.blocks.html");
const H=read("mind-hub-preview.blocks.html"),V=read("zen12-film-40s.vtt");
const L=JSON.parse(read("claims-sources-and-gates.json"));
const I=read("investigation.md"),G=read("zen12-independent-guide.md");
test("draft release strictly closed and no validated earning link",()=>{
 assert.equal(L.affiliate_url,null);assert.equal(L.active_tracking,false);
 assert.equal(L.release_gates.length,30);
 assert.ok(L.release_gates.every(g=>g.state==="HOLD_CLOSED"));
});
test("both buyer guides contain identical primary evidence text, B adds optional scene only",()=>{
 const section=B.match(/<section class="film"[\s\S]*?<\/section>/)?.[0];
 assert.ok(section,"film section in B");
 assert.equal(B.replace(section,"").replace('data-variant="B"','data-variant="A"'),A);
});
test("commercial CTA remains a native disabled button with adjacent disclosure",()=>{
 for(const s of [A,B]){
  assert.match(s,/<button type="button" disabled/);
  assert.match(s,/aria-describedby="fv102-disclosure fv102-disabled"/);
  assert.match(s,/If you purchase through this link, Final Vestige may earn a commission at no additional cost to you/);
  const at=s.indexOf('id="fv102-disclosure"'),button=s.indexOf('<button type="button" disabled');
  assert.ok(at>=0&&button>at&&button-at<600);
 }
});
test("no active marketing, external media, collection, autoplay, code or tracking",()=>{
 for(const s of [A,B,H]){
  assert.doesNotMatch(s,/<script\b|<form\b|<iframe\b|<video\b|autoplay\s*=|onload\s*=|onclick\s*=/i);
  assert.doesNotMatch(s,/href=["'][^"']*(?:clickbank\.net|hop\.clickbank|affiliates\.inspire3|[?&](?:aid|hop|affid)=)/i);
 }
 assert.equal(A.match(/<button /g)?.length,1);
 assert.doesNotMatch(H,/<button /);
});
test("film captions have six continuous positive intervals, exact 40 seconds",()=>{
 const m=[...V.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
 assert.equal(m.length,6);let prev=0;
 const ms=(a,b,c,d)=>((+a*60+ +b)*60+ +c)*1000+ +d;
 for(const x of m){const st=ms(...x.slice(1,5)),en=ms(...x.slice(5,9));assert.equal(st,prev);assert.ok(en>st);prev=en;}
 assert.equal(prev,40000);
 assert.match(B,/Full six-scene transcript/);
 assert.match(B,/film is not hosted or playable/);
});
test("WCAG-aware no-JS markup available, reduced motion and responsive CSS",()=>{
 for(const s of [A,B,H]){assert.match(s,/:focus-visible/);assert.match(s,/prefers-reduced-motion/);assert.match(s,/@media\(max-width:/);}
 assert.match(H,/NONCANONICAL/);
 for(const stream of ["PERCEPTION","HISTORY OF SUGGESTION","PRACTICE","TOOLS UNDER REVIEW"])assert.ok(H.includes(stream));
 assert.match(H,/https:\/\/finalvestige\.com\/focus\//);
});
test("science and history sources are specific and claim transfer blocked",()=>{
 for(const id of ["M01","M03","M04","M05","Z02","Z03","Z04","Z05","C01","C02","F01","F02"])
 assert.ok(L.sources.some(x=>x.id===id));
 for(const id of ["D04","D05","D06","D07","D21","D23","D24","D25","D28","D29"])
 assert.ok(L.decisions.some(x=>x.id===id&&/^(REJECT|BLOCK)/.test(x.decision)));
 assert.match(I,/McGurk/);assert.match(I,/Puységur/);
 assert.match(G,/12 levels and 48 MP3/);
});
test("synthetic counters fail closed and never infer sales",()=>{
 assert.equal(ACTIVATION.enabled,false);
 assert.throws(()=>recordLiveEvent());
 assert.throws(()=>trackPurchase());
 assert.throws(()=>aggregateSynthetic([{action:"guide_view",channel:"tiktok",count:21,topic:"zen12",email:"x@example.com"}]),/field/);
 assert.throws(()=>aggregateSynthetic([{action:"purchase",channel:"tiktok",count:21,topic:"zen12"}]),/category/);
 assert.throws(()=>aggregateSynthetic([{action:"guide_view",channel:"tiktok",count:21,topic:"zen12",url:"/secret"}]),/field/);
 const visible=aggregateSynthetic([{action:"guide_view",channel:"tiktok",count:21,topic:"zen12"},{action:"guide_view",channel:"direct",count:2,topic:"zen12"}]);
 assert.equal(visible.groups.length,1);assert.equal(visible.groups[0].synthetic_count,21);
});
