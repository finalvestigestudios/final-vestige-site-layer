'use strict';
// Offline source ledger and safety assertions. No HTTP, CMS or image writes.
const fs = require('node:fs');
function check(x) {
  const bad = message => { throw Error('MEDIA_DELTA_INVALID: ' + message); };
  if (!x || x.schema !== 'fv-media-source-count-reconciliation-20261105-v1') bad('schema');
  const i = x.inputs, r = x.reconciliation, p = x.p0_us_coast_guard_primary_record, s = x.sitewide_context;
  if (!i || i.site_qa_pr !== 154 || i.media_pr !== 183) bad('input PR identity');
  if (!/^[0-9a-f]{40}$/.test(i.site_qa_csv_git_blob || '') || !/^[0-9a-f]{40}$/.test(i.site_qa_classifier_git_blob || '')) bad('input blob identity');
  if (!i.media_source_parts || Object.keys(i.media_source_parts).sort().join(',') !== '01,02,03,04,05,06,07,08') bad('part count');
  if (Object.values(i.media_source_parts).some(v => !/^[0-9a-f]{40}$/.test(v))) bad('source blob');
  if (!r || r.post_count_both !== 61 || r.inline_source_references_both !== 355 || r.site_qa_offsite_total !== 286 || r.media_inventory_offsite_total !== 288 || r.offsite_delta_media_minus_site_qa !== 2) bad('baseline totals');
  if (!Array.isArray(r.affected_posts) || r.affected_posts.length !== 2) bad('delta rows');
  const keys = [291,285];
  for (const id of keys) {
    const matches = r.affected_posts.filter(a => a.post_id === id);
    if (matches.length !== 1) bad('post mismatch');
    const a = matches[0];
    if (a.site_qa_csv_offsite !== 5 || a.media_source_offsite !== 6 || a.inline_img_references_both !== 6) bad('per-post counts');
    if (a.classifier_treatment_of_that_url !== 'external' || !String(a.classification_note).includes('Cannot attribute')) bad('classification certainty');
    if (a.exact_external_jetpack_host_reference_key !== id + ':' + (id === 291 ? '0':'1')) bad('reference key');
    const expected = id === 291 ? 'text-message.blogs.archives.gov' : 'www.squawkpoint.com';
    if (!a.exact_external_jetpack_host_reference_url.startsWith('https://i0.wp.com/' + expected + '/')) bad('proxy source identity');
  }
  if (r.root_cause_status !== 'UNKNOWN_BASELINE_SOURCE_CONTENT_OR_PRIOR_CLASSIFIER_BEHAVIOR' || r.no_presumed_live_404 !== true) bad('causality claim');
  if (!p || p.image_key !== '418:1' || p.source_part !== '01' || !p.source_url.endsWith('/210330-G-DE713-0002.JPG') || p.primary_catalog_virin !== '210330-G-DE713-0002.JPG' || !p.verified_primary_catalog_url.endsWith('/igphoto/2002905913/')) bad('primary identity');
  if (p.exact_virin_filename_match !== true || p.binary_identity_verified !== false || !p.primary_catalog_scene.includes('portrait') || !p.primary_catalog_scene.includes('NOT tsunami debris')) bad('scene/identity uncertainty');
  if (p.conditional_max_derivative_width_px !== 960 || p.derivative_dimensions_px !== null || p.primary_catalog_dimensions_px !== null) bad('unverified geometry');
  if (p.original_web_retriever_wrapper_status !== 403 || p.wrapper_status_is_guest_browser_http !== false) bad('retriever provenance');
  for (const name of ['actual_browser_http_status','actual_browser_natural_width','actual_browser_transfer_bytes','browser_broken','source_binary_sha256']) if (p[name] !== null) bad('fabricated measured value: ' + name);
  for (const name of ['rights_and_editorial_release_approved','cache_approved','wordpress_write_approved']) if (p[name] !== false) bad('unsafe authorization: ' + name);
  if (!s || s.reported_42_broken_browser_verified !== false || s.claimed_76pct_wire_reduction_measured !== false || s.production_images_repaired !== 0 || s.oversize_originals_gt_1_5_MiB !== 13 || s.oversize_original_stored_bytes !== 43522829) bad('sitewide misclaim');
  return { ok: true, localized_delta_posts: keys.length, offsite_reference_delta: 2, production_writes: 0 };
}
if (require.main === module) {
  try { const file = process.argv[2]; if (!file || fs.statSync(file).size > 150000) throw Error('expected <=150 KB JSON path'); console.log(JSON.stringify(check(JSON.parse(fs.readFileSync(file,'utf8'))))); }
  catch (e) { console.error(e.message); process.exitCode = 2; }
}
module.exports = { check };
