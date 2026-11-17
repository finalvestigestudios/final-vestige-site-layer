'use strict';
const fs = require('node:fs');
const path = require('node:path');
const EXPECTED_ORIGINAL = 'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/19460401_UNKNOWN_37-012_copy.jpg';
const EXPECTED_CATALOG = 'https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946';
const FIELDS_NULL = ['http_status_editor','http_status_jetpack','http_status_candidate','guest_natural_width','guest_transferred_bytes','guest_image_failure_verified','original_dimensions_px','review_dimensions_px'];
const SAFETY_ZERO = ['wordpress_production_writes','media_binary_downloads','third_party_rehosting','published_block_rewrites','homepage_changes','deployments','subscription_spend_usd'];
function verify(a) {
  const errors = [];
  const fail = m => errors.push(m);
  if (a.schema !== 'fv-media-official-original-route-pair-v1') fail('schema');
  if (a.observation_method !== 'official_catalog_html_link_and_web_image_reader_not_guest_http') fail('method');
  if (a.guest_browser_failed_images_verified !== null || a.sitewide_visitor_weight_reduction_percent !== null) fail('invented_sitewide_results');
  if (!Array.isArray(a.records) || a.records.length !== 2) { fail('record_count'); return errors; }
  if (a.records.map(r=>r.slot).join('|') !== '418:5|288:5') fail('exact_slots');
  for (const r of a.records) {
    if (!r.editor_image_url.startsWith('https://') || !r.wordpress_view_url.startsWith('https://i0.wp.com/')) fail('route '+r.slot);
    if (!r.editor_image_url.includes('itok=') || r.wordpress_view_url.includes('itok=')) fail('token_provenance '+r.slot);
    for (const k of FIELDS_NULL) if (r[k] !== null) fail('unmeasured '+r.slot+' '+k);
    for (const k of ['cache_or_rehost_rights_cleared','production_media_upload_authorized','published_post_rewrite_authorized','identical_pixel_hash_verified']) if (r[k] !== false) fail('authorization '+r.slot+' '+k);
    if (r.rights_review_required !== true || r.publication_status !== 'HOLD_QA_ONLY') fail('release_hold '+r.slot);
    if (r.max_review_width_px !== 960 || r.no_upscale !== true) fail('size_hold '+r.slot);
    if (r.readback_results.editor_token_url !== 'image_reader_rendered' || r.readback_results.wordpress_view_jetpack_url !== 'image_reader_inaccessible_prior_observation') fail('reader_provenance '+r.slot);
    if (!r.recommended_next_step) fail('missing_next_step '+r.slot);
  }
  const h = a.records[0];
  if (h.candidate_official_original_url !== EXPECTED_ORIGINAL || h.authoritative_catalog_url !== EXPECTED_CATALOG || h.official_catalog_link_label !== 'Original') fail('primary_catalog_identity');
  if (h.candidate_kind !== 'direct_unchanged_official_original_same_scene_for_browser_QA' || h.same_scene_visually_observed !== true || h.readback_results.official_original_url !== 'image_reader_rendered') fail('official_candidate_proof');
  if (h.candidate_official_original_url.includes('/styles/') || h.candidate_official_original_url.includes('?') || h.candidate_official_original_url.includes('i0.wp.com')) fail('must_be_static_catalog_original');
  if (!h.scene_cues.includes('Cafe 100 sign') || !h.scene_cues.includes('Hilo Products storefront')) fail('exact_scene_cues');
  if (!h.source_rights_statement.includes('Public Domain') || !h.source_rights_statement.includes('unknown')) fail('copyright_caveat');
  const n = a.records[1];
  if (n.candidate_official_original_url !== null || n.official_catalog_link_label !== null || n.candidate_kind !== 'alternate_subject_not_verified_identical_frame' || n.same_scene_visually_observed !== false || n.readback_results.official_original_url !== 'not_applicable') fail('no_substitute_for_honda');
  if (!n.authoritative_catalog_url.includes('/NH-97985.html') || !n.source_rights_statement.includes('donated')) fail('navy_custody');
  for (const k of SAFETY_ZERO) if (a.safety?.[k] !== 0) fail('prohibited_mutation '+k);
  return errors;
}
if (require.main === module) {
  const filename=process.argv[2]||path.join(__dirname,'official_original_route_pair_20261115.json');
  const errors=verify(JSON.parse(fs.readFileSync(filename,'utf8')));
  if (errors.length) { console.error(JSON.stringify({ok:false,errors})); process.exitCode=1; }
  else console.log(JSON.stringify({ok:true,records:2,status:'HOLD_QA_ONLY'}));
}
module.exports={verify};
