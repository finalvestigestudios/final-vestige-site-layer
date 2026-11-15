'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {validate} = require('./validate_token_route_differential_20261115.cjs');
const original = require('./token_route_differential_2_20261115.json');
const clone = () => JSON.parse(JSON.stringify(original));
test('two routes remain held, no fabricated guest HTTP or savings', () => {
  assert.equal(validate(clone()).decision, 'HOLD_FOR_COLD_BROWSER');
});
test('reject invented 200 origin status', () => {
  const x=clone(); x.records[0].observations[0].origin_http_status=200;
  assert.throws(()=>validate(x));
});
test('reject fabricated visitor failure', () => {
  const x=clone(); x.records[0].guest_failure_verified=true;
  assert.throws(()=>validate(x));
});
test('reject fabricated bandwidth reduction', () => {
  const x=clone(); x.visitor_transfer_savings_percent=76;
  assert.throws(()=>validate(x));
});
test('reject silently restored Drupal itok in Jetpack route', () => {
  const x=clone(); x.records[0].wordpress_view_jetpack_url+='&itok=ex2XHVlK';
  assert.throws(()=>validate(x));
});
test('reject mismatched source image identity', () => {
  const x=clone(); x.records[1].original_without_token_url=x.records[0].original_without_token_url;
  assert.throws(()=>validate(x));
});
test('reject site-wide cache, upload or rewrite authorization', () => {
  for (const p of ['cache_authorized','wp_upload_authorized','post_rewrite_authorized']) {
    const x=clone(); x.records[0][p]=true; assert.throws(()=>validate(x));
  }
});
test('reject false 960px derivative while dimensions unknown', () => {
  const x=clone(); x.records[1].review_dimensions_px=[960,640];
  assert.throws(()=>validate(x));
});
test('reject claimed rehosting rights', () => {
  const x=clone(); x.records[0].rehosting_rights_cleared=true;
  assert.throws(()=>validate(x));
});
test('reject substituting alternative photo as exact match', () => {
  const x=clone(); x.records[0].exact_replacement_image_verified=true;
  assert.throws(()=>validate(x));
});
test('reject ambiguous retriever result as browser status', () => {
  const x=clone(); x.records[1].observations[2].guest_browser_http_status=404;
  assert.throws(()=>validate(x));
});
test('reject forged additional slot', () => {
  const x=clone(); x.records.push({...x.records[0],key:'288:6'});
  assert.throws(()=>validate(x));
});
