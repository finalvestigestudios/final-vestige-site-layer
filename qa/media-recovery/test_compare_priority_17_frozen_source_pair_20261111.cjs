'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const audit=require('./priority_17_frozen_source_binding_20261111.json');
const {validateLedger,boundP0Evidence,comparePrioritySourceBoundVisualPair,BRIDGE_GIT_BLOB,
 PRIORITY_LEDGER_GIT_BLOB}=require('./compare_priority_17_frozen_source_pair_20261111.cjs');
const H='a'.repeat(64);
const get=slot=>audit.rows.find(x=>x.slot===slot);
function fixture(slot='621:0',beforeBytes=1000,afterBytes=200){
 const row=get(slot);
 const image=(run,bytes)=>({
  slot,post_id:row.post_id,request_id:'request-'+run,resource_type:'Image',
  stored_original_src:row.stored_original_src,dom_img_src:row.stored_original_src,
  dom_alt:row.frozen_alt,current_src:row.stored_original_src,
  request_url:row.stored_original_src,final_response_url:row.stored_original_src,
  response_mime_type:'image/jpeg',final_http_status:200,loading_finished:true,
  encoded_data_length:bytes,network_data_received_bytes:500,
  network_data_received_provenance:'CDP_NETWORK_DATA_RECEIVED',
  natural_width:960,natural_height:720,decoded_selected_physical_width:960,
  decoded_selected_physical_height:720,decoded_source_provenance:'BROWSER_DECODED_CURRENT_SRC',
  decoded_selected_resource_url:row.stored_original_src,
  painted_css_width:390,painted_css_height:260,
  image_rendered_visible:true,object_fit:'contain',object_position:'50% 50%',
  from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
  image_identity:'frozen-historical-scene-synthetic-test'});
 const capture=(run,bytes)=>({
  method:'CHROME_CDP_LOGGED_OUT_COLD',post_id:row.post_id,page_url:row.post_url,
  page_http_status:200,full_scroll_complete:true,lazy_images_settled:true,
  network_capture_complete:true,cache_disabled:true,service_workers_bypassed:true,
  run_id:run,prose_fingerprint_sha256:H,viewport_width:390,
  viewport_height:844,dpr:2,images:[image(run,bytes)]});
 return {schema:'fv-cold-transfer-pair-v1',source_ledger_blob_sha:BRIDGE_GIT_BLOB,
  post_id:row.post_id,expected_slots:[slot],before:capture('before',beforeBytes),
  after:capture('after',afterBytes)};
}
function hold(edit,reason){
 const pair=fixture();edit(pair);
 const o=comparePrioritySourceBoundVisualPair(pair);
 assert.equal(o.status,'HOLD');assert.equal(o.reason,reason);
 assert.equal(o.production_change_allowed,false);
 assert.equal(o.sitewide_transfer_savings_verified,false);
}
test('pinned 17-entry ledger has exact historical 61/355 and 6/11 cohorts',()=>{
 assert.equal(validateLedger(),true);
 assert.equal(audit.rows.length,17);
 assert.equal(audit.rows.filter(x=>x.priority==='P0_SUSPECTED_BROKEN').length,6);
 assert.equal(audit.rows.filter(x=>x.priority==='P1_GT_1_5MB_INLINE').length,11);
 assert.equal(audit.frozen_source.posts,61);assert.equal(audit.frozen_source.inline_images,355);
 assert.equal(audit.rows.filter(x=>x.media_id).reduce((a,x)=>a+x.stored_original_bytes,0),38480915);
});
test('ledger SHA and historical bridge SHA are explicit',()=>{
 assert.match(PRIORITY_LEDGER_GIT_BLOB,/^[a-f0-9]{40}$/);
 assert.equal(BRIDGE_GIT_BLOB,'d1a9c7a499510ec37bcdba5858d45165752587e0');
});
test('untampered 17-row audit validates, mutation of row counts fails',()=>{
 const copy=JSON.parse(JSON.stringify(audit));copy.rows.pop();assert.equal(validateLedger(copy),false);
});
test('mutated non-null visitor status cannot become a source fact',()=>{
 const copy=JSON.parse(JSON.stringify(audit));copy.rows[0].guest_http_status=404;
 assert.equal(validateLedger(copy),false);
});
test('mutated publication approval fails the frozen ledger',()=>{
 const copy=JSON.parse(JSON.stringify(audit));copy.rows[0].publication_approved=true;
 assert.equal(validateLedger(copy),false);
});
test('a native WordPress stored-size is not a guest image-network claim',()=>{
 const pair=fixture();const r=comparePrioritySourceBoundVisualPair(pair);
 assert.equal(r.status,'VERIFIED_PRIORITY_SUBSET_SOURCE_BOUND_VISUAL_PAIR');
 assert.equal(r.image_network_before_bytes,1000);assert.equal(r.image_network_after_bytes,200);
 assert.equal(r.reduction_percent,80);
 assert.equal(r.source_binding_verified,true);
 assert.equal(r.full_post_image_census_verified,false);
 assert.equal(r.sitewide_transfer_savings_verified,false);
 assert.equal(r.production_change_allowed,false);
});
test('a synthetic exact 76 percent is explicitly not sitewide',()=>{
 const r=comparePrioritySourceBoundVisualPair(fixture('621:0',1000,240));
 assert.equal(r.status,'VERIFIED_PRIORITY_SUBSET_SOURCE_BOUND_VISUAL_PAIR');
 assert.equal(r.reduction_percent,76);assert.equal(r.sitewide_transfer_savings_verified,false);
});
test('negative transfer delta is measured only as subset regression',()=>{
 const r=comparePrioritySourceBoundVisualPair(fixture('621:0',1000,1200));
 assert.equal(r.reduction_percent,-20);assert.equal(r.production_change_allowed,false);
});
test('cannot swap a frozen source with unrelated image in baseline',()=>
 hold(p=>p.before.images[0].stored_original_src='https://finalvestige.com/unrelated.jpg','FROZEN_STORED_URL_OR_ALT_MISMATCH'));
