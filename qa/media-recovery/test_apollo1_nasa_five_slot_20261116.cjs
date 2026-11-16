'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {assess}=require('./assess_apollo1_nasa_five_slot_20261116.cjs');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'apollo1_nasa_five_slot_custody_20261116.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(baseline));
test('read-only NASA Apollo 1 source custody passes but remains HOLD',()=>{
 const r=assess(clone());assert.equal(r.ok,true,JSON.stringify(r.errors));assert.equal(r.decision,'HOLD_BROWSER_RIGHTS_FRAME');
});
const changes=[
['invent 404 guest status',x=>x.image_rows[0].guest_http_get_status=404],
['invent 200 original GET',x=>x.image_rows[1].original_http_get_status=200],
['invent 403 proxy GET',x=>x.image_rows[2].proxy_http_get_status=403],
['invent visitor currentSrc',x=>x.image_rows[3].guest_current_src=x.image_rows[3].rendered_view_src],
['invent decoded image',x=>x.image_rows[4].guest_image_decoded=true],
['invent transfer bytes',x=>x.image_rows[2].guest_transfer_bytes=15000],
['rewrite an upstream NASA asset URL',x=>x.image_rows[0].original_edit_src='https://example.com/file.jpg'],
['switch rendered proxy URL',x=>x.image_rows[4].rendered_view_src='https://example.com/test.jpg'],
['swap photo accession',x=>x.image_rows[2].accession='KSC-OTHER'],
['invent official catalog',x=>x.image_rows[1].agency_catalog_url='https://example.com'],
['claim reader 200',x=>x.image_rows[0].independent_original_reader='HTTP_200'],
['claim all readers rendered',x=>x.image_rows[1].independent_original_reader='IMAGE_RENDERED'],
['false cold browser claim',x=>x.browser_observation='COLD_CHROME'],
['invent 42 broken',x=>x.reported_broken_42_guest_confirmed=true],
['invent 76 percent savings',x=>x.claimed_76_percent_wire_savings_measured=true],
['mix stored with visitor bytes',x=>x.large_wp_originals.measured_wire_bytes=64385752],
['rewrite post revision',x=>x.post_modified='2026-11-16T08:27:00'],
['premature copyright clearance',x=>x.image_rows[3].item_rights='CLEARED'],
['premature identity proof',x=>x.image_rows[4].same_pixels_crop_verified=true],
['invent source binary checksum',x=>x.image_rows[1].source_binary_sha256='a'.repeat(64)],
['invent source native dimensions',x=>x.image_rows[0].source_binary_dimensions_px={width:960,height:640}],
['wrong Commons reported width',x=>x.image_rows[2].catalog_dimensions_px.width=960],
['upscale risky preview',x=>x.image_rows[3].upscaling_allowed=true],
['oversized derivative width',x=>x.image_rows[0].max_derivative_width_px=1920],
['wrong vertical 960 geometry',x=>x.image_rows[4].conditional_960px_geometry.height=960],
['claim cached in WordPress',x=>x.image_rows[1].wp_cached=true],
['authorize WordPress upload',x=>x.image_rows[4].wp_upload_authorized=true],
['claim media download',x=>x.downloads=1],
['claim production write',x=>x.production_writes=1],
['mutate support attribution',x=>x.image_rows[2].support_record_url='https://example.com'],
['drop image slot',x=>x.image_rows.pop()],
['edit historical census',x=>x.historical_census.images=361]
];
for(const [name,change]of changes)test('fail closed: '+name,()=>{const x=clone();change(x);const r=assess(x);assert.equal(r.ok,false,name);assert.ok(r.errors.length>0);});
