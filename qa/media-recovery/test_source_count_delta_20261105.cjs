'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const data = require('./source_count_delta_20261105.json');
const { check } = require('./validate_source_count_delta_20261105.cjs');
const copy = () => JSON.parse(JSON.stringify(data));
test('valid pinned audit passes', () => assert.equal(check(copy()).ok, true));
const cases = [
  ['missing eighth source batch', x => delete x.inputs.media_source_parts['08']],
  ['false 286 versus 288 total', x => x.reconciliation.site_qa_offsite_total = 288],
  ['fake root-cause certainty', x => x.reconciliation.root_cause_status = 'FIXED_CLASSIFICATION_BUG'],
  ['wrong delta post', x => x.reconciliation.affected_posts[0].post_id = 292],
  ['duplicate delta post', x => x.reconciliation.affected_posts[1].post_id = 291],
  ['wrong per-post count', x => x.reconciliation.affected_posts[0].media_source_offsite = 5],
  ['misclassified proxied external source', x => x.reconciliation.affected_posts[1].classifier_treatment_of_that_url = 'jetpack_proxy'],
  ['wrong original source host', x => x.reconciliation.affected_posts[0].exact_external_jetpack_host_reference_url = 'https://i0.wp.com/finalvestige.com/unsafe.jpg'],
  ['misidentified portrait', x => x.p0_us_coast_guard_primary_record.primary_catalog_scene = 'tsunami rubble'],
  ['incorrect source VIRIN', x => x.p0_us_coast_guard_primary_record.primary_catalog_virin = 'bad.JPG'],
  ['fabricated browser 404', x => x.p0_us_coast_guard_primary_record.actual_browser_http_status = 404],
  ['fabricated measured bytes', x => x.p0_us_coast_guard_primary_record.actual_browser_transfer_bytes = 12345],
  ['unlicensed caching approval', x => x.p0_us_coast_guard_primary_record.cache_approved = true],
  ['production write approval', x => x.p0_us_coast_guard_primary_record.wordpress_write_approved = true],
  ['invented source dimensions', x => x.p0_us_coast_guard_primary_record.derivative_dimensions_px = [960,720]],
  ['false identity SHA', x => x.p0_us_coast_guard_primary_record.source_binary_sha256 = 'abcdef'],
  ['claimed 42 broken verified', x => x.sitewide_context.reported_42_broken_browser_verified = true],
  ['claimed 76 percent measured', x => x.sitewide_context.claimed_76pct_wire_reduction_measured = true]
];
for (const [label, mutate] of cases) test('rejects ' + label, () => { const x = copy(); mutate(x); assert.throws(() => check(x), /MEDIA_DELTA_INVALID/); });
