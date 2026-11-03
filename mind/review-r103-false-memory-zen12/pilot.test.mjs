import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname,join } from "node:path";
import {LIVE_COLLECTION_ENABLED,validateSyntheticEvent,aggregateSyntheticOnly,recordLiveEvent,inferAffiliateSalesFromClicks,MIN_REPORTING_CELL} from "./attribution.mjs";
const root = dirname(fileURLToPath(import.meta.url));
const read=name=>readFileSync(join(root,name),"utf8");
const a=read("pilot-a.html"),b=read("pilot-b.html"),e=JSON.parse(read("evidence-and-gates.json"));
const good={source:"organic",topic:"zen12",variant:"text",action:"guide_open"};
function core(html) {
  const start=html.indexOf("<header>");
  const endTag="</strong></p></section>";
  const end=html.indexOf(endTag,start);
  assert.ok(start>=0&&end>start,"shared substantive guide found");
  return html.slice(start,end+endTag.length);
}
test("A/B variants contain exactly identical substantive decision content",()=>{
  assert.equal(core(a),core(b));
  assert.ok(b.includes("<details open")&&b.includes("40-second transcript"));
  assert.ok(!a.includes("40-second transcript"));
});
test("Both variants disclose commission directly beside native disabled CTA",()=>{
  for(const page of [a,b]){
    const disclosure=page.indexOf("If you purchase through a future link");
    const disabled=page.indexOf("<button type=\"button\" disabled");
    assert.ok(disclosure>0&&disabled>disclosure&&disabled-disclosure<350);
    assert.match(page,/id="merchant-hold"/);
    assert.ok(!page.includes('href="https://zen12.com'));
  }
});
test("No active data collection, injected code, third-party media or subscription forms",()=>{
  for(const page of [a,b]){
    assert.doesNotMatch(page,/<script\b|<iframe\b|<form\b|<video\b|<audio\b|<img\b/i);
    assert.doesNotMatch(page,/(?:onload|onclick)\s*=|dataLayer|gtag\s*\(/i);
    assert.doesNotMatch(page,/https:\/\/[^"]*(affiliate_id|affid|clickbank|hop=)/i);
  }
});
test("Scoped styles, keyboard focus and reduced-motion rules exist",()=>{
  for(const page of [a,b]) {
    assert.match(page,/\.fv-mind-r103/);
    assert.match(page,/:focus-visible/);
    assert.match(page,/prefers-reduced-motion/);
    assert.match(page,/@media\(max-width:480px\)/);
  }
});
test("Primary research sources and source-scoped caveats exist in both",()=>{
  for(const page of [a,b]){
    assert.match(page,/10\.1371\/journal\.pone\.0286023/);
    assert.match(page,/did not evaluate Zen12/);
    assert.match(page,/fourteen EEG studies/);
    assert.match(page,/name, email and purchased-product details/);
  }
});
test("Source and claims registers maintain fail-closed evidence coverage",()=>{
  assert.ok(Object.keys(e.sources).length>=12);
  assert.ok(e.claims.length>=35);
  assert.ok(e.gates.length>=30);
  assert.ok(e.gates.every(g=>g.status==="CLOSED"));
  assert.deepEqual(e.affiliate_links,[]);
  assert.equal(e.live_changes,false);
  for(const claim of e.claims) for(const ref of claim.source_refs) assert.ok(e.sources[ref]);
});
test("Synthetic attribution explicitly disabled",()=>{
  assert.equal(LIVE_COLLECTION_ENABLED,false);
  assert.throws(()=>recordLiveEvent(),/HARD HOLD/);
  assert.throws(()=>inferAffiliateSalesFromClicks(),/cannot be inferred/);
});
test("Synthetic attribution permits only categorical fields and values",()=>{
  assert.deepEqual({...validateSyntheticEvent(good)},good);
  for(const extra of ["email","ip","url","referrer","buyer_id","click_id","timestamp","utm_source","user_agent","purchase_amount"]){
    assert.throws(()=>validateSyntheticEvent({...good,[extra]:"any"}),/Unexpected/);
  }
  assert.throws(()=>validateSyntheticEvent({...good,source:"https://example.com?email=x"}),/Noncategorical/);
  assert.throws(()=>validateSyntheticEvent({...good,action:123}),/Noncategorical/);
  assert.throws(()=>validateSyntheticEvent(Object.assign(Object.create({bad:true}),good)),/plain object/);
});
test("Cells below twenty suppressed: no record-level analytics",()=>{
  assert.equal(MIN_REPORTING_CELL,20);
  assert.deepEqual(aggregateSyntheticOnly(Array.from({length:19},()=>good)),[]);
  assert.deepEqual(aggregateSyntheticOnly(Array.from({length:20},()=>good)),[{group:"organic|zen12|text|guide_open",count:20}]);
  const mixed=aggregateSyntheticOnly([...Array.from({length:20},()=>good),{...good,source:"tiktok"}]);
  assert.deepEqual(mixed,[{group:"organic|zen12|text|guide_open",count:20}]);
});
test("B uses original optional explanatory asset, not deceptive active film",()=>{
  assert.match(b,/<svg/);assert.match(b,/<title id="pTitle">/);
  assert.match(b,/not established by an independent Zen12 trial/);
  assert.match(b,/No film autoplay or hosted video/);
  assert.doesNotMatch(b,/<source\s|<track\s/i);
});
