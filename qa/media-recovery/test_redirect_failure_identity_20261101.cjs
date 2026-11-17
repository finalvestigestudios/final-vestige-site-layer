'use strict';
/** Offline synthetic CDP/DOM regression: a redirect alias is not a final-image identity.
 * These URLs are test fixtures, NOT actual FinalVestige.com browser observations.
 * No network, downloads, CMS writes, production or image copying.
 */
const {test}=require('node:test'), assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const {proofKind,assessPage}=require('./image_census_coverage_core.cjs');
const original='https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg';
const unrelated='https://cdn.example.invalid/unrelated-candidate.jpg';
const stored=[{key:'418:2',source_url:original,alt:'Scotch Cap debris'}];
const rendered=[{index:2,src:original,currentSrc:original,alt:'Scotch Cap debris',complete:true,naturalWidth:0}];
const observed=n=>classifyImages(stored,rendered,[n],true)[0];
const page=v=>({post_id:418,page_result:'inspected_browser',scroll_coverage:{complete:true,state:'full_height_scanned'},stored_image_count:1,stored_images:[v]});

for(const [name,network] of [
 ['unrelated final URL 404',{url:unrelated,url_aliases:[original],status:404,mime_type:'text/html',encodedDataLength:0}],
 ['unrelated final URL 403',{url:unrelated,url_aliases:[original],status:403,mime_type:'text/html',encodedDataLength:0}],
 ['unrelated final URL 200 HTML',{url:unrelated,url_aliases:[original],status:200,mime_type:'text/html',encodedDataLength:1500}],
 ['unrelated final URL transport error',{url:unrelated,url_aliases:[original],failed_error:'net::ERR_CONNECTION_RESET',encodedDataLength:0}],
 ['same-origin different historical image 404',{url:'https://www.history.uscg.mil/Portals/6/different.jpg',url_aliases:[original],status:404,encodedDataLength:0}]
])test('redirect alias cannot inflate verified-broken count: '+name,()=>{
 const v=observed(network);
 assert.equal(v.network_final_identity_verified,false);
 assert.equal(v.redirected_image_identity_unverified,true);
 assert.equal(v.result,'redirected_image_identity_unverified');
 assert.equal(v.verified_broken_in_browser,null);
 assert.equal(v.visual_failure_kind,null);
 assert.equal(proofKind(v),'unresolved');
 assert.equal(assessPage(page(v)).confirmed_broken_count,null);
});

for(const [name,network,kind] of [
 ['direct 404',{url:original,status:404,mime_type:'text/html',encodedDataLength:0},'http_error'],
 ['direct 403',{url:original,status:403,mime_type:'text/html',encodedDataLength:0},'http_error'],
 ['direct network error',{url:original,failed_error:'net::ERR_CONNECTION_RESET'},'network_error'],
 ['direct 200 HTML error',{url:original,status:200,mime_type:'text/html',encodedDataLength:800},'non_image_error_payload'],
 ['direct 200 undecodable JPEG',{url:original,status:200,mime_type:'image/jpeg',encodedDataLength:900},'image_decode_failure']
])test('exact final identity retains real browser failure classification: '+name,()=>{
 const v=observed(network);
 assert.equal(v.network_final_identity_verified,true);
 assert.equal(v.result,'confirmed_broken_in_probe_browser');
 assert.equal(v.visual_failure_kind,kind);
 assert.equal(proofKind(v),'broken');
 assert.equal(assessPage(page(v)).confirmed_broken_count,1);
});

for(const [name,edit] of [
 ['wrong final request URL',v=>{v.request_url=unrelated;}],
 ['missing final identity flag',v=>{v.network_final_identity_verified=false;}],
 ['unverified redirect flag',v=>{v.redirected_image_identity_unverified=true;}],
 ['changed currentSrc',v=>{v.current_src=unrelated;}],
 ['missing request URL',v=>{v.request_url=null;}],
 ['source filename replaced',v=>{v.stored_url=unrelated;}]
])test('independent census rejects forged HTTP-404 evidence: '+name,()=>{
 const v=observed({url:original,status:404,mime_type:'text/html',encodedDataLength:0});
 edit(v);
 assert.equal(proofKind(v),'unresolved');
 assert.equal(assessPage(page(v)).confirmed_broken_count,null);
});

for(const [name,network] of [
 ['network failure',{url:original,failed_error:'net::ERR_CONNECTION_RESET'}],
 ['HTTP 200 HTML',{url:original,status:200,mime_type:'text/html',encodedDataLength:500}]
])test('census rejects altered final URL for '+name,()=>{
 const v=observed(network); v.request_url=unrelated; v.network_final_identity_verified=true;
 assert.equal(proofKind(v),'unresolved');
});

test('without an alias even an unrelated 404 has no stored-image network proof',()=>{
 const v=observed({url:unrelated,status:404,encodedDataLength:0});
 assert.equal(v.result,'zero_intrinsic_width_needs_review');
 assert.equal(proofKind(v),'unresolved');
});
test('offsite redirect ambiguity never establishes complete 61-post census from one image',()=>{
 const v=observed({url:unrelated,url_aliases:[original],status:404,encodedDataLength:0});
 assert.equal(assessPage(page(v)).complete,false);
});
