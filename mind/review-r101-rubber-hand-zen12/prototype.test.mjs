/* R101 static policy tests. Execute: node --test mind/review-r101-rubber-hand-zen12/*.test.mjs */
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const read = name=>readFileSync(new URL("./"+name, import.meta.url),"utf8");
const A=read("pilot-A-text-only.blocks.html");
const B=read("pilot-B-film-concept.blocks.html");
const hub=read("mind-hub-preview.blocks.html");
const vtt=read("film-40s.vtt");
const claims=JSON.parse(read("claims-and-sources.json"));

test("all release gates fail closed and tracking is null",()=>{
 assert.ok(claims.release_gates.length>=30);
 assert.ok(claims.release_gates.every(g=>g.state==="HOLD_CLOSED"));
 assert.equal(claims.affiliate_url,null);
 assert.equal(claims.active_tracking,false);
});
test("exact same substantive guide in text and film variants",()=>{
 const removeFilm=B.replace(/<section class="fv101-film"[\s\S]*?<\/section>/,"");
 assert.equal(A.replace('data-fv-variant="A"','data-fv-variant="B"'),removeFilm);
});
test("zero merchant activation, capture, embeds, or scripts",()=>{
 for(const s of [A,B]){
  assert.doesNotMatch(s,/<script\b|<form\b|<iframe\b|<video\b|\bautoplay\b\s*=|\bfetch\(|navigator\./i);
  assert.doesNotMatch(s,/href=["']https?:\/\/(?:www\.)?(?:affiliates\.inspire3\.com|clickbank\.net|hop\.clickbank\.net)/i);
  assert.match(s,/button type="button" disabled/);
  assert.match(s,/If you purchase through this link, Final Vestige may earn a commission at no additional cost to you/);
  assert.match(s,/No affiliate link is active in this draft/);
  assert.match(s,/https:\/\/finalvestige.com\/focus\//);
 }
});
test("required no-JS and disclosure proximity checks",()=>{
 for(const s of [A,B]){
   const d=s.indexOf("If you purchase through this link");const c=s.indexOf("<button type=\"button\" disabled");
   assert.ok(d>=0&&c>d&&c-d<400,"commission disclosure next to disabled CTA");
   assert.match(s,/aria-describedby="fv101-reason"/);
   assert.match(s,/:focus-visible/);
   assert.match(s,/prefers-reduced-motion/);
   assert.match(s,/@media\(max-width:840px\)/);
 }
});
test("optional film is a truthful unhosted storyboard with transcript",()=>{
 assert.doesNotMatch(A,/fv101-film-h/);
 assert.match(B,/film is not hosted or playable yet/);
 assert.match(B,/<details class="fv101-transcript" open>/);
 assert.match(B,/<summary>/);
 assert.doesNotMatch(B,/<video\b/);
 assert.match(B,/Original, six-scene visual storyboard/);
});
test("VTT cues continuous, exact 40 seconds, six stages",()=>{
 const matches=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
 assert.equal(matches.length,6);
 const ms=(a,b,c,d)=>Number(a)*3600000+Number(b)*60000+Number(c)*1000+Number(d);
 let cursor=0;
 for(const m of matches){const start=ms(m[1],m[2],m[3],m[4]),end=ms(m[5],m[6],m[7],m[8]);assert.equal(start,cursor);assert.ok(end>start);cursor=end;}
 assert.equal(cursor,40000);
});
test("source register documents true opposing rubber-hand literature",()=>{
 const ids=new Set(claims.source_records.map(s=>s.id));
 for(const k of ["R02","R03","R05","R06","R07","R01","C01","C02","S02","S03","S04"])assert.ok(ids.has(k));
 for(const k of ["Z07","Z09","Z21","Z26","R11"])assert.match(claims.decisions.find(d=>d.id===k).decision,/^(REJECT|BLOCK)/);
});
test("archive remains a noncanonical four-stream proposal",()=>{
 for(const section of ["PERCEPTION","HISTORY OF SUGGESTION","PRACTICE","TOOLS UNDER REVIEW"]) assert.ok(hub.includes(section));
 assert.match(hub,/NONCANONICAL/);
 assert.doesNotMatch(hub,/<form\b|<script\b/);
});
