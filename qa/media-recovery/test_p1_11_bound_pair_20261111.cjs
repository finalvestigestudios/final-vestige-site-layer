'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {evaluatePinnedPair,PINS,EXPOSURE_BLOB,P0_FIRST}=require('./verify_p1_11_bound_pair_20261111.cjs');
const {evaluatePair,INVENTORY_BLOB}=require('./measure_image_transfer_pair_20261111.cjs');
const hash='a'.repeat(64);
function fixture(post=621,before=1000,after=240){
 const rows=PINS.filter(p=>p.post_id===post);
 const capture=(run,bytes)=>({
   method:'CHROME_CDP_LOGGED_OUT_COLD',post_id:post,page_url:rows[0].page,
   page_http_status:200,full_scroll_complete:true,lazy_images_settled:true,
   network_capture_complete:true,cache_disabled:true,service_workers_bypassed:true,
   run_id:run,prose_fingerprint_sha256:hash,viewport_width:390,viewport_height:844,
   dpr:2,images:rows.map((p,index)=>({
     slot:p.slot,post_id:post,request_id:run+'-'+index,resource_type:'Image',
     current_src:p.src,request_url:p.src,final_response_url:p.src,
     response_mime_type:'image/'+(p.src.includes('.png')?'png':'jpeg'),
     final_http_status:200,loading_finished:true,encoded_data_length:bytes,
     natural_width:960,natural_height:Math.round(960*p.native_height/p.native_width),from_disk_cache:false,
     from_memory_cache:false,from_service_worker:false,
     image_identity:'wp-media:'+p.media_id}))
 });
 return {schema:'fv-cold-transfer-pair-v1',source_ledger_blob_sha:INVENTORY_BLOB,
   oversize_exposure_blob_sha:EXPOSURE_BLOB,post_id:post,
   expected_slots:rows.map(p=>p.slot),before:capture('b',before),after:capture('a',after)};
}
function held(change,reason){const f=fixture();change(f);
 const o=evaluatePinnedPair(f);assert.equal(o.status,'HOLD');
 assert.equal(o.reason,reason);assert.equal(o.production_change_allowed,false);
 assert.equal(o.sitewide_transfer_savings_verified,false);
 assert.equal(o.full_article_transfer_verified,false);}
