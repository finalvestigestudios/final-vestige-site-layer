"use strict";
// Node test runner; all inputs offline (no external network).
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {validate}=require("./validate_navy_west_loch_tang_7_20261109.cjs");
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,"navy_west_loch_tang_7_live_20261109.json"),"utf8"));
const clone=()=>JSON.parse(JSON.stringify(audit));
test("frozen official-catalog audit is structurally valid",()=>assert.equal(validate(audit).ok,true,validate(audit).errors.join(", ")));
test("all seven live source slots are unique and in exactly two posts",()=>{
 assert.deepEqual(audit.rows.map(x=>x.slot).sort(),["274:1","274:2","274:4","370:0","370:1","370:3","370:4"]);
 assert.deepEqual([...new Set(audit.rows.map(x=>x.post_id))].sort(),[274,370]);
});
const mutants=[
["fabricated guest HTTP",a=>a.rows[0].external_web_retriever.actual_guest_http=200],
["fabricated origin HTTP",a=>a.rows[0].external_web_retriever.actual_origin_http=502],
["invented transfer bytes",a=>a.rows[0].external_web_retriever.guest_encoded_transfer_bytes=123],
["unjustified failure flag",a=>a.rows[0].external_web_retriever.visitor_broken=true],
["fabricated image decode",a=>a.rows[0].external_web_retriever.guest_decoded_px=[960,600]],
["unauthorized caching",a=>a.rows[1].release.cache=true],
["unauthorized WordPress upload",a=>a.rows[1].release.wordpress_upload=true],
["invented item rights",a=>a.rows[1].rights.item_specific_clearance=true],
["invented license",a=>a.rows[1].rights.license="public-domain"],
["wrong accession",a=>a.rows[1].catalog.accession="80-G-999999"],
["nonofficial catalog",a=>a.rows[1].catalog.url="https://example.com/not-navy"],
["fictional medium dimensions",a=>a.rows[1].catalog.actual_medium_jpeg_px=[960,1000]],
["upscaled derivative",a=>a.rows[1].catalog.conditional_960_from_catalog_high_px=[1280,999]],
["invalid source geometry",a=>a.rows[1].catalog.high_tiff_catalog_px=[5860,0]],
["swapped image src",a=>a.rows[0].stored_src=a.rows[1].stored_src],
["extra browser claim",a=>a.rows[0].browser_verified=true],
["duplicate source slot",a=>a.rows[0].slot=a.rows[1].slot],
["invented post-modified date",a=>a.rows[0].post_modified="2026-11-09"],
["wrong 1943 vs 1944 chronology",a=>a.rows.find(x=>x.slot==="370:1").catalog.chronology="MAY_1944_WEST_LOCH"],
["misidentified Army Signal Corps photo",a=>a.rows.find(x=>x.slot==="370:4").catalog.source_origin="US_NAVY_PHOTO_NARA"],
["unmeasured 76% asserted proven",a=>a.known_limits.actual_76_pct_wire_savings_proven=true],
["reported 42 asserted confirmed",a=>a.known_limits.reported_42_broken_guest_verified=true],
["wrapper misclassified as HTTP 200",a=>a.rows[0].external_web_retriever.wrapper_code=200],
["invalid census SHA",a=>a.frozen_census_ref="0".repeat(40)],
["extra top-level fact",a=>a.newly_verified=true],
["extra rights key",a=>a.rows[0].rights.unknown_approval=true]
];
for(const [name,mutate] of mutants) test("reject: "+name,()=>{
 const changed=clone();mutate(changed);
 assert.equal(validate(changed).ok,false,"adversarial source mutation incorrectly accepted: "+name);
});
