"use strict";
const assert=require("node:assert/strict");
const {validate}=require("./validate_tmi_285_p0_20261103.cjs");
const evidence=require("./tmi_285_p0_publisher_original_20261103.json");
const frozen=require("./parts/03.json");
const sha="49183f66f880f7c4dfd363acca906876877f2e5e";
const clone=x=>JSON.parse(JSON.stringify(x));
assert.deepEqual(validate(evidence,frozen,sha),[],"source inventory and safe claims must pass");
const cases=[
["wrong SHA",x=>x.inventory_blob_sha="f".repeat(40)],["wrong post",x=>x.word_press.status="draft"],["fewer sources",x=>x.rows.pop()],
["duplicate",x=>x.rows[1].image_key="285:0"],["URL",x=>x.rows[5].source_url="https://evil.example/p.jpg"],
["ALT",x=>x.rows[3].alt="staff"],["wrong host",x=>x.rows[0].source_host="wrong.example"],
["invent HTTP",x=>x.rows[5].browser.origin_http_status=404],["invent decode",x=>x.rows[5].browser.img_decode_ok=true],
["fabricate bytes",x=>x.rows[5].browser.cdp_transfer_bytes=10324],["fake Chrome",x=>x.observation_protocol.visitor_chromium_executed=true],
["wrong wrapper",x=>x.rows[5].retriever_wrapper_code=200],["fake 200",x=>x.rows[5].retriever_status="DISPLAYED_INDEPENDENT_VIEWER"],
["rights",x=>x.rows[5].rights_review="CLEARED"],["cache",x=>x.rows[5].source_cache_authorized=true],
["write",x=>x.rows[5].wordpress_write_authorized=true],["publication",x=>x.editorial_proposals[0].publish_approved=true],
["fake 76%",x=>x.historic_baseline.weight_reduction_measured=true],["fake 42",x=>x.historic_baseline.reported_broken_browser_verified=true],
["claimed repairs",x=>x.historic_baseline.production_replacements=1],["width upscale",x=>x.rows[5].conditional_derivative_width_px=960],
["height crop",x=>x.rows[5].conditional_derivative_height_px=460],["wrong master",x=>x.rows[5].verified_original_width_px=960],
["false rights",x=>x.rows[5].primary_candidate.license="CC0"],["wrong license source",x=>x.rows[5].primary_candidate.catalog_url="https://other.example/"],
["swap 1979",x=>x.rows[5].different_scene_historical_option.exact_scene_equivalent=true],
["auto release",x=>x.rows[5].different_scene_historical_option.publication_allowed=true],
["miss crop flag",x=>delete x.rows[5].visual_crop_difference],["edit 4 other",x=>x.rows[4].verified_original_width_px=960],
["invent HTTP 285:2",x=>x.rows[2].browser.origin_http_status=500],["visitor status",x=>x.rows[0].browser.visibly_broken=false],
["fake baseline",x=>x.historic_baseline.external_source_slots=286],["not exact source census",x=>x.word_press.exact_source_and_alt_match=5],
["no NARA equiv",x=>x.rows[5].different_scene_historical_option.conditional_no_upscale_px=[1280,1229]],
["missing 285:5",x=>x.rows.splice(5,1)],
];
for(const [name,mutate] of cases){const x=clone(evidence);mutate(x);assert.ok(validate(x,frozen,sha).length,name+" must fail closed");}
assert.ok(validate(evidence,frozen,"0".repeat(40)).length,"source SHA mismatch fails");
console.log("TMI 285 P0 source gate: "+(cases.length+2)+"/"+(cases.length+2)+" native Node checks PASS");
