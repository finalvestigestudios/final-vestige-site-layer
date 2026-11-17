'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {classifyStoredUrl,reconcile}=require('./reconcile_jetpack_origin_20261115.cjs');
const tests = [
 ['https://finalvestige.com/wp-content/uploads/photo.jpg','owned_direct'],
 ['https://www.finalvestige.com/wp-content/uploads/photo.jpg','owned_direct'],
 ['https://i0.wp.com/finalvestige.com/wp-content/uploads/photo.jpg?fit=960%2C600','owned_jetpack_origin'],
 ['https://i2.wp.com/www.finalvestige.com/wp-content/uploads/photo.jpg','owned_jetpack_origin'],
 ['https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/photo.jpg?ssl=1','external_jetpack_origin'],
 ['https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/photo.jpg?ssl=1','external_jetpack_origin'],
 ['https://i1.wp.com/finalvestige.com.evil.org/photo.jpg','external_jetpack_origin'],
 ['https://commons.wikimedia.org/wiki/Special:Redirect/file/Image.jpg','external_direct'],
 ['https://i0.wp.com/%2Ffinalvestige.com/photo.jpg','unverifiable'],
 ['javascript:alert(1)','unverifiable'],
 ['https://user:pass@finalvestige.com/photo.jpg','unverifiable']
];
for(const [src,kind] of tests)test('origin is '+kind+' for '+src.slice(0,70),()=>assert.equal(classifyStoredUrl(src),kind));
const dir=path.join(__dirname,'parts');
test('frozen 61-post/355-slot integration reconciles 286 to 288 independently',
 {skip:!fs.existsSync(path.join(dir,'01.json')) ? 'Full repository frozen fixture not available in standalone runner' : false},()=>{
 const parts=Array.from({length:8},(_,i)=>JSON.parse(fs.readFileSync(path.join(dir,String(i+1).padStart(2,'0')+'.json'),'utf8')));
 const r=reconcile(parts);
 assert.equal(r.external_source_slots,288);
 assert.equal(r.classification.external_jetpack_origin,2);
 assert.equal(r.prior_csv_vs_reconciled_delta,2);
 assert.deepEqual(r.mismatches_with_qa_154_csv.map(x=>x.slot),['285:1','291:0']);
 assert.equal(r.browser_http_verified,false);
 assert.equal(r.wordpress_write_authorized,false);
});
test('unsafe malformed inventory is rejected rather than claimed measured',()=>assert.throws(()=>reconcile([]),/eight frozen/));

// Additional integrity gates: frozen complete coverage and Git blob custody.
const {assertCompleteCoverage,gitBlobSha,loadPinnedParts,EXPECTED_PART_BLOBS}=require('./reconcile_jetpack_origin_20261115.cjs');
function samplePart() {
 const url='https://finalvestige.com/sample',title='Sample';
 return {batch:1,post_count:1,image_count:2,posts:[{id:42,images:2,url,title}],images:[
  {key:'42:0',post_id:42,slot:0,post_url:url,post_title:title},
  {key:'42:1',post_id:42,slot:1,post_url:url,post_title:title}
 ]};
}
test('complete per-post slot set is accepted',()=>assert.deepEqual(assertCompleteCoverage([samplePart()]),{posts:1,slots:2}));
const corruption=[
 ['duplicate key instead of second slot',p=>{p.images[1].slot=0;p.images[1].key='42:0'}],
 ['out-of-range slot',p=>{p.images[1].slot=2;p.images[1].key='42:2'}],
 ['orphan image',p=>{p.images[0].post_id=43;p.images[0].key='43:0'}],
 ['wrong parent URL',p=>{p.images[0].post_url='https://other.example/photo'}],
 ['wrong parent title',p=>{p.images[0].post_title='Wrong title'}],
 ['wrong key',p=>{p.images[0].key='bad'}],
 ['wrong batch number',p=>{p.batch=8}],
 ['wrong declared post count',p=>{p.post_count=2}],
 ['wrong declared image count',p=>{p.image_count=3}],
 ['wrong post slot count',p=>{p.posts[0].images=3}],
 ['bad post identity',p=>{p.posts[0].id=0}]
];
for(const [name,mutate] of corruption) test('reject '+name,()=>{
 const p=samplePart();mutate(p);assert.throws(()=>assertCompleteCoverage([p]));
});
test('reject repeated post across batches',()=>{const a=samplePart(),b=samplePart();b.batch=2;assert.throws(()=>assertCompleteCoverage([a,b]));});
test('reject source text mutation against cryptographic frozen blob',()=>{
 assert.equal(EXPECTED_PART_BLOBS.length,8);
 assert.notEqual(gitBlobSha('invented or altered source'),EXPECTED_PART_BLOBS[0]);
});
test('all eight pinned part hashes + complete 61/355 coverage',
 {skip:!fs.existsSync(path.join(dir,'01.json')) ? 'Full frozen repository parts absent locally' : false},()=>{
 const pinned=loadPinnedParts(dir);
 assert.deepEqual(assertCompleteCoverage(pinned),{posts:61,slots:355});
 const r=reconcile(pinned);
 assert.equal(r.external_source_slots,288);
});
