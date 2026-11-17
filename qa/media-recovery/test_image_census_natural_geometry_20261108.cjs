'use strict';
/** Offline census geometry regression; no HTTP, CDP, downloads or CMS writes. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {proofKind,assessPage,assessRun}=require('./image_census_coverage_core.cjs');
const url='https://example.org/archive-picture.jpg';
const base={image_key:'285:5',stored_url:url,current_src:url,request_url:url,
  current_src_identity_verified:true,complete:true,network_final_identity_verified:true,
  redirected_image_identity_unverified:false,response_mime_type:'image/jpeg',transfer_bytes:700};
const loaded=()=>({...base,result:'loaded_in_probe_browser',verified_broken_in_browser:false,
 natural_width:960,natural_height:540,http_status:200,loaded_network_proof_verified:true});
const broken=()=>({...base,result:'confirmed_broken_in_probe_browser',verified_broken_in_browser:true,
 natural_width:0,natural_height:0,http_status:404,visual_failure_kind:'http_error'});
const page=(v)=>({post_id:285,page_result:'inspected_browser',
 scroll_coverage:{complete:true,state:'full_height_scanned'},stored_image_count:v?1:0,
 stored_images:v?[v]:[]});
test('valid decoded 960x540 image remains loaded',()=>{
 assert.equal(proofKind(loaded()),'loaded');assert.equal(assessPage(page(loaded())).complete,true);
});
test('valid cold 404 with 0x0 decoded geometry remains broken',()=>{
 assert.equal(proofKind(broken()),'broken');assert.equal(assessPage(page(broken())).confirmed_broken_count,1);
});
for(const invalid of [0,-1,1.5,null,undefined,'540',NaN,Infinity]) {
 test('loaded image with invalid intrinsic height '+String(invalid)+' is unresolved',()=>{
  const s=loaded();s.natural_height=invalid;
  assert.equal(proofKind(s),'unresolved');
  const p=assessPage(page(s));
  assert.equal(p.complete,false);assert.equal(p.confirmed_broken_count,null);
 });
}
for(const invalid of [1,480,null,undefined,-1,'0',NaN,Infinity]) {
 test('broken image with invalid/nonzero intrinsic height '+String(invalid)+' is unresolved',()=>{
  const s=broken();s.natural_height=invalid;
  assert.equal(proofKind(s),'unresolved');
  assert.equal(assessPage(page(s)).complete,false);
 });
}
test('unresolved loaded geometry fails site-wide census even when other pages are sound',()=>{
 const p=page(loaded());p.stored_images[0].natural_height=0;
 const p2=page(broken());p2.post_id=287;p2.stored_images[0].image_key='287:5';
 const out=assessRun([p,p2],2);
 assert.equal(out.complete,false);assert.equal(out.confirmed_broken_count,null);
});
test('unresolved broken geometry fails site-wide census even when other pages are sound',()=>{
 const p=page(broken());p.stored_images[0].natural_height=480;
 const p2=page(loaded());p2.post_id=287;p2.stored_images[0].image_key='287:5';
 const out=assessRun([p,p2],2);
 assert.equal(out.complete,false);assert.equal(out.confirmed_broken_count,null);
});
test('valid page with no inline images remains complete',()=>{
 const p=page(null);p.post_id=1922;
 assert.equal(assessPage(p).complete,true);
 const out=assessRun([p],1);assert.equal(out.complete,true);
 assert.equal(out.confirmed_broken_count,0);
});
test('fully populated, consistent run remains complete',()=>{
 const p=page(loaded());
 const p2=page(broken());p2.post_id=287;p2.stored_images[0].image_key='287:5';
 const out=assessRun([p,p2],2);
 assert.equal(out.complete,true);assert.equal(out.confirmed_broken_count,1);
});
