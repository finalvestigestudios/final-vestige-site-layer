'use strict';
const { URL } = require('node:url');
const SLOT_IDS = Object.freeze(['288:0','288:1','288:2','288:3','288:4','288:5']);
function requireCondition(ok, code) { if (!ok) throw new Error(code); }
function urlHost(input) { try { const u = new URL(input); return u.protocol === 'https:' ? u.hostname : null; } catch { return null; } }
function verify(a) {
  requireCondition(a && a.schema === 'fv-honda288-archive-crosswalk-v1', 'schema');
  requireCondition(a.site_post_id === 288 && a.site_post_modified === '2026-08-19T14:37:40', 'source revision');
  requireCondition(a.source_method === 'AUTHENTICATED_WORDPRESS_EDIT_VIEW_PLUS_PUBLIC_RETRIEVER', 'source method');
  requireCondition(Array.isArray(a.rows) && a.rows.length === 6, 'slot count');
  requireCondition(a.historical_census?.posts === 61 && a.historical_census?.inline_images === 355, 'historical cohort');
  requireCondition(a.claims?.reported_broken === 42 && a.claims?.guest_confirmed_broken === null, 'broken claim');
  requireCondition(a.claims?.reported_wire_savings_pct === 76 && a.claims?.measured_wire_savings_pct === null, 'wire claim');
  requireCondition(a.claims?.oversized_originals_count === 20 && a.claims?.oversized_stored_bytes === 64385752, 'stored-byte tally');
  requireCondition(a.production_writes === 0 && a.downloaded_images === 0 && a.authorized_replacements === 0, 'side effects');
  const seen = new Set();
  for (const r of a.rows) {
    requireCondition(SLOT_IDS.includes(r.slot) && !seen.has(r.slot), 'unique slot');
    seen.add(r.slot);
    requireCondition(urlHost(r.source_url) && r.source_url.startsWith('https://'), 'source URL');
    requireCondition(urlHost(r.view_current_markup_src) === 'i0.wp.com', 'actual Jetpack src');
    requireCondition(r.view_current_markup_src.includes(new URL(r.source_url).hostname), 'proxy origin mismatch');
    requireCondition(r.wp_view_width === null && r.wp_view_height === null && r.wp_view_srcset === null && r.wp_view_sizes === null, 'markup attrs');
    requireCondition(['IMAGE_DISPLAYED','FETCH_TOOL_ERROR'].includes(r.public_retriever?.original_outcome), 'retriever class');
    requireCondition(r.public_retriever?.original_numeric_http_status === null && r.public_retriever?.proxy_numeric_http_status === null, 'fabricated status');
    requireCondition(r.public_retriever?.proxy_outcome === 'INACCESSIBLE_TO_RETRIEVER', 'proxy observation');
    requireCondition(r.guest_browser?.current_src === null && r.guest_browser?.http_status === null && r.guest_browser?.mime_type === null && r.guest_browser?.decoded === null && r.guest_browser?.wire_bytes === null, 'fabricated visitor observation');
    requireCondition(r.broken_for_visitors_confirmed === false && r.rights_release === 'HOLD' && r.media_cache_authorized === false && r.wordpress_write_authorized === false, 'unsafe release');
    requireCondition(r.exact_pixel_match_verified === false && r.media_sha256 === null, 'unverified pixel identity');
    requireCondition(r.source_url !== r.view_current_markup_src, 'source/proxy duplication');
    const c = r.primary_source_candidate;
    if (c?.asset_catalog_id) {
      requireCondition(/^NH (69586|69059|84820|84822)$/.test(c.asset_catalog_id), 'unapproved accession');
      requireCondition(urlHost(c.catalog_url) === 'www.history.navy.mil', 'catalog authority');
      requireCondition(c.high_tiff_native_width > 960 && c.high_tiff_native_height > 0, 'native geometry');
      requireCondition(c.conditional_target_width === 960 && c.conditional_target_height > 0, 'target geometry');
      requireCondition(Math.abs(c.conditional_target_height - 960*c.high_tiff_native_height/c.high_tiff_native_width) <= 1, 'aspect ratio');
      requireCondition(c.pixel_identity_verified === false && c.individual_rights_approved === false, 'premature catalog release');
      requireCondition(c.available_web_medium === '1280x1280 CATALOG LABEL; RENDITION GEOMETRY UNVERIFIED', 'false rendition assertion');
    } else {
      requireCondition(c === null || (c.asset_catalog_id === null && c.conditional_target_width === null && c.conditional_target_height === null && c.individual_rights_approved === false), 'invented candidate');
    }
  }
  requireCondition(seen.size === 6 && a.rows.filter(r=>r.primary_source_candidate?.asset_catalog_id).length === 4, 'mapping coverage');
  return {status:'PASS_NO_RELEASE',rows:6,official_catalog_crosswalks:4,guest_broken_confirmed:0,production_writes:0};
}
module.exports = {verify};
if (require.main === module) {
  const fs = require('node:fs');
  try { const data = JSON.parse(fs.readFileSync(process.argv[2] || '', 'utf8')); console.log(JSON.stringify(verify(data))); }
  catch(e) { console.error(e.message); process.exitCode = 1; }
}
