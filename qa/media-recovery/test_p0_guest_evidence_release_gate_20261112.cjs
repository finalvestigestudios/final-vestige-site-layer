'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {adjudicateP0,P0}=require('./p0_guest_evidence_release_gate_20261112.cjs');
const clone=x=>JSON.parse(JSON.stringify(x));
function packet(slot='418:1',status=404){const x=P0[slot];return {slot,post_id:x.post_id,page_url:x.page,
 published_original_src:x.src,siteqa_pr:154,method:'SITEQA154_CHROME_CDP_LOGGED_OUT_COLD',
 capture_git_blob_sha:'a'.repeat(40),screenshot_sha256:'b'.repeat(64),
 guest:{page_http_status:200,full_scroll_complete:true,network_capture_complete:true,
  cache_disabled:true,from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
  current_src:x.src,request_url:x.src,final_response_url:x.src,cdp_request_id:'req-1',
  response_event_provenance:'CDP_NETWORK_RESPONSE_RECEIVED',
  completion_event_provenance:'CDP_NETWORK_LOADING_FINISHED',final_status:status,
  natural_width:0,natural_height:0,image_decoded:false,
  viewport_css_width:390,viewport_css_height:844,dpr:2}};}
function review(slot='418:1'){return {slot,candidate_catalog:P0[slot].catalog,
 item_rights_evidence_url:P0[slot].catalog,asset_url:'https://www.history.uscg.mil/assets/proposed.jpg',
 asset_sha256:'c'.repeat(64),rights_review_git_blob_sha:'d'.repeat(40),
 item_level_reuse_permission_verified:true,credit_and_restrictions_recorded:true,
 scene_and_crop_reviewed_by_editor:true,staging_editor_approved:true,
 replacement_mode:'SAME_PHOTO',exact_photo_identity_verified:true,
 compared_screenshots_at_target_dpr:true,geometry:{native_width:1920,native_height:1080,
 output_width:960,output_height:540,painted_css_width:390,painted_css_height:219.375,dpr:2}};}
function held(change,match){const p=packet(),r=review();change(p,r);const a=adjudicateP0(p,r);
 assert.notEqual(a.status,'STAGING_REVIEW_PACKET_ELIGIBLE_NO_WRITE');if(match)assert.match(a.reason||'',match);
 assert.equal(a.production_write_allowed,false);assert.equal(a.third_party_cache_allowed,false);}
test('exact six original source URLs and pages pinned',()=>{
 assert.equal(Object.keys(P0).length,6);
 assert.deepEqual(Object.keys(P0),['285:5','285:2','287:5','418:1','418:2','407:1']);});
test('no packet cannot be called browser failure',()=>assert.equal(adjudicateP0({slot:'418:1'}).status,'HOLD'));
test('bare claimed BROWSER_CONFIRMED_BROKEN and SHA cannot stage',()=>{
 const a=adjudicateP0({slot:'418:1',site_qa_result:'BROWSER_CONFIRMED_BROKEN',
 site_qa_evidence_blob_sha:'b'.repeat(40),editor_staging_approved:true});assert.equal(a.status,'HOLD');});
test('real CDP-like failure evidence recorded but rights pending',()=>{
 const a=adjudicateP0(packet());assert.equal(a.status,'GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED');
 assert.equal(a.visitor_observation,'CDP_HTTP_FAILURE_WITH_ZERO_DECODED_PIXELS');});
test('200 successful decoded image kept, never stage a replacement',()=>{
 const p=packet('418:1',200);Object.assign(p.guest,{natural_width:960,natural_height:540,image_decoded:true});
 assert.equal(adjudicateP0(p,review()).status,'GUEST_IMAGE_LOADED_KEEP_ORIGINAL');});
test('200 unconfirmed decode fails closed',()=>held((p)=>{p.guest.final_status=200},/INCONSISTENT/));
test('200 explicitly recorded decoder error is an observed failure',()=>{
 const p=packet('418:1',200);p.guest.decode_error_recorded=true;
 assert.equal(adjudicateP0(p).visitor_observation,'CDP_200_EXPLICIT_DECODE_FAILURE');});
test('missing response event cannot be inferred from wrapper code',()=>held((p)=>{p.guest.response_event_provenance='WEB_OPEN_WRAPPER'},/MISSING_OR_UNBOUND/));
test('cached response rejected',()=>held(p=>{p.guest.from_disk_cache=true},/MISSING_OR_UNBOUND/));
test('missing cache signal rejected',()=>held(p=>{delete p.guest.from_memory_cache},/MISSING_OR_UNBOUND/));
test('original source swapped across image slots rejected',()=>held(p=>{p.published_original_src=P0['418:2'].src},/MISSING_OR_UNBOUND/));
test('page URL tampering rejected',()=>held(p=>{p.page_url='https://finalvestige.com/other/'},/MISSING_OR_UNBOUND/));
test('unverified redirect rejected',()=>held(p=>{p.guest.final_response_url='https://example.org/elsewhere.jpg'},/MISSING_OR_UNBOUND/));
test('linked completed redirect may be evaluated',()=>{
 const p=packet();p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
 p.guest.redirect_chain=[{url:p.guest.request_url,cdp_request_id:'req-1',response_status:302},{url:p.guest.final_response_url,cdp_request_id:'req-1',response_status:404}];
 assert.equal(adjudicateP0(p).status,'GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED');});
