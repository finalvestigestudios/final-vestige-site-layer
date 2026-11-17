'use strict';
// Offline-only, read-only adjudication. Never fetches, rewrites, or republishes image bytes.
const assert = require('node:assert/strict');
function validate(a) {
  assert.equal(a?.schema, 'fv-media-token-route-differential-v1');
  assert.equal(a?.records?.length, 2);
  assert.deepEqual(a.records.map(x => x.key).sort(), ['288:5', '418:5']);
  assert.equal(a.method, 'web_reader_open_not_browser_http');
  assert.equal(a.reported_broken_browser_verified, null);
  assert.equal(a.visitor_transfer_savings_percent, null);
  assert.equal(a.actions?.wordpress_writes, 0);
  assert.equal(a.actions?.image_downloads, 0);
  assert.equal(a.actions?.production_deploys, 0);
  assert.equal(a.actions?.subscription_spend_usd, 0);
  for (const r of a.records) {
    const u = new URL(r.original_with_token_url);
    const proxy = new URL(r.wordpress_view_jetpack_url);
    const untokened = new URL(r.original_without_token_url);
    assert.equal(u.protocol, 'https:');
    assert.equal(untokened.protocol, 'https:');
    assert.equal(proxy.protocol, 'https:');
    assert.equal(proxy.hostname, 'i0.wp.com');
    assert.equal(u.searchParams.get('itok'), r.itok);
    assert.equal(untokened.searchParams.get('itok'), null);
    assert.equal(proxy.searchParams.get('itok'), null);
    assert.equal(untokened.origin, u.origin);
    assert.equal(untokened.pathname, u.pathname);
    const without = new URL(r.original_with_token_url);
    without.searchParams.delete('itok');
    assert.equal(without.toString(), untokened.toString());
    assert.equal(proxy.pathname.slice(1), u.hostname + u.pathname);
    assert.equal(r.observations.length, 3);
    assert.deepEqual(r.observations.map(x => x.route).sort(), ['original_with_token', 'original_without_token', 'wordpress_view_jetpack']);
    for (const o of r.observations) {
      assert.ok(['web_reader_image_rendered', 'web_reader_inaccessible'].includes(o.reader_result));
      assert.equal(o.origin_http_status, null);
      assert.equal(o.guest_browser_http_status, null);
      assert.equal(o.guest_browser_natural_width, null);
      assert.equal(o.network_encoded_bytes, null);
      assert.equal(o.visitor_broken_verified, null);
    }
    assert.equal(r.observations.find(x => x.route === 'original_with_token').reader_result, 'web_reader_image_rendered');
    for (const p of ['original_without_token','wordpress_view_jetpack'])
      assert.equal(r.observations.find(x => x.route === p).reader_result, 'web_reader_inaccessible');
    assert.ok(r.authoritative_catalog_url.startsWith('https://'));
    assert.equal(r.exact_replacement_image_verified, false);
    assert.equal(r.rehosting_rights_cleared, false);
    assert.equal(r.max_review_width_px, 960);
    assert.equal(r.original_dimensions_px, null);
    assert.equal(r.review_dimensions_px, null);
    assert.equal(r.no_upscale, true);
    assert.equal(r.cache_authorized, false);
    assert.equal(r.wp_upload_authorized, false);
    assert.equal(r.post_rewrite_authorized, false);
    assert.equal(r.guest_failure_verified, false);
  }
  return { decision: 'HOLD_FOR_COLD_BROWSER', query_token_risk_keys: a.records.map(r => r.key), browser_confirmed_broken: null, measured_weight_savings: null };
}
if (require.main === module) {
  const path = require('node:path');
  const data = require(path.join(__dirname, 'token_route_differential_2_20261115.json'));
  process.stdout.write(JSON.stringify(validate(data)) + '\n');
}
module.exports = { validate };
