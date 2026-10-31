'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {loadSnapshot} = require('./validate_inventory.cjs');
const {validatePulaski} = require('./validate_pulaski.cjs');
const census = loadSnapshot().parts.flatMap(part => part.images);
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'pulaski_bigburn_primary_20261030.json'), 'utf8'));
const copy = () => JSON.parse(JSON.stringify(fixture));

test('read-only source crosswalk: five exact archive items, five viewer images, zero browser claims', () => {
  const result = validatePulaski(copy(), census);
  assert.equal(result.ok, true, result.errors.join(' / '));
  assert.equal(result.exact_archival_crosswalks, 5);
  assert.equal(result.verified_guest_browser_failures, null);
});
const invalid = [
  ['wrong article', x => x.post_id = 432],
  ['false live CMS status', x => x.published_in_cms = false],
  ['changed modified time', x => x.post_modified = '2026-10-30'],
  ['wrong total images', x => x.fresh_cms_exact_img_count = 5],
  ['extra offsite item', x => x.external_images = 6],
  ['invented archival catalog count', x => x.official_catalog_exact_matches = 6],
  ['invented browser probe', x => x.actual_guest_browser_checks = 5],
  ['42 failures misreported as confirmed', x => x.claim_42_broken = 'VERIFIED'],
  ['76 percent presented as measured', x => x.claim_76_percent_savings = 76],
  ['production edits falsely recorded', x => x.production_wordpress_writes = 1],
  ['remove a source row', x => x.rows.pop()],
  ['duplicate a source row', x => x.rows[2].image_key = '428:1'],
  ['replace exact Idaho URL', x => x.rows[0].source_url = 'https://example.org/image.jpg'],
  ['alter source alt', x => x.rows[1].stored_alt = 'burned photograph'],
  ['spoof official catalog', x => x.rows[2].official_identifier = '8-X545e'],
  ['relabel official item URL', x => x.rows[3].official_record_url = 'https://www.lib.uidaho.edu/digital/bigburn/items/bigburn10.html'],
  ['unverified image date', x => x.rows[0].archive_date = '1923'],
  ['invent source markup width', x => x.rows[0].wp_markup_width_px = 1024],
  ['claim viewer is guest browser', x => x.rows[0].viewer_observation = 'guest_browser_http_200'],
  ['invent HTTP status', x => x.rows[0].guest_browser_http_status = 200],
  ['invent natural width', x => x.rows[0].guest_browser_natural_width_px = 1000],
  ['invent transfer bytes', x => x.rows[0].guest_browser_transfer_bytes = 49202],
  ['invent broken image finding', x => x.rows[0].broken_in_guest_browser = true],
  ['invent wire savings', x => x.rows[0].measured_weight_savings_pct = 76],
  ['invent source file SHA', x => x.rows[0].original_binary_sha256 = 'a'.repeat(64)],
  ['invent original pixels', x => x.rows[0].original_file_dimensions_px = [1024, 768]],
  ['publish derivative dimensions without binary', x => x.rows[0].derivative_dimensions_px = [960, 720]],
  ['upscale guard disabled', x => x.rows[0].never_upscale = false],
  ['wrong 960 constraint', x => x.rows[0].maximum_derivative_width_px = 1280],
  ['public domain misrepresented as publication clearance', x => x.rows[0].publication_rights_cleared = true],
  ['fabricated WordPress media ID', x => x.rows[0].wp_media_id = 34],
  ['unauthorized upload', x => x.rows[0].wp_upload_authorized = true],
  ['unauthorized post edit', x => x.rows[0].wp_post_edit_authorized = true],
  ['false responsive image verification', x => x.rows[0].wordpress_responsive_delivery_unverified = false],
  ['fake LOC source', x => x.rows[4].source_url = 'https://tile.loc.gov/something-else.jpg'],
  ['false LOC identity', x => x.rows[4].identity_basis = 'EDITORIAL_SIMILAR_IMAGE'],
  ['false rights status', x => x.rows[4].official_rights_statement = 'NO_RESTRICTIONS_UNIVERSALLY']
];
for (const [label, change] of invalid) test('reject ' + label, () => {
  const modified = copy();
  change(modified);
  assert.equal(validatePulaski(modified, census).ok, false, label);
});
test('reject partial inventory', () => {
  const shorter = census.filter(x => x.key !== '428:5');
  assert.equal(validatePulaski(copy(), shorter).ok, false);
});