test('cannot swap a frozen source with unrelated image in candidate',()=>
 hold(p=>p.after.images[0].stored_original_src='https://finalvestige.com/unrelated.jpg','FROZEN_STORED_URL_OR_ALT_MISMATCH'));
test('DOM image source must match immutable frozen Gutenberg src',()=>
 hold(p=>p.before.images[0].dom_img_src='https://example.org/other.jpg','FROZEN_STORED_URL_OR_ALT_MISMATCH'));
test('must preserve frozen ALT and image subject semantics',()=>
 hold(p=>p.after.images[0].dom_alt='A different historical photograph','FROZEN_STORED_URL_OR_ALT_MISMATCH'));
test('missing baseline ALT fails closed',()=>
 hold(p=>delete p.before.images[0].dom_alt,'FROZEN_STORED_URL_OR_ALT_MISMATCH'));
test('matching URL on unrelated article cannot pass',()=>
 hold(p=>p.before.page_url='https://finalvestige.com/unrelated/','PINNED_POST_ID_OR_PERMALINK_MISMATCH'));
test('a different post ID with same image fails',()=>
 hold(p=>p.post_id=299,'PINNED_POST_ID_OR_PERMALINK_MISMATCH'));
test('P0 suspect item cannot pass a performance-only two-success run',()=>{
 const r=comparePrioritySourceBoundVisualPair(fixture('285:5'));
 assert.equal(r.reason,'P0_GUEST_BROKEN_TRIAGE_REQUIRED_BEFORE_PERFORMANCE');
});
test('out-of-target slot never counts toward 17 priority positions',()=>{
 const p=fixture();p.expected_slots=['621:2'];
 const r=comparePrioritySourceBoundVisualPair(p);
 assert.equal(r.reason,'SLOT_NOT_IN_17_PRIORITY_LEDGER');
});
test('invalid inventory blob does not justify a measurement',()=>
 hold(p=>p.source_ledger_blob_sha='f'.repeat(40),'PAIR_SCHEMA_OR_FROZEN_BRIDGE_MISMATCH'));
test('missing candidate image row cannot measure source-bound transfer',()=>
 hold(p=>p.after.images=[],'FROZEN_STORED_URL_OR_ALT_MISMATCH'));
