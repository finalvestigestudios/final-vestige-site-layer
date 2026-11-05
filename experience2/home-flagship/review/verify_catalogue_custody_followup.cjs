'use strict';
/**
 * Conservative release-status regression for the 2026-11-05 catalogue follow-up.
 * Native execution: node experience2/home-flagship/review/verify_catalogue_custody_followup.cjs
 * Source-only: NOT a WordPress render, media binary match, legal approval or browser QA.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const file = path.join(__dirname, 'archive-media-contract-20261105.json');
const contract = JSON.parse(fs.readFileSync(file,'utf8'));
const doc = fs.readFileSync(path.join(__dirname,'ARCHIVE_CATALOGUE_CUSTODY_FOLLOWUP_20261105.md'),'utf8');
const home = fs.readFileSync(path.resolve(__dirname,'..','index.html'),'utf8');

function accept(c) {
  assert.equal(c.release_decision, 'HOLD', 'No research may silently promote a release');
  assert.equal(c.assets.length, 3);
  const ap=c.assets.find(a=>a.key==='apollo');
  const fr=c.assets.find(a=>a.key==='franklin');
  const ny=c.assets.find(a=>a.key==='nypl');
  assert.ok(ap && fr && ny);
  assert.equal(ap.wp_media_id, 473);
  assert.equal(ap.claimed_archive_identifier, 'S67-19766');
  assert.equal(ap.source_identity, 'REVIEW_REQUIRED');
  assert.equal(ap.catalogue_trace.identifier, 'S67-19766');
  assert.equal(ap.catalogue_trace.status,'SECONDARY_INDEX_CORROBORATES_IDENTIFIER_NOT_LOCAL_BINARY');
  assert.match(ap.catalogue_trace.index_reference, /^https:\/\/nara\.getarchive\.net\//);
  assert.match(ap.catalogue_trace.index_owner_notice, /NOT an official/);
  assert.equal(ap.catalogue_trace.primary_image_url_directly_verified, false);
  assert.equal(ap.catalogue_trace.uploaded_webp_binary_matched, false);
  assert.equal(ap.network_body_sha256, null);
  assert.equal(ap.browser_response_status, null);
  assert.deepEqual(ap.catalogue_trace.indexed_large_dimensions, [7920,6160]);
  assert.deepEqual(ap.wp_media_dimensions, [1041,810]);

  assert.equal(fr.wp_media_id,474);
  assert.equal(fr.commons_preview_trace.status,'DIMENSIONS_MATCH_COMMONS_LISTED_PREVIEW_BINARY_UNMATCHED');
  assert.deepEqual(fr.commons_preview_trace.preview_dimensions,[960,1526]);
  assert.deepEqual(fr.wp_media_dimensions,fr.commons_preview_trace.preview_dimensions);
  assert.deepEqual(fr.commons_preview_trace.listed_original_dimensions,[1576,2506]);
  assert.equal(fr.commons_preview_trace.wp_media_binary_matched,false);
  assert.equal(fr.network_body_sha256,null);
  assert.equal(fr.browser_response_status,null);

  assert.equal(ny.embedded,false,'NYPL rights remain unresolved');
  assert.equal(ny.network_body_sha256,null);
  assert.equal(ny.browser_response_status,null);
  assert.equal((home.match(/<img\b/g)||[]).length,2);
  assert.ok(!home.includes('src="'+ny.src+'"'));
  assert.ok(home.includes('src="'+ap.src+'"') && home.includes('src="'+fr.src+'"'));
  assert.match(doc,/RELEASE HOLD/);
  assert.match(doc,/not a rights opinion|neither a rights opinion/i);
  return true;
}
assert.equal(accept(contract),true);
const bad=[
  ['NASA prematurely verified', c=>c.assets.find(a=>a.key==='apollo').source_identity='VERIFIED'],
  ['NASA upload claimed matched', c=>c.assets.find(a=>a.key==='apollo').catalogue_trace.uploaded_webp_binary_matched=true],
  ['NASA primary claimed fetched', c=>c.assets.find(a=>a.key==='apollo').catalogue_trace.primary_image_url_directly_verified=true],
  ['Franklin binary claimed matched', c=>c.assets.find(a=>a.key==='franklin').commons_preview_trace.wp_media_binary_matched=true],
  ['Franklin dimensions altered', c=>c.assets.find(a=>a.key==='franklin').commons_preview_trace.preview_dimensions=[900,1526]],
  ['NYPL embedded before rights', c=>c.assets.find(a=>a.key==='nypl').embedded=true],
  ['Release wrongly promoted', c=>c.release_decision='PASS'],
  ['NASA catalog identifier swapped', c=>c.assets.find(a=>a.key==='apollo').catalogue_trace.identifier='S67-19770']
];
for(const [name,mutate] of bad){
  const copy=JSON.parse(JSON.stringify(contract)); mutate(copy);
  assert.throws(()=>accept(copy),undefined,'Bad state must fail: '+name);
}
console.log('PASS: source catalogue scope, 3 media records, 2 unchanged archive images, 8/8 adversarial release-overclaim mutations rejected.');
console.log('HOLD: no source/upload byte comparison, currentSrc response receipts, isolated WordPress stage, anonymous Jetpack signup, WCAG, Lighthouse or commercial sale proof.');
