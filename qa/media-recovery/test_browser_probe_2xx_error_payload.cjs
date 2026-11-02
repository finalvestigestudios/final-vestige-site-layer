'use strict';
/** Read-only visitor-visual-integrity regression tests. Fixtures are synthetic, not live HTTP claims. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const stored='https://archive.example.gov/photograph.jpg';
function probe({mime='text/html',status=200,width=0,complete=true,pageVerified=true,currentSrc=stored,network=true}={}){
 const req=network?[{url:currentSrc,status,mime_type:mime,encodedDataLength:320}]:[];
 return classifyImages([{key:'789:0',source_url:stored,alt:'Historical image'}],
  [{src:stored,currentSrc,alt:'Historical image',complete,naturalWidth:width}],req,pageVerified)[0];
}
test('200 HTML error document AND a completed failed image decode is broken for visitor',()=>{
 const r=probe();
 assert.equal(r.result,'confirmed_broken_in_probe_browser');
 assert.equal(r.verified_broken_in_browser,true);
 assert.equal(r.http_status,200);
 assert.equal(r.response_mime_type,'text/html');
 assert.equal(r.visual_failure_kind,'non_image_error_payload');
});
test('200 JSON and XML error payloads with zero decoded width are also broken',()=>{
 for(const mime of ['application/json','application/xml','text/xml']){
  const r=probe({mime});assert.equal(r.verified_broken_in_browser,true,mime);
  assert.equal(r.visual_failure_kind,'non_image_error_payload',mime);
 }
});
test('Content-Type parameters are parsed safely, case-insensitively',()=>{
 const r=probe({mime:'Text/HTML; charset=utf-8'});
 assert.equal(r.response_mime_type,'text/html');
 assert.equal(r.visual_failure_kind,'non_image_error_payload');
});
test('missing network event never proves broken even if DOM width is zero',()=>{
 const r=probe({network:false});
 assert.equal(r.result,'zero_intrinsic_width_needs_review');
 assert.equal(r.verified_broken_in_browser,null);
});
test('200 image/jpeg with positive uncached bytes and zero decoded width is now a verified decode failure',()=>{
 const r=probe({mime:'image/jpeg'});
 assert.equal(r.result,'confirmed_broken_in_probe_browser');
 assert.equal(r.verified_broken_in_browser,true);
 assert.equal(r.visual_failure_kind,'image_decode_failure');
});
test('200 octet-stream body is not automatically called a broken image',()=>{
 const r=probe({mime:'application/octet-stream'});
 assert.equal(r.result,'zero_intrinsic_width_needs_review');
});
test('a 200 HTML-labelled image which did decode is not counted broken',()=>{
 const r=probe({width:640});
 assert.equal(r.result,'decoded_without_verified_response');
 assert.equal(r.verified_broken_in_browser,null);
 assert.equal(r.visual_failure_kind,null);
});
test('pending lazy image cannot be called broken',()=>{
 const r=probe({complete:false});
 assert.equal(r.verified_broken_in_browser,null);
});
test('blocked or unverified page cannot produce a browser-broken conclusion',()=>{
 const r=probe({pageVerified:false});
 assert.equal(r.result,'page_not_verified');
 assert.equal(r.verified_broken_in_browser,null);
});
test('unrelated decoded currentSrc blocks 200 HTML broken-image attribution',()=>{
 const r=probe({currentSrc:'https://archive.example.gov/other.jpg'});
 assert.equal(r.result,'current_src_identity_unverified');
 assert.equal(r.verified_broken_in_browser,null);
});
test('403 remains a normal HTTP failure, with explicit distinct failure kind',()=>{
 const r=probe({status:403});
 assert.equal(r.result,'confirmed_broken_in_probe_browser');
 assert.equal(r.visual_failure_kind,'http_error');
});
test('200 HTML error body is only a probe-browser observation, never rights clearance',()=>{
 const r=probe();
 assert.equal(r.verified_broken_in_browser,true);
 assert.equal('rights_cleared' in r,false);
 assert.equal('wordpress_upload_authorized' in r,false);
});