test('frozen registry contains 11 distinct slots, 8 posts, precise 38,480,915 B storage',()=>{
 assert.equal(PINS.length,11);assert.equal(new Set(PINS.map(x=>x.slot)).size,11);
 assert.equal(new Set(PINS.map(x=>x.post_id)).size,8);
 assert.equal(PINS.reduce((a,x)=>a+x.stored_bytes,0),38480915);
 assert.equal(P0_FIRST,true);
});
test('two Malbone original slots must both be measured, not just one',()=>{
 assert.deepEqual(PINS.filter(x=>x.post_id===621).map(x=>x.slot),['621:0','621:1']);
});
test('Vasa has 3 pinned Jetpack transformed slots, not direct original transfers',()=>{
 const s=PINS.filter(x=>x.post_id===299);
 assert.deepEqual(s.map(x=>x.slot),['299:0','299:1','299:7']);
 assert.ok(s.every(x=>x.src.startsWith('https://i0.wp.com/')));
});
test('valid cold pair produces only scoped 76 percent, not article/sitewide saving',()=>{
 const r=evaluatePinnedPair(fixture());
 assert.equal(r.status,'VERIFIED_PINNED_OVERSIZE_SLOTS_COLD_PAIR');
 assert.equal(r.reduction_percent,76);assert.equal(r.pinned_oversize_slot_pair_verified,true);
 assert.equal(r.full_article_transfer_verified,false);
 assert.equal(r.sitewide_transfer_savings_verified,false);
 assert.equal(r.production_change_allowed,false);
 assert.equal(r.pinned_oversize_source_stored_bytes,10352064);
});
test('eight post cohorts independently accept fully scoped synthetic cold pairs',()=>{
 for(const post of new Set(PINS.map(x=>x.post_id))){
   const r=evaluatePinnedPair(fixture(post));
   assert.equal(r.status,'VERIFIED_PINNED_OVERSIZE_SLOTS_COLD_PAIR');
   assert.equal(r.pinned_oversize_slots.length,PINS.filter(x=>x.post_id===post).length);
 }
});
test('counterexample: generic comparator incorrectly accepts unrelated matching cold image as 76 percent',()=>{
 const f=fixture();
 for(const phase of ['before','after']){
   for(const x of f[phase].images){
     x.current_src=x.request_url=x.final_response_url='https://other.example/unrelated.jpg';
   }
 }
 assert.equal(evaluatePair(f).status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(evaluatePinnedPair(f).reason,'UNREVIEWED_SOURCE_OR_DELIVERY_URL_CHANGE');
});
test('counterexample: partial Vasa pair was accepted by generic comparator but is now held',()=>{
 const f=fixture(299);f.expected_slots=['299:0'];
 f.before.images=f.before.images.filter(x=>x.slot==='299:0');
 f.after.images=f.after.images.filter(x=>x.slot==='299:0');
 assert.equal(evaluatePair(f).status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(evaluatePinnedPair(f).reason,'PARTIAL_OR_FOREIGN_OVERSIZE_SLOT_COHORT');
});
test('counterexample: self-asserted rights and visual approval do not validate changed photo',()=>{
 const f=fixture();let x=f.after.images[0];
 x.current_src=x.request_url=x.final_response_url='https://finalvestige.com/new-960.webp';
 x.response_mime_type='image/webp';
 x.rights_review_approved=x.visual_parity_approved=true;
 x.item_rights_evidence_url='https://www.archives.gov/item';
 assert.equal(evaluatePair(f).status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(evaluatePinnedPair(f).reason,'UNREVIEWED_SOURCE_OR_DELIVERY_URL_CHANGE');
});
test('unknown cohort is rejected',()=>held(f=>{f.post_id=777;},'POST_NOT_IN_REVIEWED_OVERSIZE_COHORT'));
test('missing or wrong provenance rejected',()=>held(f=>{delete f.oversize_exposure_blob_sha},'FROZEN_SOURCE_PROVENANCE_NOT_BOUND'));
test('changed provenance rejected',()=>held(f=>{f.oversize_exposure_blob_sha=hash},'FROZEN_SOURCE_PROVENANCE_NOT_BOUND'));
test('source ledger mismatch rejected',()=>held(f=>{f.source_ledger_blob_sha=hash},'FROZEN_SOURCE_PROVENANCE_NOT_BOUND'));
test('missing source slot rejected',()=>held(f=>f.expected_slots.pop(),'PARTIAL_OR_FOREIGN_OVERSIZE_SLOT_COHORT'));
test('foreign source slot rejected',()=>held(f=>f.expected_slots.push('621:4'),'PARTIAL_OR_FOREIGN_OVERSIZE_SLOT_COHORT'));
test('only one baseline photo rejected',()=>held(f=>f.before.images.pop(),'PARTIAL_OR_FOREIGN_CAPTURE_IMAGE_SLOTS'));
test('only one candidate photo rejected',()=>held(f=>f.after.images.pop(),'PARTIAL_OR_FOREIGN_CAPTURE_IMAGE_SLOTS'));
test('different post permalink rejected',()=>held(f=>f.before.page_url='https://finalvestige.com/','PUBLISHED_ARTICLE_URL_OR_CAPTURE_MISMATCH'));
test('same URL on a different page rejected',()=>held(f=>f.after.page_url='https://finalvestige.com/','PUBLISHED_ARTICLE_URL_OR_CAPTURE_MISMATCH'));
test('wrong media identity rejected',()=>held(f=>f.before.images[0].image_identity='wp-media:9999','UNBOUND_MEDIA_IDENTITY'));
test('changed raw CDN responsive currentSrc held',()=>held(f=>f.before.images[0].current_src='https://i0.wp.com/other.jpg','UNREVIEWED_SOURCE_OR_DELIVERY_URL_CHANGE'));
test('candidate HTTP 404 rejected by CDP core',()=>held(f=>f.after.images[0].final_http_status=404,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('HTML response rejected by CDP core',()=>held(f=>f.after.images[0].response_mime_type='text/html','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('cached response rejected by CDP core',()=>held(f=>f.after.images[0].from_disk_cache=true,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('zero transferred bytes rejected',()=>held(f=>f.after.images[0].encoded_data_length=0,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('incomplete lazy scroll rejected',()=>held(f=>f.after.lazy_images_settled=false,'CANDIDATE_INCOMPLETE_COLD_CAPTURE'));
test('changed historical article prose rejected',()=>held(f=>f.after.prose_fingerprint_sha256='b'.repeat(64),'UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT'));
test('different DPR rejected',()=>held(f=>f.after.dpr=1,'UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT'));
test('no actual guest captures in source audit',()=>{
 const a={"stats":{"original_store_over_1500000_bytes_count":15,"original_store_total_bytes":47096779,"pinned_inline_exposures":11,"pinned_post_count":8,"pinned_inline_original_stored_bytes":38480915,"historical_external_positions_researched":288,"reported_broken_42_browser_confirmed":false,"purported_76_percent_sitewide_wire_saving_measured":false,"actual_guest_statuses_observed":0,"actual_network_byte_measurements":0,"rights_or_derivatives_approved":0,"production_images_repaired":0}};
 assert.equal(a.stats.actual_guest_statuses_observed,0);
 assert.equal(a.stats.actual_network_byte_measurements,0);
 assert.equal(a.stats.purported_76_percent_sitewide_wire_saving_measured,false);
 assert.equal(a.stats.reported_broken_42_browser_confirmed,false);
});
test('exported source pins are immutable under adversarial mutation',()=>{
 assert.ok(Object.isFrozen(PINS));assert.ok(PINS.every(x=>Object.isFrozen(x)));
 const original=PINS[0].src;
 assert.throws(()=>{PINS[0].src='https://other.example/unrelated.jpg';},TypeError);
 assert.equal(PINS[0].src,original);
});

test('frozen native geometry pinned to all 11 WordPress original media records',()=>{
 const wh=new Map([[39,[1672,941]],[40,[1672,941]],[41,[1672,941]],[42,[1672,941]],
 [43,[1672,941]],[1714,[1280,1280]],[389,[2147,1417]],[388,[4256,2832]],
 [382,[1800,1200]],[1257,[4000,3000]],[1258,[5667,3831]]]);
 for(const p of PINS)assert.deepEqual([p.native_width,p.native_height],wh.get(p.media_id));
});
test('synthetic 76 percent Malbone with 16:9 pixels but 4:3 original is held',()=>
 held(f=>{for(const phase of ['before','after'])for(const x of f[phase].images){
   x.natural_width=960;x.natural_height=540;
 }},'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL'));
test('identical 1x1 tracker pixels cannot masquerade as original photo',()=>
 held(f=>{for(const phase of ['before','after'])for(const x of f[phase].images){
   x.natural_width=1;x.natural_height=1;
 }},'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL'));
test('identical 32x24 low-resolution placeholders are held',()=>
 held(f=>{for(const phase of ['before','after'])for(const x of f[phase].images){
   x.natural_width=32;x.natural_height=24;
 }},'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL'));
test('single tiny candidate is not a network optimization',()=>
 held(f=>{f.after.images[0].natural_width=1;f.after.images[0].natural_height=1;},
 'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL'));
test('candidate changes aspect ratio to 16:9 without approved crop',()=>
 held(f=>{f.after.images[0].natural_height=540;},
 'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL'));
test('same URL downsampled candidate on same device is not apples-to-apples',()=>
 held(f=>{f.after.images[0].natural_width=480;
 f.after.images[0].natural_height=Math.round(480*3000/4000);},
 'UNMATCHED_SAME_SOURCE_IMAGE_DIMENSIONS'));
test('Malbone second image rotated to portrait is held',()=>
 held(f=>{f.after.images[1].natural_width=649;f.after.images[1].natural_height=960;},
 'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL'));
test('single Vasa image changed shape holds its three-image cohort',()=>{
 const f=fixture(299);f.after.images[2].natural_height=400;
 const r=evaluatePinnedPair(f);assert.equal(r.status,'HOLD');
 assert.equal(r.reason,'IMAGE_GEOMETRY_INCONSISTENT_WITH_FROZEN_ORIGINAL');
});
test('all eight real article cohorts accept matching synthetic native ratios',()=>{
 for(const post of new Set(PINS.map(p=>p.post_id)))
   assert.equal(evaluatePinnedPair(fixture(post)).status,'VERIFIED_PINNED_OVERSIZE_SLOTS_COLD_PAIR');
});
