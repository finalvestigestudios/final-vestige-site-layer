'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const {inspect,prepareGalleryRepair,BAD,FIX}=require('./r143_gallery_source_repair.cjs');
const ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
function fixture(js=BAD, figures='0,1,2'){
 return '<section data-fvx-chronology><input type="range" min="0" max="15" step="0.1">'+
 '<div data-fvx-chrono-gallery>'+figures.split(',').map(n=>`<figure data-fvx-chrono-photo="${n}"><figcaption>Original NASA record</figcaption></figure>`).join('')+'</div></section>'+
 `<a href="${ARTICLE}">Read the full investigation</a><script>(()=>{const $=(root,s)=>root.querySelector(s);const $$=(root,s)=>Array.from(root.querySelectorAll(s));${js}if (photos.length === 3) { photos.forEach((photo,i)=>{photo.hidden=i!==0;});}})();</script>`;
}
test('source audit isolates actual selector defect',()=>{
 const s=inspect(fixture());assert.deepEqual(s.blockers,[]);
 assert.equal(s.findings.originalCount,1);assert.equal(s.findings.fixedCount,0);
});
test('one-character repair only and explicit release hold',()=>{
 const s=fixture();const a=prepareGalleryRepair(s);
 assert.equal(a.output.length,s.length+1);assert.equal(a.output.replace(FIX,BAD),s);
 assert.equal(a.receipt.approval,'STAGING_HOLD');assert.equal(a.receipt.actualBrowser,'NOT_TESTED');
 assert.equal(a.receipt.realizedRevenue,'NOT_OBSERVED');
});
test('repair retains all 3 source gallery records and exact reader CTA',()=>{
 const a=prepareGalleryRepair(fixture());assert.deepEqual(a.receipt.post.figures,[0,1,2]);
 assert.equal(a.receipt.post.staticLinks,1);assert.equal(a.receipt.post.originalCount,0);
});
test('refuses already-fixed source',()=>assert.throws(()=>prepareGalleryRepair(fixture(FIX)),/ALREADY_REPAIRED/));
test('refuses double selector occurrence',()=>assert.throws(()=>prepareGalleryRepair(fixture(BAD+'\n'+BAD)),/EXACT_GALLERY_SELECTOR_DRIFT/));
test('refuses missing or extra photos',()=>{for(const n of ['0,1','0,1,2,3'])assert.throws(()=>prepareGalleryRepair(fixture(BAD,n)),/THREE_ORDERED/);});
test('refuses duplicated, swapped or speculative photo ids',()=>{for(const n of ['0,0,1','2,1,0','0,1,9'])assert.throws(()=>prepareGalleryRepair(fixture(BAD,n)),/THREE_ORDERED/);});
test('refuses missing static CTA or deceptive replacement',()=>{
 assert.throws(()=>prepareGalleryRepair(fixture().replace('Read the full investigation','Buy the official NASA casefile')),/READER_ACTION_DRIFT/);
 assert.throws(()=>prepareGalleryRepair(fixture().replace(ARTICLE,'https://example.test/checkout')),/READER_ACTION_DRIFT/);
});
test('refuses missing slider and gallery',()=>{
 assert.throws(()=>prepareGalleryRepair(fixture().replace('type="range"','type="text"')),/CHRONOLOGY/);
 assert.throws(()=>prepareGalleryRepair(fixture().replace('data-fvx-chrono-gallery','data-unknown')),/GALLERY/);
});
test('rejects multiple script tags, missing selector and wrong input',()=>{
 assert.throws(()=>prepareGalleryRepair(fixture()+'<script></script>'),/SCRIPT_COUNT_DRIFT/);
 assert.throws(()=>prepareGalleryRepair(fixture('const photos=[];')),/EXACT_GALLERY_SELECTOR_DRIFT/);
 assert.throws(()=>inspect(null),/must be a string/);
});
test('deterministic output and no fabricated conversion evidence',()=>{
 const a=prepareGalleryRepair(fixture());assert.deepEqual(a,prepareGalleryRepair(fixture()));
 assert.equal(a.receipt.merchant,'NOT_VERIFIED');assert.equal(a.receipt.mediaRights,'NOT_REVIEWED');
});
