"use strict";
const {test}=require("node:test"), assert=require("node:assert/strict"), fs=require("node:fs"),path=require("node:path");
const {verify}=require("./validate_wp_live15_metadata_hold_20261112.cjs");
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,"wp_live15_metadata_hold_20261112.json"),"utf8"));
const copy=()=>JSON.parse(JSON.stringify(fixture));
test("full fifteen-row live WordPress provenance snapshot validates",()=>assert.equal(verify(fixture).valid,true));
function rejects(name,mutate){test(name,()=>{const a=copy();mutate(a);assert.equal(verify(a).valid,false)})}
rejects("forged 76% transfer",a=>a.metrics.visitor_transfer_saving_percent=76);
rejects("invented broken visitor count",a=>a.metrics.actual_broken_guest_count=42);
rejects("fake origin HTTP",a=>a.records[0].origin_http_status=404);
rejects("fake candidate availability",a=>a.records.find(x=>x.candidate_existing_wp_virtual_variant).candidate_existing_wp_virtual_variant.actual_http_status=200);
rejects("fake rights approval",a=>a.records[0].rights_verified_for_transform=true);
rejects("unsafe 1024 derivative",a=>a.records[0].conditional_max_960_no_upscale_px[0]=1024);
rejects("invented on-disk subsize",a=>a.records.find(x=>x.candidate_existing_wp_virtual_variant).candidate_existing_wp_virtual_variant.listed_virtual=false);
rejects("missing no-subsize 1024 author size",a=>a.records.find(x=>x.media_id===39).image_inline_match.html_author_width_px=960);
rejects("wrong Vasa network source type",a=>a.records.find(x=>x.media_id===388).image_inline_match.source_kind="wordpress_original_direct");
rejects("overstated stored bytes",a=>a.records[0].original_stored_bytes++);
rejects("unsafe WordPress writes",a=>a.policy.wordpress_write=true);
