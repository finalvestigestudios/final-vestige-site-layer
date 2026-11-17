'use strict';
// Source-only LOC photo identity and publication-safety gate. No network or CMS writes.
const EXPECTED = Object.freeze([
  { key: '190:0', id: '2016826957', digital: 'npcc.18735', suffix: '/npcc/18700/18735v.jpg' },
  { key: '190:1', id: '2022653666', digital: 'stereo.1s46043', suffix: '/stereo/1s40000/1s46000/1s46000/1s46043v.jpg' },
  { key: '190:2', id: '2016844556', digital: 'npcc.18713', suffix: '/npcc/18700/18713v.jpg' },
  { key: '190:3', id: '2016844568', digital: 'npcc.18729', suffix: '/npcc/18700/18729v.jpg' },
  { key: '190:4', id: '2016844555', digital: 'npcc.18712', suffix: '/npcc/18700/18712v.jpg' },
  { key: '190:5', id: '2007662234', digital: 'pan.6a05834', suffix: '/pan/6a05000/6a05800/6a05834r.jpg' }
]);
const UNKNOWN_FIELDS = Object.freeze([
  'actual_browser_http_status','actual_browser_current_src',
  'actual_browser_natural_width_px','actual_browser_transfer_bytes',
  'actual_browser_content_type','broken_in_visitor_browser',
  'master_sha256','source_width_px','source_height_px',
  'proposed_width_px','proposed_height_px'
]);
function validate(ledger, census) {
  const errors = [];
  if (!ledger || typeof ledger !== 'object' || Array.isArray(ledger)) return ['ledger missing or invalid'];
  if (!census || !Array.isArray(census.images)) return ['frozen census missing or invalid'];
  if (ledger.schema !== 'fv.media.loc-custody.v1') errors.push('schema changed');
  if (ledger.post_id !== 190 || ledger.source_count !== 6 || ledger.offsite_count !== 6) errors.push('scope/count mismatch');
  if (ledger.frozen_src_alt_exact_match_20261101 !== true) errors.push('CMS readback not demonstrated');
  if (ledger.browser_measured !== false || ledger.claimed_42_broken_verified !== false ||
      ledger.claimed_76_percent_saved_verified !== false) errors.push('unverified success promoted');
  if (ledger.wordpress_production_writes !== 0 || ledger.photos_downloaded !== 0) errors.push('unsafe action claimed');
  if (!Array.isArray(ledger.items) || ledger.items.length !== EXPECTED.length) return errors.concat('not six items');
  const original = census.images.filter(x => x.post_id === 190);
  if (original.length !== 6) errors.push('frozen source inventory changed');
  if (ledger.frozen_census_blob_sha !== '0f3dfe398a76838049cebba7cb773d5c5a0c8c69') errors.push('frozen census SHA mismatch');
  const keys = new Set();
  for (let i = 0; i < EXPECTED.length; i++) {
    const e = EXPECTED[i], a = ledger.items[i], src = original[i];
    if (!a || typeof a !== 'object') { errors.push('missing item ' + i); continue; }
    if (keys.has(a.key)) errors.push('duplicate item ' + a.key);
    keys.add(a.key);
    if (a.key !== e.key || a.slot !== i) errors.push('slot identity mismatch ' + i);
    if (!src || a.source_url !== src.source_url || a.stored_alt !== src.alt || a.source_host !== src.source_host)
      errors.push('frozen URL/ALT mismatch ' + e.key);
    let host = '';
    try { host = new URL(a.source_url).hostname.toLowerCase(); }
    catch (_) { errors.push('malformed source URL ' + e.key); }
    if (typeof a.source_url !== 'string' ||
        !a.source_url.startsWith('https://') ||
        !a.source_url.includes(e.suffix) ||
        !['cdn.loc.gov','tile.loc.gov'].includes(host))
      errors.push('expected LOC original URL mismatch ' + e.key);
    if (a.loc_lccn !== e.id || a.loc_digital_id !== e.digital ||
        a.loc_record_url !== 'https://www.loc.gov/item/' + e.id + '/')
      errors.push('LOC catalog identity mismatch ' + e.key);
    if (a.identity_basis !== 'stored exact LOC digital ID embedded in pathname; official catalog record same digital ID')
      errors.push('source match provenance missing ' + e.key);
    if (a.rights_item_review !== 'HOLD' || a.wordpress_upload_authorized !== false ||
        a.wordpress_post_write_authorized !== false || a.asset_downloaded !== false ||
        a.binary_hash_matched !== false)
      errors.push('unlicensed or unauthorized action ' + e.key);
    if (typeof a.rights_advisory !== 'string' || !a.rights_advisory.includes('does not license rights') ||
        typeof a.credit !== 'string' || !a.credit.length || typeof a.rights_notes !== 'string')
      errors.push('rights/credit evidence missing ' + e.key);
    if (a.max_derivative_width_px !== 960 || a.prohibit_upscale !== true) errors.push('resize safety mismatch ' + e.key);
    for (const k of UNKNOWN_FIELDS) if (a[k] !== null) errors.push('fabricated or unapproved data ' + e.key + '/' + k);
    if (typeof a.localization_plan !== 'string' || !a.localization_plan.includes('do not rewrite Gutenberg posts'))
      errors.push('staging must remain conditional ' + e.key);
  }
  return errors;
}
module.exports = { validate, EXPECTED };
if (require.main === module) {
  const fs = require('node:fs');
  const path = require('node:path');
  const root = path.resolve(__dirname, '..', '..');
  const ledger = JSON.parse(fs.readFileSync(path.join(__dirname, 'baltimore_190_loc_20261101.json'), 'utf8'));
  const census = JSON.parse(fs.readFileSync(path.join(__dirname, 'parts', '06.json'), 'utf8'));
  const issues = validate(ledger, census);
  if (issues.length) { console.error(issues.join('\\n')); process.exitCode = 1; }
  else console.log('PASS: six source-only Baltimore LOC photo records, all release gates held');
}
