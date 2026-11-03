'use strict';
/** Offline, read-only evidence gate for Hebgen 407:1. Never performs network or CMS writes. */
const EXPECTED = Object.freeze({
  src: 'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg',
  alt: 'Fresh fault scarp near Hebgen Lake produced by the August 1959 earthquake.',
  post: 'https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/',
  record: 'https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959',
  candidate: 'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg',
  sha: '48e1ebf07207e948ba5802e714eb39659d2e1c1d'
});
function validate(a) {
  const e = [];
  const err = (msg, yes) => { if (!yes) e.push(msg); };
  const isNull = x => x === null;
  if (!a || typeof a !== 'object') return ['audit_not_object'];
  const p = a.post || {}, f = a.frozen_source || {}, old = a.published || {};
  const obs = a.exact_published_source_observation || {};
  const c = a.official_candidate || {}, d = a.derivative || {}, ed = a.editorial || {};
  const g = a.gates || {}, b = a.guest_browser || {}, claim = a.claim_context || {};
  err('schema_and_key', a.schema_version === 1 && a.image_key === '407:1' && a.investigation_date === '2026-11-02');
  err('scope', a.scope === 'SOURCE_RETRIEVAL_AND_OFFICIAL_ALT_URL_NOT_GUEST_BROWSER');
  err('live_wp', p.id === 407 && p.url === EXPECTED.post && p.status === 'publish' && p.modified === '2026-10-29T18:30:30' && p.verification === 'authenticated_wordpress_posts_get_context_edit_read_only_2026_11_02');
  err('frozen_census', f.path === 'qa/media-recovery/parts/02.json' && f.git_blob_sha === EXPECTED.sha);
  err('exact_published_source', old.src === EXPECTED.src && old.alt === EXPECTED.alt && old.source_url_verified_in_live_raw_post === true);
  err('exact_source_retriever_nonbrowser', obs.tool === 'independent_web_open' && obs.date === '2026-11-02' && obs.result === 'RETRIEVER_UNSUPPORTED_CONTENT_TYPE' && obs.wrapper_error_code === 400 && obs.reported_media_type === 'binary/octet-stream' && isNull(obs.origin_http_status) && isNull(obs.visitor_browser_http_status) && isNull(obs.visitor_decoded_image) && isNull(obs.visitor_transferred_bytes));
  err('official_identity', c.authority === 'U.S. Geological Survey' && c.record_url === EXPECTED.record && c.photographer === 'J. R. Stacy' && c.catalog_usage === 'Public Domain');
  err('official_original_link', c.linked_original_url === EXPECTED.candidate && c.exact_usgs_original_link === true && c.independent_image_renderer === 'DISPLAYED');
  err('catalog_visual_measurement_not_binary', c.renderer_canvas_width_px === 1000 && c.renderer_canvas_height_px === 1000 && isNull(c.source_binary_sha256) && c.exact_published_binary_match_verified === false && isNull(c.final_origin_http_status) && c.original_master_dimensions_verified_from_binary === false);
  err('conditional_960_square_no_upscale', d.conditional_width_px === 960 && d.conditional_height_px === 960 && d.aspect_preserved === true && d.no_upscale === true && d.only_if_catalog_geometry_matches_original_binary === true && d.conditional_width_px <= c.renderer_canvas_width_px && d.conditional_height_px <= c.renderer_canvas_height_px);
  err('scene_and_crop_hold', ed.same_subject_candidate === true && ed.same_exact_crop_verified === false && ed.alt_keep_until_scene_review === true && ed.alternate_scape_replacement_authorized === false && ed.credit_required === 'J. R. Stacy / U.S. Geological Survey');
  err('rights_and_publication_holds', g.rights_review === 'HOLD_ITEM_SPECIFIC' && g.rehost_permission_confirmed === false && g.download_authorized === false && g.wp_media_upload_authorized === false && g.wp_post_edit_authorized === false && g.asset_substitution_authorized === false && g.production_changed === false && g.subscription_spend_usd === 0);
  const guestKeys=['current_src','final_image_get_url','final_http_status','mime_type','natural_width_px','natural_height_px','transfer_bytes','visibly_broken','screenshot'];
  err('no_fabricated_visitor_evidence', guestKeys.every(k => Object.prototype.hasOwnProperty.call(b,k) && isNull(b[k])));
  err('sitewide_claims_unmeasured', claim.reported_sitewide_broken_42_confirmed === false && claim.reported_76pct_savings_measured === false && claim.sitewide_posts === 61 && claim.stored_image_refs === 355 && claim.external_origin_refs === 288 && claim.original_wp_media_over_1_5_mib === 13 && claim.production_repaired_images === 0);
  err('next_action_hold', typeof a.next_action === 'string' && a.next_action.includes('Site QA #154') && a.next_action.includes('nosniff') && a.next_action.includes('rights'));
  return e;
}
module.exports = { validate, EXPECTED };
