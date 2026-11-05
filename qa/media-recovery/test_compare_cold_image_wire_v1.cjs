'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {compareColdImageWire}=require('./compare_cold_image_wire_v1.cjs');
const copy=x=>JSON.parse(JSON.stringify(x));
function fixture(bytes=1000){
 const src='https://finalvestige.com/wp-content/uploads/2026/08/test.png';
 const key='34:0';
 const slot={image_key:key,result:'loaded_in_probe_browser',match:'exact_url_or_jetpack_origin',
 verified_broken_in_browser:false,current_src_identity_verified:true,network_final_identity_verified:true,
 loaded_network_proof_verified:true,redirected_image_identity_unverified:false,complete:true,
 natural_width:960,http_status:200,response_mime_type:'image/png',transfer_bytes:bytes,stored_url:src,
 current_src:src,request_url:src,request_id:'r1'};
 const page={post_id:34,url:'https://finalvestige.com/2026/08/01/post/',page_result:'inspected_browser',
 scroll_coverage:{complete:true,state:'full_height_scanned'},image_census:{complete:true,confirmed_broken_count:0},
 confirmed_broken_count:0,article_wire_evidence_complete:true,article_wire_evidence_errors:[],
 article_wire_attribution_mode:'strict_cdp_request_id',stored_image_count:1,stored_images:[slot],
 matched_article_network_requests:1,article_image_wire_bytes_total:bytes,
 network_images:[{request_id:'r1',url:src,status:200,mime_type:'image/png',encoded_data_length:bytes,
 was_cached:false,from_disk_cache:false,from_service_worker:false}]};
 return {status:'complete_browser_image_census',image_census_coverage:{complete:true,confirmed_broken_count:0},
 confirmed_broken_count:0,requested_pages:1,verified_pages:1,viewport:'390x844',mode:'priority',
 browser_product:'Chrome/140',run_profile:{cache_disabled:true,service_worker_bypassed:true},pages:[page]};
}
const compare=(mutBefore,mutAfter)=>{const b=fixture(),a=fixture(240);mutBefore?.(b);mutAfter?.(a);return compareColdImageWire(b,a)};
const hold=(name,mutBefore,mutAfter,why)=>test(name,()=>{const r=compare(mutBefore,mutAfter);assert.equal(r.state,'HOLD');assert.equal(r.reduction_percent,null);assert.equal(r.sitewide_76_percent_claim_permitted,false);if(why)assert.ok(r.reasons.some(x=>x.includes(why)),JSON.stringify(r.reasons))});
test('1000 vs 240 exact verified cold bytes = 76%, but not site-wide proof',()=>{
 const r=compare();assert.equal(r.state,'LAB_PAIR_MEASURED');assert.equal(r.reduction_percent,76);assert.equal(r.at_least_76_percent_in_this_pair,true);assert.equal(r.sitewide_76_percent_claim_permitted,false);assert.equal(r.production_repair_claim_permitted,false);
});
test('reductions below threshold remain measured but not claimed',()=>{const r=compare(null,a=>{a.pages[0].stored_images[0].transfer_bytes=500;a.pages[0].network_images[0].encoded_data_length=500;a.pages[0].article_image_wire_bytes_total=500});assert.equal(r.reduction_percent,50);assert.equal(r.at_least_76_percent_in_this_pair,false)});
test('increased bytes produce a negative reduction',()=>{const r=compare(null,a=>{a.pages[0].stored_images[0].transfer_bytes=1200;a.pages[0].network_images[0].encoded_data_length=1200;a.pages[0].article_image_wire_bytes_total=1200});assert.equal(r.reduction_percent,-20)});
hold('no invented 76% when baseline has a broken image',b=>{b.pages[0].stored_images[0].result='confirmed_broken_in_probe_browser'},null,'unverified_or_broken_image');
hold('missing viewport match',null,a=>{a.viewport='1440x900'},'unmatched_browser');
hold('cached candidate never counts',null,a=>{a.pages[0].network_images[0].from_disk_cache=true},'uncached_cdp');
hold('offline service-worker probe not acceptable',b=>{b.run_profile.service_worker_bypassed=false},null,'uncached_run');
hold('fake network byte summary rejected',null,a=>{a.pages[0].article_image_wire_bytes_total=1},'article_byte_total');
hold('CDP request mismatch rejected',null,a=>{a.pages[0].stored_images[0].request_id='unknown'},'uncached_cdp');
hold('duplicate CDP request IDs rejected',b=>{b.pages[0].network_images.push(copy(b.pages[0].network_images[0]))},null,'duplicate_or_missing_cdp');
hold('extra same-photo preload rejected',b=>{b.pages[0].network_images.push({...copy(b.pages[0].network_images[0]),request_id:'preload'})},null,'unbound_same_photo');
hold('partial scan rejected',b=>{b.pages[0].scroll_coverage.complete=false},null,'page_or_scroll');
hold('wrong page URL rejected',null,a=>{a.pages[0].url='https://finalvestige.com/not-original'},'post_url_or_image_slot');
hold('new missing slot rejected',null,a=>{a.pages[0].stored_images[0].image_key='34:1'},'post_url_or_image_slot');
hold('page broken-count declared rejects comparison',b=>{b.pages[0].confirmed_broken_count=1},null,'page_or_scroll');
hold('census incompleteness rejected',b=>{b.image_census_coverage.complete=false},null,'census_or_image_failure');
hold('unattributed source URL is invalid',b=>{b.pages[0].stored_images[0].current_src='not-a-url'},null,'unverified_or_broken_image');
hold('mime text/html rejected',null,a=>{a.pages[0].network_images[0].mime_type='text/html'},'uncached_cdp');
hold('missing network packet rejected',null,a=>{a.pages[0].network_images=[]},'uncached_cdp');
hold('missing bytes rejected',null,a=>{a.pages[0].stored_images[0].transfer_bytes=null},'unverified_or_broken_image');
hold('a document served from cache rejects',b=>{b.run_profile.cache_disabled=false},null,'uncached_run');
