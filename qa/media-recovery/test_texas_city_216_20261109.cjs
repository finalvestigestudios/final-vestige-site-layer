"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const data=require("./texas_city_216_six_primary_rights_20261109.json");
const {validate}=require("./validate_texas_city_216_20261109.cjs");
const clone=()=>JSON.parse(JSON.stringify(data));
test("clean frozen-source six-slot batch",()=>assert.deepEqual(validate(clone()),[]));
for(const k of ["216:0","216:1","216:2","216:3","216:4","216:5"]){
 test(k+" exact original URL bound",()=>{const x=clone();x.rows.find(r=>r.slot===k).stored_url+="?bad=1";assert.ok(validate(x).some(e=>e.startsWith("source_or_alt_mismatch")))});
}
test("duplicate slot blocked",()=>{const x=clone();x.rows[5].slot=x.rows[4].slot;assert.ok(validate(x).length)});
test("fabricated guest broken blocked",()=>{const x=clone();x.rows[0].visitor.guest_broken=true;assert.ok(validate(x).length)});
test("fabricated origin 404 blocked",()=>{const x=clone();x.rows[0].retriever.actual_origin_http_status=404;assert.ok(validate(x).length)});
test("invented wire bytes blocked",()=>{const x=clone();x.rows[0].visitor.transfer_bytes=12000;assert.ok(validate(x).length)});
test("caching permission blocked",()=>{const x=clone();x.rows[0].release.cache_authorized=true;assert.ok(validate(x).length)});
test("WP write permission blocked",()=>{const x=clone();x.rows[0].release.wordpress_upload_authorized=true;assert.ok(validate(x).length)});
test("UH conflict suppress blocked",()=>{const x=clone();x.rows[0].candidate.source_rights_conflict=false;assert.ok(validate(x).length)});
test("no 960px upscaling on tiny anchor",()=>{const x=clone();x.rows[5].candidate.conditional_max960_px=[960,640];assert.ok(validate(x).length)});
test("altered stored ALT blocked",()=>{const x=clone();x.rows[0].original_alt="disaster";assert.ok(validate(x).length)});
test("invented 76% metric blocked",()=>{const x=clone();x.proposed_76pct_wire_savings_measured=true;assert.ok(validate(x).length)});
test("catalog crop identity cannot be fabricated",()=>{const x=clone();x.rows[3].candidate.exact_binary_or_crop_verified=true;assert.ok(validate(x).length)});
test("rights clearance cannot be fabricated",()=>{const x=clone();x.rows[2].release.rights_cleared=true;assert.ok(validate(x).length)});
test("source custody SHA cannot be altered",()=>{const x=clone();x.source_inventory.blob_sha="bad";assert.ok(validate(x).length)});
test("modern memorial attribution remains licensed",()=>{const x=clone();x.rows[1].candidate.rights_observation="public domain";assert.ok(validate(x).length)});
