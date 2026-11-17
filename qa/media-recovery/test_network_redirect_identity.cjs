'use strict';
/** Synthetic CDP redirect-chain regressions. No image downloads or CMS writes. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const {assessPage,proofKind}=require('./image_census_coverage_core.cjs');
const original='https://archive.example.gov/photos/photo-A.jpg';
const source=(u=original)=>[{key:'268:0',source_url:u,alt:'Photo A'}];
const dom=(u=original,width=960)=>[{index:0,src:u,currentSrc:u,alt:'Photo A',complete:true,naturalWidth:width}];
const response=(url,aliases=[],status=200,mime_type='image/jpeg')=>[{url,url_aliases:aliases,status,mime_type,encodedDataLength:2500}];
const classify=(u,final,aliases=[],status=200,width=960,mime='image/jpeg')=>
 classifyImages(source(u),dom(u,width),response(final,aliases,status,mime),true)[0];
test('direct response retains proven source identity',()=>{
 const s=classify(original,original);assert.equal(s.result,'loaded_in_probe_browser');
 assert.equal(s.network_final_identity_verified,true);
});
test('HTTP 200 redirect to a different image cannot certify the historical original',()=>{
 const s=classify(original,'https://cdn.example.gov/other-photo.jpg',[original]);
 assert.equal(s.result,'redirected_image_identity_unverified');
 assert.equal(s.verified_broken_in_browser,null);
 assert.equal(s.network_final_identity_verified,false);
 assert.equal(s.redirected_image_identity_unverified,true);
 assert.equal(s.request_url,'https://cdn.example.gov/other-photo.jpg');
});
test('full image census with a redirected substitute must not claim zero broken',()=>{
 const s=classify(original,'https://cdn.example.gov/other-photo.jpg',[original]);
 const p=assessPage({post_id:268,page_result:'inspected_browser',
  scroll_coverage:{complete:true,state:'full_height_scanned'},
  stored_image_count:1,stored_images:[s]});
 assert.equal(p.complete,false);assert.equal(p.confirmed_broken_count,null);
});
test('same filename on unrelated host is not proven identical',()=>{
 const s=classify(original,'https://other.example.gov/photos/photo-A.jpg',[original]);
 assert.equal(s.result,'redirected_image_identity_unverified');
});
test('same-host different filename after redirect is unverified',()=>{
 const s=classify(original,'https://archive.example.gov/photos/photo-B.jpg',[original]);
 assert.equal(s.verified_broken_in_browser,null);
});
test('HTTP 404 after cross-host redirect is not proof of the archived image identity',()=>{
 const s=classify(original,'https://cdn.example.gov/error.jpg',[original],404,0);
 assert.equal(s.result,'redirected_image_identity_unverified');
 assert.equal(s.verified_broken_in_browser,null);
});
test('cross-host HTML redirect without final source identity stays unverified',()=>{
 const s=classify(original,'https://cdn.example.gov/login',[original],200,0,'text/html');
 assert.equal(s.result,'redirected_image_identity_unverified');
 assert.equal(s.verified_broken_in_browser,null);
});
test('Commons canonical redirect to matching hashed upload is verified',()=>{
 const u='https://commons.wikimedia.org/wiki/Special:Redirect/file/Archimedes_Palimpsest.jpg?width=960';
 const final='https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Archimedes_Palimpsest.jpg/960px-Archimedes_Palimpsest.jpg';
 const s=classify(u,final,[u]);assert.equal(s.result,'loaded_in_probe_browser');
 assert.equal(s.network_final_identity_verified,true);
});
test('Navy dynamic endpoint must preserve image selector through redirect',()=>{
 const u='https://www.history.navy.mil/bin/imageDownload?image=80-G-276907&rendition=small';
 const final='https://www.history.navy.mil/bin/imageDownload?image=80-G-276940&rendition=small';
 const s=classify(u,final,[u]);assert.equal(s.result,'redirected_image_identity_unverified');
});
test('Navy dynamic endpoint may change rendition of the SAME image',()=>{
 const u='https://www.history.navy.mil/bin/imageDownload?image=80-G-276907&rendition=small';
 const final='https://www.history.navy.mil/bin/imageDownload?image=80-G-276907&rendition=large';
 const s=classify(u,final,[u]);assert.equal(s.result,'loaded_in_probe_browser');
});
test('Jetpack resize may crop: final transformed request does not certify full photo',()=>{
 const u='https://archive.example.gov/photos/photo-A.jpg';
 const final='https://i0.wp.com/archive.example.gov/photos/photo-A.jpg?resize=960%2C640';
 const s=classify(u,final,[u]);assert.equal(s.result,'redirected_image_identity_unverified');
 assert.equal(s.verified_broken_in_browser,null);
});
test('an unrelated decoded currentSrc is never verified by a stale source URL alias',()=>{
 const substitute='https://cdn.example.gov/photo-B.jpg';
 const s=classifyImages(source(),[{...dom()[0],currentSrc:substitute}],
  response(substitute,[original]),true)[0];
 assert.equal(s.result,'current_src_identity_unverified');
 assert.equal(s.verified_broken_in_browser,null);
});
test('independent census rejects forged loaded status after mismatched final HTTP URL',()=>{
 const s=classify(original,'https://cdn.example.gov/other-photo.jpg',[original]);
 s.result='loaded_in_probe_browser';s.verified_broken_in_browser=false;
 assert.equal(proofKind(s),'unresolved');
});
test('independent census rejects a fabricated original even if identity flag is true',()=>{
 const s=classify(original,original);s.stored_url='https://other.example.gov/fake-original.jpg';
 s.current_src_identity_verified=true;
 assert.equal(proofKind(s),'unresolved');
});
test('independent census rejects a changed final URL even without the new guard field',()=>{
 const s=classify(original,original);
 s.request_url='https://cdn.example.gov/unrelated.jpg';
 delete s.network_final_identity_verified;delete s.redirected_image_identity_unverified;
 assert.equal(proofKind(s),'unresolved');
});
