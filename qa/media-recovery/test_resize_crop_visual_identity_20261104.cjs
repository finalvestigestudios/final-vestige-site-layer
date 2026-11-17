'use strict';
// Offline, synthetic CDP fixtures only. Preserve archived photo crops, don't claim a 404.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {sameSource,imageIdentity,classifyImages}=require('./browser_probe_core.cjs');
const townnews='https://bloximages.chicago2.vip.townnews.com/enidnews.com/content/tncms/assets/v3/editorial/b/4e/b4e59e84-74da-5f9e-b24f-5e9e3658fd34/54716e12ac97b.image.jpg';
const published=townnews+'?resize=1200%2C804';
const otherCrop=townnews+'?resize=960%2C640';
const fit=townnews+'?fit=960%2C640';
const stored=[{key:'283:3',source_url:published,alt:'Charred seating and stage area inside the Iroquois Theatre after the 1903 fire.'}];
const dom=(url,width=0)=>[{index:3,src:published,currentSrc:url,dataSrc:'',alt:stored[0].alt,complete:true,naturalWidth:width}];
const net=(url,status=404,width=0)=>[{request_id:'TEST-283-3',url,status,mime_type:'image/jpeg',encodedDataLength:width?10240:115}];
test('exact published 283:3 image URL remains self-identical',()=>assert.equal(sameSource(published,published),true));
test('original full image is NOT certified same historical composition as resize',()=>assert.equal(sameSource(townnews,published),false));
test('crop geometry change is NOT identity-equivalent',()=>assert.equal(sameSource(published,otherCrop),false));
test('untrusted TownNews numeric fit is not documented as WP size-only and fails closed',()=>assert.equal(sameSource(townnews,fit),false));
test('same exact resize through different Jetpack proxy host remains equal',()=>{
 const p='https://i0.wp.com/'+new URL(townnews).host+new URL(townnews).pathname+'?resize=1200%2C804&ssl=1';
 const q=p.replace('i0.wp.com','i1.wp.com');
 assert.equal(sameSource(p,q),true);
});
test('Jetpack resize of unresized original must not silently certify crop',()=>{
 const proxy='https://i0.wp.com/'+new URL(townnews).host+new URL(townnews).pathname+'?resize=960%2C640&ssl=1';
 assert.equal(sameSource(townnews,proxy),false);
});
test('published resize selector survives source identity computation',()=>assert.ok(imageIdentity(published).includes('resize=1200%2C804')));
test('synthetic 404 for a DIFFERENT responsive crop cannot confirm visitor 283:3 failure',()=>{
 const r=classifyImages(stored,dom(otherCrop),net(otherCrop),true)[0];
 assert.equal(r.current_src_identity_verified,false);
 assert.equal(r.verified_broken_in_browser,null);
});
test('synthetic exact-source 404 with complete zero-width DOM can be reported as failed',()=>{
 const r=classifyImages(stored,dom(published),net(published),true)[0];
 assert.equal(r.verified_broken_in_browser,true);
 assert.equal(r.visual_failure_kind,'http_error');
});
test('same exact source success and decoded pixels can be identified',()=>{
 const r=classifyImages(stored,dom(published,720),net(published,200,720),true)[0];
 assert.equal(r.result,'loaded_in_probe_browser');
 assert.equal(r.verified_broken_in_browser,false);
});
test('no CDP image request means 283:3 failure is unverified',()=>{
 const r=classifyImages(stored,dom(published),[],true)[0];
 assert.equal(r.verified_broken_in_browser,null);
});
test('unrelated final redirect does not certify source origin failure',()=>{
 const r=classifyImages(stored,dom(published),[{
  url:'https://cdn.other-example.org/unrelated.jpg',url_aliases:[published],status:404,
  encodedDataLength:100,mime_type:'image/jpeg'}],true)[0];
 assert.equal(r.verified_broken_in_browser,null);
 assert.equal(r.result,'redirected_image_identity_unverified');
});
