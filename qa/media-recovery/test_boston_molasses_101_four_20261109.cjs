"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const {validate}=require("./validate_boston_molasses_101_four_20261109.cjs");
const a=JSON.parse(fs.readFileSync(path.join(__dirname,"boston_molasses_101_four_20261109.json"),"utf8"));
const c=JSON.parse(fs.readFileSync(path.join(__dirname,"offsite_upstream_288_20261109.json"),"utf8"));
assert.equal(validate(a,c).pass,true);let checks=1;
const clone=()=>JSON.parse(JSON.stringify(a));
const mutations=[
d=>{d.schema="modified"},
d=>{d.source_inventory.blob_sha="abc"},
d=>{d.performance.historical_broken_42_browser_verified=true},
d=>{d.performance.claimed_76pct_wire_reduction_measured=true},
d=>{d.performance.guest_wire_bytes=10000},
d=>{d.rows[0].release.wordpress_upload=true},
d=>{d.rows[0].release.asset_download=true},
d=>{d.rows[1].guest_browser.http_status=404},
d=>{d.rows[0].guest_browser.broken=true},
d=>{d.rows[0].external_viewer.http_status=200},
d=>{d.rows[0].commons_candidate.original_binary_exact_match=true},
d=>{d.rows[0].commons_candidate.rights_review_complete=true},
d=>{d.rows[0].commons_candidate.conditional_no_upscale_960px=[960,752]},
d=>{d.rows[1].commons_candidate.catalog_original_dimensions_px=[960,816]},
d=>{d.rows[3].commons_candidate.claimed_license="PUBLIC_DOMAIN"},
d=>{d.rows[3].commons_candidate.creator_credit=""},
d=>{d.rows[1].commons_candidate.historical_scene_note="A genuine 1919 contemporary map with no possible caveats."},
d=>{d.rows[2].slot="101:1"},
d=>{d.rows[0].exact_stored_url="https://example.com/fake.jpg"},
d=>{d.primary_archive_context.same_image_match=true},
d=>{d.performance.oversize_original_stored_bytes=100}
];
for(const mutate of mutations){const d=clone();mutate(d);assert.throws(()=>validate(d,c));checks++;}
assert.equal(checks,22);console.log("PASS "+checks+"/22 Boston Molasses source/rights/960px/guest-claim regressions");
