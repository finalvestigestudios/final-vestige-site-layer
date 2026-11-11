"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {validatePrimaryVisualLineage}=require("./validate_p0_285_407_official_lineage_20261111.cjs");
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"p0_285_407_exact_primary_visual_lineage_20261111.json"),"utf8"));
const copy=()=>JSON.parse(JSON.stringify(original));
test("official source-chain audit passes with two held P0 images",()=>assert.deepEqual(validatePrimaryVisualLineage(copy()).errors,[]));
const mutations=[
 ["invented guest 404",a=>a.items[0].guest_http_status=404],
 ["invented guest bytes",a=>a.items[1].guest_wire_bytes=12000],
 ["invented origin 200",a=>a.items[1].origin_http_status=200],
 ["published saymedia URL drift",a=>a.items[0].exact_published_src+="?wrong=1"],
 ["forged publisher media ID",a=>a.items[0].evidence.publisher_media_identifier="fake"],
 ["forged Commons source URL",a=>a.items[0].evidence.publisher_links_public_domain_original="https://wrong.invalid/photo.jpg"],
 ["2010 scene relabeled as 1979 event",a=>a.items[0].attribution.photographed_year=1979],
 ["TMI upscale to 960",a=>a.items[0].geometry.conditional_no_upscale_px=[960,720]],
 ["automatic 16:9 crop permitted",a=>a.items[0].geometry.automatic_crop_allowed=true],
 ["unsupported USGS binary conflated with guest success",a=>a.items[1].evidence.published_original_retriever_result="HTTP_200"],
 ["USGS original link changed away from WordPress",a=>a.items[1].evidence.primary_catalog_original_link_url+="?other"],
 ["USGS alternate thumbnail treated as native geometry",a=>a.items[1].geometry.published_original_native_px=[1000,1000]],
 ["unlicensed publication allowed",a=>a.items[0].upload_authorized=true],
 ["rehost approved without review",a=>a.items[1].caching_authorized=true],
 ["76 percent savings fabricated",a=>a.history.measured_transfer_reduction_percent=76],
 ["42 sources reported browser-confirmed",a=>a.history.guest_confirmed_broken=42],
 ["incorrect source roster",a=>a.items.push(copy().items[0])],
 ["download asserted without evidence",a=>a.release.source_candidate_assets_downloaded=1],
 ["publish changed",a=>a.release.wordpress_production_writes=1],
 ["false photo parity",a=>a.items[1].replacement_visual_parity_approved=true]
];
for(const [name,mutate] of mutations)test("FAIL CLOSED: "+name,()=>{const x=copy();mutate(x);assert.equal(validatePrimaryVisualLineage(x).ok,false)});
