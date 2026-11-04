'use strict';
// Run on a full checkout: node --test mind/r119/test-r119.cjs
// Fail closed: checks draft material and already-existing R114 canonical candidates, never live CMS.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..', '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');
const article = read('mind/r119/the-gorilla-you-were-looking-through.md');
const memo = read('mind/r119/eligibility-to-paid-revenue.md');
const matrix = JSON.parse(read('mind/r119/merchant-claims-and-revenue-gates.json'));
const textA = read('mind/r114/zen12-text-A.html');
const videoB = read('mind/r114/zen12-film-B.html');
const plain = (v) => JSON.stringify(v);
test('investigation has meaningful original depth', () => assert.ok(article.trim().split(/\s+/).length > 2200));
test('research includes original source trail', () => assert.ok(article.includes('## Research source trail')));
for (const id of ['S1','S2','S3','S4','S5','S6']) {
  test('citation '+id+' appears in article', () => assert.ok(article.includes('['+id+']')));
}
test('inattentional distinct from change blindness', () => assert.ok(article.includes('**Change blindness**')));
test('study distinction with attentional blink', () => assert.ok(article.includes('attentional blink')));
test('2023 counterbalance and N reported', () => assert.ok(article.includes('4,493')));
test('observational exercise is not validated', () => assert.ok(article.includes('not a validated experiment')));
test('no fabricated original video imagery', () => assert.ok(article.includes('copyrighted basketball video')));
test('editorial article contains no active affiliate hyperlink', () => assert.ok(!/\]\(https?:\/\/[^)]*(?:awin1|clickbank|hop\.clickbank|affiliate\?)/i.test(article)));
test('declared matrix rejects premature commercial activation', () => assert.equal(matrix.status, 'UNPUBLISHED_HARD_HOLD'));
test('minimum independent evidence breadth', () => assert.ok(matrix.sources.length >= 12));
test('claims include clear support classifications', () => assert.ok(matrix.claims.length >= 18));
test('all commercial and release gates closed', () => assert.ok(matrix.gates.length >= 12 && matrix.gates.every(g => g.open === false)));
test('merchant source exact Zen12 sales page', () => assert.equal(matrix.merchant_product_url_public_nonaffiliate_reference, 'https://zen12.com/hnp'));
test('seller page price is dated, not final checkout', () => assert.ok(matrix.buyer_offer_observation.price_basis.includes('NOT confirmed final checkout')));
test('seller hour-equivalence excluded from supported efficacy', () => assert.ok(matrix.claims.some(x => x.id === 'C09' && x.status.includes('UNSUPPORTED'))));
test('merchant approval status explicitly unverified', () => assert.ok(matrix.claims.some(x => x.id === 'C14' && x.status.includes('UNVERIFIED'))));
test('buyers data exposure is flagged', () => assert.ok(matrix.claims.some(x => x.id === 'C13' && x.status === 'SELLER_POLICY_VERIFIED')));
test('creator assets stay unknown until Grok verifies', () => assert.ok(matrix.creator_to_offer.length === 3 && matrix.creator_to_offer.every(x => x.asset_id === null && x.verified_asset_url === null)));
test('unpublished gorilla has no invented article URL', () => assert.ok(matrix.creator_to_offer.some(x => x.topic === 'invisible_gorilla' && x.article_url === null)));
test('no completed order or commission invented', () => assert.ok(matrix.measurement.verified_affiliate_commissions === null && matrix.measurement.merchant_confirmed_orders === null));
test('revenue per qualified session stays uncomputable', () => assert.equal(matrix.measurement.net_revenue_per_1000_qualified_sessions, null));
test('no buyer identifiers allowed in measurement plan', () => assert.ok(matrix.measurement.explicit_no_pii_fields.includes('email') && matrix.measurement.explicit_no_pii_fields.includes('ip')));
test('existing Focus is accurately free', () => assert.ok(memo.includes('52-page Seven Day Focus Fieldbook') && memo.includes('not a paid order')));
test('one canonical R114 guide rather than competing page', () => assert.ok(memo.includes('sole proposed canonical commercial experience')));
test('7/30-day cohort with accurate net-revenue denominator', () => assert.ok(memo.includes('7-/30-day cohorts') && memo.includes('qualified human sessions')));
test('actual Grok IDs require TASK-008 verification', () => assert.ok(memo.includes('TASK-008') && memo.includes('asset_id')));
test('no commercial sender action authorized', () => assert.ok(memo.includes('No email, live post, merchant enrollment')));
for (const [name,html] of [['text A',textA],['video B',videoB]]) {
 test(name+' preserves disabled merchant action', () => assert.ok(/<button[^>]*disabled/.test(html)));
 test(name+' disclosure precedes purchase button', () => assert.ok(html.indexOf('class="disclosure"') < html.indexOf('<button type="button" disabled')));
 test(name+' no active affiliate merchant hyperlink', () => assert.ok(!/<a[^>]*href=["'][^"']*(?:zen12\.com|awin1\.com|clickbank)[^"']*["']/i.test(html)));
 test(name+' no third party tracking scripts', () => assert.ok(!/<script/i.test(html)));
 test(name+' no duplicate email/signup form', () => assert.ok(!/<form\b/i.test(html)));
 test(name+' no autoplay', () => assert.ok(!/\sautoplay\b/i.test(html)));
}
test('B retains optional transcript presentation', () => assert.ok(videoB.includes('transcript') || videoB.includes('Transcript')));
test('FTC claims guidance explicitly linked', () => assert.ok(memo.includes('ftcs-endorsement-guides') && memo.includes('health-products-compliance')));
test('staging responsive checks include 360, 390, 768, 1440', () => assert.ok(['360','390','768','1440'].every(n => memo.includes(n))));
