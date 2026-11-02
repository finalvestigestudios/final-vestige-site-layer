'use strict';
// Native Node replay for the authenticated 61-post / 355-image WP source audit.
// Offline only: reads committed fixture JSON, never fetches or edits WordPress.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { originClass, validateLiveCensus } = require('./validate_live_wp_source_recheck_20261102.cjs');
const read = relative => JSON.parse(fs.readFileSync(path.join(__dirname, relative), 'utf8'));
const nums = ['01','02','03','04','05','06','07','08'];
const source = read('live_wp_source_recheck_summary_20261102.json');
const live = nums.map(n => read('wp_live_recheck_20261102_part' + n + '.json'));
const frozen = nums.map(n => read('parts/' + n + '.json'));
const clone = o => JSON.parse(JSON.stringify(o));
const valid = (s=source,l=live,o=frozen) => validateLiveCensus(s,l,o);
assert.deepEqual(valid(), []);
let total = 1;
const negative = [
  ['forged 42 broken', d => d.s.aggregate.reported_42_broken_guest_verified = true],
  ['forged 76% transfer savings', d => d.s.aggregate.claimed_76_percent_wire_weight_saved_measured = true],
  ['invented production repair', d => d.s.aggregate.production_media_repairs = 1],
  ['publication permission', d => d.s.interpretation.publish_permission = true],
  ['wrong external count', d => d.s.aggregate.external_origin_total = 286],
  ['wrong first-party count', d => d.s.aggregate.first_party_direct = 61],
  ['wrong first-party proxy count', d => d.s.aggregate.first_party_jetpack = 8],
  ['wrong third-party proxy count', d => d.s.aggregate.third_party_via_jetpack = 1],
  ['fabricated guest HTTP', d => d.l[0].posts[0].slots[0].guest_browser_http_status = 404],
  ['fabricated guest bytes', d => d.l[0].posts[0].slots[0].visitor_transfer_bytes = 1000],
  ['fabricated decoded image', d => d.l[0].posts[0].slots[0].guest_browser_decoded = true],
  ['wrong historic ALT', d => d.l[0].posts[0].slots[0].alt += ' altered'],
  ['wrong historic src', d => d.l[0].posts[0].slots[0].source_url = 'https://example.com/a.jpg'],
  ['false source-match flag', d => d.l[0].posts[0].slots[0].matches_20261030_snapshot = false],
  ['wrong slot key', d => d.l[0].posts[0].slots[0].key = 'wrong:key'],
  ['unpublished post', d => d.l[0].posts[0].status = 'draft'],
  ['post timestamp drift', d => d.l[0].posts[0].modified = '2026-11-02'],
  ['unapproved asset rights', d => d.l[0].rights_cleared_for_rehosting = true],
  ['unapproved WordPress mutation', d => d.l[0].wordpress_writes_authorized = true],
  ['made-up network proof', d => d.l[0].network_source_statuses_verified = true],
  ['priority rights bypass', d => d.s.priority_source_identity[0].rights_to_republish = 'APPROVED'],
  ['priority 960px limit bypass', d => d.s.priority_source_identity[0].derivative_max_width_px = 1500],
  ['priority visitor status invented', d => d.s.priority_source_identity[0].visitor_browser_http_status = 200],
  ['priority image changed', d => d.s.priority_source_identity[0].stored_image_url = 'https://example.org/wrong.jpg'],
  ['third-party proxy mislabel', d => d.l[1].posts.flatMap(p=>p.slots).find(x=>x.key==='291:0').origin_class = 'FIRST_PARTY_JETPACK'],
  ['first-party proxy mislabel', d => d.l[1].posts.flatMap(p=>p.slots).find(x=>x.key==='299:0').origin_class = 'THIRD_PARTY_JETPACK'],
  ['deleted image slot', d => d.l[0].posts[0].slots.pop()],
  ['edited historical evidence', d => d.o[0].images[0].source_url = 'https://example.org/forged.jpg'],
  ['forged frozen git blob', d => d.l[0].frozen_git_blob_sha = '0'.repeat(40)],
  ['wrong partition identity', d => d.l[0].part = 7],
  ['wrong per-part image count', d => d.l[0].counts.inline_img_tags = 0],
];
for (const [label, change] of negative) {
  const data = {s:clone(source), l:clone(live), o:clone(frozen)};
  change(data);
  const errors = valid(data.s, data.l, data.o);
  assert.ok(errors.length > 0, 'validator failed open: ' + label);
  total++;
}
const examples = [
  ['https://finalvestige.com/wp-content/uploads/photo.jpg','FIRST_PARTY'],
  ['https://i0.wp.com/finalvestige.com/wp-content/uploads/photo.jpg?ssl=1','FIRST_PARTY_JETPACK'],
  ['https://i0.wp.com/text-message.blogs.archives.gov/photo.jpg?ssl=1','THIRD_PARTY_JETPACK'],
  ['https://i0.wp.com/www.squawkpoint.com/photo.jpg?ssl=1','THIRD_PARTY_JETPACK'],
  ['https://commons.wikimedia.org/wiki/File:X.jpg','THIRD_PARTY'],
  ['javascript:alert(1)','NON_HTTP_OR_INVALID'],
  ['ftp://example.com/photo.jpg','NON_HTTP_OR_INVALID'],
];
for (const [url, kind] of examples) { assert.equal(originClass(url),kind); total++; }
console.log(total + '/' + total + ' live-WP source provenance/regression tests passed (offline).');
