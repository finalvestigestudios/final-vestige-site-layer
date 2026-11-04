'use strict';
// Synthetic identity/negative-status fixtures only; no network, media or CMS writes.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {sameSource,imageIdentity,classifyImages}=require('./browser_probe_core.cjs');
const base='https://images.example.org/archive/station.jpg';
const fitCrop=base+'?fit=crop&w=960&h=640';
const fitCropTall=base+'?fit=crop&w=640&h=960';
const fitSmart=base+'?fit=smart-crop&w=960&h=640';
const fitFace=base+'?fit=facearea&w=960&h=640';
const wpRaw='https://finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg';
const wpActual='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg?fit=1024%2C676&ssl=1';
const townnews='https://bloximages.chicago2.vip.townnews.com/enidnews.com/content/tncms/assets/v3/editorial/b/4e/b4e59e84-74da-5f9e-b24f-5e9e3658fd34/54716e12ac97b.image.jpg';
const source=[{key:'283:3',source_url:base,alt:'Historic railway view'}];
function rendered(url,width=0){return [{index:3,src:base,currentSrc:url,dataSrc:'',alt:source[0].alt,complete:true,naturalWidth:width}];}
function net(url,status=404){return [{request_id:'test',url,status,mime_type:'image/jpeg',encodedDataLength:1000}];}

test('P1: actual 299:0 first-party Jetpack fit=W,H is noncropping',()=>assert.equal(sameSource(wpRaw,wpActual),true));
test('P1: direct first-party WordPress numeric fit remains size-only',()=>assert.equal(sameSource(wpRaw,wpRaw+'?fit=1024%2C676'),true));
test('P1: Jetpack numeric fit of external original is size-only',()=>assert.equal(sameSource(base,'https://i0.wp.com/images.example.org/archive/station.jpg?fit=960%2C640&ssl=1'),true));
test('untrusted third-party numeric fit is NOT automatically assumed noncropping',()=>assert.equal(sameSource(base,base+'?fit=960%2C640'),false));
test('fit=crop cannot masquerade as an uncropped historical photo',()=>assert.equal(sameSource(base,fitCrop),false));
test('different fit=crop aspect ratios are different photographic compositions',()=>assert.equal(sameSource(fitCrop,fitCropTall),false));
test('fit=smart-crop is a content-changing selector',()=>assert.equal(sameSource(base,fitSmart),false));
test('fit=facearea is a content-changing selector',()=>assert.equal(sameSource(base,fitFace),false));
test('fit=crop vs fit=smart-crop cannot collapse to one identity',()=>assert.equal(sameSource(fitCrop,fitSmart),false));
test('dual-axis without fit is uncertain: preserve width/height',()=>assert.equal(sameSource(base,base+'?w=960&h=600'),false));
test('dual-axis with long names is uncertain: preserve width/height',()=>assert.equal(sameSource(base,base+'?width=960&height=600'),false));
test('width alone with quality remains ordinary size-only request',()=>assert.equal(sameSource(base,base+'?w=960&q=80'),true));
test('one-axis width is size-only for existing gallery URLs',()=>assert.equal(sameSource(base,base+'?width=960'),true));
test('query crop and resize continue to preserve photographic identity',()=>assert.equal(sameSource(base,base+'?resize=960%2C600'),false));
test('untrusted fit=crop persists in canonical identity',()=>assert.ok(imageIdentity(fitCrop).includes('fit=crop')));
test('crop aspect-ratio dimensions survive canonical identity',()=>assert.ok(imageIdentity(fitCrop).includes('w=960&h=640')));
test('actual published 283:3 crop remains distinct from base',()=>assert.equal(sameSource(townnews,townnews+'?resize=1200%2C804'),false));
test('synthetic 404 on a cropped currentSrc cannot falsely mark uncropped source broken',()=>{
 const row=classifyImages(source,rendered(fitCrop),net(fitCrop),true)[0];
 assert.equal(row.current_src_identity_verified,false);
 assert.equal(row.verified_broken_in_browser,null);
});
test('synthetic 200 on a cropped currentSrc cannot falsely mark uncropped source loaded',()=>{
 const row=classifyImages(source,rendered(fitCrop,800),net(fitCrop,200),true)[0];
 assert.equal(row.verified_broken_in_browser,null);
 assert.equal(row.result,'current_src_identity_unverified');
});
test('synthetic same exact cropped original with CDP 404 still proves crop failure',()=>{
 const original=[{...source[0],source_url:fitCrop}];
 const dom=[{...rendered(fitCrop)[0],src:fitCrop}];
 const row=classifyImages(original,dom,net(fitCrop),true)[0];
 assert.equal(row.verified_broken_in_browser,true);
 assert.equal(row.visual_failure_kind,'http_error');
});
test('synthetic exact currentSrc/CDP 200 and decoded pixels can prove cropped rendition loaded',()=>{
 const original=[{...source[0],source_url:fitCrop}];
 const dom=[{...rendered(fitCrop,800)[0],src:fitCrop}];
 const row=classifyImages(original,dom,net(fitCrop,200),true)[0];
 assert.equal(row.result,'loaded_in_probe_browser');
 assert.equal(row.verified_broken_in_browser,false);
});

const rotterdam='https://stadsarchief.rotterdam.nl/sites/default/files/styles/gallery_large/public/2025-04/hal-prinsendam-nl-rtsa_4121_24162-1-14.jpg';
const rotterdamPublished=rotterdam+'?h=3e6ca723&itok=wjXwUo3w';
test('actual 292:1 Drupal h style hash cannot be discarded as a height',()=>assert.equal(sameSource(rotterdamPublished,rotterdam+'?itok=wjXwUo3w'),false));
test('different 292:1 Drupal style hashes cannot be same-source certified',()=>assert.equal(sameSource(rotterdamPublished,rotterdam+'?h=0deadbea&itok=wjXwUo3w'),false));
test('292:1 style hash is retained in computed image identity',()=>assert.ok(imageIdentity(rotterdamPublished).includes('h=3e6ca723')));
test('non-numeric width selector is preserved instead of normalized as a pixel size',()=>assert.equal(sameSource(base,base+'?w=original'),false));
