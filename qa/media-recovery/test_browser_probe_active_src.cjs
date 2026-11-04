'use strict';
/** Browser-decoded-currentSrc evidence gates. All fixtures are synthetic. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const stored=[{key:'900:0',source_url:'https://archive.example.gov/original.jpg',alt:'Historic original'}];
const rendered=(overrides={})=>[{
 src:stored[0].source_url,currentSrc:stored[0].source_url,dataSrc:'',
 alt:'Historic original',complete:true,naturalWidth:640,...overrides
}];
const net=(url,status=200,bytes=1000)=>[{url,status,mime_type:'image/jpeg',encodedDataLength:bytes}];
test('real decoded currentSrc is verified, with matching response',()=>{
 const d=classifyImages(stored,rendered(),net(stored[0].source_url),true)[0];
 assert.equal(d.result,'loaded_in_probe_browser');
 assert.equal(d.current_src_identity_verified,true);
 assert.equal(d.http_status,200);
});
test('srcset substitution: stored src matches but decoded currentSrc is different; do not certify original',()=>{
 const active='https://other.example.com/unrelated.jpg';
 const d=classifyImages(stored,rendered({currentSrc:active}),net(active),true)[0];
 assert.equal(d.result,'current_src_identity_unverified');
 assert.equal(d.current_src_identity_verified,false);
 assert.equal(d.verified_broken_in_browser,null);
 assert.equal(d.request_url,active);
});
test('missing currentSrc never proves stored image loaded, even when naturalWidth > 0',()=>{
 const d=classifyImages(stored,rendered({currentSrc:''}),net(stored[0].source_url),true)[0];
 assert.equal(d.result,'current_src_identity_unverified');
 assert.equal(d.http_status,null);
 assert.equal(d.verified_broken_in_browser,null);
});
test('lazy data-src match cannot certify an unrelated decoded image',()=>{
 const active='https://other.example.com/fallback.jpg';
 const d=classifyImages(stored,rendered({src:'',dataSrc:stored[0].source_url,currentSrc:active}),net(active),true)[0];
 assert.equal(d.result,'current_src_identity_unverified');
 assert.equal(d.verified_broken_in_browser,null);
});
test('stale original src failure cannot be attributed to successfully decoded active source',()=>{
 const active='https://other.example.com/fallback.jpg';
 const d=classifyImages(stored,rendered({currentSrc:active,naturalWidth:0}),
   [net(active,200)[0],net(stored[0].source_url,404)[0]],true)[0];
 assert.equal(d.result,'current_src_identity_unverified');
 assert.equal(d.http_status,200);
 assert.equal(d.verified_broken_in_browser,null);
});
test('active source failed response and zero intrinsic width confirms actual failure',()=>{
 const d=classifyImages(stored,rendered({naturalWidth:0}),net(stored[0].source_url,404,135),true)[0];
 assert.equal(d.result,'confirmed_broken_in_probe_browser');
 assert.equal(d.current_src_identity_verified,true);
 assert.equal(d.verified_broken_in_browser,true);
});
test('Commons canonical redirect and thumbnail currentSrc remain same file',()=>{
 const src='https://commons.wikimedia.org/wiki/Special:Redirect/file/Archive_photo.jpg?width=960';
 const active='https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Archive_photo.jpg/960px-Archive_photo.jpg';
 const d=classifyImages([{...stored[0],source_url:src}],rendered({src,currentSrc:active}),net(active),true)[0];
 assert.equal(d.result,'loaded_in_probe_browser');
 assert.equal(d.current_src_identity_verified,true);
});
test('crop-capable Jetpack resize is decoded but uncropped archival scene identity stays unverified',()=>{
 const active='https://i0.wp.com/archive.example.gov/original.jpg?resize=960%2C600';
 const d=classifyImages(stored,rendered({currentSrc:active}),net(active),true)[0];
 assert.equal(d.result,'current_src_identity_unverified');
 assert.equal(d.current_src_identity_verified,false);
 assert.equal(d.verified_broken_in_browser,null);
});
test('identity still requires matching DOM URL, not alternative text alone',()=>{
 const active='https://other.example.com/fake.jpg';
 const d=classifyImages(stored,rendered({src:active,currentSrc:active,dataSrc:''}),net(active,404),true)[0];
 assert.equal(d.result,'alt_only_identity_unverified');
 assert.equal(d.verified_broken_in_browser,null);
});
