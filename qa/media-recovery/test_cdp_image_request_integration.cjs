'use strict';
/** Offline end-to-end resource-type regressions. Synthetic network events, not live HTTP. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const {selectCdpImageRequests}=require('./cdp_image_request_scope.cjs');
const url='https://archive.example.gov/ship.jpg';
const stored=[{key:'999:0',source_url:url,alt:'Historic ship'}];
const dom=(width=960)=>[{index:0,src:url,currentSrc:url,alt:'Historic ship',complete:true,naturalWidth:width}];
const request=(type,status=200,mime='image/jpeg')=>({type,url,status,mime_type:mime,encodedDataLength:300});
const classify=(requests,width=960)=>classifyImages(stored,dom(width),selectCdpImageRequests(requests),true)[0];
test('only Fetch with image MIME cannot certify displayed archival image',()=>{
 const r=classify([request('Fetch')]);
 assert.equal(r.result,'decoded_without_verified_response');assert.equal(r.verified_broken_in_browser,null);
});
test('XHR 200 cannot conceal a failed CDP Image 403 when pixels do not decode',()=>{
 const r=classify([request('Image',403),request('XHR',200)],0);
 assert.equal(r.result,'confirmed_broken_in_probe_browser');
 assert.equal(r.http_status,403);assert.equal(r.visual_failure_kind,'http_error');
});
test('Fetch 200 cannot convert contradictory Image 403 into a verified loaded photograph',()=>{
 const r=classify([request('Image',403),request('Fetch',200)],960);
 assert.equal(r.result,'decoded_without_verified_response');
 assert.equal(r.verified_broken_in_browser,null);
});
test('successful Image 200 remains loaded even when a later Fetch shares its URL',()=>{
 const r=classify([request('Image'),request('Fetch')]);
 assert.equal(r.result,'loaded_in_probe_browser');
 assert.equal(r.verified_broken_in_browser,false);
});
test('only non-Image 404 with zero-width DOM cannot fabricate a broken image',()=>{
 const r=classify([request('Document',404)],0);
 assert.equal(r.result,'zero_intrinsic_width_needs_review');
 assert.equal(r.verified_broken_in_browser,null);
});
test('genuine Image 200 HTML error is still a visible media failure',()=>{
 const r=classify([request('Image',200,'text/html'),request('Fetch',200)],0);
 assert.equal(r.result,'confirmed_broken_in_probe_browser');
 assert.equal(r.visual_failure_kind,'non_image_error_payload');
});
