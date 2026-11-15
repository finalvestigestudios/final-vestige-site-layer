'use strict';
// Native Node regression definitions for six-post, forty-two-slot WordPress EDIT/VIEW ledger.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {validateAudit} = require('./validate_wp_view_six_archival_20261115.cjs');
const ledger = JSON.parse(fs.readFileSync(path.join(__dirname,'wp_view_six_archival_posts_42_slots_20261115.json'),'utf8'));
const fresh = () => JSON.parse(JSON.stringify(ledger));
test('committed read-only audit validates exact 42 URL/image slots', () => {
  assert.equal(validateAudit(fresh()).counts.slots,42);
});
const negative = [
  ['invented guest HTTP status', a => {a.rows[0].guest_http_status = 404;}],
  ['invented transferred bytes', a => {a.rows[0].guest_network_bytes = 25000;}],
  ['origin and proxy identity diverge', a => {a.rows[0].view_src = 'https://i0.wp.com/unrelated.example/missing.jpg?ssl=1';}],
  ['slot collision', a => {a.rows[1].key = a.rows[0].key;}],
  ['missing slot', a => {a.rows.pop();}],
  ['wrong per-post count', a => {a.posts[0].image_slots = 1;}],
  ['unlicensed cache approval', a => {a.rows[0].caching_authorized = true;}],
  ['WordPress upload approval fabricated', a => {a.rows[0].wp_upload_authorized = true;}],
  ['Gutenberg rewrite approval fabricated', a => {a.rows[0].post_rewrite_authorized = true;}],
  ['invented native geometry', a => {a.rows[0].review_px = [960,960];}],
  ['wrong 960px derivative for 665px master', a => {a.rows.find(x => x.key === '268:0').review_px = [960,647];}],
  ['unmeasured wire-claim replaced', a => {a.comparison_baseline.claimed_visitor_transfer_reduction_unmeasured_percent = 0;}],
  ['Florida item ID substitution', a => {a.rows.find(x => x.key === '432:6').candidate.id = 'PR04493';}],
  ['fabricated visitor broken proof', a => {a.rows[0].visitor_broken_verified = true;}],
  ['aggregate route count tampered', a => {a.counts.jetpack_external++;}],
  ['responsive geometry fabricated', a => {a.rows[0].view_width = 960;}],
  ['ALT evidence erased', a => {a.rows[0].alt = '';}],
  ['duplicate post metadata', a => {a.posts[0].id = a.posts[1].id;}],
  ['invalid short post URL', a => {a.posts[0].link = 'https://example.com/a';}],
  ['all rights cleared without evidence', a => {a.rows[0].review_requires_rights = false;}],
];
for (const [name, edit] of negative) {
  test('rejects '+name, () => {
    const x = fresh(); edit(x);
    assert.throws(() => validateAudit(x));
  });
}
