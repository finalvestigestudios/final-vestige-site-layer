'use strict';
const assert=require('node:assert/strict');
const {dimensionsAtMost,validate,reviewStage}=require('./verify_tmi_panel_source_20261111.cjs');
const r=require('./p0_285_2_tmi_feedwater_panel_source_20261111.json');
let count=0;function check(f){f();count++}
function edit(f){const x=JSON.parse(JSON.stringify(r));f(x);return x}
check(()=>assert.equal(validate(r).ok,true));
check(()=>assert.deepEqual(dimensionsAtMost([604,590],960),[604,590]));
check(()=>assert.deepEqual(dimensionsAtMost([1200,900],960),[960,720]));
check(()=>assert.deepEqual(dimensionsAtMost([600,1200],960),[600,1200]));
check(()=>assert.equal(dimensionsAtMost([0,1200],960),null));
check(()=>assert.equal(dimensionsAtMost([604.5,590],960),null));
check(()=>assert.equal(validate(edit(x=>x.post.published_src='https://example.org/image.jpg')).ok,false));
check(()=>assert.equal(validate(edit(x=>x.observations.guest_cdp.http_status=404)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.observations.guest_cdp.encoded_transfer_bytes=23000)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.observations.confirmed_guest_broken=true)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.observations.real_origin_http_status=500)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.provenance.ucs_figure='3')).ok,false));
check(()=>assert.equal(validate(edit(x=>x.provenance.printed_page=98)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.provenance.pdf_zero_index_page=28)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.provenance.strict_binary_identity_verified=true)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.candidates[2].retouched_revision=false)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.candidates[2].native_px=[960,938])).ok,false));
check(()=>assert.equal(validate(edit(x=>x.candidates[2].cache_authorized=true)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.candidates[2].pixel_identity_verified=true)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.size.conditional_output_px=[960,938])).ok,false));
check(()=>assert.equal(validate(edit(x=>x.editorial.distinct_failure_mechanisms=false)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.editorial.proposed_caption='A picture of the PORV light')).ok,false));
check(()=>assert.equal(validate(edit(x=>x.decision.allow_wordpress_post_edit=true)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.decision.allow_binary_download=true)).ok,false));
check(()=>assert.equal(validate(edit(x=>x.sitewide.measured_transfer_reduction_pct=76)).ok,false));
check(()=>assert.equal(reviewStage(r).decision,'HOLD_NO_PRODUCTION_WRITES'));
check(()=>{
 const e={completed_cold_image_request:true,http_status:200,cache:'EXPLICIT_UNCACHED',natural_width:604,natural_height:590,visual_same_photo_review:true,item_rights_clearance:true,editor_approval:true};
 assert.deepEqual(reviewStage(r,e),{decision:'HOLD_NO_PRODUCTION_WRITES',missing:[],ready_for_separate_staging_review:true});
});
check(()=>{
 const e={completed_cold_image_request:true,http_status:200,cache:'CACHED',natural_width:604,natural_height:590,visual_same_photo_review:true,item_rights_clearance:true,editor_approval:true};
 assert.equal(reviewStage(r,e).ready_for_separate_staging_review,false);
});
console.log('PASS '+count+'/'+count+' isolated checks');
