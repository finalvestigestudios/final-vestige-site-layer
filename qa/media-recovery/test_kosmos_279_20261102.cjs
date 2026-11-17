'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const { validate } = require('./validate_kosmos_279_20261102.cjs');
const root = __dirname;
const text = fs.readFileSync(path.join(root, 'parts/03.json'));
const sha = crypto.createHash('sha1').update(Buffer.from('blob ' + text.length + '\0')).update(text).digest('hex');
const census = JSON.parse(text.toString('utf8'));
const actual = JSON.parse(fs.readFileSync(path.join(root, 'kosmos_279_hotlink_source_recovery_20261102.json'),'utf8'));
const clone = x => JSON.parse(JSON.stringify(x));
const tests = [
  ['baseline', d => {}, true],
  ['invented 404 origin', d => { d.rows[0].independent_retriever.numeric_origin_http_status = 404; }],
  ['fabricated browser success', d => { d.rows[0].guest_browser.image_http_status = 200; }],
  ['fabricated broken browser', d => { d.rows[0].guest_browser.visibly_broken = true; }],
  ['swap picture URL', d => { d.rows[0].stored_image_url = d.rows[1].stored_image_url; }],
  ['invented clear license', d => { d.rows[0].rights_approved = true; }],
  ['unauthorized WordPress cache', d => { d.rows[0].wordpress_cache_authorized = true; }],
  ['unauthorized post rewrite', d => { d.rows[0].wordpress_post_edit_authorized = true; }],
  ['upscaled DOE original', d => { d.rows[0].archive_candidate_assets[0].conditional_preview_px.width = 960; }],
  ['altered crop shape', d => { d.rows[0].archive_candidate_assets[0].conditional_preview_px.height = 200; }],
  ['different archival scene mislabeled same', d => { d.rows[2].archive_candidate_assets[0].relation = 'SAME_SCENE_VISUALLY_VERIFIED_NOT_BINARY'; }],
  ['false 42 broken claim', d => { d.site_wide_context.reported_42_broken_not_browser_verified = false; }],
  ['false 76 measured claim', d => { d.site_wide_context.claimed_76pct_not_measured = false; }],
  ['editorial ALT approved without review', d => { d.rows[3].visual_integrity_issue.approved = true; }],
  ['rewrite Site QA', d => { d.release.site_qa_pr154_edited = true; }],
  ['falsified author source SHA', d => { d.census.source_blob_sha = '0'.repeat(40); }],
];
assert.equal(sha,'49183f66f880f7c4dfd363acca906876877f2e5e','source census has changed');
for (const [name, mutate, shouldPass] of tests) {
  const d = clone(actual); mutate(d);
  const errors = validate(d,census,sha);
  assert.equal(errors.length === 0,shouldPass === true,name+': '+errors.join(', '));
}
process.stdout.write(tests.length+' native Node cases PASS\n');
