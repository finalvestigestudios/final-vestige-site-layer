'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {classifySource,parseCsv,reconcile}=require('./reconcile_jetpack_origin_20261109.cjs');
const fx = () => ({ post_count:1,image_count:3, posts:[{id:1,images:3}], images:[
  {key:'1:0',post_id:1,slot:0,source_url:'https://finalvestige.com/x.jpg',source_kind:'first_party'},
  {key:'1:1',post_id:1,slot:1,source_url:'https://i0.wp.com/finalvestige.com/a.jpg?ssl=1',source_kind:'jetpack_proxy'},
  {key:'1:2',post_id:1,slot:2,source_url:'https://i0.wp.com/www.example.org/thirdparty.jpg',source_kind:'external'} ]});
const csv = 'post_id,stored_img_src_count,offsite_src_count\n1,3,0\n';
test('primary WordPress CDN origin is first-party',()=>assert.equal(classifySource('https://i0.wp.com/finalvestige.com/a.jpg').kind,'jetpack_proxy'));
test('third-party WordPress CDN origin remains external',()=>assert.equal(classifySource('https://i0.wp.com/www.squawkpoint.com/a.jpg').kind,'external'));
test('NARA Teton WordPress CDN origin remains external',()=>assert.equal(classifySource('https://i0.wp.com/text-message.blogs.archives.gov/b.jpg').upstream_host,'text-message.blogs.archives.gov'));
test('Commons redirect is offsite',()=>assert.equal(classifySource('https://commons.wikimedia.org/wiki/Special:Redirect/file/a.jpg').kind,'wikimedia_redirect'));
test('generic Commons pages are not image-redirect class',()=>assert.equal(classifySource('https://commons.wikimedia.org/wiki/File:a.jpg').kind,'external'));
test('prefix spoofing fails',()=>assert.equal(classifySource('https://i1.wp.com/finalvestige.com.evil.test/x').kind,'external'));
test('first-party subdomain not implicitly trusted',()=>assert.equal(classifySource('https://cdn.finalvestige.com/x').kind,'external'));
test('other proxy hosts are handled',()=>assert.equal(classifySource('https://i2.wp.com/www.finalvestige.com/x').kind,'jetpack_proxy'));
test('i3 CDN shares upstream-origin semantics',()=>assert.equal(classifySource('https://i3.wp.com/elsewhere.gov/photo.jpg').kind,'external'));
test('bad/missing source rejects',()=>{for(const s of ['',null,'abc','data:image/png;base64,a'])assert.throws(()=>classifySource(s));});
test('corrects synthetic CSV offsite count',()=>{const r=reconcile([fx()],csv,{enforceFrozen:false});assert.equal(r.corrected_offsite,1);assert.equal(r.qa_offsite,0);assert.equal(r.differences[0].third_party_jetpack_slots[0].slot,'1:2');assert.equal(r.guest_http_verified,false);});
test('default frozen baseline blocks unrelated fixture',()=>assert.throws(()=>reconcile([fx()],csv),/Frozen/));
test('altered source kind rejected',()=>{const a=fx();a.images[2].source_kind='jetpack_proxy';assert.throws(()=>reconcile([a],csv,{enforceFrozen:false}),/kind mismatch/)});
test('wrong alt row count rejected',()=>{const a=fx();a.images.pop();assert.throws(()=>reconcile([a],csv,{enforceFrozen:false}),/part totals/)});
test('duplicate slot rejected',()=>{const a=fx();a.images[1].key='1:0';assert.throws(()=>reconcile([a],csv,{enforceFrozen:false}),/invalid image slot/)});
test('unknown source kind rejected',()=>{const a=fx();a.images[1].source_kind='invented';assert.throws(()=>reconcile([a],csv,{enforceFrozen:false}),/Unknown/)});
test('bad CSV header rejects',()=>assert.throws(()=>parseCsv('id,images,offsite\n1,3,0'),/header/));
test('duplicate QA row rejects',()=>assert.throws(()=>parseCsv(csv+'1,3,0\n'),/Duplicate/));
test('changed QA per-post image count rejects',()=>assert.throws(()=>reconcile([fx()],csv.replace('1,3,0','1,4,0'),{enforceFrozen:false}),/QA image-count/));
test('missing QA post rejects',()=>assert.throws(()=>reconcile([fx()], 'post_id,stored_img_src_count,offsite_src_count\n2,3,0\n',{enforceFrozen:false}),/QA image-count/));
test('no browser or rights claims emitted',()=>{const r=reconcile([fx()],csv,{enforceFrozen:false}); assert.equal(r.rights_verified,false);assert.equal(r.visitor_broken_count,null);assert.equal(r.actual_wire_bytes,null);assert.equal(r.percentage_savings_measured,null);});
