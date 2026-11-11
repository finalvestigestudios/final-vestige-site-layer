'use strict';
/**
 * Offline paired cold-guest image transfer evaluator, not a browser collector.
 * Site QA #154 owns CDP collection. This module cannot access WordPress,
 * download images, assert copyright clearance, or approve publication.
 * Every response byte is from a real collected CDP Network.loadingFinished
 * encodedDataLength, never from WordPress original stored sizes.
 */
const INVENTORY_BLOB = 'd1a9c7a499510ec37bcdba5858d45165752587e0';
const PERCENT_TARGET = 76;
const positive = n => Number.isSafeInteger(n) && n > 0;
const nonnegative = n => Number.isSafeInteger(n) && n >= 0;
const goodMime = x => typeof x === 'string' && /^image\/(?:jpeg|png|gif|webp|avif|bmp|svg\+xml)(?:\s*;.*)?$/i.test(x);
const https = x => typeof x === 'string' && /^https:\/\/[^\s/]+\//.test(x);
const hash = x => typeof x === 'string' && /^[a-f0-9]{64}$/.test(x);
const fail = (code, detail) => ({status:'HOLD', reason:code, detail:detail || null,
  image_network_before_bytes:null, image_network_after_bytes:null,
  reduction_percent:null, target_76_percent_met:null,
  sitewide_transfer_savings_verified:false, production_change_allowed:false});
const equalLists = (a,b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());

