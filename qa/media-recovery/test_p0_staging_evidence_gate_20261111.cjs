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
  final_http_status:404,natural_width:0,natural_height:0,encoded_data_length:0,screenshot_evidence_id:'test-only'});
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
