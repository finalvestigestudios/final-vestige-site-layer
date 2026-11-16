'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {evaluate, sourceMatches,STATUS} = require('./evaluate_guest_image_evidence.cjs');
const keys=['285:5','285:2','287:5','418:1','418:2','407:1'];
const paths=['a.jpg','b.jpg','c.jpg','d.jpg','e.jpg','f.jpg'];
const manifest={schema:'fv-p0-web-retriever-matrix-v1',rows:keys.map((key,i)=>({
 key,post_url:`https://finalvestige.com/articles/${key.replace(':','-')}/`,
 authored_url:`https://images.example.net/${paths[i]}`,
 jetpack_view_url:`https://i0.wp.com/images.example.net/${paths[i]}?ssl=1`}))};
const clone = x=> structuredClone(x);
const one = (i=0)=>({
 key:keys[i],post_url:manifest.rows[i].post_url,current_src:manifest.rows[i].jetpack_view_url,
 complete:true,natural_width:600,natural_height:400,decode_succeeded:true,
 request:{url:manifest.rows[i].jetpack_view_url,http_status:200,mime_type:'image/jpeg',wire_bytes:7000,from_cache:false,network_error:null}
});
const env = {browser:'chromium',session:'logged_out',collector:'Site QA #154',cache:'disabled',captured_at_utc:'2026-11-16T23:31:33Z'};
const capture=(slots=[one()])=>({schema:'fv-siteqa-guest-image-evidence-v1',environment:clone(env),slots});

