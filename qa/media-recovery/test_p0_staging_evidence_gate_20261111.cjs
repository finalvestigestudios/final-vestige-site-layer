'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {P0_ORDER,guestFinding,candidateReview,compileRecovery} = require('./p0_staging_evidence_gate_20261111.cjs');
const source = require('./browser_handoff_6_p0_15_oversize_20261110.json');
const img = source.p0_queue[0];
const good = () => ({source_slot:img.slot,post_id:img.post_id,stored_original_src:img.original_src,
  method:'CHROME_CDP_LOGGED_OUT_COLD',network_capture_complete:true,
  current_src:img.original_src,request_url:img.original_src,final_response_url:img.original_src,
  was_cached:false,from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
  final_http_status:404,natural_width:0,natural_height:0,encoded_data_length:0,screenshot_evidence_id:'test-only',
  page_url:'https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/',
  page_http_status:200,page_census_complete:true,full_scroll_complete:true,
  stored_inline_ordinal:5,dom_img_src:img.original_src,
  capture_run_id:'synthetic-run',request_id:'synthetic-request',
  response_request_id:'synthetic-request',dom_element_request_id:'synthetic-request',
  screenshot_sha256:'b'.repeat(64)});
const approval = () => ({source_slot:img.slot,original_src:img.original_src,
  candidate_catalog_url:img.catalog_candidate_url,
  item_rights_evidence_url:'https://example.org/rights/1',rights_reviewer:'human-reviewer',
  rights_reviewed_date:'2026-11-10',commercial_republication_cleared:true,
  attribution_plan_checked:true,exact_photographic_identity_verified:true,
  historical_date_and_scene_verified:true,alt_and_caption_editor_approved:true,
  crop_and_layout_editor_approved:true,candidate_asset_sha256:'a'.repeat(64),
  native_width:819,native_height:614,output_width:819,output_height:614});
test('frozen P0 inventory and 15 media originals',()=>{
  assert.deepEqual(P0_ORDER,source.p0_queue.map(x=>x.slot));
  assert.equal(source.oversized_media.length,15);
});
test('no browser evidence is unverified',()=>assert.equal(guestFinding(img).verdict,'UNVERIFIED'));
test('no approvals imply no staging',()=>assert.equal(candidateReview(img,null,'CONFIRMED_GUEST_BROKEN').staging_permitted,false));
for(const field of ['source_slot','post_id','stored_original_src'])
  test('guest mismatched '+field,()=>{const e=good();e[field]='wrong';assert.equal(guestFinding(img,e).verdict,'HOLD')});
for(const field of ['method','network_capture_complete','current_src','request_url','final_response_url'])
  test('guest network incomplete '+field,()=>{const e=good();e[field]=null;assert.equal(guestFinding(img,e).verdict,'HOLD')});
for(const field of ['was_cached','from_disk_cache','from_memory_cache','from_service_worker'])
  test('cached or ambiguous '+field,()=>{const e=good();e[field]=true;assert.equal(guestFinding(img,e).verdict,'HOLD');e[field]=null;assert.equal(guestFinding(img,e).verdict,'HOLD')});
for(const field of ['final_http_status','natural_width','natural_height','encoded_data_length'])
  test('missing numeric '+field,()=>{const e=good();e[field]=null;assert.equal(guestFinding(img,e).verdict,'HOLD')});
test('missing screenshot holds',()=>{const e=good();e.screenshot_evidence_id=null;assert.equal(guestFinding(img,e).verdict,'HOLD')});
test('synthetic cold guest 404 + zero dimensions confirms',()=>assert.equal(guestFinding(img,good()).verdict,'CONFIRMED_GUEST_BROKEN'));
test('success with positive image dimensions displays',()=>{const e=good();e.final_http_status=200;e.natural_width=819;e.natural_height=614;assert.equal(guestFinding(img,e).verdict,'CONFIRMED_GUEST_DISPLAYED')});
test('200 with zero dimensions inconclusive',()=>{const e=good();e.final_http_status=200;assert.equal(guestFinding(img,e).verdict,'HOLD')});
test('404 with positive dimensions inconclusive',()=>{const e=good();e.natural_width=819;e.natural_height=614;assert.equal(guestFinding(img,e).verdict,'HOLD')});
for(const field of ['source_slot','original_src','candidate_catalog_url'])
  test('approval source mismatch '+field,()=>{const e=approval();e[field]='wrong';assert.equal(candidateReview(img,e,'CONFIRMED_GUEST_BROKEN').state,'HOLD')});
