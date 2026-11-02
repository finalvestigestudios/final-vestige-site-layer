'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {assessPair}=require('./weight_claim_pair_gate_20261102.cjs');
function fixture(){
 const pages=[];
 for(let j=0;j<61;j++){
  const id=1000+j,n=j<50?6:5,stored_images=[],network_images=[];
  for(let i=0;i<n;i++){
   const src='https://finalvestige.com/wp-content/uploads/2026/08/test-'+id+'-'+i+'.jpg';
   const rid='cdp-'+id+'-'+i;
   stored_images.push({image_key:id+':'+i,stored_url:src,current_src:src,request_url:src,request_id:rid,
    match:'exact_url_or_jetpack_origin',result:'loaded_in_probe_browser',verified_broken_in_browser:false,
    current_src_identity_verified:true,network_final_identity_verified:true,loaded_network_proof_verified:true,
    redirected_image_identity_unverified:false,complete:true,natural_width:960,http_status:200,
    response_mime_type:'image/jpeg',transfer_bytes:1000});
   network_images.push({request_id:rid,url:src,url_aliases:[],status:200,mime_type:'image/jpeg',encoded_data_length:1000,
    from_disk_cache:false,from_service_worker:false,was_cached:false});
  }
  pages.push({post_id:id,url:'https://finalvestige.com/story-'+id+'/',page_result:'inspected_browser',
   scroll_coverage:{complete:true,state:'full_height_scanned'},stored_image_count:n,stored_images,network_images,
   image_census:{complete:true,known_loaded_count:n,known_broken_count:0},
   article_wire_attribution_mode:'strict_cdp_request_id',article_wire_evidence_complete:true,
   article_image_wire_bytes_total:n*1000,matched_article_network_requests:n,unattributed_image_wire_bytes_total:0,
   unmeasured_article_network_requests:0,image_wire_bytes_total:n*1000,browser_wire_bytes_total:n*1000+100});
 }
 const base={mode:'all',requested_pages:61,status:'complete_browser_image_census',
  image_census_coverage:{complete:true,confirmed_broken_count:0},confirmed_broken_count:0,
  run_profile:{cache_disabled:true,service_worker_bypassed:true,scroll_step_px:720,
   scroll_wait_ms:220,settle_wait_ms:1000},browser_product:'Chrome/143.0',viewport:'390x844',
  created:'2026-11-01T12:00:00Z',pages};
 const next=JSON.parse(JSON.stringify(base));next.created='2026-11-02T12:00:00Z';
 return {base,next};
}
function adjust(run,value){
 for(const p of run.pages){
  for(const n of p.network_images)n.encoded_data_length=value;
  for(const s of p.stored_images)s.transfer_bytes=value;
  p.article_image_wire_bytes_total=p.stored_image_count*value;
  p.image_wire_bytes_total=p.stored_image_count*value;
  p.browser_wire_bytes_total=p.stored_image_count*value+100;
 }
}
function denied(mutate){
 const {base,next}=fixture();adjust(next,200);mutate(base,next);
 const r=assessPair(base,next);
 assert.equal(r.status,'NOT_MEASURED',JSON.stringify(r));
 assert.equal(r.savings_percent,null);assert.equal(r.claim_76_percent_supported,false);
}
test('61/355 full identical benchmark, 80% actual CDP wire reduction qualifies',()=>{
 const {base,next}=fixture();adjust(next,200);
 const r=assessPair(base,next);assert.equal(r.status,'MEASURED',JSON.stringify(r));
 assert.equal(r.measured_post_count,61);assert.equal(r.measured_slot_count,355);
 assert.equal(r.measured_sitewide_image_bytes_before,355000);
 assert.equal(r.measured_sitewide_image_bytes_after,71000);
 assert.equal(r.savings_bytes,284000);assert.equal(r.savings_percent,80);
 assert.equal(r.claim_76_percent_supported,true);
 assert.equal(r.production_changes_approved_by_this_tool,false);
});
test('75% is measured but cannot support the 76% claim',()=>{
 const {base,next}=fixture();adjust(next,250);const r=assessPair(base,next);
 assert.equal(r.status,'MEASURED');assert.equal(r.savings_percent,75);
 assert.equal(r.claim_76_percent_supported,false);
});
test('negative savings are reported without a positive spin',()=>{
 const {base,next}=fixture();adjust(next,1200);const r=assessPair(base,next);
 assert.equal(r.status,'MEASURED');assert.equal(r.savings_percent,-20);
 assert.equal(r.claim_76_percent_supported,false);
});
const bad=[
 ['priority-only scan is not site-wide',(b)=>{b.mode='priority'}],
 ['60 pages cannot prove 61',(b)=>{b.pages.pop()}],
 ['missing one stored slot',(b)=>{b.pages[0].stored_images.pop()}],
 ['a duplicate post id',(b)=>{b.pages[1].post_id=b.pages[0].post_id}],
 ['a duplicate slot key',(b)=>{b.pages[0].stored_images[1].image_key=b.pages[0].stored_images[0].image_key}],
 ['incomplete page scroll',(b)=>{b.pages[0].scroll_coverage.complete=false}],
 ['reported browser breakage',(b)=>{b.confirmed_broken_count=1}],
 ['a decoded image without network evidence',(b)=>{b.pages[0].stored_images[0].loaded_network_proof_verified=false}],
 ['a false CDP requestId',(b)=>{b.pages[0].stored_images[0].request_id='made-up'}],
 ['cached network bytes',(b)=>{b.pages[0].network_images[0].from_disk_cache=true}],
 ['service worker not bypassed',(b)=>{b.run_profile.service_worker_bypassed=false}],
 ['cache was not disabled',(b)=>{b.run_profile.cache_disabled=false}],
 ['the JPEG is an HTML error',(b)=>{b.pages[0].network_images[0].mime_type='text/html'}],
 ['a forged total article transfer claim',(b)=>{b.pages[0].article_image_wire_bytes_total=100}],
 ['missing image transfer count',(b)=>{b.pages[0].network_images[0].encoded_data_length=null}],
 ['browser version differs',(_b,n)=>{n.browser_product='Chrome/142.0'}],
 ['mobile vs desktop profiles',(_b,n)=>{n.viewport='1440x900'}],
 ['changed scroll profile',(_b,n)=>{n.run_profile.scroll_wait_ms=0}],
 ['candidate capture predates baseline',(_b,n)=>{n.created='2026-10-01T12:00:00Z'}],
 ['post URL changed',(_b,n)=>{n.pages[0].url='https://finalvestige.com/different/'}],
 ['unapproved WordPress image rewrite',(_b,n)=>{n.pages[0].stored_images[0].stored_url='https://finalvestige.com/wp-content/uploads/new.jpg'}],
 ['partial or fake 42 count',(b)=>{b.image_census_coverage.complete=false}],
 ['forged completed audit flag',(b)=>{b.pages[0].image_census.complete=false}],
 ['missing image network log',(b)=>{b.pages[0].network_images=[]}],
 ['zero baseline image budget',(b)=>{b.pages[0].article_image_wire_bytes_total=0}],
 ['unattributed same-photo duplicate request',(b)=>{
  const n={...b.pages[0].network_images[0],request_id:'preload-0'};
  b.pages[0].network_images.push(n);
 }],
];
for(const [label,fn]of bad)test('fail closed: '+label,()=>denied(fn));
test('wrong approval cannot bless a new image URL',()=>{
 const {base,next}=fixture();adjust(next,200);
 const s=next.pages[0].stored_images[0];s.stored_url='https://finalvestige.com/wp-content/uploads/next.jpg';
 const approval=[{image_key:s.image_key,before_source_url:base.pages[0].stored_images[0].stored_url,
  after_source_url:s.stored_url,rights_clearance_recorded:false,same_scene_crop_review_passed:true,
  no_upscale_confirmed:true,publication_authorized:true,derivative_width_px:960,derivative_height_px:540}];
 const r=assessPair(base,next,approval);
 assert.equal(r.status,'NOT_MEASURED');assert.ok(r.reasons.includes('unapproved_or_unverified_media_change:'+s.image_key));
});
