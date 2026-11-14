'use strict';
// Native Node regression suite for immutable, rights-HOLD audit. All test bytes synthetic.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_p0_wp125_six_live_20261114.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_wp125_six_live_20261114.json'),'utf8'));
const mutations=[
  ["invented browser 404", d=>{d.source_slots[0].source_status.guest_http_status=404;}],
  ["invented browser success", d=>{d.source_slots[1].source_status.guest_http_status=200;}],
  ["invented browser broken count", d=>{d.historical_baseline.confirmed_guest_broken=42;}],
  ["invented 76 percent savings", d=>{d.historical_baseline.claimed_76_percent_wire_savings_measured=true; d.historical_baseline.measured_savings_percent=76;}],
  ["fake wire bytes from storage", d=>{d.wp_media.visitor_network_bytes=d.wp_media.oversized_stored_bytes;}],
  ["invented origin 200", d=>{d.source_slots[2].source_status.origin_http_status=200;}],
  ["fake browser currentSrc", d=>{d.source_slots[4].source_status.guest_current_src='https://bad.example/wrong.jpg';}],
  ["invented natural dimensions", d=>{d.source_slots[0].source_status.guest_intrinsic_dimensions=[960,720];}],
  ["fake visitor bytes", d=>{d.source_slots[3].source_status.guest_transfer_bytes=1212;}],
  ["all rights cleared", d=>{d.release.item_rights_cleared=true;}],
  ["wordpress production allowed", d=>{d.release.wp_production_write_allowed=true;}],
  ["silently approve caching", d=>{d.release.cache_or_download_allowed=true;}],
  ["silently approve scene substitution", d=>{d.release.source_identity_verified=true;}],
  ["silently approve candidate", d=>{d.asset_candidates[0].reuse_approved=true;}],
  ["museum image upscaled", d=>{d.asset_candidates[5].max_960_no_upscale_px=[960,741];}],
  ["wrong Commons pixels", d=>{d.asset_candidates[0].native_px=[1000,1000];}],
  ["unverified candidate deleted", d=>{d.asset_candidates.pop();}],
  ["source URL drift 285:5", d=>{d.source_slots[0].published_source='https://example.org/new.jpg';}],
  ["source URL drift 418:2", d=>{d.source_slots[4].published_source='https://example.org/new.jpg';}],
  ["source slot moved", d=>{d.source_slots[0].slot='287:5';}],
  ["missing post", d=>{delete d.posts[418];}],
  ["stale published figure count", d=>{d.posts[407].inline_images=7;}],
  ["fake media count", d=>{d.wp_media.image_attachments_total=123;}],
  ["media size changed", d=>{d.wp_media.oversized_origins[0].bytes=120000;}],
  ["duplicate media attachment", d=>{d.wp_media.oversized_origins[1].id=d.wp_media.oversized_origins[0].id;}],
  ["wrong oversized total", d=>{d.wp_media.oversized_stored_bytes-=1;}],
  ["false 1.5MiB threshold", d=>{d.wp_media.strict_decimal_gt_bytes=1572864;}],
  ["fake method", d=>{d.method='Production browser confirmed all 42 broken';}],
  ["fake original HTTP", d=>{d.source_slots[0].source_status.retriever_wrapper_code=200;}],
  ["disable no upscale", d=>{d.release.no_upscale=false;}],
  ["duplicate P0", d=>{d.source_slots[5].slot=d.source_slots[4].slot;}],
  ["fake subscription budget", d=>{d.release.subscriptions_usd=5;}]
];
assert.deepEqual(validate(original),{ok:true,errors:[]},'positive exact-source inventory');
let passed=1;
for(const [name,mutate] of mutations){const d=JSON.parse(JSON.stringify(original));mutate(d);const result=validate(d);assert.equal(result.ok,false,name);assert.ok(result.errors.length>0,name);passed++;}
console.log(`PASS ${passed}/${mutations.length+1} native Node regression cases`);
