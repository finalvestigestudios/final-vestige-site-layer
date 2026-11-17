"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {verify}=require("./validate_scotch_cap_4182_20261105.cjs");
const d=JSON.parse(fs.readFileSync(path.join(__dirname,"scotch_cap_4182_photo_lineage_20261105.json"),"utf8"));
const mutations=[
["source","visitor_broken",true],["source","guest_browser_http",200],["source","transfer_bytes",41234],
["source","origin_http",403],["source","exact_url","https://example.org/fake.jpg"],
["source","pinned_live_wp_blob","bad"],["catalog","uscg_event_date","1964-04-01"],
["catalog","same_scene_image","https://example.org/a.jpg"],["catalog","rendition_dimensions",[960,741]],
["catalog","exact_binary_or_crop_identity",true],["catalog","original_master_pixels",[960,960]],
["catalog","rights_to_cache",true],["noaa","caption_year",1946],
["noaa","copy_noaa_alt",true],["noaa","chronology_mismatch",false],
["release","no_upscale",false],["release","existing_rendition_ceiling",[960,741]],
["release","rights_approved",true],["release","chrome_failure_confirmed",true],
["release","download_performed",true],["release","wordpress_upload",true],
["release","wordpress_post_edit",true],["release","automatic_publish",true],
["context","actual_broken_count",42],["context","measured_weight_savings_percent",76],
["context","live_repairs",1],["context","oversize_stored_bytes",1]
];
test("source-only verified catalog remains HOLD",()=>assert.equal(verify(d).status,"HOLD"));
for(const [scope,key,value] of mutations)test("reject "+scope+"."+key,()=>{
 const m=JSON.parse(JSON.stringify(d));m[scope][key]=value;assert.throws(()=>verify(m));
});
