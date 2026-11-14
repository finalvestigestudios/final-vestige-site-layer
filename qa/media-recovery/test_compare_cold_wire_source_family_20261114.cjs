'use strict';
/**
 * Regression for misleading wire-byte "savings" when an unbound second
 * transfer is a Jetpack/Commons alias of a measured historical source.
 * Synthetic CDP fixtures only. No network, binary downloads or CMS writes.
 */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {compareColdImageWire}=require('./compare_cold_image_wire_v1.cjs');
const original='https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg';
const jetpack='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg?fit=1024%2C768&ssl=1';
const jetpackSmall='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg?fit=480%2C360&ssl=1';
function fixture(bytes=1000,source=original,current=jetpack) {
 const s={image_key:'621:0',result:'loaded_in_probe_browser',match:'exact_url_or_jetpack_origin',
  verified_broken_in_browser:false,current_src_identity_verified:true,network_final_identity_verified:true,
  loaded_network_proof_verified:true,redirected_image_identity_unverified:false,complete:true,
  natural_width:960,natural_height:720,rendered_alt:'Malbone tunnel',http_status:200,
  response_mime_type:'image/jpeg',transfer_bytes:bytes,stored_url:source,current_src:current,
  request_url:current,request_id:'r1'};
 const n={request_id:'r1',url:current,status:200,mime_type:'image/jpeg',
  encoded_data_length:bytes,was_cached:false,from_disk_cache:false,
  from_memory_cache:false,from_service_worker:false};
 const p={post_id:621,url:'https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/',
  page_result:'inspected_browser',scroll_coverage:{complete:true,state:'full_height_scanned'},
  image_census:{complete:true,confirmed_broken_count:0},confirmed_broken_count:0,
  article_wire_evidence_complete:true,article_wire_evidence_errors:[],
  article_wire_attribution_mode:'strict_cdp_request_id',stored_image_count:1,
  stored_images:[s],network_images:[n],matched_article_network_requests:1,
  article_image_wire_bytes_total:bytes};
 return {status:'complete_browser_image_census',image_census_coverage:{complete:true,confirmed_broken_count:0},
  confirmed_broken_count:0,requested_pages:1,verified_pages:1,viewport:'390x844',mode:'priority',
  browser_product:'Chrome/140',run_profile:{cache_disabled:true,service_worker_bypassed:true},pages:[p]};
}
function extra(run, url, aliases=[]) {
 run.pages[0].network_images.push({request_id:'extra',url,url_aliases:aliases,
   status:200,mime_type:'image/jpeg',encoded_data_length:1200,
   was_cached:false,from_disk_cache:false,from_memory_cache:false,from_service_worker:false});
}
const pair=(b,a=fixture(240))=>compareColdImageWire(b,a);
function hold(r) {
 assert.equal(r.state,'HOLD',JSON.stringify(r));
 assert.equal(r.reduction_percent,null);
 assert.equal(r.sitewide_76_percent_claim_permitted,false);
 assert.ok(r.reasons.some(s=>s.includes('unbound_same_photo_request:621')),JSON.stringify(r.reasons));
}
test('valid unmodified synthetic CDP pair still reports only a 76% LAB comparison',()=>{
 const r=pair(fixture());assert.equal(r.state,'LAB_PAIR_MEASURED');
 assert.equal(r.reduction_percent,76);assert.equal(r.sitewide_76_percent_claim_permitted,false);
});
test('baseline extra direct WP original hidden behind current Jetpack resize is HOLD',()=>{
 const b=fixture();extra(b,original);hold(pair(b));
});
test('baseline second Jetpack width variant is HOLD',()=>{
 const b=fixture();extra(b,jetpackSmall);hold(pair(b));
});
test('candidate extra original is HOLD, not a measured pair',()=>{
 const a=fixture(240);extra(a,original);hold(pair(fixture(),a));
});
test('extra request alias pointing to direct original is HOLD',()=>{
 const b=fixture();extra(b,'https://unrelated.example.net/redirect.jpg',[original]);hold(pair(b));
});
test('reverse direct original with extra Jetpack request is HOLD',()=>{
 const b=fixture(1000,original,original);extra(b,jetpack);hold(pair(b,fixture(240,original,original)));
});
test('exact URL duplicate remains HOLD',()=>{
 const b=fixture();extra(b,jetpack);hold(pair(b));
});
test('Commons Special:Redirect to hashed upload variant is HOLD',()=>{
 const src='https://commons.wikimedia.org/wiki/Special:Redirect/file/Example_History.jpg';
 const target='https://upload.wikimedia.org/wikipedia/commons/a/ab/Example_History.jpg';
 const thumb='https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Example_History.jpg/480px-Example_History.jpg';
 const b=fixture(1000,src,target),a=fixture(240,src,target);extra(b,thumb);hold(pair(b,a));
});
test('independent theme/logo media is not incorrectly attributed to article',()=>{
 const b=fixture();extra(b,'https://finalvestige.com/wp-content/uploads/2026/08/site-logo.jpg');
 const r=pair(b);assert.equal(r.state,'LAB_PAIR_MEASURED');
 assert.equal(r.reduction_percent,76);
});
test('unparseable URL alias cannot claim an article transfer',()=>{
 const b=fixture();extra(b,'https://unrelated.example.net/other.jpg',['not-a-url']);
 assert.equal(pair(b).state,'LAB_PAIR_MEASURED');
});
test('unchanged source with only different CSS/DPR transformations still requires all request bytes',()=>{
 const b=fixture();extra(b,'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg?fit=960%2C720&ssl=1');
 hold(pair(b));
});