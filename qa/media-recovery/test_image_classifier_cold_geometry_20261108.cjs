'use strict';
/** Strict uncached/geometry regression: synthetic inputs only, no web/WP operations. */
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {classifyImages,scopeArticleImageWire}=require('./browser_probe_core.cjs');
const url='https://www.history.uscg.mil/Portals/6/example.jpg';
const stored=[{key:'418:2',source_url:url,alt:'Scotch Cap archive'}];
const dom=(w=0,h=0)=>[{src:url,currentSrc:url,alt:'Scotch Cap archive',complete:true,naturalWidth:w,naturalHeight:h}];
const req=(over={})=>[{url,status:404,mime_type:'text/html',encodedDataLength:100,was_cached:false,from_disk_cache:false,from_service_worker:false,...over}];
const classify=(w,h,over={},page=true)=>classifyImages(stored,dom(w,h),req(over),page)[0];
const broken=(w,h,over={})=>classify(w,h,over);
const healthy=(w=960,h=540,over={})=>classify(w,h,{status:200,mime_type:'image/jpeg',...over});
const expectState=(name,get,expected)=>test(name,()=>{const r=get();assert.equal(r.result,expected);assert.equal(r.verified_broken_in_browser,expected==='confirmed_broken_in_probe_browser'?true:expected==='loaded_in_probe_browser'?false:null)});
expectState('uncached 404 zero x zero remains provable',()=>broken(0,0),'confirmed_broken_in_probe_browser');
expectState('cached 404 is not a fresh-source failure',()=>broken(0,0,{was_cached:true}),'zero_intrinsic_width_needs_review');
expectState('service worker 404 cannot certify origin failure',()=>broken(0,0,{from_service_worker:true}),'zero_intrinsic_width_needs_review');
expectState('disk cached 404 cannot certify origin failure',()=>broken(0,0,{from_disk_cache:true}),'zero_intrinsic_width_needs_review');
expectState('missing was_cached cannot certify failure',()=>broken(0,0,{was_cached:undefined}),'zero_intrinsic_width_needs_review');
expectState('missing from_disk_cache cannot certify failure',()=>broken(0,0,{from_disk_cache:undefined}),'zero_intrinsic_width_needs_review');
expectState('missing from_service_worker cannot certify failure',()=>broken(0,0,{from_service_worker:undefined}),'zero_intrinsic_width_needs_review');
expectState('0 x 480 cannot certify 404 broken',()=>broken(0,480),'zero_intrinsic_width_needs_review');
expectState('0 x 0 legitimate uncached image decode failure',()=>classify(0,0,{status:200,mime_type:'image/jpeg',encodedDataLength:350}),'confirmed_broken_in_probe_browser');
expectState('0 x 0 cached decode error is not fresh origin proof',()=>classify(0,0,{status:200,mime_type:'image/jpeg',was_cached:true}),'zero_intrinsic_width_needs_review');
expectState('failed uncached network with zero pixels is distinguishable',()=>broken(0,0,{status:null,mime_type:null,failed_error:'net::ERR_CONNECTION_RESET'}),'confirmed_broken_in_probe_browser');
expectState('cached network-error evidence cannot certify broken',()=>broken(0,0,{status:null,failed_error:'net::ERR_CONNECTION_RESET',was_cached:true}),'zero_intrinsic_width_needs_review');
expectState('uncached 200 with positive dimensions remains loaded',()=>healthy(),'loaded_in_probe_browser');
expectState('200 loaded with zero intrinsic height must be unresolved',()=>healthy(960,0),'decoded_without_verified_response');
expectState('200 loaded with unknown cache state must be unresolved',()=>healthy(960,540,{was_cached:undefined}),'decoded_without_verified_response');
expectState('200 loaded via service worker must be unresolved',()=>healthy(960,540,{from_service_worker:true}),'decoded_without_verified_response');
expectState('200 loaded with missing disk-cache field is unresolved',()=>healthy(960,540,{from_disk_cache:undefined}),'decoded_without_verified_response');
test('even a complete image requires a verified page',()=>{const r=classify(960,540,{status:200,mime_type:'image/jpeg'},false);assert.equal(r.result,'page_not_verified')});
function wire(flags){const s=healthy();return scopeArticleImageWire([s],[{url,status:200,mime_type:'image/jpeg',encoded_data_length:340,...flags}])}
test('article bytes measured only for explicitly cold complete CDP flags',()=>{
 const r=wire({was_cached:false,from_disk_cache:false,from_service_worker:false});
 assert.equal(r.article_bytes,340);assert.equal(r.unmeasured_article_requests,0);
});
test('article byte calculation rejects missing cache-state fields',()=>{
 const r=wire({was_cached:false,from_disk_cache:false});
 assert.equal(r.article_bytes,null);assert.equal(r.unmeasured_article_requests,1);
});
test('article byte calculation rejects disk-cache proof even with encoded bytes',()=>{
 const r=wire({was_cached:false,from_disk_cache:true,from_service_worker:false});
 assert.equal(r.article_bytes,null);assert.equal(r.unmeasured_article_requests,1);
});
