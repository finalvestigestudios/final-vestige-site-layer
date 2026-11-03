/* Node 18+ reproducible native tests; test file does not collect or transmit user data. */
import test from "node:test";
import assert from "node:assert/strict";
import { ATTRIBUTION_ACTIVATION, aggregateSynthetic, recordLiveEvent } from "./synthetic-attribution.mjs";

const clean = (n=20)=>({topic:"zen12_guide",channel:"tiktok",action:"guide_view",count:n});
test("every release/measurement toggle is closed",()=>{
  assert.equal(ATTRIBUTION_ACTIVATION.enabled,false);
  assert.equal(ATTRIBUTION_ACTIVATION.externalMerchantLinkActive,false);
  assert.equal(ATTRIBUTION_ACTIVATION.purchaserIdentityCollection,false);
  assert.equal(ATTRIBUTION_ACTIVATION.analyticsNetworkRequests,false);
  assert.throws(()=>recordLiveEvent({}),/CLOSED/);
});
test("count 19 is suppressed, 20 permitted in synthetic-only result",()=>{
 assert.deepEqual(aggregateSynthetic([clean(19)]).groups,[]);
 assert.deepEqual(aggregateSynthetic([clean(20)]).groups,[{topic:"zen12_guide",channel:"tiktok",action:"guide_view",synthetic_count:20}]);
});
test("synthetic aggregation combines only exact dimension groups",()=>{
 const r=aggregateSynthetic([clean(11),clean(9),{...clean(30),channel:"direct"},{...clean(19),topic:"rubber_hand"}]);
 assert.equal(r.groups.length,2);assert.deepEqual(r.groups.map(x=>x.synthetic_count),[30,20]);
});
test("PII and raw URL fields are denied, never copied",()=>{
 for (const field of ["email","ip","name","phone","user_agent","referrer","url","query","utm_source","affiliate_id","buyer_products","postal_code","cookie","timestamp","session_id","device_id","order_id","tracking_id"]) {
   assert.throws(()=>aggregateSynthetic([{...clean(),[field]:"sample"}]),/unapproved keys/);
 }
});
test("invalid categories and coercion fail closed",()=>{
 for(const input of [{...clean(),channel:"https://example.test/?email=abc"},{...clean(),topic:"other"},{...clean(),action:"purchase"},{...clean(),count:"20"},{...clean(),count:20.2},{...clean(),count:-1},{...clean(),count:Infinity},{...clean(),count:NaN},{...clean(),count:10001}])
 assert.throws(()=>aggregateSynthetic([input]));
});
test("rejects arrays, null, symbols and oversize input",()=>{
 assert.throws(()=>aggregateSynthetic("bad"));assert.throws(()=>aggregateSynthetic(new Array(1001).fill(clean())));
 assert.throws(()=>aggregateSynthetic([null]));assert.throws(()=>aggregateSynthetic([Object.assign(clean(),{[Symbol("identifier")]:"hidden"})]));
});
test("no raw rows or totals exposed; returned results frozen",()=>{
 const r=aggregateSynthetic([clean(20)]); assert.equal(r.rows,undefined);assert.equal(r.total,undefined);
 assert.equal(r.enabled,false);assert.equal(Object.isFrozen(r.groups),true);assert.equal(Object.isFrozen(r.groups[0]),true);
});
