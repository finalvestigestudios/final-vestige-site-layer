import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {ATTRIBUTION_ENABLED, sanitizeCategoricalEvent, recordEvent, aggregateSyntheticOnly} from "./attribution.mjs";
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=(name)=>fs.readFileSync(path.join(dir,name),"utf8");
const A=read("pilot-A-text.html");
const B=read("pilot-B-film.html");
const core=read("guide-core.html");
const article=read("investigation.html");
const articleWP=read("investigation-wp.html");
const hub=read("hub-candidate.html");
const css=read("style.css");
const vtt=read("film.vtt");
const poster=read("poster.svg");
const csv=read("claims-and-permissions.csv");
const ledger=read("source-register.md");
const plan=read("navigation-experiment.md");
const readme=read("README.md");
function count(regex,txt){return [...txt.matchAll(regex)].length;}
function safePresell(html){
  assert.equal(count(/<button\b[^>]*\bdisabled\b/gi,html),1,"exactly one disabled CTA");
  assert.equal(count(/<button\b/gi,html),1,"no surprise buttons");
  assert.match(html,/Affiliate disclosure:[\s\S]{0,290}<button[^>]*disabled/,"near-button disclosure");
  assert.doesNotMatch(html,/<(?:script|iframe|form)\b/i,"no scripts, third-party embeds or form");
  assert.doesNotMatch(html,/\bautoplay\b/i,"no autoplay");
  assert.doesNotMatch(html,/<a\b[^>]*href=["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i,"no merchant href");
  assert.doesNotMatch(html,/\b(?:utm_|clickid|aff_id|affiliate_id|fbclid|gclid)\b/i,"no tracking parameter");
  assert.match(html,/refund|money-back/i);
  assert.match(html,/privacy/i);
  assert.match(html,/no purchase is necessary/i);
}
test("A/B both use exactly identical substantive guide core",()=>{
 assert.ok(A.includes(core));
 assert.ok(B.includes(core));
 assert.equal(A.split(core).length,2);
 assert.equal(B.split(core).length,2);
});
test("Text-only variant has no film or media player",()=>{
 assert.doesNotMatch(A,/<(?:svg|video|audio|source)\b/i);
 assert.doesNotMatch(A,/film-heading/);
});
test("Film variant contains full non-JS static alternate, source controlled poster and transcript",()=>{
 assert.match(B,/film-heading/);
 assert.match(B,/<svg\b/);
 assert.match(B,/<details><summary>/);
 assert.match(B,/40-second/);
 assert.doesNotMatch(B,/<video\b/i,"no fake player until media hosted");
});
test("No merchant activation, tracking or duplicate collection on either variant",()=>{
 safePresell(A);safePresell(B);
});
test("Disabling the button is a mutation-resistant gate",()=>{
 const unsafe=A.replace(/\sdisabled aria-disabled="true"/,' aria-disabled="false"');
 assert.throws(()=>safePresell(unsafe));
});
test("Removing the disclosure is detected",()=>{
 const unsafe=A.replace(/<p class="fv-disclosure">[\s\S]*?<\/p>/,"");
 assert.throws(()=>safePresell(unsafe));
});
test("Introducing an earning link is detected",()=>{
 const unsafe=A.replace("</button>",'</button><a href="https://zen12.com/hnp">Buy</a>');
 assert.throws(()=>safePresell(unsafe));
});
test("Introducing a tracking form is detected",()=>{
 const unsafe=B.replace("</main>",'<form method="post"></form></main>');
 assert.throws(()=>safePresell(unsafe));
});
test("Original standalone investigation has citations and no shopping",()=>{
 assert.match(article, /1852/);
 assert.match(article, /1854/);
 assert.match(article, /1976/);
 assert.match(article, /2018/);
 assert.match(article, /wellcomecollection\.org/);
 assert.match(article, /doi\.org\/10\.1007\/s11097-018-9585-8/);
 assert.match(article, /puysegurs-animal-magnetism-files/);
 assert.doesNotMatch(article, /<button|zen12\.com|href[^>]*affiliates\.inspire3/i);
 assert.ok(article.length > 12000);
});
test("Standalone WordPress article contains same original content and scoped style",()=>{
 assert.ok(articleWP.includes(article));
 assert.match(articleWP, /<style>[\s\S]*\.fv-mind-investigation/);
});
test("Candidate hub is noncanonical and links existing published pages",()=>{
 assert.match(hub, /NOT CANONICAL|noncanonical/i);
 assert.match(hub, /finalvestige\.com\/focus/);
 assert.match(hub, /finalvestige\.com\/explore/);
 assert.match(hub, /puysegurs-animal-magnetism-files/);
 assert.doesNotMatch(hub, /<form|<script|zen12\.com|autoplay/i);
});
test("Accessible source-controlled vertical poster and film caption cues",()=>{
 assert.match(poster, /viewBox="0 0 540 960"/);
 assert.match(poster, /<title/);
 assert.match(poster, /<desc/);
 const cues=[...vtt.matchAll(/(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})/g)];
 assert.equal(cues.length,6);
 const time=(h,m,s,ms)=>((+h*3600)+(+m*60)+(+s))*1000+(+ms);
 let last=0;
 for(const c of cues){
   const start=time(...c.slice(1,5));
   const end=time(...c.slice(5,9));
   assert.equal(start,last,"cues must be contiguous");
   assert.ok(end>start,"cue duration positive");
   last=end;
 }
 assert.equal(last,40000);
});
test("Draft styling is mobile, accessible and reduced-motion conscious",()=>{
 assert.match(css,/prefers-reduced-motion/);
 assert.match(css,/:focus-visible/);
 assert.match(css,/max-width:390px/);
 assert.match(css,/max-width/);
 assert.match(css,/font-size:clamp|font:400 clamp/);
 assert.match(css,/button\[disabled\]/);
 assert.doesNotMatch(css,/@import\b/i);
});
test("Minimum claims matrix and external evidence ledger",()=>{
 const lines=csv.trim().split("\n");
 assert.ok(lines.length>=67);
 assert.match(lines[0],/source_ids/);
 assert.match(csv,/"BLOCK"/);
 assert.match(csv,/"SELLER_ONLY"/);
 for(const ref of ["S01","S02","S03","S04","M01","M02","M05","M06","M07","M08","R01","R02","R03","F02"]){
  assert.ok(ledger.includes(ref+" "), "missing source "+ref);
 }
 assert.match(ledger,/FTC/);
});
test("Privacy feature flag is OFF and no record can be collected",()=>{
 assert.equal(ATTRIBUTION_ENABLED,false);
 assert.deepEqual(recordEvent({channel:"tiktok",topic:"ideomotor",variant:"B",action:"guide_view"}),{recorded:false,reason:"disabled_by_design"});
 assert.doesNotMatch(read("attribution.mjs"),/fetch\(|sendBeacon\(|XMLHttpRequest|localStorage|sessionStorage|document\.cookie/);
});
test("PII, unrecognized fields and invalid categories are rejected",()=>{
 const good={channel:"organic_search",topic:"ideomotor",variant:"A",action:"guide_view"};
 assert.deepEqual(sanitizeCategoricalEvent(good),good);
 for(const bad of [{...good,email:"person@example.com"},{...good,ip:"127.0.0.1"},{...good,referrer:"https://example.com/path"},{...good,channel:"my-private-search"},{...good,action:"sale"}]){
  assert.equal(sanitizeCategoricalEvent(bad),null);
 }
});
test("Synthetic aggregates suppress n=19 and admit n=20, minimum cannot be lowered",()=>{
 const item={channel:"tiktok",topic:"ideomotor",variant:"B",action:"guide_view"};
 assert.equal(aggregateSyntheticOnly(Array(19).fill(item)).length,0);
 assert.deepEqual(aggregateSyntheticOnly(Array(20).fill(item)),[{key:"tiktok/ideomotor/B/guide_view",count:20}]);
 assert.throws(()=>aggregateSyntheticOnly(Array(19).fill(item),19));
 assert.throws(()=>aggregateSyntheticOnly([{...item,email:"x@y.com"}]));
});
test("Explicit release ownership boundaries remain documented",()=>{
 for(const phrase of ["PR #49","PR #172","Issue #150","Issue #174","Jetpack","HARD HOLD"]) assert.ok(readme.includes(phrase));
 for(const phrase of ["Issue #126","Issue #150","Issue #174","PR #172","no real","outbound"]) assert.ok(plan.toLowerCase().includes(phrase.toLowerCase()));
});
