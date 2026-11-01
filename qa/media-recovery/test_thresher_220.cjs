"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {validate} = require("./validate_thresher_220.cjs");
const original = JSON.parse(fs.readFileSync(path.join(__dirname,"thresher_220_navy_primary_20261031.json"),"utf8"));
const census = JSON.parse(fs.readFileSync(path.join(__dirname,"parts","05.json"),"utf8"));
const copy = () => JSON.parse(JSON.stringify(original));
function rejectsMutation(name, mutation, expected) {
  test(name, () => {
    const m = copy(); mutation(m);
    const problems = validate(m,census);
    assert.ok(problems.some(x=>x.includes(expected)),JSON.stringify(problems));
  });
}
test("authoritative seven-slot custody manifest passes",()=>assert.deepEqual(validate(original,census),[]));
rejectsMutation("reject invented browser 404",m=>m.items[0].observed_image_http_status=404,"invented live/binary evidence");
rejectsMutation("reject invented browser 200",m=>m.items[6].observed_image_http_status=200,"invented live/binary evidence");
rejectsMutation("reject fabricated browser broken count",m=>m.confirmed_visitor_broken_images=42,"unverified site failures");
rejectsMutation("reject 42 unproven failures",m=>m.claimed_42_sitewide_broken_images_verified=true,"42 failure claim");
rejectsMutation("reject invented 76 percent savings",m=>m.sitewide_76_percent_weight_reduction_verified=true,"76 percent claim");
rejectsMutation("reject changed original image URL",m=>m.items[0].published_original_url="https://example.invalid/not-thresher.jpg","source/ALT changed");
rejectsMutation("reject changed historical ALT",m=>m.items[3].published_original_alt="A different submarine door","source/ALT changed");
rejectsMutation("reject counterfeit Navy ID",m=>m.items[3].navy_catalog_number="NH 97570","Navy photo ID");
rejectsMutation("reject invented Trieste II official photo ID",m=>{m.items[4].navy_catalog_number="NH 00000";m.items[4].source_match_level="nhhc_exact"},"Navy photo ID");
rejectsMutation("reject unauthorized mirroring",m=>m.items[5].mirror_authorized=true,"release gate 5");
rejectsMutation("reject WordPress upload",m=>m.items[2].wordpress_media_upload_authorized=true,"release gate 2");
rejectsMutation("reject claimed rights clearance",m=>m.rights_review_complete=true,"release gate");
rejectsMutation("reject fabricated image hash",m=>m.items[1].original_binary_sha256="a".repeat(64),"invented live/binary evidence");
rejectsMutation("reject fabricated decoded width",m=>m.items[1].observed_naturalWidth=740,"invented live/binary evidence");
rejectsMutation("reject untrusted source confidence",m=>m.items[2].source_match_level="verified_live_image","source confidence");
rejectsMutation("reject width over 960",m=>m.items[0].derivative_target_dimensions.width=1280,"no-upscale geometry");
rejectsMutation("reject upscaled narrow photograph",m=>m.items[1].derivative_target_dimensions.width=960,"no-upscale geometry");
rejectsMutation("reject aspect ratio distortion",m=>m.items[0].derivative_target_dimensions.height=900,"no-upscale geometry");
rejectsMutation("reject duplicate slots",m=>m.items[6].key="220:0","slot key");
rejectsMutation("reject missing slot",m=>m.items.pop(),"seven image records");
rejectsMutation("reject Skylark image date overclaim",m=>m.items[2].historical_context="Photo was taken during April 1963 Thresher trials.","Skylark photo chronology");
rejectsMutation("reject Trieste II unverified ID omission",m=>m.items[4].historical_context="Trieste II 1964.","Trieste II archive uncertainty");
test("frozen 61-post input cannot silently change Thresher source",()=>{
 const clone=structuredClone(census); const rec=clone.images.find(x=>x.key==="220:5");
 rec.source_url="https://example.invalid/changed.jpg";
 assert.ok(validate(original,clone).some(x=>x.includes("source/ALT changed")));
});
test("exact-source records cannot be misordered",()=>{
 const m=copy(); [m.items[1],m.items[2]]=[m.items[2],m.items[1]];
 assert.ok(validate(m,census).some(x=>x.startsWith("slot key")));
});