for(const field of ['item_rights_evidence_url','rights_reviewer','rights_reviewed_date','commercial_republication_cleared','attribution_plan_checked'])
  test('missing independent rights '+field,()=>{const e=approval();e[field]=null;assert.equal(candidateReview(img,e,'CONFIRMED_GUEST_BROKEN').state,'HOLD')});
for(const field of ['exact_photographic_identity_verified','historical_date_and_scene_verified','alt_and_caption_editor_approved','crop_and_layout_editor_approved','candidate_asset_sha256'])
  test('missing identity/editor '+field,()=>{const e=approval();e[field]=false;assert.equal(candidateReview(img,e,'CONFIRMED_GUEST_BROKEN').state,'HOLD')});
for(const field of ['native_width','native_height','output_width','output_height'])
  test('missing geometry '+field,()=>{const e=approval();e[field]=null;assert.equal(candidateReview(img,e,'CONFIRMED_GUEST_BROKEN').state,'HOLD')});
test('819px Commons source never upscaled to 960',()=>{const e=approval();e.output_width=960;assert.equal(candidateReview(img,e,'CONFIRMED_GUEST_BROKEN').state,'HOLD')});
test('16:9 crop of 4:3 source rejected',()=>{const e=approval();e.output_height=461;assert.equal(candidateReview(img,e,'CONFIRMED_GUEST_BROKEN').state,'HOLD')});
test('synthetic full approval never authorizes staging or production write',()=>{
  const v=candidateReview(img,approval(),'CONFIRMED_GUEST_BROKEN');
  assert.equal(v.state,'ELIGIBLE_FOR_HUMAN_STAGING_REVIEW_ONLY');
  assert.equal(v.staging_permitted,false);assert.equal(v.production_permitted,false);
});
test('evidence-free actual bridge reports zero confirmed',()=>{
  const report=compileRecovery(source);assert.equal(report.verified_broken_in_supplied_guest_evidence,0);
  assert.equal(report.actual_wire_saving_pct,null);assert.equal(report.priority.length,6);
  assert.equal(report.oversized.length,15);
  assert.equal(report.priority.every(x=>x.candidate_review.staging_permitted===false),true);
});
test('one synthetic browser failure is isolated to the correct slot',()=>{
  const report=compileRecovery(source,{[img.slot]:good()});
  assert.equal(report.verified_broken_in_supplied_guest_evidence,1);
  assert.equal(report.priority[0].candidate_review.state,'HOLD');
  assert.equal(report.priority[1].guest_browser.verdict,'UNVERIFIED');
});
test('source mismatch fails inventory closed',()=>{
 const copy=JSON.parse(JSON.stringify(source));copy.p0_queue.reverse();
 assert.throws(()=>compileRecovery(copy));
});
test('15-original mismatch fails closed',()=>{
 const copy=JSON.parse(JSON.stringify(source));copy.oversized_media.pop();
 assert.throws(()=>compileRecovery(copy));
});

test('synthetic unrelated cold 404 cannot convict the published original',()=>{
  const e=good();const wrong='https://unrelated.invalid/missing.jpg';
  e.current_src=wrong;e.request_url=wrong;e.final_response_url=wrong;
  assert.equal(guestFinding(img,e).verdict,'HOLD');
  assert.equal(guestFinding(img,e).reason,'SELECTED_SOURCE_NOT_THE_PUBLISHED_ORIGINAL');
});
test('synthetic same-origin alternate path 404 cannot convict original',()=>{
  const e=good();const wrong=img.original_src.slice(0,img.original_src.lastIndexOf('/')+1)+'different.jpg';
  e.current_src=wrong;e.request_url=wrong;e.final_response_url=wrong;
  assert.equal(guestFinding(img,e).verdict,'HOLD');
});
test('synthetic catalog image 404 cannot substitute for failed original',()=>{
  const e=good();e.current_src=img.catalog_candidate_url;
  e.request_url=e.current_src;e.final_response_url=e.current_src;
  assert.equal(guestFinding(img,e).verdict,'HOLD');
});
test('synthetic successful 200 different image not evidence original displays',()=>{
  const e=good();const other='https://unrelated.invalid/loaded.jpg';
  e.current_src=other;e.request_url=other;e.final_response_url=other;
  e.final_http_status=200;e.natural_width=819;e.natural_height=614;
  assert.equal(guestFinding(img,e).verdict,'HOLD');
});
test('alternate currentSrc cannot inflate compileRecovery broken count',()=>{
  const e=good();const other='https://unrelated.invalid/404.jpg';
  e.current_src=other;e.request_url=other;e.final_response_url=other;
  const report=compileRecovery(source,{[img.slot]:e});
  assert.equal(report.verified_broken_in_supplied_guest_evidence,0);
  assert.equal(report.priority[0].guest_browser.reason,'SELECTED_SOURCE_NOT_THE_PUBLISHED_ORIGINAL');
});


