'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {validate, sourceRoute} = require('./verify_live_view_12_20261115.cjs');
const source = JSON.parse(fs.readFileSync(path.join(__dirname, 'wp_twelve_remaining_posts_view_routes_20261115.json'), 'utf8'));
const cloned = () => JSON.parse(JSON.stringify(source));
const rejected = (mutation) => { const doc = cloned(); mutation(doc); assert.equal(validate(doc).ok, false); };

test('exact 12 post / 54 slot snapshot passes', () => {
  const result = validate(source);
  assert.deepEqual(result.errors, []);
  assert.deepEqual(result.route_counts, {wikimedia_external:27, firstparty_jetpack:8, external_jetpack:19});
});
test('Jetpack with offsite origin is not first party', () => {
  assert.deepEqual(sourceRoute('https://i0.wp.com/images-assets.nasa.gov/example.jpg?resize=960%2C640&ssl=1'), ['external_jetpack','images-assets.nasa.gov']);
});
test('Jetpack with site origin is first party', () => {
  assert.deepEqual(sourceRoute('https://i0.wp.com/finalvestige.com/wp-content/uploads/test.jpg'), ['firstparty_jetpack','finalvestige.com']);
});
test('direct Commons redirect is not first party', () => {
  assert.deepEqual(sourceRoute('https://commons.wikimedia.org/wiki/Special:Redirect/file/photo.jpg?width=960'), ['wikimedia_external','commons.wikimedia.org']);
});
test('invented 404 guest status is rejected', () => rejected(d=>{d.posts[0].images[0].guest_http_status=404;}));
test('invented decoded width is rejected', () => rejected(d=>{d.posts[0].images[0].guest_decode_width=640;}));
test('invented network bytes are rejected', () => rejected(d=>{d.posts[0].images[0].guest_transfer_bytes=2048;}));
test('false 42 broken confirmation is rejected', () => rejected(d=>{d.release_gates.reported_42_broken_guest_verified=true;}));
test('false 76% measured claim is rejected', () => rejected(d=>{d.release_gates.claimed_76_pct_weight_measured=true;}));
test('unauthorized cache approval is rejected', () => rejected(d=>{d.posts[0].images[0].cache_authorized=true;}));
test('unauthorized rehosting approval is rejected', () => rejected(d=>{d.posts[0].images[0].rights_to_rehost_verified=true;}));
test('invented 960+ pixel derivative cap is rejected', () => rejected(d=>{d.release_gates.max_derivative_width_px=1200;}));
test('one dropped slot is rejected even if aggregate count is unchanged', () => rejected(d=>{d.posts[5].images.pop();}));
test('duplicate slot ID is rejected', () => rejected(d=>{d.posts[10].images[1].key=d.posts[10].images[0].key;}));
test('incorrect remote Jetpack classification is rejected', () => rejected(d=>{d.posts[5].images[1].origin_route='firstparty_jetpack';}));
test('invalid URL is rejected', () => rejected(d=>{d.posts[0].images[0].view_src='javascript:alert(1)';}));
test('negative dimensions are rejected', () => rejected(d=>{d.posts[5].images[0].width_px=-1;}));
test('fabricated responsive census is rejected', () => rejected(d=>{d.counts.with_srcset=54;}));
test('production write authorization is rejected', () => rejected(d=>{d.release_gates.wordpress_writes_authorized=true;}));
