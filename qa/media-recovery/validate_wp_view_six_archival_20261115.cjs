'use strict';
// Isolated, read-only verification of a dated WordPress EDIT/VIEW image-route snapshot.
// No network calls, file writes, media downloads or production edits.
function invariant(ok, reason) { if (!ok) throw Error(reason); }
function underlying(url) {
  const m = String(url || '').match(/^https:\/\/([^/?#]+)(\/[^?#]*)/i);
  invariant(!!m, 'invalid_https_url');
  let host = m[1].toLowerCase(), path;
  try { path = decodeURIComponent(m[2]); } catch { throw Error('invalid_percent_encoding'); }
  if (!/^i\d+\.wp\.com$/.test(host)) return {host, path, proxy:false};
  const rest = path.slice(1), n = rest.indexOf('/');
  invariant(n > 0, 'malformed_jetpack_proxy');
  return {host:rest.slice(0,n).toLowerCase(), path:rest.slice(n), proxy:true};
}
function route(url) {
  const p = underlying(url);
  if (p.proxy) return p.host === 'finalvestige.com' ? 'jetpack_firstparty' : 'jetpack_external';
  if (p.host === 'finalvestige.com') return 'direct_firstparty';
  if (p.host === 'commons.wikimedia.org' && p.path.startsWith('/wiki/Special:Redirect/file/')) return 'commons_redirect';
  return 'direct_external';
}
const expectedPosts = new Map([[268,10],[257,7],[217,6],[432,7],[280,6],[288,6]]);
const expectedFlorida = ['PR04493','RC17068','RC10673','N031889','RC04344','RC07668','MSF-PB11548-001'];
const expectedNavy = {'280:0':'428-GX-USN-1129207','280:1':'NH 75559','280:2':'NH 75561','280:3':'K-64683','280:5':'K-64728','288:0':'NH 69586'};
const expectedNative = {'268:0':[665,448], '268:6':[8160,10880], '257:6':[800,800]};
function validateAudit(a) {
  invariant(a && a.schema === 'fv-cms-edit-view-six-post-archival-route-v1', 'schema');
  invariant(a.release === 'HOLD' && a.no_wordpress_writes === true, 'production_hold');
  invariant(a.comparison_baseline?.posts === 61 && a.comparison_baseline?.stored_image_slots === 355 && a.comparison_baseline?.external_origin_dependencies === 288, 'historical_baseline');
  invariant(a.comparison_baseline?.reported_broken_unconfirmed === 42 && a.comparison_baseline?.claimed_visitor_transfer_reduction_unmeasured_percent === 76, 'claims_not_verified');
  invariant(a.latest_wp_original_census_previous_run?.attachments === 132 && a.latest_wp_original_census_previous_run?.above_1500000_bytes_count === 20 && a.latest_wp_original_census_previous_run?.above_1500000_bytes_total === 64385752, 'storage_baseline');
  invariant(Array.isArray(a.posts) && a.posts.length === 6 && Array.isArray(a.rows) && a.rows.length === 42, 'scope');
  const ids = new Set();
  for (const p of a.posts) {
    invariant(expectedPosts.get(p.id) === p.image_slots && !ids.has(p.id), 'post_id_or_count');
    invariant(typeof p.title === 'string' && p.title.length > 2 && p.link?.startsWith('https://finalvestige.com/') && typeof p.modified === 'string' && p.modified.length > 10, 'post_identity');
    ids.add(p.id);
  }
  invariant(ids.size === expectedPosts.size, 'missing_post');
  const keys = new Set(), counts = {posts:6, slots:42, jetpack_firstparty:0,jetpack_external:0,direct_firstparty:0,commons_redirect:0,direct_external:0,path_mismatches:0,no_width_height:0,no_srcset:0,no_sizes:0,official_catalog_candidates:0};
  for (const row of a.rows) {
    invariant(expectedPosts.has(row.post_id) && Number.isInteger(row.slot) && row.slot >= 0 && row.slot < expectedPosts.get(row.post_id), 'slot_range');
    invariant(row.key === row.post_id + ':' + row.slot && !keys.has(row.key), 'slot_key_collision');
    keys.add(row.key);
    invariant(typeof row.alt === 'string' && row.alt.length >= 10 && row.edit_src?.startsWith('https://') && row.view_src?.startsWith('https://'), 'alt_or_url');
    const e = underlying(row.edit_src), v = underlying(row.view_src), same = e.host === v.host && e.path === v.path;
    invariant(row.origin_path_matches === same && same && row.underlying_origin === e.host && row.view_mode === route(row.view_src), 'origin_path_or_route');
    counts[row.view_mode]++;
    invariant(row.guest_current_src === null && row.guest_http_status === null && row.guest_natural_width === null && row.guest_network_bytes === null && row.visitor_broken_verified === false, 'invented_guest_proof');
    invariant(row.review_requires_rights === true && row.caching_authorized === false && row.wp_upload_authorized === false && row.post_rewrite_authorized === false, 'unauthorized_reuse_or_edit');
    invariant(typeof row.view_has_width_height === 'boolean' && typeof row.view_has_srcset === 'boolean' && typeof row.view_has_sizes === 'boolean', 'responsive_fields');
    if (!row.view_has_width_height) {
      invariant(row.view_width === null && row.view_height === null, 'geometry_conflict');
      counts.no_width_height++;
    } else {
      invariant(Number.isInteger(row.view_width) && row.view_width > 0 && Number.isInteger(row.view_height) && row.view_height > 0, 'geometry_invalid');
    }
    if (!row.view_has_srcset) counts.no_srcset++;
    if (!row.view_has_sizes) counts.no_sizes++;
    const native = expectedNative[row.key] || null;
    if (native) {
      const width = Math.min(960,native[0]), height = Math.round(native[1] * width / native[0]);
      invariant(JSON.stringify(row.native_px) === JSON.stringify(native) && JSON.stringify(row.review_px) === JSON.stringify([width,height]), 'native_or_preview_geometry');
    } else invariant(row.native_px === null && row.review_px === null, 'unproven_native_geometry');
    const required = row.post_id === 432 ? expectedFlorida[row.slot] : expectedNavy[row.key] || null;
    if (required) {
      invariant(row.candidate?.id === required && row.candidate?.url?.startsWith('https://') && row.candidate?.source_identity === 'catalog_path_match_prior_review', 'archive_catalog_identity');
      counts.official_catalog_candidates++;
    } else invariant(row.candidate === null, 'invented_catalog');
  }
  for (const [id,n] of expectedPosts) for (let j=0;j<n;j++) invariant(keys.has(id+':'+j), 'missing_image_slot');
  for (const [key,value] of Object.entries(counts)) invariant(a.counts?.[key] === value, 'aggregate_'+key);
  invariant(counts.path_mismatches === 0 && counts.no_width_height === 42 && counts.no_srcset === 42 && counts.no_sizes === 42, 'routing_and_geometry_scope');
  return {ok:true,counts};
}
module.exports = {validateAudit, underlying, route};
if (typeof require !== 'undefined' && require.main === module) {
  const fs = require('node:fs'), path = require('node:path');
  const a = JSON.parse(fs.readFileSync(path.join(__dirname,'wp_view_six_archival_posts_42_slots_20261115.json'),'utf8'));
  process.stdout.write(JSON.stringify(validateAudit(a)) + '\n');
}
