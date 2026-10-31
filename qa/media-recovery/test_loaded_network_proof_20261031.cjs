'use strict';
/** Synthetic evidence gates only; no external media copying, WordPress writes or guest HTTP. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const {proofKind,assessPage}=require('./image_census_coverage_core.cjs');
const src='https://www.history.uscg.mil/Portals/6/photo.jpg';
function probe(o={}){
 const img={index:0,src,currentSrc:src,alt:'Archival photograph',
   complete:true,naturalWidth:o.width??960};
 const n=o.noRequest?[]:[{url:o.finalUrl||src,url_aliases:o.aliases||[],
   status:o.status??200,mime_type:o.mime??'image/jpeg',encodedDataLength:o.bytes??1000,
   failed_error:o.error||null,was_cached:o.cached||false,
   from_disk_cache:o.diskCache||false,from_service_worker:o.serviceWorker||false}];
 return classifyImages([{key:'268:0',source_url:src,alt:img.alt}],[img],n,o.pageVerified??true)[0];
}
function census(s){return assessPage({page_result:'inspected_browser',
 scroll_coverage:{complete:true,state:'full_height_scanned'},stored_image_count:1,stored_images:[s]})}
test('HTTP 200 image with real bytes and exact identity is loaded',()=>{
 const v=probe();assert.equal(v.result,'loaded_in_probe_browser');
 assert.equal(v.loaded_network_proof_verified,true);assert.equal(proofKind(v),'loaded');
 assert.equal(census(v).confirmed_broken_count,0);
});
for(const [name,settings] of [
 ['missing network row',{noRequest:true}],
 ['403 with decoded pixels',{status:403}],
 ['200 HTML with decoded fallback',{mime:'text/html'}],
 ['200 JSON with decoded fallback',{mime:'application/json'}],
 ['zero encoded bytes',{bytes:0}],
 ['failed response despite image MIME',{error:'net::ERR_ABORTED'}],
 ['served from disk cache',{diskCache:true}],
 ['served from service worker',{serviceWorker:true}]
]){
 test(name+' cannot be certified as a loaded historical image',()=>{
  const v=probe(settings);assert.equal(v.result,'decoded_without_verified_response');
  assert.equal(v.verified_broken_in_browser,null);
  assert.equal(proofKind(v),'unresolved');assert.equal(census(v).confirmed_broken_count,null);
 });
}
test('redirect to unrelated asset is not a verified loaded image',()=>{
 const v=probe({finalUrl:'https://other.example.org/wrong.jpg',aliases:[src]});
 assert.equal(v.result,'redirected_image_identity_unverified');
 assert.equal(proofKind(v),'unresolved');
});
test('genuine 404 with zero natural width remains a browser failure',()=>{
 const v=probe({status:404,width:0});
 assert.equal(v.result,'confirmed_broken_in_probe_browser');
 assert.equal(v.verified_broken_in_browser,true);
 assert.equal(proofKind(v),'broken');
});
test('200 HTML with zero natural width remains a browser failure',()=>{
 const v=probe({mime:'text/html',width:0});
 assert.equal(v.visual_failure_kind,'non_image_error_payload');
 assert.equal(v.verified_broken_in_browser,true);
});
for(const [name,mutate] of [
 ['forged loaded flag',v=>{delete v.loaded_network_proof_verified}],
 ['forged MIME',v=>{v.response_mime_type='text/html'}],
 ['forged zero bytes',v=>{v.transfer_bytes=0}],
 ['missing final network identity',v=>{delete v.network_final_identity_verified}]
]){
 test('independent census rejects '+name,()=>{
  const v=probe();mutate(v);assert.equal(proofKind(v),'unresolved');
 });
}
test('unverified page never certifies loaded visitor image',()=>{
 const v=probe({pageVerified:false});assert.equal(v.result,'page_not_verified');
 assert.equal(v.verified_broken_in_browser,null);
});
