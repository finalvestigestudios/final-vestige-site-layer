'use strict';
// Offline, read-only crosscheck of public retriever observations against the
// pinned six-slot WordPress EDIT/VIEW manifest. NOT a guest-browser test.
const fs = require('node:fs');
const P0 = Object.freeze(['285:5','285:2','287:5','418:1','418:2','407:1']);
const SOURCE_SHA = '93ed6631518dc0c06253719b61d1cf50b623f6f0';
const safeUrl = s => { try { const u = new URL(s); return u.protocol === 'https:' && !!u.hostname && !u.username && !u.password; } catch { return false; } };
const finiteInt = n => Number.isSafeInteger(n) && n >= 0;
function audit(matrix, pinned) {
  const fail = reason => ({ok:false,decision:'HOLD',error:reason,guest_broken_confirmed:0,wordpress_writes:0});
  if (!matrix || matrix.schema !== 'fv-p0-web-retriever-matrix-v1' ||
      matrix.method !== 'PUBLIC_WEB_RETRIEVER_NOT_GUEST_CHROMIUM' ||
      matrix.pinned_source_blob_sha !== SOURCE_SHA ||
      matrix.reported_42_guest_confirmed !== false ||
      matrix.measured_76_percent_wire_reduction !== false ||
      matrix.wordpress_writes !== 0 || matrix.image_downloads !== 0 ||
      !pinned || pinned.schema !== 'fv-media-p0-staging-custody-v1' ||
      pinned.upstream_source_blob_sha !== SOURCE_SHA ||
      !Array.isArray(pinned.slots) || pinned.slots.length !== P0.length ||
      !Array.isArray(matrix.rows) || matrix.rows.length !== P0.length)
    return fail('INVALID_COHORT_OR_PIN');
  let alternativeReaderDisplays = 0;
  const results = [];
  for (let i=0;i<P0.length;i++) {
    const row = matrix.rows[i], pin = pinned.slots[i];
    if (!row || !pin || row.key !== P0[i] || pin.key !== P0[i] ||
        row.post_url !== pin.post_url || row.authored_url !== pin.authored_url ||
        row.jetpack_view_url !== pin.rendered_url || row.wp_modified !== pin.wp_modified ||
        !safeUrl(row.post_url) || !safeUrl(row.authored_url) || !safeUrl(row.jetpack_view_url) ||
        row.guest_current_src !== null || row.guest_http_status !== null ||
        row.guest_decoded !== null || row.guest_transferred_bytes !== null ||
        row.broken_for_visitors_confirmed !== false ||
        !['RETRIEVER_ERROR','IMAGE_DISPLAYED'].includes(row.reader_outcome) ||
        row.reader_numeric_http_status !== null ||
        row.reader_result_is_browser_http !== false ||
        row.cache_authorized !== false || row.wordpress_write_authorized !== false ||
        row.rights_release !== 'HOLD' || row.pixel_identity_verified !== false ||
        row.max_review_width_px !== 960)
      return fail('BAD_SLOT_OR_FALSE_BROWSER_CLAIM:' + P0[i]);
    if (row.reader_outcome === 'RETRIEVER_ERROR') {
      if (![400,403,404,500].includes(row.reader_tool_code) ||
          !['UNSUPPORTED_CONTENT_TYPE','FETCHER_FORBIDDEN','FETCHER_NOT_FOUND','REDIRECT_TOOL_INACCESSIBLE'].includes(row.reader_reason))
        return fail('UNSUPPORTED_RETRIEVER_ERROR:' + P0[i]);
    } else if (row.reader_tool_code !== null || row.reader_reason !== 'IMAGE_RENDERED')
      return fail('UNSUPPORTED_RENDER_ASSERTION:' + P0[i]);
    const a = row.alternative;
    if (a !== null) {
      if (!safeUrl(a.catalog_url) || !safeUrl(a.image_url) ||
          !['IMAGE_DISPLAYED','TOOL_INACCESSIBLE'].includes(a.reader_outcome) ||
          a.numeric_http_status !== null || a.same_pixels_and_crop_verified !== false ||
          a.rehosting_rights_approved !== false || a.review_only !== true ||
          a.native_dimensions_verified !== false || !finiteInt(a.preview_width_px) ||
          !finiteInt(a.preview_height_px) || (a.preview_width_px > 0 && a.preview_height_px === 0) ||
          a.proposed_width_px !== null || a.proposed_height_px !== null)
        return fail('UNAPPROVED_ALTERNATIVE:' + P0[i]);
      if (a.reader_outcome === 'IMAGE_DISPLAYED') alternativeReaderDisplays++;
    }
    results.push({key:row.key, reader_observation:row.reader_outcome,
      source_tool_code:row.reader_tool_code, guest_broken_confirmed:false,
      alternative_reader_displayed:a?.reader_outcome==='IMAGE_DISPLAYED',
      staging:'HOLD', reason:'No logged-out guest evidence, matching pixels, and item-level rights approval'});
  }
  return {ok:true,decision:'HOLD',p0_slots_crosschecked:results.length,
    retriever_errors:results.filter(r=>r.reader_observation==='RETRIEVER_ERROR').length,
    alternatives_displayed_in_reader:alternativeReaderDisplays,guest_broken_confirmed:0,
    visitor_network_bytes_measured:false,wordpress_writes:0,results};
}
module.exports = {audit,P0};
if (require.main === module) {
  try { if (process.argv.length !== 4) throw Error('Usage: node verify_p0_reader_matrix_20261116.cjs matrix.json pinned_manifest.json');
    const a = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const b = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
    const result = audit(a,b); console.log(JSON.stringify(result,null,2));
    if (!result.ok) process.exitCode=1;
  } catch(e) { console.error(String(e.message)); process.exitCode=2; }
}
