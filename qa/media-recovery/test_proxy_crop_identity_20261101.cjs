'use strict';
/** Regression: URL-level source identity must not erase historical photo selectors or crops. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {imageIdentity,sameSource,classifyImages,matchStoredImages}=require('./browser_probe_core.cjs');
const plain='https://archive.example.org/photo.jpg';
const cropA='https://archive.example.org/photo.jpg?crop=0%2C0%2C400%2C300';
const cropB='https://archive.example.org/photo.jpg?crop=400%2C0%2C400%2C300';
const proxyA='https://i0.wp.com/archive.example.org/photo.jpg?crop=0%2C0%2C400%2C300&w=960&ssl=1';
const dynA='https://archive.example.org/gallery.php?image=NH43900';
const dynB='https://archive.example.org/gallery.php?image=NH98039';
const pdynA='https://i0.wp.com/archive.example.org/gallery.php?image=NH43900&ssl=1';
const pdynB='https://i1.wp.com/archive.example.org/gallery.php?image=NH98039&ssl=1';
const src=(u)=>[{key:'418:4',source_url:u,alt:'Specific archival image'}];
const dom=(u,decoded=0)=>[{src:u,currentSrc:u,dataSrc:'',alt:'Specific archival image',complete:true,naturalWidth:decoded}];

test('identical original URL is identical',()=>assert.ok(sameSource(plain,plain)));
test('static size/quality changes remain equivalent',()=>assert.ok(sameSource(plain,plain+'?w=960&q=80')));
test('Jetpack resize is crop-capable: do not equate its result with an uncropped original',()=>assert.equal(sameSource('https://finalvestige.com/wp-content/uploads/a.jpg','https://i0.wp.com/finalvestige.com/wp-content/uploads/a.jpg?resize=960%2C540&ssl=1'),false));
test('identical crop-capable resize through Jetpack variants remains identifiable',()=>assert.ok(sameSource('https://i0.wp.com/finalvestige.com/wp-content/uploads/a.jpg?resize=960%2C540&ssl=1','https://i1.wp.com/finalvestige.com/wp-content/uploads/a.jpg?resize=960%2C540&ssl=1')));
test('cross-proxy wrappers retain original static source identity',()=>assert.ok(sameSource('https://i0.wp.com/archive.example.org/photo.jpg?ssl=1','https://i1.wp.com/archive.example.org/photo.jpg?w=960&ssl=1')));
test('crop selectors distinguish two regions of one archival source',()=>assert.equal(sameSource(cropA,cropB),false));
test('a cropped photograph is not certified equivalent to the full image',()=>assert.equal(sameSource(plain,cropA),false));
test('same crop through Jetpack stays equivalent despite width transform',()=>assert.ok(sameSource(cropA,proxyA)));
test('Jetpack cropped photo is not automatically equivalent to uncropped master',()=>assert.equal(sameSource(plain,proxyA),false));
test('dynamic direct image IDs remain distinct',()=>assert.equal(sameSource(dynA,dynB),false));
test('dynamic image selector survives Jetpack unwrapping',()=>assert.ok(sameSource(dynA,pdynA)));
test('different dynamic selector values through Jetpack stay distinct',()=>assert.equal(sameSource(pdynA,pdynB),false));
test('selectors with similar filenames are still distinct',()=>assert.equal(sameSource('https://archive.example.org/view.php?id=1','https://archive.example.org/view.php?id=2'),false));
test('dynamic width may select content and remains distinct',()=>assert.equal(sameSource('https://archive.example.org/view.php?width=1','https://archive.example.org/view.php?width=2'),false));
test('known image-specific query selectors are not lost by Jetpack stripping SSL',()=>assert.ok(imageIdentity(pdynA).endsWith('?image=NH43900')));
test('mismatched historical image cannot create a false broken original',()=>{
 const out=classifyImages(src(pdynA),dom(pdynB),[{url:pdynB,status:404}],true)[0];
 assert.equal(out.verified_broken_in_browser,null);
 assert.equal(out.result,'alt_only_identity_unverified');
});
test('mismatched crop cannot create false original-image failure',()=>{
 const out=classifyImages(src(cropA),dom(cropB),[{url:cropB,status:404}],true)[0];
 assert.equal(out.verified_broken_in_browser,null);
 assert.equal(out.result,'alt_only_identity_unverified');
});
test('same dynamic selector genuinely returning 404 remains detectable',()=>{
 const out=classifyImages(src(pdynA),dom(pdynA),[{url:pdynA,status:404}],true)[0];
 assert.equal(out.verified_broken_in_browser,true);
 assert.equal(out.visual_failure_kind,'http_error');
});
test('same crop genuinely returning 200 decoded image stays visible',()=>{
 const out=classifyImages(src(cropA),dom(proxyA,700),[{url:proxyA,status:200,mime_type:'image/jpeg',encodedDataLength:25000}],true)[0];
 assert.equal(out.verified_broken_in_browser,false);
 assert.equal(out.result,'loaded_in_probe_browser');
});
test('two distinct archived image proxies do not collide under URL matching',()=>{
 const matched=matchStoredImages(src(pdynA),dom(pdynB));
 assert.equal(matched[0].match,'alt_only_unverified');
});
