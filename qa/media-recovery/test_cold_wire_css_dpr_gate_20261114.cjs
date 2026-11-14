'use strict';
/** Source-only synthetic CDP fixtures. No browser/network or WordPress actions. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {compareColdImageWire}=require('./compare_cold_image_wire_v1.cjs');
const {classifyImages}=require('./browser_probe_core.cjs');
function fixture(bytes=1000,w=1600,h=1200,cw=390,ch=292,viewport='390x844') {
 const src='https://finalvestige.com/wp-content/uploads/2026/08/test.jpg';
 const slot={image_key:'34:0',result:'loaded_in_probe_browser',match:'exact_url_or_jetpack_origin',
  verified_broken_in_browser:false,current_src_identity_verified:true,network_final_identity_verified:true,
  loaded_network_proof_verified:true,redirected_image_identity_unverified:false,complete:true,
  natural_width:w,natural_height:h,css_width_px:cw,css_height_px:ch,rendered_alt:'historic',
  http_status:200,response_mime_type:'image/jpeg',transfer_bytes:bytes,
  stored_url:src,current_src:src,request_url:src,request_id:'r1'};
 const page={post_id:34,url:'https://finalvestige.com/2026/08/01/post/',page_result:'inspected_browser',
  scroll_coverage:{complete:true,state:'full_height_scanned'},
  image_census:{complete:true,confirmed_broken_count:0},confirmed_broken_count:0,
  article_wire_evidence_complete:true,article_wire_evidence_errors:[],
  article_wire_attribution_mode:'strict_cdp_request_id',stored_image_count:1,
  stored_images:[slot],matched_article_network_requests:1,article_image_wire_bytes_total:bytes,
  network_images:[{request_id:'r1',url:src,status:200,mime_type:'image/jpeg',
   encoded_data_length:bytes,was_cached:false,from_disk_cache:false,
   from_memory_cache:false,from_service_worker:false}]};
 return {status:'complete_browser_image_census',image_census_coverage:{complete:true,confirmed_broken_count:0},
  confirmed_broken_count:0,requested_pages:1,verified_pages:1,viewport,mode:'priority',
  browser_product:'Chrome/140',run_profile:{cache_disabled:true,service_worker_bypassed:true},pages:[page]};
}
const compare=(b,a)=>compareColdImageWire(b||fixture(),a||fixture(240,960,720));
function hold(name,b,a,reason) {
 test(name,()=>{const r=compare(b,a);assert.equal(r.state,'HOLD',JSON.stringify(r));
  assert.equal(r.reduction_percent,null);assert.equal(r.sitewide_76_percent_claim_permitted,false);
  assert.ok(r.reasons.some(x=>x.includes(reason)),JSON.stringify(r.reasons));});
}
test('collector exposes actual rounded CSS box, never inventing a width',()=>{
 const src='https://finalvestige.com/wp-content/uploads/2026/08/test.jpg';
 const stored=[{key:'34:0',source_url:src,alt:'historic'}];
 const rendered=[{index:0,src,currentSrc:src,alt:'historic',complete:true,
  naturalWidth:1600,naturalHeight:1200,rectWidth:390,rectHeight:292}];
 const req=[{request_id:'r1',url:src,status:200,mime_type:'image/jpeg',encodedDataLength:1000,
  was_cached:false,from_disk_cache:false,from_memory_cache:false,from_service_worker:false}];
 const r=classifyImages(stored,rendered,req,true)[0];
 assert.equal(r.result,'loaded_in_probe_browser');assert.equal(r.css_width_px,390);assert.equal(r.css_height_px,292);
 const missing=classifyImages(stored,[{...rendered[0],rectWidth:0,rectHeight:0}],req,true)[0];
 assert.equal(missing.css_width_px,null);assert.equal(missing.css_height_px,null);
});
test('mobile CSS 390 at DPR2: 960px rendition preserves required 780px display detail',()=>{
 const r=compare();assert.equal(r.state,'LAB_PAIR_MEASURED',JSON.stringify(r));
 assert.equal(r.reduction_percent,76);assert.equal(r.sitewide_76_percent_claim_permitted,false);
 assert.equal(r.visual_parity_verified,false);
});
hold('mobile CSS 500 at DPR2: 960px rendition is too small',
 fixture(1000,1600,1200,500,375),fixture(240,960,720,500,375),'candidate_display_density_regression');
hold('mobile CSS 390 at DPR2: 600px rendition is too small',
 fixture(),fixture(240,600,450),'candidate_display_density_regression');
hold('mobile older CDP export missing CSS cannot claim bytes',
 fixture(),fixture(240,960,720,undefined,292),'unverified_or_broken_image');
hold('mobile zero CSS box is unverified',fixture(),fixture(240,960,720,0,292),'unverified_or_broken_image');
hold('CSS box shrinkage must not disguise byte savings',
 fixture(),fixture(240,960,720,300,225),'rendered_css_geometry_changed');
hold('CSS height drift must not disguise changed crop',
 fixture(),fixture(240,960,720,390,260),'rendered_css_geometry_changed');
test('desktop CSS 800 at DPR1 allows a 960px asset',()=>{
 const b=fixture(1000,1600,1200,800,600,'1440x900');
 const a=fixture(240,960,720,800,600,'1440x900');
 const r=compare(b,a);assert.equal(r.state,'LAB_PAIR_MEASURED',JSON.stringify(r));
});
hold('desktop CSS 1024 at DPR1 rejects a 960px asset',
 fixture(1000,1600,1200,1024,768,'1440x900'),
 fixture(240,960,720,1024,768,'1440x900'),'candidate_display_density_regression');
test('pre-existing low-density 819px baseline may be preserved, not downgraded',()=>{
 const r=compare(fixture(1000,819,614,500,375),fixture(240,819,614,500,375));
 assert.equal(r.state,'LAB_PAIR_MEASURED',JSON.stringify(r));assert.equal(r.visual_parity_verified,false);
});
hold('do not downgrade a pre-existing 819px baseline when 2x density is impossible',
 fixture(1000,819,614,500,375),fixture(240,800,600,500,375),'candidate_display_density_regression');
