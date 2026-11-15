"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {validate}=require("./validate_eastland_214_20261114.cjs");
const base=require("./eastland_214_primary_crosswalk_20261114.json");
const copy=()=>JSON.parse(JSON.stringify(base));
test("baseline validates, release remains HOLD",()=>{assert.deepEqual(validate(base),[]);assert.equal(base.release,"HOLD")});
const cases=[
["invented guest HTTP 200",x=>x.items[0].guest_http_status=200,"fabricated_wire_evidence"],
["invented origin HTTP 404",x=>x.items[1].origin_http_status=404,"fabricated_wire_evidence"],
["invented transferred bytes",x=>x.items[0].encoded_transfer_bytes=2000,"fabricated_wire_evidence"],
["invented natural width",x=>x.items[0].guest_natural_width=500,"fabricated_wire_evidence"],
["reader evidence recast as origin 404",x=>x.items[4].source_reader="origin_404","fabricated_wire_evidence"],
["claim 42 confirmed",x=>x.baseline.guest_confirmed_broken=42,"unsubstantiated_sitewide_claim"],
["claim 76% measured",x=>x.baseline.measured_transfer_savings_percent=76,"unsubstantiated_sitewide_claim"],
["alter source URL",x=>x.items[0].source_url+="?x=1","source_custody"],
["alter primary catalog",x=>x.items[4].record_url="https://example.org","source_custody"],
["duplicate slot",x=>x.items[1].slot="214:0","source_custody"],
["remove original",x=>x.items.pop(),"six_slots_required"],
["permit cache",x=>x.items[3].cache_allowed=true,"unauthorized_reuse"],
["permit WP write",x=>x.items[3].wp_write_allowed=true,"unauthorized_reuse"],
["claim rights approved",x=>x.items[0].rights_cleared_for_wp=true,"unauthorized_reuse"],
["claim identical binary",x=>x.items[0].exact_binary_identity_verified=true,"unauthorized_reuse"],
["claim release",x=>x.release="READY","release_scope"],
["allow homepage edits",x=>x.homepage_untouched=false,"release_scope"],
["invent panorama upscale",x=>x.items[1].proposed_non_upscale_px={width:1280,height:342},"geometry_or_upscale"],
["hide panorama small height",x=>x.items[1].proposed_non_upscale_px.height=900,"geometry_or_upscale"],
["upscale 475px Kenosha",x=>x.items[2].proposed_non_upscale_px={width:960,height:770},"geometry_or_upscale"],
["remove rights basis",x=>x.items[3].rights_evidence="PD","missing_provenance"],
["remove source link",x=>x.items[2].archive_candidate="unverified","catalog_candidate"],
["erase government-authorship concern",x=>x.items[5].rights_evidence="NARA record 281841, presumed automatically federal employee work; rights unquestioned; proceed to publish","nara_authorship_caveat"],
["erase incompatible date signal",x=>x.items[4].rights_evidence="LOC Bain publication is without known restriction, fully checked and available for republication","loc_date_conflict"],
["inflate stored bytes as transfer",x=>x.baseline.wp_original_stored_bytes=25000,"unsubstantiated_sitewide_claim"],
["change first-party comparisons",x=>x.baseline.historical_images=400,"unsubstantiated_sitewide_claim"]
];
for(const [name,mutation,error] of cases)test(name,()=>{const x=copy();mutation(x);assert.ok(validate(x).some(s=>s.includes(error)),name)});
