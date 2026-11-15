'use strict';
// Offline source-only gate; no network, assets, CMS, or publishing effects.
const EXPECTED = Object.freeze({
  original: 'https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg',
  museum: 'https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg',
  mirror: 'https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg',
  article: 'https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/'
});
function assess(a) {
  const errors = [];
  const requireField = (ok, reason) => { if (!ok) errors.push(reason); };
  const p = a && a.article || {}, obs = a && a.observations || {};
  const museum = a && a.candidate_mapping && a.candidate_mapping[0] || {};
  const mirror = a && a.candidate_mapping && a.candidate_mapping[1] || {};
  const src = obs.original_retriever || {}, cd = obs.actual_guest_cdp || {};
  const rights = a && a.rights_and_size || {}, decision = a && a.decision || {};
  const base = a && a.sitewide_baseline || {};
  requireField(a && a.schema === 'fv-media-uscg418-museum-primary-corroboration-v1', 'schema_mismatch');
  requireField(p.post_id === 418 && p.slot === '418:2' && p.url === EXPECTED.article, 'wrong_post_or_slot');
  requireField(p.published_original_src === EXPECTED.original, 'published_source_mismatch');
  requireField(src.method === 'WEB_OPEN_RETRIEVER_ONLY_NOT_ORIGIN_OR_GUEST' && src.wrapper_status === 403 && src.wrapper_result === 'FORBIDDEN', 'original_wrapper_evidence_mismatch');
  requireField(Object.keys(cd).length === 9 && Object.values(cd).every(v => v === null), 'fake_guest_evidence');
  requireField(obs.museum_preview_retriever?.method === 'WEB_CLICK_IMAGE_DISPLAYED_NOT_CDP' && obs.museum_preview_retriever.rendered === true && obs.museum_preview_retriever.origin_http_status === null && obs.museum_preview_retriever.guest_http_status === null && obs.museum_preview_retriever.transferred_bytes === null, 'museum_retriever_claim_overstated');
  requireField(obs.lighthousefriends_retriever?.method === 'WEB_OPEN_IMAGE_DISPLAYED_NOT_CDP' && obs.lighthousefriends_retriever.rendered === true && obs.lighthousefriends_retriever.origin_http_status === null && obs.lighthousefriends_retriever.guest_http_status === null && obs.lighthousefriends_retriever.transferred_bytes === null, 'mirror_retriever_claim_overstated');
  requireField(Array.isArray(a?.candidate_mapping) && a.candidate_mapping.length === 2, 'two_distinct_candidates_required');
  requireField(museum.kind === 'COAST_GUARD_MUSEUM_EDITORIAL_CREDITED_PREVIEW' && museum.editorial_catalog === 'https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/' && museum.preview_image_url === EXPECTED.museum && museum.displayed_credit === 'U.S. Coast Guard', 'museum_source_or_credit_mismatch');
  requireField(Array.isArray(museum.preview_filename_geometry_hint_px) && museum.preview_filename_geometry_hint_px[0] === 600 && museum.preview_filename_geometry_hint_px[1] === 463, 'museum_preview_size_hint_mismatch');
  requireField(museum.original_native_dimensions_px === null && museum.verified_derivative_dimensions_px === null && museum.conditional_960px_output_px === null, 'museum_preview_not_verified_master_dimensions');
  requireField(mirror.kind === 'THIRD_PARTY_MIRROR_SAME_SCENE' && mirror.preview_image_url === EXPECTED.mirror && mirror.original_native_dimensions_px === null && mirror.conditional_960px_output_px === null, 'mirror_source_or_geometry_mismatch');
  for (const [i,c] of (Array.isArray(a?.candidate_mapping) ? a.candidate_mapping : []).entries()) {
    requireField(c.subject_scene_correspondence === 'SAME_HISTORICAL_PHOTOGRAPH_SCENE_VISUALLY_CORROBORATED' && c.exact_pixel_or_file_hash_identity_proven === false, 'candidate_'+i+'_scene_not_binary');
    requireField(c.item_specific_commercial_reuse_clearance === false && c.rights_decision === 'HOLD' && c.cache_or_mirror_approved === false, 'candidate_'+i+'_rights_not_cleared');
  }
  requireField(rights.maximum_requested_width_px === 960 && rights.original_dimensions_verified === false && rights.preview_600x463_is_not_verified_original_native_size === true && rights.derivative_960px_authorized === false && rights.no_upscale === true && rights.no_crop === true, 'unsafe_width_or_upscale');
  requireField(decision.status === 'HOLD_PRIMARY_SOURCE_CORROBORATED_GUEST_AND_RIGHTS_PENDING' && decision.confirmed_guest_failure === false && decision.publish_replacement_approved === false && decision.wordpress_media_upload_approved === false && decision.wordpress_block_rewrite_approved === false && decision.homepage_visual_edit_approved === false && decision.binary_download_or_rehost_approved === false && decision.merge_or_deploy_approved === false && decision.subscription_spend_usd === 0, 'unsafe_action_or_failure_claim');
  requireField(base.historical_posts === 61 && base.historical_inline_images === 355 && base.offsite_image_slots === 288 && base.prior_reported_broken_unconfirmed === 42 && base.guest_confirmed_broken === 0, 'historical_cohort_or_broken_claim_changed');
  requireField(base.oversized_wordpress_originals_gt_1500000_bytes === 15 && base.oversized_original_stored_bytes === 47096779 && base.suggested_reduction_pct === 76 && base.measured_cold_image_transfer_reduction_pct === null, 'unmeasured_weight_claim');
  return { valid: errors.length === 0, decision: 'HOLD_FOR_GUEST_RIGHTS_AND_VISUAL_QA', errors };
}
module.exports = { assess, EXPECTED };
