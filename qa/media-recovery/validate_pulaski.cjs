'use strict';
/**
 * Offline source-identity/rights validator for Pulaski post 428.
 * Deliberately does not request URLs, download images or write WordPress content.
 */
const EXPECTED = Object.freeze([
  ['428:1', 'bigburn23', '8-B498b', null, null],
  ['428:2', 'bigburn38', '8-C05b', 1024, 1487],
  ['428:3', 'bigburn10', '8-X90', 1024, 823],
  ['428:4', 'bigburn18', '8-X545e', 1024, 730],
  ['428:5', 'sanborn01687_005 / g4274wm.g016871905 / 01687_1905-0001', 'sanborn01687_005 / g4274wm.g016871905 / 01687_1905-0001', null, null]
]);
const BASE = 'https://www.lib.uidaho.edu/digital/bigburn/items/';
const LOC_SRC = 'https://tile.loc.gov/image-services/iiif/service%3Agmd%3Agmd427m%3Ag4274m%3Ag4274wm%3Ag016871905%3A01687_1905-0001/full/pct%3A25/0/default.jpg';
const LOC_ITEM = 'https://www.loc.gov/item/sanborn01687_005/';
function validatePulaski(data, census) {
  const errors = [], check = (pass, message) => { if (!pass) errors.push(message); };
  check(data && data.schema_version === 1 && data.post_id === 428 &&
    data.post_modified === '2026-10-29T18:28:59' &&
    data.post_url === 'https://finalvestige.com/2026/08/20/the-way-out-was-underground-ed-pulaski-1910/' &&
    data.published_in_cms === true, 'snapshot identity');
  check(data.fresh_cms_exact_img_count === 6 && data.external_images === 5 &&
    data.first_party_images === 1 && data.official_catalog_exact_matches === 5 &&
    data.independent_web_viewer_decodes === 5, 'scope/counts');
  check(data.evidence_type === 'AUTHORITATIVE_SOURCE_CROSSWALK_AND_INDEPENDENT_IMAGE_VIEWER_NOT_BROWSER_AUDIT' &&
    data.actual_guest_browser_checks === 0 && data.claim_42_broken === 'UNVERIFIED' &&
    data.claim_76_percent_savings === 'UNMEASURED' &&
    data.production_wordpress_writes === 0 && data.all_original_dimensions_known === false,
    'no invented browser/transfer/production result');
  check(Array.isArray(data.rows) && data.rows.length === 5, 'expected five records');
  const post = (census || []).filter(x => x.post_id === 428);
  check(post.length === 6, 'census source rows');
  const sources = new Map(post.map(x => [x.key, x]));
  for (let i = 0; i < (data.rows || []).length; i++) {
    const row = data.rows[i], ex = EXPECTED[i];
    if (!row || !ex) { errors.push('unexpected row ' + i); continue; }
    const src = sources.get(ex[0]);
    const loc = i === 4, id = ex[1];
    const expectedSource = loc ? LOC_SRC : 'https://objects.lib.uidaho.edu/bigburn/' + id + '.jpg';
    const expectedRecord = loc ? LOC_ITEM : BASE + id + '.html';
    check(row.image_key === ex[0] && row.post_id === 428 && row.source_kind === 'external',
      'ordered slot/source kind ' + i);
    check(row.source_url === expectedSource && row.source_url === src?.source_url &&
      row.stored_alt === src?.alt, 'exact source URL/ALT ' + i);
    check(row.official_record_url === expectedRecord &&
      row.official_identifier === ex[2] &&
      row.identity_basis === (loc ? 'EXACT_LOC_DIGITAL_ID_AND_IMAGE_SHEET' :
      'EXACT_CMS_LINKED_ARCHIVE_ITEM_AND_JPEG_FILENAME'), 'original record identity ' + i);
    check(row.creator === (loc ? 'Sanborn Map Company' : 'Barnard-Stockbridge Studio') &&
      row.archive_date === (i === 0 ? '1910-08-20' : i === 1 ? '1910' :
        i === 2 || i === 3 ? '1910-08' : '1905-09') &&
      typeof row.official_title === 'string' && row.official_title.length > 28,
      'official description/date ' + i);
    check(row.wp_markup_width_px === ex[3] && row.wp_markup_height_px === ex[4],
      'source HTML dimensions are not intrinsic pixels ' + i);
    check(row.official_rights_statement === (loc ?
      'LOC_SANBORN_COLLECTION_PUBLIC_DOMAIN_FREE_TO_USE_REUSE' :
      'INSTITUTION_DETERMINED_PUBLIC_DOMAIN_BY_PUBLICATION_DATE') &&
      typeof row.proposed_credit === 'string' && row.proposed_credit.length > 30,
      'archive rights statement/attribution ' + i);
    check(typeof row.historical_caution === 'string' && row.historical_caution.length >= 50,
      'chronology caution ' + i);
    check(row.viewer_decode_observed === true &&
      row.viewer_observation === 'independent_image_viewer_rendered_exact_source_url_not_guest_browser',
      'independent viewer is not guest browser ' + i);
    check(row.original_file_dimensions_px === null && row.original_binary_sha256 === null &&
      row.source_binary_downloaded === false && row.derivative_dimensions_px === null &&
      row.maximum_derivative_width_px === 960 && row.never_upscale === true &&
      row.preserve_aspect_ratio === true, 'safe sizing/no invented file metadata ' + i);
    check(row.guest_browser_http_status === null && row.guest_browser_natural_width_px === null &&
      row.guest_browser_transfer_bytes === null && row.broken_in_guest_browser === null &&
      row.measured_weight_savings_pct === null, 'no claimed HTTP/transfer result ' + i);
    check(row.publication_rights_cleared === false &&
      row.item_rights_checked_for_localization === false &&
      row.wp_upload_authorized === false && row.wp_post_edit_authorized === false &&
      row.wp_media_id === null && row.wordpress_responsive_delivery_unverified === true,
      'rights/WordPress release gates ' + i);
  }
  return {ok: errors.length === 0, errors, exact_archival_crosswalks: 5,
    independently_rendered_source_urls: 5, verified_guest_browser_failures: null};
}
if (require.main === module) {
  const fs = require('node:fs'), path = require('node:path'),
    {loadSnapshot} = require('./validate_inventory.cjs');
  const f = path.join(__dirname, 'pulaski_bigburn_primary_20261030.json');
  const result = validatePulaski(JSON.parse(fs.readFileSync(f, 'utf8')),
    loadSnapshot().parts.flatMap(p => p.images));
  console.log(JSON.stringify(result, null, 2));
  if (!result.ok) process.exitCode = 1;
}
module.exports = {validatePulaski, EXPECTED};
