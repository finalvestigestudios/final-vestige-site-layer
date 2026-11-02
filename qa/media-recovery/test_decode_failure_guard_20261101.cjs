'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const url='https://www.history.uscg.mil/Portals/6/scotch.jpg';
const stored=[{key:'418:1',source_url:url,alt:'Official Coast Guard image'}];
const rendered=[{index:0,src:url,currentSrc:url,alt:'Official Coast Guard image',complete:true,naturalWidth:0}];
const valid=[{url,status:200,mime_type:'image/jpeg',encodedDataLength:2048}];
const probe=(net=valid,dom=rendered,page=true)=>classifyImages(stored,dom,net,page)[0];
test('HTTP 200 plus image MIME and received bytes but zero decoded width is verified broken',()=>{
 const r=probe();assert.equal(r.result,'confirmed_broken_in_probe_browser');
 assert.equal(r.visual_failure_kind,'image_decode_failure');assert.equal(r.verified_broken_in_browser,true);
});
for(const [name,net]of [
 ['missing request',[]],['zero bytes',[{...valid[0],encodedDataLength:0}]],
 ['negative bytes',[{...valid[0],encodedDataLength:-1}]],
 ['missing bytes',[{...valid[0],encodedDataLength:null}]],
 ['cached response',[{...valid[0],was_cached:true}]],
 ['disk cached',[{...valid[0],from_disk_cache:true}]],
 ['service worker',[{...valid[0],from_service_worker:true}]],
 ['redirect to another identity',[{...valid[0],url:'https://example.org/other.jpg',url_aliases:[url]}]]
])test('fail closed without exact response evidence: '+name,()=>{
 assert.notEqual(probe(net).verified_broken_in_browser,true);
});
test('valid decoded 200 response remains loaded',()=>{
 const r=probe(valid,[{...rendered[0],naturalWidth:800}]);
 assert.equal(r.result,'loaded_in_probe_browser');assert.equal(r.verified_broken_in_browser,false);
});
test('non-image HTML 200 still classified as non-image error payload',()=>{
 assert.equal(probe([{...valid[0],mime_type:'text/html'}]).visual_failure_kind,'non_image_error_payload');
});
test('real 404 still classified as HTTP error',()=>{
 assert.equal(probe([{...valid[0],status:404}]).visual_failure_kind,'http_error');
});
test('unverified page cannot claim a guest image failure',()=>{
 assert.equal(probe(valid,rendered,false).verified_broken_in_browser,null);
});
test('different DOM source cannot claim this historical photograph',()=>{
 const r=probe(valid,[{...rendered[0],src:'https://example.org/else.jpg',currentSrc:'https://example.org/else.jpg'}]);
 assert.equal(r.verified_broken_in_browser,null);
});
