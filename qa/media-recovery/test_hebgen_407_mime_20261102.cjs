'use strict';
/** Run: node qa/media-recovery/test_hebgen_407_mime_20261102.cjs */
const assert = require('node:assert/strict');
const { validate } = require('./validate_hebgen_407_mime_20261102.cjs');
const audit = require('./hebgen_407_fault_scarp_mime_20261102.json');
function runTests() {
  const failed = []; let passed = 0;
  function check(name, run) { try { run(); passed++; } catch (e) { failed.push({name, error: String(e)}); } }
  const clone = () => JSON.parse(JSON.stringify(audit));
  check('authentic_evidence_accepted', () => assert.deepEqual(validate(audit), []));
  const mutations = [
    ['not_an_object', a => a = null],
    ['unknown_slot', a => {a.image_key = '407:2';}],
    ['made_up_post', a => {a.post.id=999;}],
    ['fake_live_verification',a=>{a.post.verification='guessed';}],
    ['swapped_source_census_sha',a=>{a.frozen_source.git_blob_sha='000000';}],
    ['changed_original_url',a=>{a.published.src+='?copy=1';}],
    ['changed_existing_alt',a=>{a.published.alt='Some random image';}],
    ['invented_origin_http_404',a=>{a.exact_published_source_observation.origin_http_status=404;}],
    ['wrapper_error_misrepresented_as_visitor_400',a=>{a.exact_published_source_observation.visitor_browser_http_status=400;}],
    ['source_retriever_403_instead_of_octet',a=>{a.exact_published_source_observation.result='RETRIEVER_FETCH_403';}],
    ['wrong_mime',a=>{a.exact_published_source_observation.reported_media_type='image/jpeg';}],
    ['different_archive_record',a=>{a.official_candidate.record_url='https://example.org/';}],
    ['different_linked_original',a=>{a.official_candidate.linked_original_url='https://example.org/a.jpg';}],
    ['made_up_byte_hash',a=>{a.official_candidate.source_binary_sha256='deadbeef';}],
    ['pretend_binary_match',a=>{a.official_candidate.exact_published_binary_match_verified=true;}],
    ['pretend_original_pixel_dimensions_verified',a=>{a.official_candidate.original_master_dimensions_verified_from_binary=true;}],
    ['upscaled_derivative',a=>{a.derivative.conditional_width_px=1200;}],
    ['wrong_aspect',a=>{a.derivative.conditional_height_px=600;}],
    ['unreviewed_scene_swap',a=>{a.editorial.same_exact_crop_verified=true;}],
    ['unlicensed_rehosting',a=>{a.gates.rehost_permission_confirmed=true;}],
    ['production_post_rewrite',a=>{a.gates.wp_post_edit_authorized=true;}],
    ['download_authorized',a=>{a.gates.download_authorized=true;}],
    ['fabricated_guest_http_200',a=>{a.guest_browser.final_http_status=200;}],
    ['fabricated_natwidth',a=>{a.guest_browser.natural_width_px=1000;}],
    ['fabricated_transfer_bytes',a=>{a.guest_browser.transfer_bytes=42100;}],
    ['fabricated_screenshot',a=>{a.guest_browser.screenshot='passed';}],
    ['claims_42_confirmed',a=>{a.claim_context.reported_sitewide_broken_42_confirmed=true;}],
    ['claims_76pct_measured',a=>{a.claim_context.reported_76pct_savings_measured=true;}],
    ['subscription_cost',a=>{a.gates.subscription_spend_usd=1;}]
  ];
  for (const [name,mutate] of mutations) check(name,()=>{let x=clone(); const returned=mutate(x); if (returned !== undefined) x=returned; assert.ok(validate(x).length>0, name+' must fail closed');});
  return {passed,failed};
}
if (require.main === module) { const r=runTests(); process.stdout.write(JSON.stringify(r)+'\n'); if (r.failed.length) process.exitCode=1; }
module.exports={runTests};
