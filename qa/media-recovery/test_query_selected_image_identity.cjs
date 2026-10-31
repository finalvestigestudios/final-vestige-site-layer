'use strict';
/** Offline adversarial identity tests: no network access, CMS changes or copyrighted media copies. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {imageIdentity,sameSource,classifyImages}=require('./browser_probe_core.cjs');
const {inspectRun}=require('./compare_wire_core.cjs');
function audit(){
 const src='https://historical.example.gov/photo.jpg?id=alpha';
 return {schema_version:1,probe_version:3,created:'2026-10-31T07:00:00Z',mode:'priority',viewport:'390x844',
 probe:'logged-out Chrome CDP, no npm dependencies or WordPress writes',browser_product:'Chrome/142.0.0.0',
 run_profile:{cache_disabled:true,service_worker_bypassed:true,scroll_step_px:720,scroll_wait_ms:220,settle_wait_ms:1000},
 requested_pages:1,verified_pages:1,pages:[{post_id:123,url:'https://finalvestige.com/example/',
 document_url:'https://finalvestige.com/example/',page_result:'inspected_browser',
 scroll_coverage:{complete:true,state:'full_height_scanned'},document_network_failures:[],
 stored_image_count:1,rendered_image_count:1,image_wire_bytes_total:1000,
 article_image_wire_bytes_total:1000,
 stored_images:[{image_key:'123:0',stored_url:src,current_src:src,request_url:src,
 current_src_identity_verified:true,result:'loaded_in_probe_browser',verified_broken_in_browser:false,
 natural_width:500,http_status:200,transfer_bytes:1000}],
 network_images:[{url:src,url_aliases:[],status:200,mime_type:'image/jpeg',encoded_data_length:1000,
 error:null,from_disk_cache:false,from_service_worker:false,was_cached:false}]}]};
}
test('same path but different photo selectors represent different images',()=>{
 assert.equal(sameSource('https://historical.example.gov/render?id=alpha','https://historical.example.gov/render?id=beta'),false);
 assert.equal(sameSource('https://historical.example.gov/render?file=a.jpg','https://historical.example.gov/render?file=b.jpg'),false);
});
test('size and WordPress Jetpack transform knobs retain same-file identity',()=>{
 assert.equal(sameSource('https://historical.example.gov/photo.jpg?id=alpha&width=960',
  'https://historical.example.gov/photo.jpg?id=alpha&width=640&ssl=1'),true);
 assert.equal(sameSource('https://i0.wp.com/historical.example.gov/photo.jpg?fit=960%2C640&ssl=1',
  'https://historical.example.gov/photo.jpg'),true);
});
test('unknown selectors and signed tokens remain material',()=>{
 assert.equal(sameSource('https://historical.example.gov/image?token=abc','https://historical.example.gov/image?token=def'),false);
 assert.equal(imageIdentity('https://historical.example.gov/image.jpg?key=abc&width=960'),
  'https://historical.example.gov/image.jpg?key=abc');
});
test('dynamic image endpoints preserve all query selectors including width',()=>{
 assert.equal(sameSource('https://historical.example.gov/render?width=one',
  'https://historical.example.gov/render?width=two'),false);
 assert.equal(sameSource('https://historical.example.gov/render?key=a&width=100',
  'https://historical.example.gov/render?key=a&width=200'),false);
});
test('canonical Commons filename and thumbnail match, different filenames do not',()=>{
 assert.equal(sameSource('https://commons.wikimedia.org/wiki/Special:Redirect/file/Photo_A.jpg?width=960',
  'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Photo_A.jpg/960px-Photo_A.jpg'),true);
 assert.equal(sameSource('https://commons.wikimedia.org/wiki/File:Photo_A.jpg',
  'https://commons.wikimedia.org/wiki/File:Photo_B.jpg'),false);
});
test('different decoded query-selected photograph never verifies the original',()=>{
 const a='https://historical.example.gov/render?photo=first',b='https://historical.example.gov/render?photo=second';
 const row=classifyImages([{key:'123:0',source_url:a,alt:'Historic photo'}],
  [{src:a,currentSrc:b,dataSrc:'',alt:'Historic photo',complete:true,naturalWidth:800}],
  [{url:b,status:200,encodedDataLength:1200}],true)[0];
 assert.equal(row.current_src_identity_verified,false);
 assert.equal(row.result,'current_src_identity_unverified');
 assert.equal(row.verified_broken_in_browser,null);
});
test('v3 comparator accepts internally corroborated source and decoded image',()=>{
 assert.equal(inspectRun(audit()).ok,true);
});
test('v3 comparator rejects forged identity flag for different query-selected photograph',()=>{
 const x=audit(),row=x.pages[0].stored_images[0];
 row.current_src='https://historical.example.gov/photo.jpg?id=beta';
 row.request_url=row.current_src;x.pages[0].network_images[0].url=row.current_src;
 assert.equal(inspectRun(x).ok,false);
 assert.ok(inspectRun(x).errors.some(v=>v.startsWith('unsettled_or_unmeasured')));
});
test('v3 comparator rejects missing original stored URL despite identity-verified flag',()=>{
 const x=audit();delete x.pages[0].stored_images[0].stored_url;
 assert.equal(inspectRun(x).ok,false);
});