test('invalid screenshot hash rejected',()=>held(p=>{p.screenshot_sha256='x'.repeat(64)},/MISSING_OR_UNBOUND/));
test('HTTP 404 but positive decoded pixels cannot count as broken',()=>held(p=>{p.guest.natural_width=900},/INCONSISTENT/));
test('generic external candidate cannot silently replace recorded catalog',()=>held((p,r)=>{r.candidate_catalog='https://example.org/other.jpg'},/RIGHTS/));
test('rights assertion missing cannot stage',()=>held((p,r)=>{r.item_level_reuse_permission_verified=false},/RIGHTS/));
test('same photograph requires identity confirmation',()=>held((p,r)=>{r.exact_photo_identity_verified=false},/RIGHTS/));
test('editorial alternative must be disclosed and ALT revised',()=>held((p,r)=>{r.replacement_mode='DISCLOSED_EDITORIAL_ALTERNATIVE'},/RIGHTS/));
test('960px output insufficient for 640 CSS px at 2 DPR',()=>held((p,r)=>{r.geometry.painted_css_width=640},/960PX/));
test('upscaling from 819 physical pixels blocked',()=>held((p,r)=>{r.geometry.native_width=819},/960PX/));
test('distorted aspect ratio blocked',()=>held((p,r)=>{r.geometry.output_height=480},/960PX/));
test('staging screenshots at DPR are mandatory',()=>held((p,r)=>{r.compared_screenshots_at_target_dpr=false},/960PX/));
test('valid mock review is only staging packet, never cache or WordPress permission',()=>{
 const a=adjudicateP0(packet(),review());assert.equal(a.status,'GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED');
 assert.match(a.reason,/BYTE_BOUND_ARTIFACTS_REQUIRED/);
 assert.equal(a.production_write_allowed,false);assert.equal(a.wordpress_upload_allowed,false);
 assert.equal(a.third_party_cache_allowed,false);assert.equal(a.historical_42_broken_verified,false);
 assert.equal(a.sitewide_76_percent_verified,false);});
test('cleared editorial alternative still not a silent same-photo replacement',()=>{
 const p=packet(),r=review();r.replacement_mode='DISCLOSED_EDITORIAL_ALTERNATIVE';
 r.exact_photo_identity_verified=false;r.alternative_disclosed=true;
 r.revised_alt='Editorially selected archive photograph of the Scotch Cap shoreline';
 const a=adjudicateP0(p,r);assert.equal(a.status,'GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED');
 assert.match(a.reason,/BYTE_BOUND_ARTIFACTS_REQUIRED/);
 assert.equal(a.staging_reviewer_packet,null);});

test('unrelated image 404 is not attributed to pinned original',()=>held(p=>{
 p.guest.current_src=p.guest.request_url=p.guest.final_response_url='https://unrelated.example/broken.jpg';
},/MISSING_OR_UNBOUND/));
test('unrelated image successful load is not evidence pinned source loads',()=>{
 const p=packet('418:1',200);
 p.guest.current_src=p.guest.request_url=p.guest.final_response_url='https://unrelated.example/healthy.jpg';
 Object.assign(p.guest,{natural_width:960,natural_height:540,image_decoded:true});
 assert.equal(adjudicateP0(p).status,'HOLD');
});
test('swapped image currentSrc across P0 slots is rejected',()=>held(p=>{
 p.guest.current_src=p.guest.request_url=p.guest.final_response_url=P0['418:2'].src;
},/MISSING_OR_UNBOUND/));
test('unverified runtime rewrite requires Site QA source-binding proof',()=>held(p=>{
 p.guest.current_src=p.guest.request_url=p.guest.final_response_url=P0['418:1'].src+'?rewritten=1';
},/MISSING_OR_UNBOUND/));
test('bare redirect verified boolean cannot admit a failed image',()=>held(p=>{
 p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
},/MISSING_OR_UNBOUND/));
test('redirect array must begin at captured original URL',()=>held(p=>{
 p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
 p.guest.redirect_chain=[{url:'https://other.example/other.jpg',cdp_request_id:'req-1',response_status:302},{url:p.guest.final_response_url,cdp_request_id:'req-1',response_status:404}];
},/MISSING_OR_UNBOUND/));
test('redirect chain terminal status must match final observation',()=>held(p=>{
 p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
 p.guest.redirect_chain=[{url:p.guest.request_url,cdp_request_id:'req-1',response_status:302},{url:p.guest.final_response_url,cdp_request_id:'req-1',response_status:200}];
},/MISSING_OR_UNBOUND/));
test('redirect chain must bind same CDP request ID',()=>held(p=>{
 p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
 p.guest.redirect_chain=[{url:p.guest.request_url,cdp_request_id:'req-1',response_status:302},{url:p.guest.final_response_url,cdp_request_id:'other',response_status:404}];
},/MISSING_OR_UNBOUND/));
test('redirect cycles do not establish coherent request chain',()=>held(p=>{
 p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
 p.guest.redirect_chain=[{url:p.guest.request_url,cdp_request_id:'req-1',response_status:302},{url:p.guest.request_url,cdp_request_id:'req-1',response_status:302},{url:p.guest.final_response_url,cdp_request_id:'req-1',response_status:404}];
},/MISSING_OR_UNBOUND/));
test('redirect chain cannot invent HTTP success as intermediate redirect',()=>held(p=>{
 p.guest.final_response_url='https://example.org/other.jpg';p.guest.redirect_chain_verified=true;
 p.guest.redirect_chain=[{url:p.guest.request_url,cdp_request_id:'req-1',response_status:200},{url:p.guest.final_response_url,cdp_request_id:'req-1',response_status:404}];
},/MISSING_OR_UNBOUND/));
test('all six frozen originals still allow coherent synthetic failed-capture triage only',()=>{
 for(const slot of Object.keys(P0)){const a=adjudicateP0(packet(slot));
  assert.equal(a.status,'GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED');
  assert.equal(a.production_write_allowed,false);}
});
