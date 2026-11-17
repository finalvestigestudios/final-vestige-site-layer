'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { validate, EXPECTED } = require('./validate_baltimore_190.cjs');
const ledger = JSON.parse(fs.readFileSync(path.join(__dirname, 'baltimore_190_loc_20261101.json'), 'utf8'));
const census = JSON.parse(fs.readFileSync(path.join(__dirname, 'parts', '06.json'), 'utf8'));
const copy = x => JSON.parse(JSON.stringify(x));
function rejects(label, mutate, needle) {
  test(label, () => {
    const d = copy(ledger), c = copy(census);
    mutate(d, c);
    const result = validate(d, c);
    assert.ok(result.length, 'tampering should be rejected');
    assert.ok(result.some(x => x.includes(needle)), JSON.stringify(result));
  });
}
test('baseline exact six LOC URLs, IDs and rights-hold gates pass', () => {
  assert.equal(EXPECTED.length, 6);
  assert.deepEqual(validate(ledger, census), []);
});
rejects('reject mismatched frozen inventory SHA', d => { d.frozen_census_blob_sha = 'bad'; }, 'frozen census SHA');
rejects('reject fabricated 42 broken claim', d => { d.claimed_42_broken_verified = true; }, 'unverified success');
rejects('reject fabricated 76 percent savings claim', d => { d.claimed_76_percent_saved_verified = true; }, 'unverified success');
rejects('reject staged WordPress production write', d => { d.wordpress_production_writes = 1; }, 'unsafe action');
rejects('reject swapped source image', d => { d.items[0].source_url = d.items[1].source_url; }, 'frozen URL/ALT');
rejects('reject changed source ALT', d => { d.items[2].stored_alt = 'other photo'; }, 'frozen URL/ALT');
rejects('reject catalog masquerade', d => { d.items[1].loc_lccn = d.items[0].loc_lccn; }, 'catalog identity');
rejects('reject missing published source', d => { d.items.pop(); }, 'not six items');
rejects('reject duplicate post slot', d => { d.items[3].key = '190:0'; }, 'duplicate item');
rejects('reject wrong LOC CDN hostname', d => { d.items[0].source_url = 'https://example.net/service/pnp/npcc/18700/18735v.jpg'; }, 'expected LOC');
rejects('reject release before rights approval', d => { d.items[0].rights_item_review = 'APPROVED'; }, 'unauthorized action');
rejects('reject unauthorized media upload', d => { d.items[5].wordpress_upload_authorized = true; }, 'unauthorized action');
rejects('reject downloaded master', d => { d.items[5].asset_downloaded = true; }, 'unauthorized action');
rejects('reject fabricated SHA-256', d => { d.items[3].master_sha256 = 'deadbeef'; }, 'fabricated');
rejects('reject unsupported Image HTTP 404', d => { d.items[3].actual_browser_http_status = 404; }, 'fabricated');
rejects('reject unsupported decoded currentSrc', d => { d.items[3].actual_browser_current_src = 'https://cdn.loc.gov/x.jpg'; }, 'fabricated');
rejects('reject unsupported browser bytes', d => { d.items[4].actual_browser_transfer_bytes = 99000; }, 'fabricated');
rejects('reject unsupported naturalWidth', d => { d.items[4].actual_browser_natural_width_px = 1; }, 'fabricated');
rejects('reject fabricated broken visitor image', d => { d.items[4].broken_in_visitor_browser = true; }, 'fabricated');
rejects('reject speculative original dimensions', d => { d.items[5].source_width_px = 4000; }, 'fabricated');
rejects('reject speculative 960px derivative', d => { d.items[5].proposed_width_px = 960; }, 'fabricated');
rejects('reject over-960 plan', d => { d.items[2].max_derivative_width_px = 1280; }, 'resize safety');
rejects('reject upscaling', d => { d.items[2].prohibit_upscale = false; }, 'resize safety');
rejects('reject missing individual rights notes', d => { d.items[0].rights_notes = null; }, 'rights/credit');
rejects('reject missing exact publisher ID', d => { d.items[4].loc_digital_id = ''; }, 'catalog identity');
rejects('reject lack of staging safeguards', d => { d.items[5].localization_plan = 'bulk replacement'; }, 'staging');
rejects('reject poisoned census image source', (d,c) => { c.images.find(x => x.key === '190:1').source_url = 'https://unknown.example/b.jpg'; }, 'frozen URL/ALT');
rejects('reject malformed URL without throwing', d => { d.items[0].source_url = 'https://%/npcc/18700/18735v.jpg'; }, 'malformed source URL');
for (let i = 0; i < 6; i++) {
  rejects('image ' + i + ': tampered per-slot LCCN rejected', d => { d.items[i].loc_lccn += '0'; }, 'catalog identity');
  rejects('image ' + i + ': forged successful browser status rejected', d => { d.items[i].actual_browser_http_status = 200; }, 'fabricated');
}
