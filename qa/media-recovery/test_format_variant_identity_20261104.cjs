'use strict';
// Synthetic URL identity and browser-response fixtures only. No HTTP, CMS, scraping or media writes.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {isFormatSensitive,isFormatSelector,materialSelectors}=require('./format_variant_identity_core_20261104.cjs');
const {imageIdentity,sameSource,classifyImages}=require('./browser_probe_core.cjs');

const gif='https://tile.loc.gov/storage-services/service/pnp/habshaer/ca/ca3000/ca3095/sheet/00002a.gif';
const svg='https://commons.wikimedia.org/wiki/Special:Redirect/file/HRWalkway.svg';
const apollo='https://commons.wikimedia.org/wiki/Special:Redirect/file/Apollo%20Command%20Module%20Main%20Control%20Panel.gif?width=1280';
const png='https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v03r2-six-mph-curve-responsive.png';
const jpg='https://finalvestige.com/wp-content/uploads/2026/08/documentary-photo.jpg';
function source(u){return [{key:'257:4',source_url:u,alt:'Technical source drawing'}]}
function dom(u,decoded){return [{index:0,src:u,currentSrc:u,alt:'Technical source drawing',complete:true,naturalWidth:decoded}]}
function network(u,status,mime='image/png'){return [{url:u,status,mime_type:mime,encodedDataLength:1000}]}

test('native format guard: PNG/GIF/SVG are sensitive',()=>{
 assert.deepEqual(['figure.PNG','panel.gif','HRWalkway.svg'].map(isFormatSensitive),[true,true,true]);
});
test('native format guard: JPEG is not sensitive and query suffix is ignored',()=>{
 assert.equal(isFormatSensitive('documentary.jpg?format=webp'),false);
 assert.equal(isFormatSensitive('figure.png?width=960'),true);
});
test('native format guard: format selectors case-insensitive',()=>{
 assert.deepEqual(['format','Fm','auto','q','w','ssl'].map(isFormatSelector),[true,true,true,false,false,false]);
});
test('native format guard: material selectors preserve query ordering',()=>{
 assert.deepEqual(materialSelectors('figure.png',[['width','960'],['format','jpeg'],['fm','webp'],['q','80']]),
  [['format','jpeg'],['fm','webp']]);
});
test('native format guard: non-sensitive and empty selectors',()=>{
 assert.deepEqual(materialSelectors('photo.jpg',[['format','webp']]),[]);
 assert.deepEqual(materialSelectors('panel.gif',[]),[]);
});

test('real 166:1 LOC GIF cannot be certified as JPEG-transcoded image',()=>assert.equal(sameSource(gif,gif+'?format=jpg'),false));
test('real 166:1 LOC GIF cannot be certified with auto=format',()=>assert.equal(sameSource(gif,gif+'?auto=format'),false));
test('real 255:1 Hyatt SVG cannot be certified as a rasterized output format',()=>assert.equal(sameSource(svg,svg+'?fm=png'),false));
test('real 257:4 Apollo Commons GIF remains identifiable across width-only redirects',()=>{
 assert.equal(sameSource(apollo,apollo.replace('width=1280','width=960')),true);
});
test('real 257:4 Apollo Commons GIF and transformed JPEG are different',()=>{
 assert.equal(sameSource(apollo,apollo+'&format=jpeg'),false);
 assert.ok(imageIdentity(apollo+'&format=jpeg').includes('format=jpeg'));
});
test('real 255:1 Commons SVG cannot discard auto-format selector',()=>{
 assert.equal(sameSource(svg,svg+'?auto=format'),false);
});
test('technical first-party PNG and JPEG-transcoded version stay separate',()=>assert.equal(sameSource(png,png+'?fm=jpg'),false));
test('technical first-party PNG and auto-format version stay separate',()=>assert.equal(sameSource(png,png+'?auto=format'),false));
test('numeric Jetpack fit of original technical PNG still preserves layout aspect',()=>{
 const proxy='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v03r2-six-mph-curve-responsive.png?fit=960%2C540&ssl=1';
 assert.equal(sameSource(png,proxy),true);
});
test('Jetpack PNG format transformation cannot bypass source integrity',()=>{
 const proxy='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v03r2-six-mph-curve-responsive.png?fit=960%2C540&fm=jpg&ssl=1';
 assert.equal(sameSource(png,proxy),false);
});
test('ordinary JPEG format delivery remains a source-level equivalence',()=>{
 assert.equal(sameSource(jpg,jpg+'?fm=webp&q=80'),true);
});
test('format variation is not an HTTP failure of the stored GIF',()=>{
 const modified=gif+'?fm=jpeg';
 const row=classifyImages(source(gif),dom(modified,0),network(modified,404,'image/jpeg'),true)[0];
 assert.equal(row.verified_broken_in_browser,null);
 assert.equal(row.current_src_identity_verified,false);
});
test('format variation is not verified loaded from the stored GIF',()=>{
 const modified=gif+'?fm=webp';
 const row=classifyImages(source(gif),dom(modified,900),network(modified,200,'image/webp'),true)[0];
 assert.equal(row.verified_broken_in_browser,null);
 assert.equal(row.result,'current_src_identity_unverified');
});
test('unaltered GIF with a genuine response failure can still be proven broken',()=>{
 const row=classifyImages(source(gif),dom(gif,0),network(gif,404,'image/gif'),true)[0];
 assert.equal(row.verified_broken_in_browser,true);
 assert.equal(row.visual_failure_kind,'http_error');
});
test('unaltered technical PNG with decoded pixels can be proven loaded',()=>{
 const row=classifyImages(source(png),dom(png,960),network(png,200),true)[0];
 assert.equal(row.result,'loaded_in_probe_browser');
 assert.equal(row.verified_broken_in_browser,false);
});
