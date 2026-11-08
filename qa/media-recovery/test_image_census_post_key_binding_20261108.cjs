'use strict';
/** Offline post/slot identity regressions. No network, WordPress writes or image download. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {assessPage,assessRun}=require('./image_census_coverage_core.cjs');
const source='https://example.org/preserved-historical-image.jpg';
function image(image_key,broken=false){
 return {image_key,stored_url:source,current_src:source,request_url:source,
  current_src_identity_verified:true,network_final_identity_verified:true,
  redirected_image_identity_unverified:false,complete:true,
  result:broken?'confirmed_broken_in_probe_browser':'loaded_in_probe_browser',
  verified_broken_in_browser:broken,
  natural_width:broken?0:960,natural_height:broken?0:540,
  http_status:broken?404:200,visual_failure_kind:broken?'http_error':null,
  response_mime_type:'image/jpeg',transfer_bytes:800,loaded_network_proof_verified:true};
}
function page(post_id,images=[]){
 return {post_id,page_result:'inspected_browser',
  scroll_coverage:{complete:true,state:'full_height_scanned'},
  stored_image_count:images.length,stored_images:images};
}
test('correct image key belongs to its article and remains complete',()=>{
 const p=page(268,[image('268:0')]);
 assert.equal(assessPage(p).complete,true);
 assert.equal(assessRun([p],1).confirmed_broken_count,0);
});
test('a loaded image from article 268 cannot certify article 432',()=>{
 const p=page(432,[image('268:0')]);
 const v=assessPage(p),r=assessRun([p],1);
 assert.equal(v.complete,false);
 assert.ok(v.errors.includes('source_slot_post_mismatch'));
 assert.equal(r.confirmed_broken_count,null);
});
test('foreign-post 404 is a known observation but not confirmed article-wide breakage',()=>{
 const p=page(432,[image('268:0',true)]);
 const r=assessRun([p],1);
 assert.equal(r.complete,false);
 assert.equal(r.known_broken_count,1);
 assert.equal(r.confirmed_broken_count,null);
});
test('one foreign slot contaminates an otherwise valid article census',()=>{
 const p=page(285,[image('285:5'),image('418:2')]);
 assert.equal(assessPage(p).complete,false);
 assert.equal(assessRun([p],1).confirmed_broken_count,null);
});
test('two separate pages cannot exchange otherwise loaded proofs',()=>{
 const a=page(285,[image('418:2')]),b=page(418,[image('285:5')]);
 const r=assessRun([a,b],2);
 assert.equal(r.complete,false);
 assert.equal(r.confirmed_broken_count,null);
});
test('valid distinct article IDs do not require adjacent image ordinals',()=>{
 // P0 test fixtures can be source subsets; entire-corpus comparison is a separate gate.
 const a=page(285,[image('285:5'),image('285:2')]);
 assert.equal(assessRun([a],1).complete,true);
});
test('leading-zero post portion does not alias an authoritative post number',()=>{
 assert.equal(assessRun([page(285,[image('0285:5')])],1).complete,false);
});
test('similar numeric prefix of another article cannot match',()=>{
 assert.equal(assessRun([page(285,[image('2850:5')])],1).complete,false);
});
test('valid previously broken image stays countable when linked to correct post',()=>{
 const r=assessRun([page(418,[image('418:2',true)])],1);
 assert.equal(r.complete,true);
 assert.equal(r.confirmed_broken_count,1);
});
test('valid image-free published article stays in the complete census',()=>{
 const r=assessRun([page(1922,[])],1);
 assert.equal(r.complete,true);
 assert.equal(r.confirmed_broken_count,0);
});
test('unbound preliminary per-page evidence is permitted but final run requires ID',()=>{
 const p=page(432,[image('268:0')]);delete p.post_id;
 assert.equal(assessPage(p).complete,true);
 assert.equal(assessRun([p],1).complete,false);
});
test('changed article post ID cannot reuse a former post full-scroll image ledger',()=>{
 const p=page(285,[image('285:5')]);p.post_id=287;
 assert.equal(assessRun([p],1).complete,false);
});
