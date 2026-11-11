'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {evaluatePair,INVENTORY_BLOB}=require('./measure_image_transfer_pair_20261111.cjs');
const H='a'.repeat(64);
function fixture() {
  const row=(bytes,id='r1',src='https://finalvestige.com/image.jpg')=>({
    slot:'621:0', post_id:621,request_id:id,resource_type:'Image',
    current_src:src,request_url:src,final_response_url:src,
    response_mime_type:'image/jpeg',final_http_status:200,loading_finished:true,
    encoded_data_length:bytes,natural_width:960,natural_height:640,
    from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
    image_identity:'malbone-verified-original'});
  const cap=(run,bytes)=>({method:'CHROME_CDP_LOGGED_OUT_COLD',
    post_id:621,page_url:'https://finalvestige.com/2026/08/example/',
    page_http_status:200,full_scroll_complete:true,lazy_images_settled:true,
    network_capture_complete:true,cache_disabled:true,service_workers_bypassed:true,
    run_id:run,prose_fingerprint_sha256:H,viewport_width:390,
    viewport_height:844,dpr:2,images:[row(bytes,run)]});
  return {schema:'fv-cold-transfer-pair-v1',source_ledger_blob_sha:INVENTORY_BLOB,
    post_id:621,expected_slots:['621:0'],before:cap('b',1000),after:cap('a',200)};
}
const hold=(edit,expected)=>{const p=fixture();edit(p);
 assert.equal(evaluatePair(p).status,'HOLD');assert.equal(evaluatePair(p).reason,expected)};
