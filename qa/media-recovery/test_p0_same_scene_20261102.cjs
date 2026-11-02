'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_p0_same_scene_20261102.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_same_scene_2010_tmi_hebgen_20261102.json'),'utf8'));
const sample=()=>JSON.parse(JSON.stringify(source));
test('verified primary records remain read-only with guest HTTP unknown',()=>assert.deepEqual(validate(sample()),{ok:true,verified_records:2,browser_verified_failures:0,publication_authorized:false}));
const bad=[
 ['forged 42 browser failures',x=>{x.baseline.reported_broken_42_browser_verified=true}],
 ['forged 76 percent savings',x=>{x.baseline.claimed_76_percent_wire_reduction_measured=true}],
 ['fabricated production repair',x=>{x.baseline.production_repairs=1}],
 ['wrong published TMI source',x=>{x.entries[0].published_url+='?moved'}],
 ['pretend retriever 404 is Chrome',x=>{x.entries[0].retriever.visitor_http_status=404}],
 ['pretend Hebgen is guest HTTP 200',x=>{x.entries[1].retriever.visitor_http_status=200}],
 ['invent guest image decode',x=>{x.entries[1].retriever.visitor_natural_width=1000}],
 ['invent transfer bytes',x=>{x.entries[0].retriever.visitor_transfer_bytes=235000}],
 ['TMI binary equivalence invented',x=>{x.entries[0].source_chain.same_bytes_verified=true}],
 ['TMI unrelated original photo',x=>{x.entries[0].source_chain.original_creator_file='https://example.com/other.jpg'}],
 ['1979 miscaption',x=>{x.entries[0].rights.not_a_1979_accident_photograph=false}],
 ['TMI photo date invented',x=>{x.entries[0].rights.exact_master_photo_date='2010-06-06'}],
 ['TMI upscaled',x=>{x.entries[0].geometry.conditional_derived_width_px=960}],
 ['Hebgen incorrect original',x=>{x.entries[1].source_chain.catalog_original_link+='?different'}],
 ['Hebgen wrong original geometry',x=>{x.entries[1].geometry.viewer_rendered_height_px=713}],
 ['Hebgen wrong resize geometry',x=>{x.entries[1].geometry.conditional_derived_height_px=684}],
 ['Hebgen incorrect photographer',x=>{x.entries[1].rights.creator_credit='Unknown'}],
 ['false rights clearance',x=>{x.entries[0].rights.item_rights_cleared_for_wordpress_upload=true}],
 ['production WordPress edit',x=>{x.entries[1].wordpress_post_edit_authorized=true}],
 ['production image upload',x=>{x.entries[1].wordpress_media_upload_authorized=true}],
 ['media downloaded',x=>{x.common_controls.no_binary_downloads=false}],
 ['reordered slots',x=>{x.entries.reverse()}],
 ['invented no-upscale exception',x=>{x.entries[1].geometry.no_upscale=false}],
 ['fabricated source rights conclusion',x=>{x.entries[0].rights.publisher_processed_derivative_rights_assumed=true}]
];
for(const [name,fn] of bad)test('fail-closed: '+name,()=>{const x=sample();fn(x);assert.throws(()=>validate(x),/RECOVERY_EVIDENCE_REJECTED/)});
