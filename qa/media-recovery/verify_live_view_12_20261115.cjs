'use strict';
const fs = require('node:fs');
const path = require('node:path');

const EXPECTED_IDS = [1926, 1924, 1922, 1920, 1917, 434, 433, 431, 428, 425, 413, 367];
const EXPECTED_CLASSES = {wikimedia_external: 27, firstparty_jetpack: 8, external_jetpack: 19};

function sourceRoute(url) {
  const match = typeof url === 'string' && url.match(/^https?:\/\/([^/?#]+)(\/[^?#]*)?/i);
  if (!match) return ['invalid', null];
  const hostname = match[1].toLowerCase();
  if (/^i\d\.wp\.com$/.test(hostname)) {
    const origin = (match[2] || '').split('/')[1]?.toLowerCase() || '';
    return [origin === 'finalvestige.com' ? 'firstparty_jetpack' : 'external_jetpack', origin];
  }
  if (hostname === 'finalvestige.com' || hostname === 'www.finalvestige.com') return ['firstparty_direct', hostname];
  return [hostname.endsWith('wikimedia.org') ? 'wikimedia_external' : 'external_direct', hostname];
}

function validate(doc) {
  const errors = [];
  const fail = (condition, message) => { if (!condition) errors.push(message); };
  fail(doc && doc.schema === 'fv-wp-published-12post-view-route-v1', 'schema');
  fail(doc?.date_pacific === '2026-11-15', 'date');
  fail(Array.isArray(doc?.posts) && doc.posts.length === 12, 'post count');
  fail(doc?.counts?.posts === 12 && doc?.counts?.images === 54, 'declared census');
  const ids = [], keys = new Set(), types = {}, records = [];
  for (const p of doc?.posts || []) {
    ids.push(p.id);
    fail(Number.isInteger(p.id) && typeof p.link === 'string' && p.link.startsWith('https://finalvestige.com/'), 'post id/link');
    fail(typeof p.modified === 'string' && Array.isArray(p.images), 'modified/images');
    for (const [slot, r] of (p.images || []).entries()) {
      fail(r.key === p.id + ':' + slot && r.slot === slot && !keys.has(r.key), 'unique contiguous slot');
      keys.add(r.key);
      const [route, host] = sourceRoute(r.view_src);
      fail(route === r.origin_route && host === r.origin_host && route !== 'invalid', 'actual URL origin route');
      fail(typeof r.alt === 'string' && r.alt.trim().length > 0, 'alt');
      for (const dimension of ['width_px', 'height_px']) {
        fail(r[dimension] === null || (Number.isInteger(r[dimension]) && r[dimension] > 0), 'dimensions');
      }
      fail(typeof r.srcset_present === 'boolean' && typeof r.sizes_present === 'boolean', 'responsive flags');
      for (const key of ['guest_current_src', 'guest_http_status', 'guest_decode_width', 'guest_transfer_bytes']) {
        fail(r[key] === null, 'no invented guest network/browser evidence: ' + key);
      }
      fail(r.rights_to_rehost_verified === false && r.cache_authorized === false, 'no rights/caching approvals');
      types[route] = (types[route] || 0) + 1;
      records.push(r);
    }
  }
  fail(JSON.stringify(ids) === JSON.stringify(EXPECTED_IDS), 'fixed selected live cohort');
  fail(records.length === 54 && keys.size === 54, '54 distinct slots');
  fail(JSON.stringify(types) === JSON.stringify(EXPECTED_CLASSES), 'observed origin routes');
  const missingDim = records.filter(r => !(r.width_px > 0 && r.height_px > 0)).length;
  fail(doc?.counts?.missing_width_or_height === missingDim && missingDim === 35, 'dimension census');
  const srcset = records.filter(r => r.srcset_present).length;
  const sizes = records.filter(r => r.sizes_present).length;
  fail(srcset === 8 && sizes === 8 && doc?.counts?.with_srcset === srcset && doc?.counts?.with_sizes === sizes, 'responsive census');
  fail(doc?.counts?.blank_alt === 0 && doc?.counts?.invalid_src === 0 && doc?.counts?.visitor_failures_verified === null, 'no unproven broken claim');
  for (const [name, count] of Object.entries(EXPECTED_CLASSES)) fail(doc?.counts?.route_counts?.[name] === count, 'declared origin route ' + name);
  const gates = doc?.release_gates || {};
  fail(gates.browser_http_status_known === false && gates.actual_network_bytes_known === false &&
    gates.reported_42_broken_guest_verified === false && gates.claimed_76_pct_weight_measured === false,
    'no unmeasured failure or savings claim');
  fail(gates.requires_exact_scene_and_rights === true && gates.max_derivative_width_px === 960 &&
    gates.no_upscale === true && gates.wordpress_writes_authorized === false &&
    gates.third_party_image_downloads === 0 && gates.production_changes === 0, 'release hold');
  return {ok: errors.length === 0, errors, image_count: records.length, route_counts: types};
}

if (require.main === module) {
  const file = process.argv[2] || path.join(__dirname, 'wp_twelve_remaining_posts_view_routes_20261115.json');
  const result = validate(JSON.parse(fs.readFileSync(file, 'utf8')));
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  if (!result.ok) process.exitCode = 1;
}
module.exports = {validate, sourceRoute};
