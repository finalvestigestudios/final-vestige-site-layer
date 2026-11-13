'use strict';
/** Bounded offline source-origin reconciliation. No network or WordPress writes. */
const fs = require('node:fs');
const path = require('node:path');
function sourceKind(raw) {
  if (typeof raw !== 'string' || !raw.trim()) return 'missing';
  let url;
  try { url = new URL(raw.trim().replace(/&amp;/gi, '&')); }
  catch { return 'invalid'; }
  if (url.protocol !== 'https:' && url.protocol !== 'http:') return 'invalid';
  const host = url.hostname.toLowerCase().replace(/^www\./, '');
  if (host === 'finalvestige.com') return 'first_party';
  if (/^i[012]\.wp\.com$/.test(host)) {
    const tenant = url.pathname.split('/')[1]?.toLowerCase();
    return tenant === 'finalvestige.com' ? 'first_party_jetpack' : 'external_jetpack';
  }
  return 'external';
}
function validate(input) {
  const errors = [];
  const need = (test, label) => { if (!test) errors.push(label); };
  need(input?.schema === 'fv-frozen-image-origin-count-reconciliation-v1', 'schema');
  const c = input?.historical_counts || {};
  need(c.published_posts === 61 && c.stored_image_positions === 355, 'frozen cohort');
  need(c.siteqa_csv_offsite === 286 && c.media_inventory_offsite === 288, 'baseline counts');
  need(c.media_inventory_offsite === c.inventory_external + c.inventory_wikimedia_redirect, 'inventory breakdown');
  need(c.stored_image_positions === c.inventory_first_party + c.inventory_own_jetpack + c.inventory_external + c.inventory_wikimedia_redirect, 'image denominator');
  const rows = input?.discrepancies;
  need(Array.isArray(rows) && rows.length === 2, 'delta row count');
  if (Array.isArray(rows)) {
    const ids = new Set(); let totalDelta = 0;
    for (const row of rows) {
      ids.add(row.post_id);
      const slot = {285:'285:1',291:'291:0'}[row.post_id];
      need(slot === row.proxy_candidate_slot, 'slot ' + row.post_id);
      need(row.siteqa_csv_image_count === 6 && row.siteqa_csv_offsite_count === 5 && row.media_inventory_offsite_count === 6, 'post counts ' + row.post_id);
      totalDelta += row.media_inventory_offsite_count - row.siteqa_csv_offsite_count;
      need(Array.isArray(row.frozen_source_urls) && row.frozen_source_urls.length === 6, 'sources ' + row.post_id);
      if (Array.isArray(row.frozen_source_urls)) {
        need(row.frozen_source_urls.every(u => sourceKind(u).startsWith('external')), 'source classification ' + row.post_id);
        need(row.frozen_source_urls[Number(row.proxy_candidate_slot?.split(':')[1])] === row.proxy_source_url, 'source-slot binding ' + row.post_id);
      }
      need(sourceKind(row.proxy_source_url) === 'external_jetpack', 'proxy provenance ' + row.post_id);
      try {
        const tenant = new URL(row.proxy_source_url).pathname.split('/')[1];
        need(tenant === row.proxy_target_host, 'proxy target ' + row.post_id);
      } catch { need(false, 'invalid proxy URL ' + row.post_id); }
      need(row.guest_origin_http_status === null && row.guest_image_decoded === null && row.guest_transfer_bytes === null, 'invented guest result ' + row.post_id);
      need(row.rights_release === 'HOLD' && row.allowed_to_cache_or_upload === false && row.max_proposed_width_px === 960 && row.catalog_same_photo_confirmed === false, 'rights/960 gate ' + row.post_id);
    }
    need(ids.size === 2 && ids.has(285) && ids.has(291), 'post set');
    need(totalDelta === 2 && c.difference === totalDelta && c.per_post_discrepancy_count === 2 && c.otherwise_matching_post_rows === 59, 'difference arithmetic');
  }
  need(input?.limits?.root_cause_proven === false && input?.limits?.reported_42_broken_guest_verified === false && input?.limits?.proposed_76_percent_wire_reduction_measured === false, 'unsupported live claims');
  need(input?.limits?.no_image_downloads === true && input?.limits?.no_wordpress_writes === true && input?.limits?.siteqa_existing_browser_collector_owner === 154, 'safety boundary');
  return { ok: errors.length === 0, errors, delta: c.difference, delta_posts: [285,291], actual_guest_failures_confirmed: 0, claim_76_percent_measured: false };
}
function load() {return JSON.parse(fs.readFileSync(path.join(__dirname, 'siteqa_286_288_proxy_reconciliation_20261113.json'), 'utf8'));}
if (require.main === module) {const result = validate(load());console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;}
module.exports = { sourceKind, validate, load };
