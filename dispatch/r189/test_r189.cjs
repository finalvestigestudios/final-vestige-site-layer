/** R189 exact-source review guards. Run with: node --test dispatch/r189/test_r189.cjs
 * Offline synthetic policy tests only. They do NOT prove Jetpack email rendering,
 * legal compliance, partner authorization, email consent, or settled revenue.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { test } = require('node:test');
const read = (name) => fs.readFileSync(path.join(__dirname, name), 'utf8');
const md = read('05_OPTIONAL_FARADAY_TO_TOTAL_FOCUS.md');
const plain = read('05_OPTIONAL_FARADAY_TO_TOTAL_FOCUS.txt');
const html = read('05_OPTIONAL_FARADAY_TO_TOTAL_FOCUS_REVIEW.html');
const gate = JSON.parse(read('CLAIM_AND_PARTNER_GATE.json'));
test('subject, preheader, and product metadata across three previews', () => {
  for (const s of [md,plain,html]) {
    assert.ok(s.includes("The table moved. The hands said they hadn't."));
    assert.ok(s.includes("Faraday's 1853 test shows how to question a convincing experience."));
    assert.ok(s.includes('33-minute, 47-MB'));
    assert.ok(s.includes('Final Vestige may earn a commission'));
  }
});
test('legal hard stops in all review assets', () => {
  for (const s of [md,plain,html]) {
    assert.ok(s.includes('[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]'));
    assert.ok(s.includes('[[GENUINE_JETPACK_UNSUBSCRIBE_MUST_BE_VERIFIED]]'));
  }
});
test('no invented efficacy proof or dynamic price', () => {
  assert.equal(gate.claims.find(x => x.id === 'total_focus_effectiveness').include_as_proven, false);
  assert.equal(gate.claims.find(x => x.id === 'total_focus_price').include_in_email, false);
  assert.equal(gate.claims.find(x => x.id === 'total_focus_refund').verified_transaction_fulfillment, false);
  assert.doesNotMatch(md, /(?:guaranteed success|clinically proven to reprogram|buy now before midnight)/i);
  assert.doesNotMatch(md, /\$[0-9]+(?:\.[0-9]+)?/);
});
test('merchant release cannot pass without permissions', () => {
  for (const val of Object.values(gate.permissions)) assert.equal(val,false);
  for (const val of Object.values(gate.release)) assert.equal(val,false);
  assert.equal(gate.send_state,'HOLD_UNSENT');
  assert.equal(gate.merchant_state,'HOLD_MERCHANT');
  assert.equal(gate.cta.earning_link,null);
  assert.equal(gate.cta.verified_live_guide_url,null);
});
test('tracking links blocked but vendor citations allowed', () => {
  for (const s of [md,plain,html]) {
    assert.doesNotMatch(s, /awin1\.com|hoplink|[?&]utm_medium=affiliate|[?&](?:aff|affiliate|hop)=/i);
  }
  assert.match(md,/https:\/\/hypnosislive\.com\/mental-skills\/total-focus/);
  assert.match(md,/https:\/\/pmc\.ncbi\.nlm\.nih\.gov\/articles\/PMC10444352/);
});
test('review HTML is basic email-safe markup with no tracking', () => {
  assert.match(html, /<html lang="en">/);
  assert.match(html, /role="presentation"/);
  assert.match(html, /<h1/);
  assert.match(html, /@media\(max-width:640px\)/);
  assert.doesNotMatch(html, /<script|<form|<iframe|<img/i);
});
test('canonical conversion and refund boundary documented', () => {
  const a = read('SUBSCRIBER_TO_CUSTOMER_PROOF.md');
  assert.match(a,/authoritative Jetpack subscription/);
  assert.match(a,/NOT IMPLEMENTED/);
  assert.match(a,/NOT COMPUTABLE/);
  assert.match(a,/refunds/);
  assert.match(a,/Grok/);
});
test('native preview does not equal receipt or opt-out verification', () => {
  const r = read('NATIVE_EMAIL_PREVIEW_AND_LEGAL_RUNBOOK.md');
  assert.match(r,/not a legal signoff/);
  assert.match(r,/Do not email a subscriber/i);
  assert.match(r,/NO edits or saves/i);
  assert.match(r,/HOLD_UNSENT/);
});