function frozenMutation(name,mutate) {
  test('source-custody guard: '+name,()=>{
    const copy=JSON.parse(JSON.stringify(source));
    mutate(copy);
    assert.throws(()=>compileRecovery(copy));
  });
}
frozenMutation('substituted P0 original URL',x=>x.p0_queue[0].original_src='https://fake.invalid/substituted.jpg');
frozenMutation('substituted same-publisher catalog URL',x=>x.p0_queue[2].catalog_candidate_url='https://media.stpetecatalyst.com/uploads/2020/04/different.jpg');
frozenMutation('invented P0 retriever outcome',x=>x.p0_queue[0].retriever_only.wrapper_code=200);
frozenMutation('fabricated P0 guest HTTP 404 in read-only ledger',x=>x.p0_queue[0].guest_http_status=404);
frozenMutation('claimed prior rights approval',x=>x.p0_queue[0].reuse_rights_cleared=true);
frozenMutation('invented 960-pixel dimension',x=>x.p0_queue[0].conditional_960px=[960,720]);
frozenMutation('changed oversized original media URL',x=>x.oversized_media[0].original_url='https://finalvestige.com/wp-content/uploads/new.jpg');
frozenMutation('inflated oversized stored size',x=>x.oversized_media[0].stored_original_bytes=999999999);
frozenMutation('manipulated native pixel dimensions',x=>x.oversized_media[0].native_px=[100,100]);
frozenMutation('deleted inline Malbone association',x=>x.oversized_media[1].inline_post_ids=[]);
frozenMutation('replaced Jetpack published delivery reference',x=>x.oversized_media[0].published_direct_srcs=['https://finalvestige.com/other.jpg']);
frozenMutation('invented oversized measured guest byte count',x=>x.oversized_media[1].guest_wire_bytes=4000000);
frozenMutation('fabricated source-only confirmed 42 failures',x=>x.release.claim_42_verified=true);
frozenMutation('fabricated 76 percent measured success',x=>x.methodology.measured_saving_pct=76);
frozenMutation('mixed 61-post and 66-post counts',x=>x.cohorts.historical.posts=66);
frozenMutation('changed worklist blob without reconciliation',x=>x.authority.worklist.blob_sha='f'.repeat(40));
test('unchanged source-only snapshot still valid',()=>assert.equal(compileRecovery(source).verified_broken_in_supplied_guest_evidence,0));

test('verified CMS permalink and stored ordinal fixture is precise',()=>{
  assert.equal(good().page_url,'https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/');
  assert.equal(good().stored_inline_ordinal,5);
});
for (const [name,change,why] of [
 ['other article at same origin',e=>e.page_url='https://finalvestige.com/other/', 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['wrong published post permalink',e=>e.page_url='https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/', 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['missing page permalink',e=>e.page_url=null, 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['non-successful article response',e=>e.page_http_status=404, 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['incomplete page image census',e=>e.page_census_complete=false, 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['incomplete lazy-image scroll',e=>e.full_scroll_complete=false, 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['other stored image ordinal',e=>e.stored_inline_ordinal=2, 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['different DOM original source',e=>e.dom_img_src='https://unrelated.invalid/image.jpg', 'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'],
 ['missing run identifier',e=>e.capture_run_id=null, 'CDP_REQUEST_DOM_SCREENSHOT_CHAIN_NOT_PROVEN'],
 ['missing CDP request ID',e=>e.request_id=null, 'CDP_REQUEST_DOM_SCREENSHOT_CHAIN_NOT_PROVEN'],
 ['response belongs to other request',e=>e.response_request_id='other-request', 'CDP_REQUEST_DOM_SCREENSHOT_CHAIN_NOT_PROVEN'],
 ['DOM image bound to other request',e=>e.dom_element_request_id='other-request', 'CDP_REQUEST_DOM_SCREENSHOT_CHAIN_NOT_PROVEN'],
 ['invalid screenshot hash',e=>e.screenshot_sha256='no-hash', 'CDP_REQUEST_DOM_SCREENSHOT_CHAIN_NOT_PROVEN']
]) test('article and CDP lineage: '+name,()=>{
  const e=good();change(e);
  const result=guestFinding(img,e);
  assert.equal(result.verdict,'HOLD');assert.equal(result.reason,why);
  assert.equal(compileRecovery(source,{[img.slot]:e}).verified_broken_in_supplied_guest_evidence,0);
});
