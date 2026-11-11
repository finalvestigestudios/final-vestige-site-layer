"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {validate}=require("./validate_p0_geometry_postweight_20261111.cjs");
const dir=__dirname;
const plan=JSON.parse(fs.readFileSync(path.join(dir,"p0_geometry_postweight_triage_20261111.json"),"utf8"));
const bridge=JSON.parse(fs.readFileSync(path.join(dir,"browser_handoff_6_p0_15_oversize_20261110.json"),"utf8"));
let count=0;
function test(name,fn,expected){const result=fn();assert.equal(result,expected,name);count++;}
function mutate(fn){const copy=JSON.parse(JSON.stringify(plan));fn(copy);return validate(copy,bridge).ok;}
test("unmodified fixture",()=>validate(plan,bridge).ok,true);
test("fabricated guest 404",()=>mutate(p=>p.p0_source_queue[0].guest_http_status=404),false);
test("source rewrite",()=>mutate(p=>p.p0_source_queue[2].original_src="https://example.com/image.jpg"),false);
test("queue reordering",()=>mutate(p=>p.p0_source_queue.reverse()),false);
test("unproved photo identity",()=>mutate(p=>p.p0_source_queue[0].exact_visual_identity_proven=true),false);
test("unapproved rights",()=>mutate(p=>p.p0_source_queue[0].reuse_rights_cleared=true),false);
test("819 pixel upscale",()=>mutate(p=>p.tmi_285_5_geometry.width_limited_if_preserve_all_pixels_px=960),false);
test("crop approval forged",()=>mutate(p=>p.tmi_285_5_geometry.crop_approved=true),false);
test("request dimensions passed off as actual",()=>mutate(p=>p.tmi_285_5_geometry.saymedia_source_transform.requested_dimensions_are_actual_browser_dimensions=true),false);
test("fabricated 76 percent",()=>mutate(p=>p.claimed_76_percent.actual_saving_pct=76),false);
test("storage swapped for transfer",()=>mutate(p=>p.claimed_76_percent.actual_cold_baseline_image_wire_bytes=47096779),false);
test("inline byte mismatch",()=>mutate(p=>p.oversized_media.inline_linked_stored_original_bytes+=1),false);
test("PNG byte mismatch",()=>mutate(p=>p.oversized_media.no_subsize_pngs.stored_original_bytes-=1),false);
test("Jetpack misreported direct",()=>mutate(p=>p.oversized_media.per_post_storage_priority[0].delivery="direct_original_in_stored_src"),false);
test("post media ID altered",()=>mutate(p=>p.oversized_media.per_post_storage_priority[0].media_ids=[123]),false);
test("production write forbidden",()=>mutate(p=>p.release.wp_production_writes=1),false);
test("staging authorization forbidden",()=>mutate(p=>p.release.staging_approved=true),false);
console.log(count+"/"+count+" media crop and storage integrity checks PASS");
