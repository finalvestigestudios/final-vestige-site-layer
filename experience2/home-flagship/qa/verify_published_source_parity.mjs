#!/usr/bin/env node
/**
 * Read-only seven-chapter parity receipt verifier.
 * Confirms SOURCE observations and known release HOLD; never calls WordPress.
 * Run from repository root: node experience2/home-flagship/qa/verify_published_source_parity.mjs
 * This does NOT assert that the currently served production DOM equals editor source.
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const qaDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(qaDir, '../../..');
const receipt = JSON.parse(fs.readFileSync(
  path.join(qaDir, 'FV_EX2_PUBLISHED_SOURCE_PARITY_RECEIPT_20261105.json'), 'utf8'));
const candidate = fs.readFileSync(path.join(root, receipt.candidate_file), 'utf8');
const chapterIds = [
  'fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
  'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title',
];
const rx = /<img\b[^>]*>/gi;
function evaluate(html) {
  const actions = (html.match(/class="fv-hf__opening-actions"[^>]*>([\s\S]*?)<\/div>/) || [,''])[1];
  const tags = [...html.matchAll(rx)].map(m => m[0]);
  const focusable = chapterIds.filter(id => {
    const at = html.indexOf('id="' + id + '"');
    if (at < 0) return false;
    const start = html.lastIndexOf('<', at);
    const end = html.indexOf('>', at);
    return start >= 0 && end >= 0 && html.slice(start, end + 1).includes('tabindex="-1"');
  }).length;
  return {
    anchors_present: chapterIds.filter(id => html.includes('id="' + id + '"')).length,
    chapter_destinations_programmatically_focusable: focusable,
    masthead_focus_cta: /class="fv-hf__mast-cta"[^>]*href="https:\/\/finalvestige.com\/focus\/"/.test(html),
    hero_focus_cta: /href="https:\/\/finalvestige.com\/focus\/"/.test(actions),
    hero_blog_cta: /href="https:\/\/finalvestige.com\/blog\/"/.test(actions),
    image_elements: tags.length,
    nypl_map_image: tags.some(tag => /nypl-5003296/i.test(tag)),
    apollo_image: tags.some(tag => /s67-19766\.webp/.test(tag)),
    franklin_image: tags.some(tag => /Franklinexpeditionnote\.jpg/i.test(tag)),
    hidden_margins_item_count: (html.match(/<span class="fv-margin-strip__item"/g) || []).length,
    jetpack_subscription_block: html.includes('wp:jetpack/subscriptions')
  };
}
const own = evaluate(candidate);
assert.deepEqual(own, receipt.candidate,
  'Candidate source diverged from saved receipt; re-inspect and regenerate instead of declaring PASS');
assert.equal(receipt.wp_site_id, 256784396);
assert.equal(receipt.wp_page_id, 6);
assert.equal(receipt.wp_page_status, 'publish');
assert.equal(receipt.published.anchors_present, 7);
assert.equal(receipt.published.hidden_margins_item_count, 72);
assert.equal(receipt.published.nypl_map_image, true);
assert.equal(receipt.candidate.nypl_map_image, false);
assert.equal(receipt.published.hero_focus_cta, false);
assert.equal(receipt.candidate.hero_focus_cta, true);
assert.equal(receipt.published.chapter_destinations_programmatically_focusable, 0);
assert.equal(receipt.candidate.chapter_destinations_programmatically_focusable, 7);
assert.equal(receipt.focus_page_static_subscribe_anchor, true);
assert.equal(receipt.focus_page_javascript_free_jetpack_block, true);
assert.equal(receipt.assessment.release, 'HOLD');
assert.equal(receipt.focus_page_fragment_links, 5);
console.log('PASS: exact checked-out candidate agrees with measured source receipt.');
console.log('HOLD: published-page evidence is an editor-source snapshot, not a browser/rights/revenue qualification.');
