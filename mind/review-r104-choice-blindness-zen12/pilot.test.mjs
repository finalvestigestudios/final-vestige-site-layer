import test from "node:test";
import assert from "node:assert/strict";
import { validateSyntheticRecord,aggregateSyntheticRecords,recordLiveEvent,SYNTHETIC_POLICY } from "./attribution.mjs";
import { readFileSync } from "node:fs";
const base = new URL(".",import.meta.url);
const read = name => readFileSync(new URL(name,base),"utf8");
const A=read("pilot-a.html"), B=read("pilot-b.html"), article=read("investigation.md"), guide=read("zen12-guide.md");
const ledger=JSON.parse(read("evidence-gates.json"));
const rec=(variant="A")=>({variant,source:"organic_search",topic:"zen12",action:"guide_view"});
test("A/B preserve exact core editorial copy after removing optional original film",()=>{
 const film=B.match(/<aside class="film"[\s\S]*?<\/aside>/);
 assert.ok(film,"B has optional film");
 const stripped=B.replace(film[0],"").replace('data-variant="B"','data-variant="A"').replace("R104 B /","R104 A /");
 assert.equal(stripped,A);
});
test("actual CTA is disabled and commercial disclosure precedes the control",()=>{
 for(const x of [A,B]) {
  const d=x.indexOf("Affiliate disclosure:"), button=x.indexOf('<button type="button" disabled');
  assert.ok(d>0&&button>d&&button-d<650);
  assert.match(x,/aria-describedby="affiliate-disclosure-r104 gate-r104"/);
 }
});
test("prototypes contain no executable scripts, trackers, forms, merchant links or embeds",()=>{
 for(const x of [A,B]) {
  assert.doesNotMatch(x,/<(?:script|iframe|form|input|video|audio)\b/i);
  assert.doesNotMatch(x,/href="https:\/\/(?:zen12|inspire3|affiliates)\./i);
  assert.doesNotMatch(x,/(?:sendBeacon|localStorage|gtag\(|analytics\.js|pixel\.gif)/i);
 }
});
test("B alone contains original accessible SVG and plain transcript with no false video control",()=>{
 assert.doesNotMatch(A,/<svg\b/);
 assert.match(B,/<svg[\s\S]*?role="img"/);
 assert.match(B,/00–06s/); assert.match(B,/34–40s/);
 assert.match(B,/no MP4 produced/i);
});
test("structural keyboard focus, mobile grid and reduced-motion guards",()=>{
 for(const x of [A,B]) {
  assert.match(x,/focus-visible/);assert.match(x,/max-width:760px/);
  assert.match(x,/prefers-reduced-motion/);assert.match(x,/aria-labelledby="fvm104title"/);
  assert.match(x,/min-height:48px/);
 }
});
test("investigation contains actual source identifiers and does not endorse commerce",()=>{
 assert.match(article,/science\.1111709/);
 assert.match(article,/cognition\.2010\.06\.010/);
 assert.match(article,/journal\.pone\.0060554/);
 assert.doesNotMatch(article,/affiliate link to Zen12|buy Zen12 now/i);
});
test("guide sources distinguish seller outcomes from independent research",()=>{
 assert.match(guide,/seller claims|seller-published/i);
 assert.match(guide,/not a study of Zen12|did not test Zen12/i);
 assert.match(guide,/inspire3\.com\/privacy/);
});
test("source matrix references only existing ids, all release gates closed",()=>{
 const ids=new Set(ledger.sources.map(x=>x.id));
 assert.ok(ledger.claims.length>=35);
 for(const c of ledger.claims) for(const id of c.source_ids) assert.ok(ids.has(id),c.id+" "+id);
 assert.ok(ledger.gates.length>=30);
 assert.ok(ledger.gates.every(x=>x.status==="CLOSED"));
});
test("reject arbitrary identifying fields",()=>{
 for(const field of ["ip","email","session_id","raw_referrer","order_id","timestamp","user_agent","amount","landing_url"]) {
   assert.throws(()=>validateSyntheticRecord({...rec(),[field]:"sensitive"}));
 }
});
test("reject missing, invalid, inherited, and noncategorical inputs",()=>{
 assert.throws(()=>validateSyntheticRecord({variant:"A"}));
 assert.throws(()=>validateSyntheticRecord({...rec(),source:"https://google.com/search?q=private"}));
 assert.throws(()=>validateSyntheticRecord(Object.create({variant:"A"})));
 assert.throws(()=>validateSyntheticRecord({...rec(),variant:1}));
 assert.throws(()=>validateSyntheticRecord(null));
});
test("suppress groups smaller than 20, never infer sales",()=>{
 assert.deepEqual(aggregateSyntheticRecords(Array.from({length:19},()=>rec())),[]);
 const out=aggregateSyntheticRecords(Array.from({length:20},()=>rec()));
 assert.equal(out.length,1); assert.equal(out[0].syntheticCount,20);
 assert.ok(!Object.hasOwn(out[0],"sales") && !Object.hasOwn(out[0],"revenue"));
});
test("live events remain impossible",()=>{
 assert.throws(()=>recordLiveEvent(rec()),/HARD HOLD/);
 assert.equal(SYNTHETIC_POLICY.liveOutboundEnabled,false);
 assert.equal(SYNTHETIC_POLICY.realSalesMeasured,false);
});
