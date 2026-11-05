// Mind R141 offline regression tests. No network, tracking, merchant navigation or CMS writes.
// Run: node mind/r141/test-r141.cjs from repository root.
// Native Node + source checkout required. Structural checks are NOT a browser, purchase or efficacy test.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..', '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const file = name => read('mind/r141/' + name);
const article = file('hypnosis-memory-confidence-investigation.md');
const guide = file('zen12-buyer-decision-guide.md');
const memo = file('merchant-and-revenue-acceptance.md');
const ledger = JSON.parse(file('verified-claim-and-gate-ledger.json'));
const A = read('mind/r139/zen12-variant-a.html');
const B = read('mind/r139/zen12-variant-b.html');
const hub = read('mind/r139/mind-hub-wp-draft.html');
let tests = 0;
const check = (condition, message) => { assert.ok(condition, message); tests++; };
const words = s => s.trim().split(/\s+/).length;
const sameBuyerCopy = (a, b) => {
  const core = s => s.split('<section id="buyer-information"')[1]?.split('</section>')[0];
  return !!core(a) && core(a) === core(b);
};
const disclosureBeforeButton = html => {
  const p = html.indexOf('class="disclose"');
  const button = html.indexOf('<button', p);
  const end = html.indexOf('may earn a commission', p);
  return p >= 0 && end > p && button > end && button - end < 650;
};
const noActiveMerchant = html => {
  const buttons = [...html.matchAll(/<button\b([^>]*)>/gi)];
  return buttons.length === 1 && /\bdisabled\b/.test(buttons[0][1]) &&
    /aria-disabled="true"/.test(buttons[0][1]) &&
    !/<script\b|<form\b|\sautoplay(?=[\s=>])|dataLayer|gtag\s*\(/i.test(html);
};
check(ledger.schema === 'fv.mind.r141.offer_evidence.v1', 'expected schema');
check(ledger.environment === 'UNPUBLISHED_DRAFT', 'must remain draft');
check(Object.keys(ledger.sources).length >= 15, 'source count');
check(ledger.claims.length >= 24, 'claim count');
check(ledger.release_gates.length >= 14, 'gate count');
check(ledger.claims.every(c => c.id && c.claim && c.decision && Array.isArray(c.source_keys)), 'claim shape');
check(ledger.claims.every(c => c.source_keys.every(k => ledger.sources[k])), 'all references resolve');
check(Object.values(ledger.sources).every(s => s.startsWith('https://')), 'all sources HTTPS');
check(ledger.release_gates.every(g => g.open === false), 'all gates must stay closed');
check(ledger.release_gates.every(g => g.owner && g.proof_required), 'gate owners and evidence');
check(ledger.release_gates.some(g => g.gate === 'named_inspire3_acceptance'), 'named approval gate');
check(ledger.release_gates.some(g => g.gate === 'affiliate_data_handling'), 'privacy gate');
check(ledger.release_gates.some(g => g.gate === 'merchant_sale_and_fee_data'), 'paid source gate');
check(ledger.release_gates.some(g => g.gate === 'video_playable_accessible'), 'playable video is not asserted');
check(ledger.claims.some(c => c.id === 'ZEN12-04' && c.decision === 'UNSUBSTANTIATED'), 'short-equivalence not validated');
check(ledger.claims.some(c => c.id === 'INSPIRE-02' && c.decision === 'NOT_VERIFIED'), 'approval unknown');
check(ledger.creator_topic_routes.length === 3, '3 creator routes');
check(ledger.creator_topic_routes.every(r => r.grok_asset_id === null && r.grok_public_permalink === null), 'no invented media IDs');
check(ledger.creator_topic_routes[2].destination === null, 'unpublished article must not have live URL');
check(ledger.measurement.facts.realized_net_revenue === null, 'missing revenue must be null');
check(ledger.measurement.facts.qualified_human_sessions === null, 'missing denominator must be null');
check(ledger.measurement.facts.kpi_net_per_1000_qualified_humans === null, 'uncomputable KPI not zero');
check(ledger.measurement.stages.includes('merchant_confirmed_paid_order'), 'paid event stage');
check(ledger.measurement.rule.includes('asset_id'), 'campaign asset mapping');
check(ledger.measurement.privacy.includes('No email'), 'no buyer PII');
check(ledger.measurement.experiments.variant_B.includes('not playable'), 'video storyboard status');
check(words(article) >= 1400, 'research depth');
check(words(guide) >= 1150, 'buyer depth');
check(words(memo) >= 1000, 'commercial-plan depth');
for (const s of ['Krass', 'Brewin', 'Muschalla', 'Wagstaff', 'Johns Hopkins', 'Puységur']) check(article.includes(s), 'investigation reference: '+s);
for (const s of ['https://zen12.com/hnp', 'twelve levels', '48 MP3', 'NOT', 'one-year', 'seller', 'commission']) check(guide.toLowerCase().includes(s.toLowerCase()), 'buyer claim: '+s);
check(guide.includes('not an active hyperlink'), 'no authorized CTA');
check(guide.includes('at no additional cost'), 'nearby disclosure copy');
check(!/<script\b|<form\b/i.test(A+B+hub), 'inherited drafts no scripts/forms');
check(noActiveMerchant(A), 'A: dormant merchant');
check(noActiveMerchant(B), 'B: dormant merchant');
check(disclosureBeforeButton(A), 'A disclosure adjacent');
check(disclosureBeforeButton(B), 'B disclosure adjacent');
check(sameBuyerCopy(A,B), 'A/B buyer copy identical');
check(B.includes('storyboard only') && B.includes('00:33–00:40') && B.includes('<details>'), 'B original transcript available without JS');
check(!/<video\b|<iframe\b/i.test(A+B), 'no hidden hosted video or playback');
check(/prefers-reduced-motion/.test(A+B), 'reduced motion CSS');
check(A.includes('https://finalvestige.com/focus/') && B.includes('https://finalvestige.com/focus/'), 'single Focus pathway');
check(hub.includes('NOT live') && hub.includes('https://finalvestige.com/focus/'), 'hub is draft and preserves Focus');
check(!/\?[^"'\s>]*(?:aff_id|affiliate_id|clickid|subid|utm_)/i.test(A+B), 'no guessed affiliate/UTM link');
// Mutation controls must fail when critical restrictions are broken.
check(!noActiveMerchant(A.replace('<button type="button" disabled', '<button type="button"')), 'mutation: enabled CTA blocked');
check(!noActiveMerchant(A.replace('</style>', '</style><script>alert(1)</script>')), 'mutation: script blocked');
check(!disclosureBeforeButton(A.replace('may earn a commission', 'receives nothing')), 'mutation: disclosure removal blocked');
check(!sameBuyerCopy(A,B.replace('Buying access to multiple audio styles', 'Guaranteed miracle outcomes from audio')), 'mutation: divergent A/B buyer copy blocked');
check(![...ledger.release_gates, {open:true}].every(g => g.open === false), 'mutation: open gate blocked');
process.stdout.write('mind/r141: ' + tests + '/' + tests + ' structural assertions passed; no browser/merchant validation performed\n');
