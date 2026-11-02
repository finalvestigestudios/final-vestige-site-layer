import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ATTRIBUTION_ENABLED, record, classify, summarizeSynthetic } from "./attribution.mjs";
const here = dirname(fileURLToPath(import.meta.url));
const read = name => readFileSync(join(here, name), "utf8");
const core = read("guide-core.html");
const A = read("zen12-guide-A.wordpress-draft.html");
const B = read("zen12-guide-B.wordpress-draft.html");
const article = read("investigation.md");
const hub = read("mind-hub-candidate.wordpress-draft.html");
const vtt = read("film.vtt");
const poster = read("film-poster.svg");
const matrix = read("claim-decisions.csv");
const ledger = read("sources.csv");
const CTA = /<button\b(?=[^>]*\sdisabled(?:\s|>|=))[^>]*>/i;
function checkOffer(html){
  const button = html.match(CTA);
  if (!button) return false;
  const i = html.indexOf(button[0]);
  const j = html.lastIndexOf('class="disclosure"', i);
  return j >= 0 && i - j < 520;
}
test("A and B retain byte-for-byte same full guide content",()=>{
 assert.ok(core.length > 12000);
 assert.equal(A.split(core).length,2);
 assert.equal(B.split(core).length,2);
});
test("both CTAs are native disabled with near-link prospective disclosure",()=>{
 assert.ok(checkOffer(A)); assert.ok(checkOffer(B));
 const mutant = A.replace(/<button type="button" disabled/, '<button type="button" aria-disabled="true"');
 assert.equal(checkOffer(mutant), false, "aria-disabled without native disabled must fail");
});
test("zero active seller links, scripts, forms, external embeds or navigation changes",()=>{
 for(const html of [A,B,hub]) {
  assert.doesNotMatch(html, /<(?:script|form|iframe)\b/i);
  assert.doesNotMatch(html, /<a\b[^>]+href=["'][^"']*(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i);
  assert.doesNotMatch(html, /autoplay\b|window\.location|fetch\(|sendBeacon|localStorage|sessionStorage/i);
 }
 assert.match(A,/https:\/\/finalvestige\.com\/focus\//);
});
test("B describes unhosted video honestly and exposes transcript without JavaScript",()=>{
 assert.doesNotMatch(B,/<video\b|<audio\b/);
 assert.match(B,/<details><summary>Read the complete 40-second transcript<\/summary>/);
 assert.equal((B.match(/<li><strong>00:/g)||[]).length,6);
 assert.match(poster,/<title id="r60-poster-title">/);
 assert.match(poster,/<desc id="r60-poster-desc">/);
});
test("caption timing is continuous 0–40 seconds",()=>{
 const times = [...vtt.matchAll(/(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})/g)];
 assert.equal(times.length,6);
 assert.equal(times[0][1],"00:00:00.000");
 assert.equal(times.at(-1)[2],"00:00:40.000");
 for(let i=0;i<times.length-1;i++) assert.equal(times[i][2],times[i+1][1]);
});
test("no merchant conclusion inside scientific investigation",()=>{
 assert.doesNotMatch(article,/\bZen12\b|\bInspire3\b|checkout|buy now/i);
 assert.match(article,/Coué/);
 assert.match(article,/https:\/\/www\.gutenberg\.org\/ebooks\/29339/);
});
test("product evidence remains seller vs study separated",()=>{
 assert.match(core,/did <em>not<\/em> evaluate Zen12/);
 assert.match(core,/not independently established for Zen12/);
 assert.match(core,/mobile-number field/i);
 assert.match(core,/At least|guarantee/i);
});
test("single existing Focus funnel, independent noncanonical hub",()=>{
 assert.match(hub,/noncanonical \/mind\/ draft candidate/i);
 assert.match(hub,/https:\/\/finalvestige\.com\/focus\//);
 assert.doesNotMatch(hub,/<input\b/i);
});
test("58 source-claim decisions with rejected clinical, approval and creative overclaims",()=>{
 const n = matrix.trim().split("\n").length - 1;
 assert.equal(n,58);
 for (const key of ["HIST05","OFFER06","OFFER19","AFF02","AFF07","EXP08"]) assert.match(matrix,new RegExp(key));
 assert.match(matrix,/HOLD/);
});
test("24 editor sources; exact offer and FTC guidance present",()=>{
 assert.equal(ledger.trim().split("\n").length-1,24);
 for(const url of ["https://zen12.com/hnp","https://zen12.com/getstarted","https://affiliates.inspire3.com/","https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance"]) assert.ok(ledger.includes(url));
});
test("attribution remains disabled, PII rejects, unknown attributes reject",()=>{
 assert.equal(ATTRIBUTION_ENABLED,false);
 assert.deepEqual(record({email:"person@example.com"}),{recorded:false,reason:"release_hold"});
 assert.equal(classify({event:"offer_intent",topic:"zen12",variant:"B",email:"person@example.com"}),null);
 assert.equal(classify({event:"offer_intent",topic:"zen12",variant:"B",ip:"192.0.2.1"}),null);
 assert.equal(classify({event:"offer_intent",topic:"zen12",variant:"B",utm:"x"}),null);
 assert.equal(classify({event:"offer_intent",topic:"zen12",variant:"B"}).topic,"zen12");
});
test("synthetic n=19 suppressed, n=20 visible, no raw events returned",()=>{
 const event={event:"offer_intent",topic:"zen12",variant:"B"};
 assert.deepEqual(summarizeSynthetic(Array.from({length:19},()=>event)),[]);
 assert.deepEqual(summarizeSynthetic(Array.from({length:20},()=>event)),[{group:"zen12/B/offer_intent",count:20}]);
 assert.throws(()=>summarizeSynthetic([{...event,visitor_id:"a"}]));
 assert.throws(()=>summarizeSynthetic([event],19));
});
