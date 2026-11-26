'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {verify} = require('./validate_honda288.cjs');
const baseline = JSON.parse(fs.readFileSync(path.join(__dirname, 'honda_288_navy_20261116_1722pt.json'), 'utf8'));
function mutated(fn) { const x = structuredClone(baseline); fn(x); assert.throws(() => verify(x)); }
test('actual six-image read-only audit is internally consistent', () => {
  assert.deepEqual(verify(baseline), {status:'PASS_NO_RELEASE',rows:6,official_catalog_crosswalks:4,guest_broken_confirmed:0,production_writes:0});
});
const cases = [
  ['invented 2xx visitor status', x=>x.rows[0].guest_browser.http_status=200],
  ['fabricated page-load image decoding', x=>x.rows[0].guest_browser.decoded=true],
  ['fabricated wire bytes', x=>x.rows[0].guest_browser.wire_bytes=19876],
  ['web retriever code misrepresented as HTTP', x=>x.rows[0].public_retriever.original_numeric_http_status=502],
  ['false no-upscale target', x=>x.rows[1].primary_source_candidate.conditional_target_width=1440],
  ['distorted proportions', x=>x.rows[1].primary_source_candidate.conditional_target_height=450],
  ['release before rights', x=>x.rows[3].primary_source_candidate.individual_rights_approved=true],
  ['cache before review', x=>x.rows[3].media_cache_authorized=true],
  ['WordPress write authorization', x=>x.rows[0].wordpress_write_authorized=true],
  ['unverified pixel identity', x=>x.rows[4].exact_pixel_match_verified=true],
  ['unapproved catalog host', x=>x.rows[4].primary_source_candidate.catalog_url='https://media.example.org/not-navy'],
  ['mismatched proxy origin', x=>x.rows[0].view_current_markup_src='https://i0.wp.com/another.org/x.jpg'],
  ['missing image slot', x=>x.rows.pop()],
  ['duplicate slot', x=>x.rows[5].slot='288:0'],
  ['inflated claimed guest image fails', x=>x.claims.guest_confirmed_broken=42],
  ['invented 76 percent savings measured', x=>x.claims.measured_wire_savings_pct=76],
  ['stored bytes passed as transfer bytes', x=>x.rows[2].guest_browser.wire_bytes=64385752],
  ['incorrect WordPress revision', x=>x.site_post_modified='2026-11-16T17:22:00'],
  ['new response width attribute falsely reported', x=>x.rows[4].wp_view_width=960],
  ['falsified confirmed copyright release', x=>x.rows[5].rights_release='APPROVED'],
  ['fabricated image SHA', x=>x.rows[3].media_sha256='deadbeef'],
  ['renamed primary catalog', x=>x.rows[1].primary_source_candidate.asset_catalog_id='NH 00000'],
  ['invented site changes', x=>x.production_writes=1],
  ['invented image download', x=>x.downloaded_images=1],
  ['invented authorization', x=>x.authorized_replacements=1],
];
for (const [name,fn] of cases) test('reject '+name, () => mutated(fn));
