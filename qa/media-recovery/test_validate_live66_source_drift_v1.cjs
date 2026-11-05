'use strict';
const assert=require('node:assert/strict');const {test}=require('node:test');const fs=require('node:fs');const path=require('node:path');const {verify}=require('./validate_live66_source_drift_v1.cjs');
const load=()=>[1,2,3,4,5,6].map(n=>JSON.parse(fs.readFileSync(path.join(__dirname,'live66_parts',String(n).padStart(2,'0')+'.json'),'utf8')));
const clone=v=>JSON.parse(JSON.stringify(v));
test('six batches satisfy live source-only census (no guest HTTP claimed)',()=>{const r=verify(load());assert.equal(r.valid,true,JSON.stringify(r.errors));assert.equal(r.summary.posts,66);assert.equal(r.summary.slots,361);assert.equal(r.summary.external,294);assert.equal(r.summary.claim_42_broken,'UNVERIFIED');});
const mutations=[
 ["source changed",a=>a[0].posts[0].images[0].original_url='https://other.example/picture.png'],
 ["wrong host",a=>a[0].posts[0].images[0].host='finalvestige.com'],
 ["wrong source origin",a=>a[0].posts[0].images[0].origin='first_party'],
 ["incorrect requested width",a=>a[0].posts[0].images[0].query_width=960],
 ["fabricated HTTP 200",a=>a[0].posts[0].images[0].actual_browser_http_status=200],
 ["invented bytes",a=>a[0].posts[0].images[0].actual_browser_transfer_bytes=1234],
 ["invented decode",a=>a[0].posts[0].images[0].actual_browser_decoded=true],
 ["unauthorized cache",a=>a[0].posts[0].images[0].local_cache_authorized=true],
 ["unauthorized WordPress publish",a=>a[0].posts[0].images[0].wp_write_authorized=true],
 ["unverified rights marked cleared",a=>a[0].posts[0].images[0].rights='PUBLIC_DOMAIN'],
 ["upscaling permitted",a=>a[0].posts[0].images[0].no_upscale=false],
 ["break 960 ceiling",a=>a[0].posts[0].images[0].max_derivative_width=1280],
 ["remove alt",a=>a[0].posts[0].images[0].alt=''],
 ["missing post",a=>a[0].posts.pop()],
 ["wrong image slot",a=>a[0].posts[0].images[0].key='1926:99'],
 ["duplicated post ID",a=>a[0].posts[1].id=a[0].posts[0].id],
 ["deleted image reference",a=>{a[1].posts[0].images.pop();a[1].posts[0].image_count--;}],
 ["wrong batch pagination",a=>a[0].page=2],
 ["invalid intrinsic tag width",a=>a[0].posts[0].images[0].html_width=-20],
 ["non-HTTP source URL",a=>a[0].posts[5].images[0].original_url='file:///unapproved.jpg']
];
for(const [name,mutate] of mutations)test('reject '+name,()=>{const a=clone(load());mutate(a);assert.equal(verify(a).valid,false)});

// A derived fixture tests the cross-baseline API; actual independent Oct 30 crosscheck
// was performed separately with immutable blob 921e09ec4a26f69cc5063e867efacbc16070a36a.
const syntheticPrevious=a=>({rows:a.flatMap(b=>b.posts).filter(p=>![1926,1924,1922,1920,1917].includes(p.id)).flatMap(p=>p.images.map(i=>({key:i.key,original_url:i.original_url})))});
test('cross-baseline strict comparison detects a changed historic photograph source',()=>{const a=load(),old=syntheticPrevious(a);assert.equal(old.rows.length,355);assert.equal(verify(a,old).valid,true);a[1].posts[0].images[0].original_url='https://finalvestige.com/wrong-image.jpg';assert.equal(verify(a,old).valid,false)});
test('cross-baseline rejects a forged earlier URL',()=>{const a=load(),old=syntheticPrevious(a);old.rows[0].original_url='https://example.org/fabricated.jpg';assert.equal(verify(a,old).valid,false)});
