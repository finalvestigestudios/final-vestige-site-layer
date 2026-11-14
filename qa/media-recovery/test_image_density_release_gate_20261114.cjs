'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {assess}=require('./image_density_release_gate_20261114.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'image_density_preflight_nine_20261114.json'),'utf8'));
const fresh=()=>structuredClone(original);
const check=(edit,expected)=>{const a=fresh();edit(a);const r=assess(a);assert.equal(r.state,'HOLD');assert.equal(r.release_authorized,false);assert.equal(r.sitewide_76_percent_claim_supported,false);assert.ok(JSON.stringify(r).includes(expected),JSON.stringify(r));};
const observable=(slot='34:0',css=460,dpr=2,w=960,h=540,height=250)=>({[slot]:{css_width_px:css,css_height_px:height,dpr,cold_browser_verified:true,candidate_http_status:200,candidate_decoded:true,candidate_current_src:'https://finalvestige.com/wp-content/example.webp',candidate_natural_width_px:w,candidate_natural_height_px:h,asset_identity_verified:true}});
test('control has nine source locked assets and cannot approve edits',()=>{const r=assess(fresh());assert.equal(r.source_inventory_valid,true);assert.equal(r.results.length,9);assert.equal(r.guest_measurement_count,0);assert.ok(r.results.every(x=>x.state==='HOLD'))});
test('actual CSS width 460 DPR2 on 960 is density-screen PASS only; release blocked',()=>{const r=assess(fresh(),observable());assert.equal(r.results[0].density,'DENSITY_SCREEN_PASS');assert.equal(r.release_authorized,false)});
test('same 960 rendition at 500 CSS pixels DPR2 is under-dense',()=>{const r=assess(fresh(),observable('34:0',500));assert.equal(r.results[0].density,'INSUFFICIENT');assert.ok(r.results[0].reasons.includes('candidate_under_density_at_actual_css_dpr'))});
test('candidate 960 width at 1024 CSS 1x undersized',()=>{const r=assess(fresh(),observable('34:0',1024,1));assert.equal(r.results[0].density,'INSUFFICIENT')});
test('TMI 819 candidate at 410 CSS DPR2 fails',()=>{const r=assess(fresh(),observable('285:5',410,2,819,614,300));const x=r.results.find(x=>x.slot==='285:5');assert.equal(x.density,'INSUFFICIENT');assert.ok(x.reasons.includes('original_publisher_16_9_crop_vs_4_3_candidate'))});
test('Scotch Cap 600 candidate at 301 CSS DPR2 fails',()=>{const r=assess(fresh(),observable('418:2',301,2,600,463,231));assert.equal(r.results.find(x=>x.slot==='418:2').density,'INSUFFICIENT')});
test('Malbone map nominal density pass still requires zoom and rights review',()=>{const r=assess(fresh(),observable('621:1',400,2,960,649,260));assert.equal(r.results.find(x=>x.slot==='621:1').density,'DENSITY_SCREEN_PASS');assert.ok(r.results.find(x=>x.slot==='621:1').reasons.includes('historic_map_label_legibility_unverified'))});
test('missing guest evidence still HOLD',()=>{const r=assess(fresh());assert.equal(r.results[0].density,'NOT_MEASURED')});
const edits=[
 ['remove ledger schema',a=>delete a.schema,'invalid_ledger_shape'],
 ['extra tenth asset',a=>a.items.push(structuredClone(a.items[0])),'invalid_ledger_shape'],
 ['duplicate slot',a=>a.items[1].slot=a.items[0].slot,'slot_missing_duplicate_or_unrecognized'],
 ['wrong media',a=>a.items[0].media_id=999,'source_metadata_drift'],
 ['different size',a=>a.items[0].original_stored_bytes=2,'source_metadata_drift'],
 ['unsafe rewrite policy',a=>a.policy.wordpress_production_write=true,'unsafe_or_changed_policy'],
 ['uncleared download enabled',a=>a.policy.media_copy_authorized=true,'unsafe_or_changed_policy'],
 ['premature release enabled',a=>a.policy.release_authorized=true,'unsafe_or_changed_policy'],
 ['max width widened',a=>a.policy.max_width_px=1200,'unsafe_or_changed_policy'],
 ['upscaling allowed',a=>a.policy.no_upscale=false,'unsafe_or_changed_policy'],
 ['external source swapped',a=>a.items[0].stored_source_url='https://images.example.com/new.png','missing_or_changed_frozen_source_catalog'],
 ['catalog swapped',a=>a.items[0].catalog_url='https://images.example.com/other','missing_or_changed_frozen_source_catalog'],
 ['invalid source protocol',a=>a.items[0].stored_source_url='http://invalid.example.com/x','missing_or_changed_frozen_source_catalog'],
 ['wrong physical width',a=>a.items[0].native_width_px=1200,'source_metadata_drift'],
 ['960 cap violated',a=>a.items[0].candidate_width_px=961,'invalid_derivative_size_or_upscale'],
 ['upscale small museum original',a=>a.items[8].candidate_width_px=960,'invalid_derivative_size_or_upscale'],
 ['upscale in height',a=>a.items[8].candidate_height_px=900,'invalid_derivative_size_or_upscale'],
 ['crop drift',a=>a.items[0].candidate_height_px=600,'crop_or_ratio_not_reviewed'],
 ['fabricated guest status',a=>a.items[0].guest_http_status=200,'unsupported_existing_evidence_or_approval'],
 ['fabricated measured bytes',a=>a.items[0].guest_wire_bytes=10000,'unsupported_existing_evidence_or_approval'],
 ['fabricated cache',a=>a.items[0].cached_or_uploaded=true,'unsupported_existing_evidence_or_approval'],
 ['fabricated rights',a=>a.items[0].rights_to_rehost_verified=true,'unsupported_existing_evidence_or_approval'],
 ['fabricated historic scene',a=>a.items[0].historical_scene_identity='PROVEN_EXACT','invented_scene_identity'],
 ['fabricated hash',a=>a.items[0].binary_identity_verified=true,'unsupported_existing_evidence_or_approval']
];
for(const [name,edit,err] of edits)test(name,()=>check(edit,err));
for(const [name,mutate] of [
 ['guest response missing',o=>delete o['34:0'].candidate_http_status],
 ['guest unknown DPR',o=>delete o['34:0'].dpr],
 ['guest cached or unproven',o=>o['34:0'].cold_browser_verified=false],
 ['guest wrong dimension',o=>o['34:0'].candidate_natural_width_px=720],
 ['guest wrong URL scheme',o=>o['34:0'].candidate_current_src='javascript:bad'],
 ['guest missing identity',o=>o['34:0'].asset_identity_verified=false],
 ['guest missing decode',o=>o['34:0'].candidate_decoded=false],
 ['guest invalid fractional width',o=>o['34:0'].css_width_px=0],
 ['guest extreme DPR',o=>o['34:0'].dpr=5]
])test(name,()=>{const obs=observable();mutate(obs);const r=assess(fresh(),obs);assert.equal(r.state,'HOLD');assert.notEqual(r.results[0].density,'DENSITY_SCREEN_PASS')});
test('unknown observation cannot certify additional media',()=>{const o=observable();o['123:1']=o['34:0'];assert.ok(assess(fresh(),o).issues.includes('unknown_observation_slot'))});
