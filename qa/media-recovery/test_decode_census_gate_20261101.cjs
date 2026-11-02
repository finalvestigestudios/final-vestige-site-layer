'use strict';
/** Offline, synthetic browser-evidence regression cases. No HTTP, image copies, or CMS writes. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {proofKind,assessPage,assessRun}=require('./image_census_coverage_core.cjs');
const url='https://www.history.uscg.mil/Portals/6/scotch-cap.jpg';
const decodedFailure=()=>({
 image_key:'418:2',stored_url:url,current_src:url,request_url:url,
 current_src_identity_verified:true,network_final_identity_verified:true,
 loaded_network_proof_verified:true,redirected_image_identity_unverified:false,
 complete:true,natural_width:0,verified_broken_in_browser:true,
 result:'confirmed_broken_in_probe_browser',visual_failure_kind:'image_decode_failure',
 http_status:200,response_mime_type:'image/jpeg',transfer_bytes:2048,network_failure:null
});
const page=(images=[decodedFailure()])=>({
 post_id:418,page_result:'inspected_browser',
 scroll_coverage:{complete:true,state:'full_height_scanned'},
 stored_image_count:images.length,stored_images:images
});
test('real 200 image MIME plus uncacheable proof and failed decode counts as a broken image',()=>{
 assert.equal(proofKind(decodedFailure()),'broken');
});
test('complete article census includes evidence-backed 200 image decode failure',()=>{
 const p=assessPage(page());
 assert.equal(p.complete,true);assert.equal(p.known_broken_count,1);
 assert.equal(p.confirmed_broken_count,1);assert.deepEqual(p.unresolved_keys,[]);
});
test('complete site crawl aggregates the decoded failure',()=>{
 const p=assessRun([page()],1);assert.equal(p.complete,true);
 assert.equal(p.confirmed_broken_count,1);
});
for(const [label,fields] of [
 ['missing final request identity',{network_final_identity_verified:false}],
 ['missing independent CDP loaded proof',{loaded_network_proof_verified:false}],
 ['changed final historical photograph',{request_url:'https://www.history.uscg.mil/Portals/6/other-photo.jpg'}],
 ['non-image 200 response',{response_mime_type:'text/html'}],
 ['zero encoded transfer',{transfer_bytes:0}],
 ['negative encoded transfer',{transfer_bytes:-1}],
 ['missing encoded transfer',{transfer_bytes:null}],
 ['partial HTTP 206',{http_status:206}],
 ['wrong failure kind',{visual_failure_kind:'unknown'}],
 ['unverified redirect',{redirected_image_identity_unverified:true}],
 ['reported network failure',{network_failure:'net::ERR_FAILED'}],
 ['incomplete image element',{complete:false}],
 ['changed stored source',{stored_url:'https://www.history.uscg.mil/Portals/6/unrelated.jpg'}],
 ['image actually decoded',{natural_width:860}],
 ['unverified browser failure',{verified_broken_in_browser:null}],
 ['incorrect decoded state',{result:'zero_intrinsic_width_needs_review'}],
 ['missing image request URL',{request_url:null}],
 ['offsite currentSrc substitution',{current_src:'https://example.org/unrelated.jpg'}]
])test('unsubstantiated decode failure stays unresolved: '+label,()=>{
 const v={...decodedFailure(),...fields};
 assert.equal(proofKind(v),'unresolved');
 assert.equal(assessPage(page([v])).confirmed_broken_count,null);
});
test('incomplete browser scroll never establishes sitewide broken count',()=>{
 const p=page();p.scroll_coverage={complete:false,state:'not_finished'};
 assert.equal(assessPage(p).confirmed_broken_count,null);
 assert.equal(assessRun([p],1).confirmed_broken_count,null);
});
test('blocked or misleading page never establishes browser broken count',()=>{
 const p=page();p.page_result='blocked_or_unverified_page';
 assert.equal(assessPage(p).confirmed_broken_count,null);
});
test('different known broken classifications continue to count',()=>{
 const r=decodedFailure();
 const http={...r,image_key:'418:3',visual_failure_kind:'http_error',http_status:404,response_mime_type:'text/html'};
 const html={...r,image_key:'418:4',visual_failure_kind:'non_image_error_payload',response_mime_type:'text/html'};
 const p=assessPage(page([r,http,html]));
 assert.equal(p.complete,true);assert.equal(p.confirmed_broken_count,3);
});
