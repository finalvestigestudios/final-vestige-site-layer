'use strict';
// Offline source-only gate. This does NOT perform HTTP, rights clearance or WordPress writes.
function validate(a, census, sourceBlobSha) {
  const errors = [];
  const fail = (code) => errors.push(code);
  if (!a || a.schema_version !== 1 || !Array.isArray(a.rows)) return ['BAD_SCHEMA'];
  if (!census || !Array.isArray(census.images)) return ['BAD_SOURCE'];
  if (sourceBlobSha !== '49183f66f880f7c4dfd363acca906876877f2e5e' ||
      a.census.source_blob_sha !== sourceBlobSha ||
      a.census.source !== 'qa/media-recovery/parts/03.json') fail('SOURCE_SHA_MISMATCH');
  const expected = census.images.filter(x => x.post_id === 279);
  if (expected.length !== 6 || a.rows.length !== 6 || a.summary.slots !== 6) fail('SLOT_COUNT');
  const keys = new Set();
  let displays = 0, missing = 0, sameScene = 0, issueCount = 0;
  for (let i = 0; i < a.rows.length; i++) {
    const row = a.rows[i], src = expected[i];
    if (!row || !src || row.key !== src.key || row.stored_image_url !== src.source_url ||
        row.stored_alt !== src.alt || row.origin_host !== src.source_host ||
        row.post_id !== 279 || row.source_kind !== src.source_kind) fail('SOURCE_MISMATCH:' + i);
    if (keys.has(row.key)) fail('DUPLICATE_KEY'); else keys.add(row.key);
    const v = row.independent_retriever;
    if (!v || v.numeric_origin_http_status !== null ||
        v.method !== 'web_open_image_display_NOT_VISITOR_BROWSER') fail('VIEWER_AS_ORIGIN:' + i);
    if (v?.outcome === 'IMAGE_DISPLAYED') displays++;
    else if (v?.outcome === 'RETRIEVER_INACCESSIBLE') missing++;
    else fail('UNKNOWN_VIEWER_OUTCOME:' + i);
    const browser = row.guest_browser;
    if (!browser || browser.observed !== false || browser.current_src !== null ||
        browser.image_http_status !== null || browser.mime !== null ||
        browser.decoded_width !== null || browser.decoded_height !== null ||
        browser.encoded_transfer_bytes !== null || browser.visibly_broken !== null) fail('FABRICATED_BROWSER:' + i);
    if (row.max_target_width_px !== 960 || row.no_upscale !== true ||
        row.rights_approved !== false || row.wordpress_cache_authorized !== false ||
        row.wordpress_post_edit_authorized !== false || row.pixel_identity_verified !== false ||
        row.source_binary_sha256 !== null) fail('UNAUTHORIZED_ACTION:' + i);
    if (!Array.isArray(row.archive_candidate_assets)) fail('CANDIDATE_SCHEMA:' + i);
    else for (const c of row.archive_candidate_assets) {
      if (c.reuse_approved !== false || !/^https:\/\//.test(c.catalog) ||
          !['SAME_SCENE_VISUALLY_VERIFIED_NOT_BINARY', 'DIFFERENT_SCENE_EDITORIAL_ALTERNATIVE_ONLY', 'EXACT_PUBLISHED_SOURCE_CATALOG'].includes(c.relation)) fail('CANDIDATE_RIGHTS:' + i);
      if (c.relation === 'SAME_SCENE_VISUALLY_VERIFIED_NOT_BINARY') {
        sameScene++;
        if (row.key !== '279:0' || c.catalog_identifier.indexOf('DOE/NV1198') === -1) fail('FALSE_SAME_SCENE:' + i);
      }
      if (!c.catalog_original_px || !c.conditional_preview_px ||
          !Number.isInteger(c.catalog_original_px.width) || !Number.isInteger(c.catalog_original_px.height) ||
          !Number.isInteger(c.conditional_preview_px.width) || !Number.isInteger(c.conditional_preview_px.height) ||
          c.catalog_original_px.width < 1 || c.catalog_original_px.height < 1 ||
          c.conditional_preview_px.width < 1 || c.conditional_preview_px.height < 1 ||
          c.conditional_preview_px.width > 960 ||
          c.conditional_preview_px.width > c.catalog_original_px.width ||
          c.conditional_preview_px.height > c.catalog_original_px.height ||
          Math.abs(c.conditional_preview_px.width * c.catalog_original_px.height -
                   c.conditional_preview_px.height * c.catalog_original_px.width) > c.catalog_original_px.width) fail('BAD_GEOMETRY:' + i);
    }
    if (row.visual_integrity_issue) {
      issueCount++;
      if (!['279:3','279:4'].includes(row.key) || row.visual_integrity_issue.approved !== false ||
          !row.visual_integrity_issue.suggested) fail('EDITORIAL_APPROVAL:' + i);
    }
  }
  if (displays !== 5 || missing !== 1 || sameScene !== 1 || issueCount !== 2 ||
      a.summary.retriever_displays !== displays || a.summary.retriever_inaccessible !== missing ||
      a.summary.known_same_scene_authoritative_leads !== sameScene ||
      a.summary.proposed_alt_corrections !== issueCount) fail('SUMMARY_MISMATCH');
  if (a.summary.guest_browser_image_statuses_observed !== 0 ||
      a.summary.confirmed_guest_browser_broken !== 0 ||
      a.summary.rights_clearances !== 0 || a.summary.production_fixes !== 0 ||
      a.release?.status !== 'HOLD' || a.release.wordpress_writes !== false ||
      a.release.downloads_performed !== false || a.release.site_qa_pr154_edited !== false ||
      a.release.homepage_changed !== false || a.release.subscription_spend !== false ||
      a.site_wide_context?.reported_42_broken_not_browser_verified !== true ||
      a.site_wide_context?.claimed_76pct_not_measured !== true) fail('RELEASE_CLAIM');
  return errors;
}
if (typeof module !== 'undefined') {
  module.exports = { validate };
  if (typeof require !== 'undefined' && require.main === module) {
    const fs = require('node:fs'), crypto = require('node:crypto'), path = require('node:path');
    const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'kosmos_279_hotlink_source_recovery_20261102.json'), 'utf8'));
    const raw = fs.readFileSync(path.join(__dirname, 'parts/03.json'));
    const sha = crypto.createHash('sha1').update(Buffer.from('blob ' + raw.length + '\0')).update(raw).digest('hex');
    const errors = validate(data, JSON.parse(raw.toString('utf8')), sha);
    if (errors.length) { process.stderr.write(errors.join('\n') + '\n'); process.exitCode = 1; }
    else process.stdout.write('Kosmos 954 source and rights gate PASS (source only, browser UNKNOWN)\n');
  }
}
