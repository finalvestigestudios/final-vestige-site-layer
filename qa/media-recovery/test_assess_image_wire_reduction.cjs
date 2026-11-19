'use strict';
// All fixture domains and captures below are SYNTHETIC, not observed visitor traffic.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { audit, parseCensus, verifyStorage, compare } = require('./assess_image_wire_reduction.cjs');
const ids = [621, 434, 433, 432, 431, 428, 425, 418, 413, 407, 370, 367, 330, 299, 292, 291, 290, 289, 288, 287, 285, 283, 280, 279, 278, 277, 276, 274, 269, 268, 258, 257, 256, 255, 254, 253, 252, 221, 220, 219, 218, 217, 216, 215, 214, 213, 211, 190, 166, 156, 151, 146, 142, 139, 108, 101, 38, 37, 36, 35, 34];
const totals = [6, 6, 6, 7, 6, 6, 9, 6, 6, 8, 8, 9, 8, 8, 6, 6, 6, 6, 6, 6, 6, 7, 6, 6, 7, 6, 6, 7, 7, 10, 6, 7, 7, 7, 7, 7, 6, 7, 7, 6, 6, 6, 6, 6, 6, 7, 6, 6, 7, 4, 3, 3, 3, 2, 2, 7, 1, 1, 1, 1, 1];
const offsites = [0, 5, 5, 7, 5, 5, 8, 6, 4, 8, 4, 8, 0, 0, 6, 5, 6, 6, 6, 6, 5, 7, 6, 6, 7, 6, 6, 7, 0, 10, 6, 7, 7, 7, 7, 7, 6, 7, 7, 6, 6, 6, 6, 6, 6, 7, 6, 6, 6, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0];
const csv = 'post_id,stored_img_src_count,offsite_src_count\n' + ids.map((id,i)=>[id,totals[i],offsites[i]].join(',')).join('\n');
function fixtureInventory() {
  const first = [2892087,2552136,2498247,2488823,2836245];
  const remaining = 64385752 - 13267538;
  const assetBytes = first.concat(Array.from({length:15},(_,i)=>i===14?remaining-14*3407880:3407880));
  const assets = assetBytes.map((bytes,i)=>({media_id:i<5?39+i:100+i,bytes,native_width:1672,native_height:941,source_url:'https://finalvestige.com/wp-content/uploads/test-' + i + '.png'}));
  const records = assets.slice(0,5).map((a,i)=>({media_id:a.media_id,post_id:34+i,post_url:'https://finalvestige.com/synthetic-post-' + (34+i) + '/', wp_original_url:a.source_url,wp_original_bytes:a.bytes,rendered_img_src:'https://i0.wp.com/finalvestige.com/wp-content/uploads/test-' + i + '.png?resize=1024%2C576&ssl=1',currentSrc_in_guest_browser:null,guest_get_http_status:null,guest_transfer_bytes:null,item_rights_review:'PENDING',conditional_960_max_no_upscale_px:[960,540]}));
  return {schema:'fv-oversize-runtime-proxy-crosscheck-v1',oversize:{assets,count:20,decimal_byte_threshold:1500000,original_storage_bytes:64385752},focus:{records,count:5,stored_bytes:13267538}};
}
function pair(onlyIds=[34], beforeBytes=2000, afterBytes=500) {
  const page=(id,bytes)=>({post_id:id,url:'https://finalvestige.com/synthetic-post-' + id + '/',scrolled_to_end:true,lazy_images_settled:true,network_capture_complete:true,visual_slots_preserved:true,image_requests:[{request_id:'image-' + id,url:'https://i0.wp.com/example.test/photo-' + id + '.jpg',http_status:200,mime_type:'image/jpeg',encoded_data_length:bytes,decoded:true,from_cache:false,from_service_worker:false,from_prefetch:false,redirected:false}]});
  return {schema:'fv-paired-image-wire-v1', environment:{collector:'Site QA #154',browser:'Chromium',mode:'logged_out',cache:'disabled',service_workers_bypassed:true,viewport_width:390,viewport_height:844,dpr:2,network_profile:'Slow 4G',browser_version:'synthetic-test-browser',captured_at_before:'2026-11-16T20:00:00Z',captured_at_after:'2026-11-16T20:01:00Z'},before:onlyIds.map(id=>page(id,beforeBytes)),after:onlyIds.map(id=>page(id,afterBytes))};
}
const bad=(name,mutate,target='capture') => test(name,()=>{let inv=fixtureInventory(), cap=pair(), census=csv; if(target==='inventory')mutate(inv);else if(target==='census')census=mutate(census);else mutate(cap);assert.throws(()=>audit(census,inv,cap))});
test('pinned historical census counts',()=>{const c=parseCensus(csv); assert.equal(c.posts.size,61);assert.equal(c.images,355);assert.equal(c.offsite,286)});
test('20 oversized storage originals verify with five virtual proxy URLs',()=>{const a=verifyStorage(fixtureInventory());assert.equal(a.total,64385752);assert.equal(a.focused,13267538)});
test('no guest capture remains unmeasured with exact scoped facts',()=>{const x=audit(csv,fixtureInventory());assert.equal(x.wire.status,'NO_BROWSER_CAPTURE');assert.equal(x.wire.percent_reduction,null);assert.equal(x.storage_only.over_1500000_byte_originals,20);assert.equal(x.observed_page_proxies.length,5);assert.equal(x.observed_page_proxies[0].guest_http_status,null);assert.equal(x.wire.claim_76_percent_verified,false)});
test('80% reduction in one synthetic page cannot be claimed as sitewide',()=>{const x=audit(csv,fixtureInventory(),pair([34],2000,400));assert.equal(x.wire.percent_reduction,80);assert.equal(x.wire.meets_76_percent_in_measured_sample,true);assert.equal(x.wire.claim_76_percent_verified,false);assert.equal(x.wire.status,'MEASURED_SUBSET_NOT_SITEWIDE')});
test('75% synthetic sample reduction does not reach 76%',()=>assert.equal(audit(csv,fixtureInventory(),pair()).wire.meets_76_percent_in_measured_sample,false));
test('all 61 synthetic pages are still self-reported / review required',()=>{const x=compare(parseCensus(csv),pair(ids,2000,400));assert.equal(x.measured_page_count,61);assert.equal(x.status,'COMPLETE_61_PAGE_SELF_REPORTED_REVIEW_REQUIRED');assert.equal(x.claim_76_percent_verified,false)});
test('regression can report a negative reduction',()=>{const x=compare(parseCensus(csv),pair([34],500,2000));assert.equal(x.percent_reduction,-300)});
// census negative cases are checked separately because mutation returns CSV string
test('reject census total drift',()=>assert.throws(()=>parseCensus(csv.replace('621,6,0','621,7,0'))));
test('reject wrong census header',()=>assert.throws(()=>parseCensus('bad-header\n'+csv.split('\n').slice(1).join('\n'))));
test('reject duplicate census id',()=>assert.throws(()=>parseCensus(csv.replace('434,6,5','621,6,5'))));
bad('reject storage total drift',i=>i.oversize.assets[0].bytes++,'inventory');
bad('reject repeated original media id',i=>i.oversize.assets[1].media_id=i.oversize.assets[0].media_id,'inventory');
bad('reject missing original URL',i=>i.oversize.assets[0].source_url='','inventory');
bad('reject low original file size',i=>i.oversize.assets[0].bytes=1500000,'inventory');
bad('reject fabricated guest HTTP for source-only inventory',i=>i.focus.records[0].guest_get_http_status=200,'inventory');
bad('reject incorrect proxy basename',i=>i.focus.records[0].rendered_img_src='https://other.example/test.png','inventory');
bad('reject cache hit despite nonzero CDP claim',x=>x.before[0].image_requests[0].from_cache=true);
bad('reject 304 response',x=>x.before[0].image_requests[0].http_status=304);
bad('reject HTML masquerading as image',x=>x.after[0].image_requests[0].mime_type='text/html');
bad('reject failed image decode',x=>x.after[0].image_requests[0].decoded=false);
bad('reject service-worker image delivery',x=>x.before[0].image_requests[0].from_service_worker=true);
bad('reject prefetched image',x=>x.after[0].image_requests[0].from_prefetch=true);
bad('reject redirected record without complete redirect accounting',x=>x.before[0].image_requests[0].redirected=true);
bad('reject negative bytes',x=>x.before[0].image_requests[0].encoded_data_length=-1);
bad('reject unsafe huge byte count',x=>x.before[0].image_requests[0].encoded_data_length=Number.MAX_SAFE_INTEGER+1);
bad('reject duplicate request id',x=>x.before[0].image_requests.push({...x.before[0].image_requests[0]}));
bad('reject unscrolled lazy page',x=>x.before[0].scrolled_to_end=false);
bad('reject unfinished network capture',x=>x.after[0].network_capture_complete=false);
bad('reject unverified visual parity',x=>x.after[0].visual_slots_preserved=false);
bad('reject mismatched before after permalink',x=>x.after[0].url='https://finalvestige.com/synthetic-other/');
bad('reject unknown post id',x=>x.before[0].post_id=999999);
bad('reject missing paired after page',x=>x.after=[]);
bad('reject bogus collector',x=>x.environment.collector='Unknown');
bad('reject invalid viewport',x=>x.environment.viewport_width=0);
bad('reject lack of disabled cache',x=>x.environment.cache='enabled');
bad('reject missing service worker bypass',x=>x.environment.service_workers_bypassed=false);
bad('reject missing browser timestamps',x=>x.environment.captured_at_before='nonsense');
