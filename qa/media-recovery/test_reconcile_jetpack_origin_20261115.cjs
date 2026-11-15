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
