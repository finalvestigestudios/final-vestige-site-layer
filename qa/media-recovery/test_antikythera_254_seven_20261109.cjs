"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validate,resize}=require("./validate_antikythera_254_seven_20261109.cjs");const base=JSON.parse(fs.readFileSync(path.join(__dirname,"antikythera_254_seven_catalog_20261109.json"),"utf8"));
const fresh=()=>JSON.parse(JSON.stringify(base));
test("exact 7-source hold baseline",()=>assert.deepEqual(validate(base),[]));
test("960px with no upscaling",()=>{assert.deepEqual(resize([783,800]),[783,800]);assert.deepEqual(resize([2736,3648]),[960,1280]);assert.deepEqual(resize([5472,3648]),[960,640]);});
for(let i=0;i<7;i++){
 test(i+" changed source denied",()=>{let x=fresh();x.records[i].stored_original_url+="?other";assert.ok(validate(x).some(s=>s.startsWith("source:")));});
 test(i+" forged visitor 404 denied",()=>{let x=fresh();x.records[i].retrieval.guest_http=404;assert.ok(validate(x).some(s=>s.startsWith("fabricated_network:")));});
 test(i+" caching denied",()=>{let x=fresh();x.records[i].release.cache=true;assert.ok(validate(x).some(s=>s.startsWith("forbidden_write:")));});
 test(i+" rights forced open denied",()=>{let x=fresh();x.records[i].candidate.item_rights_cleared=true;assert.ok(validate(x).some(s=>s.startsWith("fake_clearance:")));});
 test(i+" inappropriate output dimensions denied",()=>{let x=fresh();x.records[i].candidate.conditional_max_960_no_upscale=[1280,1280];assert.ok(validate(x).some(s=>s.startsWith("dimensions:")));});
}
test("metadata conflict preserved",()=>{let x=fresh();x.records[3].candidate.license_observed="CC-BY-4.0";assert.ok(validate(x).some(s=>s.startsWith("catalog_rights_scene:")));});
test("modern reconstruction context preserved",()=>{let x=fresh();x.records[5].candidate.scene_temporal_integrity="Ancient intact machine";assert.ok(validate(x).some(s=>s.startsWith("catalog_rights_scene:")));});
test("false 76% saving blocked",()=>{let x=fresh();x.counts.measured_wire_reduction_percent=76;assert.ok(validate(x).includes("false_guest_or_wire_claim"));});
test("museum context not a replacement",()=>{let x=fresh();x.context_is_replacement_image=true;assert.ok(validate(x).includes("metadata_conflict_or_museum_context"));});