test('duplicate expected slot cannot measure',()=>{
 const p=fixture();p.expected_slots.push('621:0');
 assert.equal(comparePrioritySourceBoundVisualPair(p).reason,'PAIR_SCHEMA_OR_FROZEN_BRIDGE_MISMATCH');
});
test('cache-hit CDP evidence cannot measure cold transfer',()=>
 hold(p=>p.after.images[0].from_memory_cache=true,'SECOND_STAGE_BASE_TRANSFER_PAIR_CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('actual 404 prevents an optimization success',()=>
 hold(p=>p.after.images[0].final_http_status=404,'SECOND_STAGE_BASE_TRANSFER_PAIR_CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('non-image MIME prevents an optimization success',()=>
 hold(p=>p.after.images[0].response_mime_type='text/html','SECOND_STAGE_BASE_TRANSFER_PAIR_CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('no CDP body proof prevents transfer claim',()=>
 hold(p=>p.after.images[0].network_data_received_bytes=0,'SECOND_STAGE_BASE_TRANSFER_PAIR_CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('2x display needs physical selected pixels',()=>
 hold(p=>p.after.images[0].decoded_selected_physical_width=390,'SECOND_STAGE_CANDIDATE_LOW_DENSITY_OR_UPSCALED_SELECTED_IMAGE'));
test('changed object crop cannot claim visual parity',()=>
 hold(p=>p.after.images[0].object_fit='cover','SECOND_STAGE_IMAGE_PRESENTATION_OR_CROP_CHANGED'));
test('new candidate URL without source/rights evidence remains HOLD',()=>{
 const p=fixture();const r=p.after.images[0];
 r.current_src=r.request_url=r.final_response_url=r.decoded_selected_resource_url='https://finalvestige.com/new.webp';
 assert.equal(comparePrioritySourceBoundVisualPair(p).status,'HOLD');
});
test('two independent frozen Malbone positions can pass a partial-post pair',()=>{
 const p=fixture(),a=get('621:1');p.expected_slots.push('621:1');
 for(const cap of [p.before,p.after]){
  const one=cap.images[0];
  cap.images.push({...one,slot:'621:1',stored_original_src:a.stored_original_src,
   dom_img_src:a.stored_original_src,dom_alt:a.frozen_alt,
   current_src:a.stored_original_src,request_url:a.stored_original_src,
   final_response_url:a.stored_original_src,decoded_selected_resource_url:a.stored_original_src,
   image_identity:'separate-historical-scene',request_id:one.request_id+'-other'});
 }
 const r=comparePrioritySourceBoundVisualPair(p);
 assert.equal(r.status,'VERIFIED_PRIORITY_SUBSET_SOURCE_BOUND_VISUAL_PAIR');
 assert.equal(r.matched_image_slots,2);assert.equal(r.full_post_image_census_verified,false);
});
test('Vasa Jetpack transformed source is bound exactly, not to the 8MB stored original',()=>{
 const row=get('299:1');assert.ok(row.stored_original_src.startsWith('https://i0.wp.com/'));
 assert.notEqual(row.stored_original_src,row.wordpress_original_url);
 const r=comparePrioritySourceBoundVisualPair(fixture('299:1'));
 assert.equal(r.status,'VERIFIED_PRIORITY_SUBSET_SOURCE_BOUND_VISUAL_PAIR');
 assert.equal(r.sitewide_transfer_savings_verified,false);
});
test('P0 source-only evidence returns NO browser broken claim even with correct URL',()=>{
 const row=get('287:5');
 const e={post_id:row.post_id,page_url:row.post_url,stored_inline_ordinal:5,
  stored_original_src:row.stored_original_src,dom_img_src:row.stored_original_src,dom_alt:row.frozen_alt};
 const r=boundP0Evidence('287:5',e);
 assert.equal(r.status,'SOURCE_BOUND_ONLY_SITE_QA_P0_ADJUDICATION_REQUIRED');
 assert.equal(r.observed_guest_http_status,null);assert.equal(r.confirmed_broken,false);
 assert.equal(r.source_retriever_wrapper_code,404);
});
test('all six P0 rows require source proof, no wrapper HTTP is guest HTTP',()=>{
 for(const row of audit.rows.filter(x=>x.priority==='P0_SUSPECTED_BROKEN')){
  const e={post_id:row.post_id,page_url:row.post_url,
   stored_inline_ordinal:Number(row.slot.split(':')[1]),
   stored_original_src:row.stored_original_src,dom_img_src:row.stored_original_src,dom_alt:row.frozen_alt};
  assert.equal(boundP0Evidence(row.slot,e).status,
   'SOURCE_BOUND_ONLY_SITE_QA_P0_ADJUDICATION_REQUIRED');
 }
});
test('P0 event from wrong article is not accepted',()=>{
 const r=get('285:5');
 const e={post_id:r.post_id,page_url:'https://finalvestige.com/other/',stored_inline_ordinal:5,
  stored_original_src:r.stored_original_src,dom_img_src:r.stored_original_src,dom_alt:r.frozen_alt};
 assert.equal(boundP0Evidence('285:5',e).reason,'P0_GUEST_SOURCE_NOT_PINNED');
});
test('P0 event from wrong DOM ordinal is not accepted',()=>{
 const r=get('285:5');
 const e={post_id:r.post_id,page_url:r.post_url,stored_inline_ordinal:2,
  stored_original_src:r.stored_original_src,dom_img_src:r.stored_original_src,dom_alt:r.frozen_alt};
 assert.equal(boundP0Evidence('285:5',e).reason,'P0_GUEST_SOURCE_NOT_PINNED');
});
test('P0 event with forged DOM original is rejected',()=>{
 const r=get('418:1');
 const e={post_id:r.post_id,page_url:r.post_url,stored_inline_ordinal:1,
  stored_original_src:r.stored_original_src,dom_img_src:'https://finalvestige.com/other.jpg'};
 assert.equal(boundP0Evidence('418:1',e).reason,'P0_GUEST_SOURCE_NOT_PINNED');
});
test('P0 frozen alternative text is mandatory',()=>{
 const row=get('287:5');const e={post_id:row.post_id,page_url:row.post_url,
  stored_inline_ordinal:5,stored_original_src:row.stored_original_src,
  dom_img_src:row.stored_original_src,dom_alt:'Other event'};
 assert.equal(boundP0Evidence('287:5',e).reason,'P0_GUEST_SOURCE_NOT_PINNED');
});
test('P1 source does not masquerade as P0 adjudication',()=>{
 assert.equal(boundP0Evidence('621:0',{}).reason,'NOT_A_PINNED_P0');
});
test('map original >1.5MB remains review-required with no 960px publication permission',()=>{
 const x=get('269:1');assert.equal(x.conditional_no_upscale_960px[0],960);
 assert.equal(x.publication_approved,false);assert.equal(x.candidate_rights_cleared,false);
});
