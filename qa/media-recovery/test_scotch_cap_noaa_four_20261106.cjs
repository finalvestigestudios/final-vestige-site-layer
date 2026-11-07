"use strict";
const {test}=require("node:test");const assert=require("node:assert/strict");const fs=require("node:fs");
const {validate}=require("./validate_scotch_cap_noaa_four_20261106.cjs");
const original=JSON.parse(fs.readFileSync(__dirname+"/scotch_cap_noaa_four_20261106.json","utf8"));
const clone=()=>structuredClone(original);
test("baseline exact four-source ledger validates",()=>assert.deepEqual(validate(clone()),{ok:true,errors:[]}));
const mutations=[
["missing row",d=>d.rows.pop()],
["wrong source URL",d=>d.rows[0].published_src="https://example.org/wrong.jpg"],
["duplicate slot",d=>d.rows[1].key="418:0"],
["fake 42 confirmed",d=>d.baseline.confirmed_broken_images=42],
["fake measured 76 percent",d=>d.baseline.measured_weight_reduction_pct=76],
["wrong 61 count",d=>d.baseline.historical_posts=66],
["wrong 66 count",d=>d.baseline.current_posts=61],
["visitor 404 claimed from wrapper",d=>d.rows[0].guest_browser_http=404],
["guessed natural width",d=>d.rows[0].guest_natural_width=600],
["invented Chrome currentSrc",d=>d.rows[2].guest_current_src=d.rows[2].candidate_url],
["invented bytes",d=>d.rows[2].guest_encoded_bytes=265000],
["fake origin status",d=>d.rows[1].origin_http=403],
["premature museum rights",d=>d.rows[1].rights_republication_cleared=true],
["premature NOAA cache",d=>d.rows[2].third_party_caching_authorized=true],
["WordPress write",d=>d.rows[3].wordpress_write_authorized=true],
["claims binary identity",d=>d.rows[0].same_binary_verified=true],
["unsafe 1200px",d=>d.rows[0].candidate_preview_pixels=[1200,960]],
["unsafe upscale",d=>d.rows[1].proposed_if_rights_cleared_pixels=[960,758]],
["invented NOAA size",d=>d.rows[2].proposed_if_rights_cleared_pixels=[960,540]],
["pre/post photo mismatch",d=>d.rows[0].subject="Aftermath"],
["NOAA 1960 substitution",d=>d.rows[2].source_catalog_url="https://www.noaa.gov/noaa-collections/photo-library/1960"],
["USGS wrong photo",d=>d.rows[3].subject="1960 tsunami"],
["missing rights details",d=>d.rows[0].item_rights=""],
["unauthorized production writes",d=>d.release.wordpress_production_writes=1],
["missing source credit",d=>d.rows[2].credit=""]
];
for(const [label,mutate] of mutations)test("reject "+label,()=>{const d=clone();mutate(d);assert.equal(validate(d).ok,false,label)});
