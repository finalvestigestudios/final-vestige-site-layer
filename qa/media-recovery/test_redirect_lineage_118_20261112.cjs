'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {evaluatePair,INVENTORY_BLOB}=require('./measure_image_transfer_pair_20261111.cjs');
const audit=require('./redirect_lineage_118_source_audit_20261112.json');
const S='https://commons.wikimedia.org/wiki/Special:Redirect/file/St.%20Francis%20abutment.jpg?width=1280';
const D='https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/St._Francis_abutment.jpg/960px-St._Francis_abutment.jpg';
function pair(){
 const img=(run,bytes)=>({slot:'166:2',post_id:166,request_id:run,resource_type:'Image',
  current_src:S,request_url:S,final_response_url:D,
  redirect_chain:[{request_id:run,from_url:S,response_url:S,to_url:D,http_status:302,
   provenance:'CDP_NETWORK_REQUEST_WILL_BE_SENT_REDIRECT_RESPONSE'}],
  response_mime_type:'image/jpeg',final_http_status:200,loading_finished:true,
  encoded_data_length:bytes,network_data_received_bytes:bytes,
  network_data_received_provenance:'CDP_NETWORK_DATA_RECEIVED',
  natural_width:960,natural_height:553,
  from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
  image_identity:'frozen-scene-st-francis'});
 const cap=(run,bytes)=>({method:'CHROME_CDP_LOGGED_OUT_COLD',post_id:166,
  page_url:'https://finalvestige.com/2026/08/18/they-checked-the-dam-that-morning/',
  page_http_status:200,full_scroll_complete:true,lazy_images_settled:true,
  network_capture_complete:true,cache_disabled:true,service_workers_bypassed:true,
  run_id:run,prose_fingerprint_sha256:'f'.repeat(64),
  viewport_width:390,viewport_height:844,dpr:2,images:[img(run,bytes)]});
 return {schema:'fv-cold-transfer-pair-v1',source_ledger_blob_sha:INVENTORY_BLOB,
  post_id:166,expected_slots:['166:2'],before:cap('run-b',1000),after:cap('run-a',240)};
}
const hold=(fn,expected)=>{const p=pair();fn(p);const r=evaluatePair(p);
 assert.equal(r.status,'HOLD');assert.equal(r.reason,expected);
 assert.equal(r.target_76_percent_met,null);};
test('synthetic complete CDP redirect lineage permits a per-post pair, not a sitewide claim',()=>{
 const r=evaluatePair(pair());assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(r.reduction_percent,76);assert.equal(r.redirected_unique_requests_before,1);
 assert.equal(r.redirected_unique_requests_after,1);assert.equal(r.recorded_redirect_hops_before,1);
 assert.equal(r.sitewide_transfer_savings_verified,false);
 assert.equal(r.production_change_allowed,false);});
test('missing redirect hop',()=>hold(p=>delete p.before.images[0].redirect_chain,'BASELINE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('untrusted redirect provenance',()=>hold(p=>p.after.images[0].redirect_chain[0].provenance='WEB_RETRIEVER','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('missing hop requestId',()=>hold(p=>delete p.after.images[0].redirect_chain[0].request_id,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('mismatched hop URL',()=>hold(p=>p.after.images[0].redirect_chain[0].from_url='https://example.org/a','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('mismatched redirectResponse URL',()=>hold(p=>p.after.images[0].redirect_chain[0].response_url='https://example.org/a','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('mismatched final URL',()=>hold(p=>p.after.images[0].redirect_chain[0].to_url='https://example.org/b','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('fake 200 redirect hop',()=>hold(p=>p.after.images[0].redirect_chain[0].http_status=200,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('unsafe http downgrade',()=>hold(p=>p.after.images[0].redirect_chain[0].to_url=p.after.images[0].final_response_url='http://example.org/a.jpg','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('credentials in target',()=>hold(p=>p.after.images[0].redirect_chain[0].to_url=p.after.images[0].final_response_url='https://u:p@example.org/a.jpg','CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('redirect chain over max',()=>hold(p=>p.after.images[0].redirect_chain=Array(6).fill(p.after.images[0].redirect_chain[0]),'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('cache used',()=>hold(p=>p.after.images[0].from_disk_cache=true,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('partial 206 final',()=>hold(p=>p.after.images[0].final_http_status=206,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('zero received image bytes',()=>hold(p=>p.after.images[0].network_data_received_bytes=0,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('photo identity mismatch',()=>hold(p=>p.after.images[0].image_identity='different','PHOTOGRAPH_IDENTITY_CHANGED'));
test('same direct source without redirect remains supported',()=>{
 const p=pair();for(const c of [p.before,p.after]){const x=c.images[0];
 x.current_src=x.request_url=x.final_response_url=D;delete x.redirect_chain;}
 const r=evaluatePair(p);assert.equal(r.status,'VERIFIED_SINGLE_POST_COLD_PAIR');
 assert.equal(r.redirected_unique_requests_before,0);});
test('direct URL with fraudulent redirect hop stays HOLD',()=>hold(p=>p.after.images[0].final_response_url=S,'CANDIDATE_MISSING_OR_INVALID_IMAGE_REQUEST'));
test('shared request with contradictory linked redirects is rejected',()=>{
 const p=pair();p.expected_slots=['166:2','166:3'];
 for(const c of [p.before,p.after]){
  const x=c.images[0];c.images.push({...x,slot:'166:3',
   redirect_chain:[{...x.redirect_chain[0],http_status:307}]});}
 assert.equal(evaluatePair(p).reason,'BASELINE_CONFLICTING_SHARED_IMAGE_REQUEST');
});
test('frozen 118 URLs are exact addresses, NOT browser-status or rights assertions',()=>{
 assert.equal(audit.summary.stored_redirect_endpoint_positions,118);
 assert.equal(audit.entries.length,118);
 assert.equal(new Set(audit.entries.map(x=>x.slot)).size,118);
 assert.equal(new Set(audit.entries.map(x=>x.post_id)).size,20);
 for(const x of audit.entries){
  assert.ok(x.exact_stored_src.includes('/wiki/Special:Redirect/file/'));
  assert.equal(x.guest_http_status,null);assert.equal(x.guest_redirect_chain,null);
  assert.equal(x.guest_wire_bytes,null);assert.equal(x.rights_cleared,false);
  assert.equal(x.wordpress_upload_approved,false);
  if(x.conditional_960_dimensions)assert.ok(x.conditional_960_dimensions[0]<=960);
 }
});