test('no capture yields six UNOBSERVED and no invented bytes, browser statuses or sitewide claim',()=>{
 const r=evaluate(manifest);
 assert.equal(r.summary.provided_capture_slots,0);
 assert.equal(r.summary.complete_six_slot_wire_bytes,null);
 assert.equal(r.summary.observed_partial_wire_bytes,null);
 assert.equal(r.summary.reported_42_broken_sitewide_verified,false);
 assert.equal(r.summary.claimed_76_percent_sitewide_wire_savings_verified,false);
 assert.deepEqual(r.rows.map(x=>x.delivery),Array(6).fill(STATUS.UNOBSERVED));
 assert.ok(r.rows.every(x=>x.browser_http_status===null && x.production_replacement_allowed===false));
});
test('one actual captured success reports only one rendered slot and a partial transfer count',()=>{
 const r=evaluate(manifest,capture());
 assert.equal(r.summary.reported_rendered_slots,1);
 assert.equal(r.summary.unresolved_slots,5);
 assert.equal(r.summary.wire_byte_slots,1);
 assert.equal(r.summary.observed_partial_wire_bytes,7000);
 assert.equal(r.summary.complete_six_slot_wire_bytes,null);
 assert.equal(r.rows[1].delivery,STATUS.MISSING_CAPTURE);
});
test('six matching independent capture rows enable six-slot wire total, never sitewide reduction',()=>{
 const r=evaluate(manifest,capture(keys.map((_,i)=>one(i))));
 assert.equal(r.summary.reported_rendered_slots,6);
 assert.equal(r.summary.complete_six_slot_wire_bytes,42000);
 assert.equal(r.summary.claimed_76_percent_sitewide_wire_savings_verified,false);
});
test('404 plus completed decode failure reports capture-broken',()=>{
 const s=one();s.request.http_status=404;s.request.mime_type='text/html';s.decode_succeeded=false;s.natural_width=0;s.natural_height=0;
 const r=evaluate(manifest,capture([s]));assert.equal(r.rows[0].delivery,STATUS.BROKEN);
});
test('200 with un-decodable image can be visibly broken',()=>{
 const s=one();s.decode_succeeded=false;s.natural_width=0;s.natural_height=0;
 assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.BROKEN);
});
test('404 alone is transport issue, NOT verified broken image',()=>{
 const s=one();s.request.http_status=404;s.complete=null;s.decode_succeeded=null;s.natural_width=null;s.natural_height=null;
 const r=evaluate(manifest,capture([s]));assert.equal(r.rows[0].delivery,STATUS.TRANSPORT);
});
test('304 is not counted as success',()=>{const s=one();s.request.http_status=304;assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.INCONCLUSIVE)});
test('200 with text MIME is not render-confirmed',()=>{const s=one();s.request.mime_type='text/html';assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.INCONCLUSIVE)});
test('200 without decode evidence is inconclusive',()=>{const s=one();s.decode_succeeded=null;assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.INCONCLUSIVE)});
test('partial non-complete image is inconclusive',()=>{const s=one();s.complete=false;assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.INCONCLUSIVE)});
test('source drift blocks success/bytes regardless of browser data',()=>{const s=one();s.current_src='https://unrelated.example/a.jpg';s.request.url=s.current_src;const r=evaluate(manifest,capture([s]));assert.equal(r.rows[0].delivery,STATUS.SOURCE_DRIFT);assert.equal(r.summary.wire_byte_slots,0)});
test('network/currentSrc disagreement blocks result',()=>{const s=one();s.request.url='https://images.example.net/other.jpg';assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.SOURCE_DRIFT)});
test('post URL drift blocks result',()=>{const s=one();s.post_url='https://finalvestige.com/other';assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.SOURCE_DRIFT)});
test('safe Jetpack i2 resize maps to same source',()=>{
 const s=one();s.current_src='https://i2.wp.com/images.example.net/a.jpg?ssl=1&w=960';s.request.url=s.current_src;
 assert.equal(sourceMatches(s.current_src,manifest.rows[0]),true);
 assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.RENDERED);
});
test('unsafe Jetpack query parameter causes source drift',()=>{const s=one();s.current_src+='&url=https://evil.test';s.request.url=s.current_src;assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.SOURCE_DRIFT)});
test('different image filename on Jetpack is not accepted',()=>{const s=one();s.current_src=s.current_src.replace('/a.jpg','/b.jpg');s.request.url=s.current_src;assert.equal(evaluate(manifest,capture([s])).rows[0].delivery,STATUS.SOURCE_DRIFT)});
test('cache-labelled transfer bytes are rejected',()=>{const c=capture();c.slots[0].request.from_cache=true;assert.throws(()=>evaluate(manifest,c),/Cached/)});
test('unknown cache provenance plus numeric bytes is rejected',()=>{const c=capture();c.slots[0].request.from_cache=null;assert.throws(()=>evaluate(manifest,c),/Cached/)});
test('cache response with no wire byte is allowed but no byte sum',()=>{const c=capture();c.slots[0].request.from_cache=true;c.slots[0].request.wire_bytes=null;assert.equal(evaluate(manifest,c).summary.wire_byte_slots,0)});
test('negative browser HTTP not accepted',()=>{const c=capture();c.slots[0].request.http_status=-1;assert.throws(()=>evaluate(manifest,c),/Invalid http_status/)});
test('invalid browser HTTP 700 not accepted',()=>{const c=capture();c.slots[0].request.http_status=700;assert.throws(()=>evaluate(manifest,c),/Invalid HTTP/)});
test('fake untrusted runtime source blocked',()=>{const c=capture();c.environment.collector='web-retriever';assert.throws(()=>evaluate(manifest,c),/Site QA Chromium/)});
test('headless session cannot pretend logged-out guest',()=>{const c=capture();c.environment.session='authenticated';assert.throws(()=>evaluate(manifest,c),/Site QA Chromium/)});
test('cache-enabled run fails closed',()=>{const c=capture();c.environment.cache='enabled';assert.throws(()=>evaluate(manifest,c),/Site QA Chromium/)});
test('missing capture timestamp fails closed',()=>{const c=capture();delete c.environment.captured_at_utc;assert.throws(()=>evaluate(manifest,c),/timestamp/)});
test('duplicate slot fails closed',()=>assert.throws(()=>evaluate(manifest,capture([one(),one()])),/duplicate/i));
test('unknown slot fails closed',()=>{const s=one();s.key='999:2';assert.throws(()=>evaluate(manifest,capture([s])),/Unknown/)});
test('wrong manifest size fails closed',()=>{const m=clone(manifest);m.rows.pop();assert.throws(()=>evaluate(m),/six-slot/)});
test('duplicate manifest key fails closed',()=>{const m=clone(manifest);m.rows[1].key=m.rows[0].key;assert.throws(()=>evaluate(m),/Duplicate/)});
test('bad natural dimensions rejected',()=>{const c=capture();c.slots[0].natural_width=3.5;assert.throws(()=>evaluate(manifest,c),/natural_width/)});
test('negative wire bytes rejected',()=>{const c=capture();c.slots[0].request.wire_bytes=-9;assert.throws(()=>evaluate(manifest,c),/wire_bytes/)});
test('non HTTP URL rejected',()=>{const c=capture();c.slots[0].current_src='file:///etc/passwd';assert.throws(()=>evaluate(manifest,c),/scheme/)});
test('explicit report never authorizes WordPress write',()=>{const r=evaluate(manifest,capture(keys.map((_,i)=>one(i))));assert.ok(r.rows.every(x=>x.production_replacement_allowed===false))});