test('positive matched cold pair is only a post-level measurement',()=>{
 const r=evaluatePair(fixture());assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(r.reduction_percent,80);assert.equal(r.sitewide_transfer_savings_verified,false);
 assert.equal(r.production_change_allowed,false);
});
test('exact 76 percent meets target but never claims sitewide',()=>{
 const p=fixture();p.after.images[0].encoded_data_length=240;
 const r=evaluatePair(p);assert.equal(r.reduction_percent,76);
 assert.equal(r.target_76_percent_met,true);assert.equal(r.sitewide_transfer_savings_verified,false);
});
test('increased network bytes is reported as negative savings',()=>{
 const p=fixture();p.after.images[0].encoded_data_length=1200;
 assert.equal(evaluatePair(p).reduction_percent,-20);
});
test('frozen ledger must match pinned blob',()=>hold(p=>p.source_ledger_blob_sha=H,'INVALID_OR_UNBOUND_FROZEN_COHORT'));
test('0 bytes cannot claim savings',()=>hold(p=>p.after.images[0].encoded_data_length=0,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('cached bytes cannot claim savings',()=>hold(p=>p.after.images[0].from_memory_cache=true,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('HTML 200 cannot claim savings',()=>hold(p=>p.after.images[0].response_mime_type='text/html','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('a 404 cannot masquerade as compression savings',()=>hold(p=>p.after.images[0].final_http_status=404,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('missing natural pixels invalid',()=>hold(p=>p.before.images[0].natural_width=0,'BASELINE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('incomplete lazy scroll invalid',()=>hold(p=>p.before.full_scroll_complete=false,'BASELINE_INCOMPLETE_COLD_CAPTURE'));
test('mismatched device invalid',()=>hold(p=>p.after.dpr=1,'UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT'));
test('mismatched article content invalid',()=>hold(p=>p.after.prose_fingerprint_sha256='b'.repeat(64),'UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT'));
test('mismatched visual identity invalid',()=>hold(p=>p.after.images[0].image_identity='different','PHOTOGRAPH_IDENTITY_CHANGED'));
test('asset changed without rights and framing invalid',()=>hold(p=>{const i=p.after.images[0];i.current_src=i.request_url=i.final_response_url='https://finalvestige.com/new.webp';},'CHANGED_ASSET_WITHOUT_RIGHTS_AND_VISUAL_GATE'));
test('candidate asset rights and framing can be measured, never published',()=>{
 const p=fixture(),i=p.after.images[0];
 i.current_src=i.request_url=i.final_response_url='https://finalvestige.com/new.webp';
 i.response_mime_type='image/webp';i.rights_review_approved=true;
 i.visual_parity_approved=true;i.item_rights_evidence_url='https://archives.gov/item';
 assert.equal(evaluatePair(p).status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(evaluatePair(p).production_change_allowed,false);
});
test('different or missing slot coverage is not comparable',()=>hold(p=>p.after.images=[],'CANDIDATE_INCOMPLETE_IMAGE_SLOT_COVERAGE'));
test('duplicate expected slot is invalid',()=>hold(p=>p.expected_slots.push('621:0'),'INVALID_OR_UNBOUND_FROZEN_COHORT'));
test('same CDP run is invalid',()=>hold(p=>p.after.run_id='b','UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT'));
test('non-image resource is invalid',()=>hold(p=>p.after.images[0].resource_type='Document','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('redirect response mismatch is on hold pending lineage',()=>hold(p=>p.after.images[0].final_response_url='https://example.org/image.jpg','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));

const TETON='https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG';
function sharedTetonPair() {
 const p=fixture();p.post_id=291;p.expected_slots=['291:2','291:5'];
 for(const cap of [p.before,p.after]){
  cap.post_id=291;cap.page_url='https://finalvestige.com/2026/08/19/one-bulldozer-never-came-back-teton-dam/';
  const r=cap.images[0];r.post_id=291;r.slot='291:2';r.current_src=r.request_url=r.final_response_url=TETON;
  cap.images.push({...r,slot:'291:5'});
 }
 return p;
}
test('Teton 291:2 and 291:5 share one completed request and count bytes only once',()=>{
 const r=evaluatePair(sharedTetonPair());
 assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(r.matched_image_slots,2);
 assert.equal(r.unique_completed_requests_before,1);
 assert.equal(r.unique_completed_requests_after,1);
 assert.equal(r.shared_request_slots_before,1);
 assert.equal(r.image_network_before_bytes,1000);
 assert.equal(r.image_network_after_bytes,200);
 assert.equal(r.reduction_percent,80);
});
test('two truly separate completed requests count as two wire transfers',()=>{
 const p=sharedTetonPair();p.before.images[1].request_id='other-before';p.after.images[1].request_id='other-after';
 const r=evaluatePair(p);
 assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(r.unique_completed_requests_before,2);
 assert.equal(r.image_network_before_bytes,2000);
 assert.equal(r.image_network_after_bytes,400);
});
for(const [what,edit] of [
 ['byte length',r=>r.encoded_data_length++],
 ['request URL',r=>r.request_url=r.current_src=r.final_response_url='https://example.net/different.jpg'],
 ['MIME type',r=>r.response_mime_type='image/png'],
 ['decoded width',r=>r.natural_width++],
 ['decoded height',r=>r.natural_height++],
 ['visual identity',r=>r.image_identity='different-photo'],
 ['HTTP status',r=>r.final_http_status=201],
 ['cache state',r=>r.from_memory_cache=true]
]) test('conflicting shared CDP request '+what+' cannot be counted',()=>{
 const p=sharedTetonPair();edit(p.before.images[1]);
 const r=evaluatePair(p);
 assert.equal(r.status,'HOLD');
 assert.ok(['BASELINE_CONFLICTING_SHARED_IMAGE_REQUEST','BASELINE_MISSING_OR_INVALID_IMAGE_REQUEST'].includes(r.reason));
});
test('one omitted DOM slot is incomplete image coverage',()=>{
 const p=sharedTetonPair();p.after.images.pop();
 assert.equal(evaluatePair(p).reason,'CANDIDATE_INCOMPLETE_IMAGE_SLOT_COVERAGE');
});
test('mixed shared and separate request evidence uses distinct request bytes per run',()=>{
 const p=sharedTetonPair();p.after.images[1].request_id='independent-after';
 const r=evaluatePair(p);
 assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(r.image_network_before_bytes,1000);
 assert.equal(r.image_network_after_bytes,400);
 assert.equal(r.reduction_percent,60);
});
