'use strict';

/**
 * Offline-only media-recovery decision contract.
 * Requires independently collected, complete, logged-out cold Chrome evidence.
 * Never fetches images or authorizes a WordPress/production mutation.
 * Source inventory: browser_handoff_6_p0_15_oversize_20261110.json.
 */
const P0_ORDER = Object.freeze(['285:5','285:2','287:5','418:1','418:2','407:1']);
const https = value => typeof value === 'string' && /^https:\/\/[^/\s]+\//.test(value);
const integer = value => Number.isSafeInteger(value) && value >= 0;
const px = value => Number.isSafeInteger(value) && value > 0;
const sha256 = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);

function guestFinding(item, evidence) {
  if (!evidence) return {verdict:'UNVERIFIED', reason:'NO_GUEST_BROWSER_EVIDENCE'};
  if (evidence.source_slot !== item.slot || evidence.post_id !== item.post_id ||
      evidence.stored_original_src !== item.original_src)
    return {verdict:'HOLD', reason:'SOURCE_SLOT_OR_POST_MISMATCH'};
  if (evidence.method !== 'CHROME_CDP_LOGGED_OUT_COLD' ||
      evidence.network_capture_complete !== true ||
      !https(evidence.current_src) || !https(evidence.request_url) ||
      evidence.request_url !== evidence.current_src ||
      evidence.final_response_url !== evidence.current_src)
    return {verdict:'HOLD', reason:'UNPROVEN_CURRENT_SRC_OR_NETWORK_CAPTURE'};
  // A different selected image's HTTP failure must not convict the frozen
  // published original. CDN/Jetpack/srcset changes require independent review.
  if (evidence.current_src !== item.original_src)
    return {verdict:'HOLD', reason:'SELECTED_SOURCE_NOT_THE_PUBLISHED_ORIGINAL'};
  if (evidence.was_cached !== false || evidence.from_disk_cache !== false ||
      evidence.from_memory_cache !== false || evidence.from_service_worker !== false)
    return {verdict:'HOLD', reason:'UNCLEAR_COLD_CACHE_STATUS'};
  if (!Number.isInteger(evidence.final_http_status) ||
      evidence.final_http_status < 100 || evidence.final_http_status > 599 ||
      !integer(evidence.natural_width) || !integer(evidence.natural_height) ||
      !integer(evidence.encoded_data_length))
    return {verdict:'HOLD', reason:'INVALID_HTTP_GEOMETRY_OR_BYTES'};
  if (!evidence.screenshot_evidence_id || typeof evidence.screenshot_evidence_id !== 'string')
    return {verdict:'HOLD', reason:'MISSING_SCREENSHOT_EVIDENCE'};
  if (evidence.final_http_status >= 400 && evidence.natural_width === 0 &&
      evidence.natural_height === 0)
    return {verdict:'CONFIRMED_GUEST_BROKEN', reason:'COLD_HTTP_ERROR_AND_ZERO_IMAGE_DIMENSIONS', observed_http:evidence.final_http_status};
  if (evidence.final_http_status >= 200 && evidence.final_http_status < 300 &&
      px(evidence.natural_width) && px(evidence.natural_height))
    return {verdict:'CONFIRMED_GUEST_DISPLAYED', reason:'COLD_HTTP_SUCCESS_AND_POSITIVE_IMAGE_DIMENSIONS', observed_http:evidence.final_http_status};
  return {verdict:'HOLD', reason:'HTTP_AND_IMAGE_GEOMETRY_INCONCLUSIVE'};
}