function validateCapture(c, expectedSlots, postId) {
  if (!c || c.method !== 'CHROME_CDP_LOGGED_OUT_COLD' ||
      c.post_id !== postId || !https(c.page_url) ||
      !/^https:\/\/finalvestige\.com\//.test(c.page_url) ||
      c.page_http_status !== 200 || c.full_scroll_complete !== true ||
      c.lazy_images_settled !== true || c.network_capture_complete !== true ||
      c.cache_disabled !== true || c.service_workers_bypassed !== true ||
      typeof c.run_id !== 'string' || !c.run_id.trim() ||
      !hash(c.prose_fingerprint_sha256) ||
      !positive(c.viewport_width) || !positive(c.viewport_height) ||
      !(c.dpr > 0 && c.dpr <= 5) || !Array.isArray(c.images))
    return {error:'INCOMPLETE_COLD_CAPTURE'};
  const requestById = new Map(), slots = new Set();
  for (const img of c.images) {
    if (!img || img.post_id !== postId || !expectedSlots.includes(img.slot) ||
        slots.has(img.slot) || typeof img.request_id !== 'string' ||
        !img.request_id ||
        img.resource_type !== 'Image' || !https(img.current_src) ||
        !https(img.request_url) || img.current_src !== img.request_url ||
        !https(img.final_response_url) || img.final_response_url !== img.request_url ||
        !goodMime(img.response_mime_type) ||
        !Number.isInteger(img.final_http_status) ||
        img.final_http_status !== 200 ||
        img.loading_finished !== true || !positive(img.encoded_data_length) ||
        !positive(img.network_data_received_bytes) ||
        img.network_data_received_provenance !== 'CDP_NETWORK_DATA_RECEIVED' ||
        !positive(img.natural_width) || !positive(img.natural_height) ||
        img.from_disk_cache !== false || img.from_memory_cache !== false ||
        img.from_service_worker !== false ||
        typeof img.image_identity !== 'string' || !img.image_identity.trim())
      return {error:'MISSING_OR_INVALID_IMAGE_REQUEST',slot:img && img.slot};
    // A single completed CDP Image request may feed multiple DOM <img> slots.
    // Its network bytes must be counted once; inconsistent duplicate evidence is invalid.
    const signature = JSON.stringify([img.post_id,img.resource_type,img.current_src,
      img.request_url,img.final_response_url,img.response_mime_type,
      img.final_http_status,img.loading_finished,img.encoded_data_length,
      img.network_data_received_bytes,img.network_data_received_provenance,
      img.natural_width,img.natural_height,img.image_identity,
      img.from_disk_cache,img.from_memory_cache,img.from_service_worker]);
    const prior = requestById.get(img.request_id);
    if (prior && prior.signature !== signature)
      return {error:'CONFLICTING_SHARED_IMAGE_REQUEST',slot:img.slot};
    if (!prior) requestById.set(img.request_id,{signature,row:img});
    slots.add(img.slot);
  }
  if (!equalLists([...slots], expectedSlots)) return {error:'INCOMPLETE_IMAGE_SLOT_COVERAGE'};
  return {ok:true, rows:new Map(c.images.map(r=>[r.slot,r])),
    requests:new Map([...requestById].map(([id,r])=>[id,r.row])),
    shared_slots:c.images.length-requestById.size};
}
function evaluatePair(input) {
  if (!input || input.schema !== 'fv-cold-transfer-pair-v1' ||
      input.source_ledger_blob_sha !== INVENTORY_BLOB ||
      !positive(input.post_id) || !Array.isArray(input.expected_slots) ||
      input.expected_slots.length === 0 ||
      new Set(input.expected_slots).size !== input.expected_slots.length ||
      input.expected_slots.some(s => !new RegExp('^'+input.post_id+':\\d+$').test(s)))
    return fail('INVALID_OR_UNBOUND_FROZEN_COHORT');
  const before = validateCapture(input.before,input.expected_slots,input.post_id);
  const after = validateCapture(input.after,input.expected_slots,input.post_id);
  if (!before.ok) return fail('BASELINE_'+before.error,before.slot);
  if (!after.ok) return fail('CANDIDATE_'+after.error,after.slot);
  const b=input.before,a=input.after;
  if (a.run_id === b.run_id || a.page_url !== b.page_url ||
      a.prose_fingerprint_sha256 !== b.prose_fingerprint_sha256 ||
      a.viewport_width !== b.viewport_width || a.viewport_height !== b.viewport_height ||
      a.dpr !== b.dpr)
    return fail('UNMATCHED_CAPTURE_ENVIRONMENT_OR_CONTENT');
  for (const slot of input.expected_slots) {
    const x=before.rows.get(slot), y=after.rows.get(slot);
    if (x.image_identity !== y.image_identity)
      return fail('PHOTOGRAPH_IDENTITY_CHANGED',slot);
    if (x.current_src !== y.current_src &&
        !(y.rights_review_approved === true &&
          y.visual_parity_approved === true &&
          https(y.item_rights_evidence_url)))
      return fail('CHANGED_ASSET_WITHOUT_RIGHTS_AND_VISUAL_GATE',slot);
  }
  const sum = capture => [...capture.requests.values()]
    .reduce((n,r)=>n+r.encoded_data_length,0);
  const initial=sum(before), candidate=sum(after);
  if (!Number.isSafeInteger(initial) || !Number.isSafeInteger(candidate) ||
      initial <= 0 || candidate <= 0) return fail('INVALID_TRANSFER_TOTALS');
  const pct=(initial-candidate)*100/initial;
  return {status:'VERIFIED_SINGLE_POST_COLD_PAIR', post_id:input.post_id,
    matched_image_slots:input.expected_slots.length,
    unique_completed_requests_before:before.requests.size,
    unique_completed_requests_after:after.requests.size,
    shared_request_slots_before:before.shared_slots,
    shared_request_slots_after:after.shared_slots,
    network_metric:'CDP Network.loadingFinished encodedDataLength',
    image_network_before_bytes:initial, image_network_after_bytes:candidate,
    reduction_percent:Math.round(pct*100)/100,
    target_76_percent_met:pct>=PERCENT_TARGET,
    sitewide_transfer_savings_verified:false,
    production_change_allowed:false,
    scope:'single-post unique completed Image requests across matched DOM slots, not sitewide page weight',
    caveat:'CDP encodedDataLength is request-network bytes, not WordPress stored originals; no CSS/background/ad image coverage'};
}
module.exports={evaluatePair,validateCapture,INVENTORY_BLOB};
