'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {compareColdPairVisualParity:verify}=require('./compare_cold_pair_visual_parity_20261111.cjs');
const {INVENTORY_BLOB}=require('./measure_image_transfer_pair_20261111.cjs');
const u='https://finalvestige.com/wp-content/uploads/2026/08/original.jpg';
const row=(bytes,id)=>({
 slot:'621:0',post_id:621,request_id:id,resource_type:'Image',
 current_src:u,request_url:u,final_response_url:u,response_mime_type:'image/jpeg',
 final_http_status:200,loading_finished:true,encoded_data_length:bytes,
 network_data_received_bytes:bytes*2,network_data_received_provenance:'CDP_NETWORK_DATA_RECEIVED',
 natural_width:960,natural_height:640,from_disk_cache:false,from_memory_cache:false,
 from_service_worker:false,image_identity:'museum-original',
 decoded_selected_physical_width:960,decoded_selected_physical_height:640,
 decoded_source_provenance:'BROWSER_DECODED_CURRENT_SRC',decoded_selected_resource_url:u,
 painted_css_width:390,painted_css_height:260,image_rendered_visible:true,
 object_fit:'cover',object_position:'50% 50%'
});
const cap=(id,bytes)=>({
 method:'CHROME_CDP_LOGGED_OUT_COLD',post_id:621,
 page_url:'https://finalvestige.com/2026/08/example/',page_http_status:200,
 full_scroll_complete:true,lazy_images_settled:true,network_capture_complete:true,
 cache_disabled:true,service_workers_bypassed:true,run_id:id,
 prose_fingerprint_sha256:'a'.repeat(64),viewport_width:390,viewport_height:844,
 dpr:2,images:[row(bytes,id)]
});
const fixture=()=>({
 schema:'fv-cold-transfer-pair-v1',source_ledger_blob_sha:INVENTORY_BLOB,
 post_id:621,expected_slots:['621:0'],before:cap('b',1000),after:cap('a',240)
});
function hold(edit,reason){
 const p=fixture();edit(p);const r=verify(p);
 assert.equal(r.status,'HOLD');assert.equal(r.reason,reason);
 assert.equal(r.sitewide_transfer_savings_verified,false);
}
test('matched CDP 76 percent is single-post only, never publication permission',()=>{
 const r=verify(fixture());assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR_WITH_VISUAL_PARITY');
 assert.equal(r.reduction_percent,76);assert.equal(r.measured_76_percent_with_visual_parity,true);
 assert.equal(r.production_change_allowed,false);assert.equal(r.sitewide_transfer_savings_verified,false);
});
test('missing baseline selected decode blocks',()=>hold(p=>delete p.before.images[0].decoded_selected_physical_width,'BASELINE_MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'));
test('missing candidate selected decode blocks',()=>hold(p=>delete p.after.images[0].decoded_selected_physical_width,'CANDIDATE_MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'));
test('DPR2 blur blocks even with synthetic 76 percent',()=>hold(p=>{
 const r=p.after.images[0];r.decoded_selected_physical_width=390;r.decoded_selected_physical_height=260;
 r.natural_width=390;r.natural_height=260;
},'CANDIDATE_LOW_DENSITY_OR_UPSCALED_SELECTED_IMAGE'));
test('untrusted physical provenance blocks',()=>hold(p=>p.after.images[0].decoded_source_provenance='GUESS','CANDIDATE_MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'));
test('different decoded source URL blocks',()=>hold(p=>p.after.images[0].decoded_selected_resource_url='https://example.org/other.jpg','CANDIDATE_MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'));
test('hidden image blocks',()=>hold(p=>p.after.images[0].image_rendered_visible=false,'CANDIDATE_MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'));
test('zero painted width blocks',()=>hold(p=>p.after.images[0].painted_css_width=0,'CANDIDATE_MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'));
test('aspect ratio mismatch blocks',()=>hold(p=>p.after.images[0].decoded_selected_physical_height=960,'CANDIDATE_SELECTED_SOURCE_AND_DOM_ASPECT_DISAGREE'));
test('shrunk image CSS box cannot fabricate saving',()=>hold(p=>p.after.images[0].painted_css_width=300,'IMAGE_PRESENTATION_OR_CROP_CHANGED'));
test('object-fit changed blocks',()=>hold(p=>p.after.images[0].object_fit='contain','IMAGE_PRESENTATION_OR_CROP_CHANGED'));
test('object-position focal shift blocks',()=>hold(p=>p.after.images[0].object_position='0% 0%','IMAGE_PRESENTATION_OR_CROP_CHANGED'));
function changed(p){
 const r=p.after.images[0],v='https://finalvestige.com/new.webp';
 r.current_src=r.request_url=r.final_response_url=r.decoded_selected_resource_url=v;
 r.response_mime_type='image/webp';r.rights_review_approved=true;
 r.visual_parity_approved=true;r.item_rights_evidence_url='https://archives.gov/item';
 return v;
}
test('self-reported DOM rights cannot authorize source substitution',()=>hold(p=>changed(p),'SOURCE_CHANGE_NEEDS_INDEPENDENT_SCENE_RIGHTS_EDITOR_REVIEW'));
test('incomplete independently reviewed replacement blocks',()=>hold(p=>{
 const v=changed(p);
 p.independent_replacement_review={'621:0':{
 original_src:u,candidate_src:v,pixel_scene_parity_verified:true,
 item_level_reuse_rights_verified:true,staging_editor_approved:false,
 provenance_evidence_url:'https://archives.gov/scene',
 rights_evidence_url:'https://archives.gov/rights'}};
},'SOURCE_CHANGE_NEEDS_INDEPENDENT_SCENE_RIGHTS_EDITOR_REVIEW'));
test('reviewed replacement can be measured without production authorization',()=>{
 const p=fixture(),v=changed(p);
 p.independent_replacement_review={'621:0':{
 original_src:u,candidate_src:v,pixel_scene_parity_verified:true,
 item_level_reuse_rights_verified:true,staging_editor_approved:true,
 provenance_evidence_url:'https://archives.gov/scene',
 rights_evidence_url:'https://archives.gov/rights'}};
 const r=verify(p);assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR_WITH_VISUAL_PARITY');
 assert.equal(r.production_change_allowed,false);
});
test('base 404 still blocks',()=>hold(p=>p.before.images[0].final_http_status=404,'BASE_TRANSFER_PAIR_BASELINE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('identical CDP run still blocks',()=>hold(p=>p.after.run_id='b','BASE_TRANSFER_PAIR_UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT'));