function candidateReview(item, approval, guestVerdict) {
  const hold = reason => ({state:'HOLD',reason,staging_permitted:false,production_permitted:false,output_px:null});
  if (guestVerdict !== 'CONFIRMED_GUEST_BROKEN') return hold('NO_CONFIRMED_GUEST_FAILURE');
  if (!approval) return hold('NO_INDEPENDENT_RIGHTS_AND_EDITOR_APPROVAL');
  if (approval.source_slot !== item.slot || approval.original_src !== item.original_src ||
      approval.candidate_catalog_url !== item.catalog_candidate_url ||
      !https(approval.candidate_catalog_url))
    return hold('CANDIDATE_NOT_BOUND_TO_EXACT_SOURCE');
  if (!https(approval.item_rights_evidence_url) || !approval.rights_reviewer ||
      !/^\d{4}-\d\d-\d\d$/.test(String(approval.rights_reviewed_date || '')) ||
      approval.commercial_republication_cleared !== true ||
      approval.attribution_plan_checked !== true)
    return hold('ITEM_SPECIFIC_COMMERCIAL_RIGHTS_NOT_CLEARED');
  if (approval.exact_photographic_identity_verified !== true ||
      approval.historical_date_and_scene_verified !== true ||
      approval.alt_and_caption_editor_approved !== true ||
      approval.crop_and_layout_editor_approved !== true ||
      !sha256(approval.candidate_asset_sha256))
    return hold('SCENE_CROP_EDITOR_OR_ASSET_IDENTITY_NOT_VERIFIED');
  if (!px(approval.native_width) || !px(approval.native_height) ||
      !px(approval.output_width) || !px(approval.output_height))
    return hold('DIMENSIONS_MISSING');
  const naturalCap = Math.min(960,approval.native_width);
  const naturalHeight = Math.round(approval.native_height * naturalCap / approval.native_width);
  if (approval.output_width !== naturalCap || approval.output_height !== naturalHeight)
    return hold('960PX_NO_UPSCALE_AND_FULL_FRAME_PARITY_FAILED');
  if (item.slot === '285:5' &&
      (approval.native_width !== 819 || approval.native_height !== 614))
    return hold('TMI_ORIGINAL_DIMENSIONS_IDENTITY_CONFLICT');
  return {state:'ELIGIBLE_FOR_HUMAN_STAGING_REVIEW_ONLY',
    reason:'ALL_EVIDENCE_GATES_PASSED_NO_UPLOAD_AUTHORITY',
    staging_permitted:false,production_permitted:false,
    output_px:[naturalCap,naturalHeight]};
}

function compileRecovery(bridge, observations = {}, approvals = {}) {
  if (!bridge || bridge.schema !== 'fv-media-recovery-siteqa-bridge-v1' ||
      !Array.isArray(bridge.p0_queue) || !Array.isArray(bridge.oversized_media) ||
      bridge.p0_queue.length !== 6 || bridge.oversized_media.length !== 15 ||
      bridge.authority.site_qa_pr !== 154)
    throw new Error('unsupported or incomplete source-only bridge');
  const slots = bridge.p0_queue.map(x=>x.slot);
  if (P0_ORDER.some((slot,i)=>slot!==slots[i]) ||
      new Set(slots).size!==6 ||
      bridge.p0_queue.some(x=>!https(x.original_src) || !https(x.catalog_candidate_url)) ||
      new Set(bridge.oversized_media.map(x=>x.media_id)).size!==15)
    throw new Error('source inventory or priority order changed');
  const priority = bridge.p0_queue.map(item=>{
    const guest = guestFinding(item,observations[item.slot]);
    const candidate = candidateReview(item,approvals[item.slot],guest.verdict);
    return {slot:item.slot,post_id:item.post_id,original_src:item.original_src,
      candidate_catalog_url:item.catalog_candidate_url,
      rights_observation_not_clearance:item.rights_observation,
      guest_browser:guest,candidate_review:candidate};
  });
  const oversized = bridge.oversized_media.map(item=>({
    media_id:item.media_id,original_url:item.original_url,
    stored_original_bytes:item.stored_original_bytes,
    inline_post_ids:item.inline_post_ids,
    delivery_source:item.published_direct_srcs.some(x=>x.includes('i0.wp.com'))?'JETPACK_TRANSFORMED_IN_STORED_SRC':item.inline_post_ids.length?'DIRECT_INLINE_ORIGINAL':'NO_INLINE_MATCH',
    guest_wire_bytes:null,optimization_savings_bytes:null,
    rights_cleared_for_new_derivative:false
  }));
  const confirmed = priority.filter(x=>x.guest_browser.verdict==='CONFIRMED_GUEST_BROKEN');
  return {schema:'fv-media-evidence-gate-v1',source_bridge:'browser_handoff_6_p0_15_oversize_20261110.json',
    historical_reported_broken:42,
    verified_broken_in_supplied_guest_evidence:confirmed.length,
    historical_42_fully_adjudicated:false,
    priority,oversized,
    proposed_wire_saving_target_pct:76,actual_wire_saving_pct:null,
    actual_cold_baseline_image_bytes:null,actual_cold_candidate_image_bytes:null,
    restrictions:{browser_collector_owner_pr:154,homepage_design_changes:false,
      wordPress_production_writes_permitted:false,third_party_binary_copy_permitted:false,
      automatic_staging_upload_permitted:false,subscription_spend_permitted:false}};
}

module.exports={P0_ORDER,guestFinding,candidateReview,compileRecovery};
