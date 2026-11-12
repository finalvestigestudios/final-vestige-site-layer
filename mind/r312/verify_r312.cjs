#!/usr/bin/env node
'use strict';
/** R312 read-only source validator. Native run: node mind/r312/verify_r312.cjs
 * Strictly source-level checks: NOT browser accessibility, WordPress sanitization,
 * playable-media proof, CI, merchant acceptance or a commercial event test.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = __dirname;
const file = name => fs.readFileSync(path.join(root, name), 'utf8');
const a = file('ZEN12-A-TEXT-ONLY-REVIEW.html');
const b = file('ZEN12-B-OPTIONAL-42S-FILM-REVIEW.html');
const hub = file('MIND-FOUR-STREAM-WP-HTML-REVIEW-ONLY.html');
const article = file('THE-SECOND-TARGET-DISAPPEARED-UNPUBLISHED.md');
const reg = JSON.parse(file('ATTENTIONAL-BLINK-CLAIMS-OFFERS-AND-GATES.json'));
const plan = file('ONE-OFFER-CONVERSION-AND-RELEASE-ACCEPTANCE.md');
let passed = 0, rejected = 0;
function pass(ok, message) { assert.ok(ok, message); passed++; }
function buttons(s) { return [...s.matchAll(/<button\b[^>]*>/gi)].map(m => m[0]); }
function nativeDisabled(s) {
  return buttons(s).some(tag => /(?:\s)disabled(?=\s|>|=)/i.test(tag));
}
function guardedHtml(s) {
  if (!s.includes('<html lang="en">')) return false;
  if (!s.includes('name="viewport"')) return false;
  if (!s.includes('name="robots" content="noindex,nofollow"')) return false;
  if (/<\s*(?:script|iframe|form|video|audio|input)\b/i.test(s)) return false;
  if (/<img\b[^>]*src=["']https?:/i.test(s)) return false;
  if (/@import\s|<link\b[^>]*stylesheet|\bon(?:click|load|error|mouseover)\s*=/i.test(s)) return false;
  if (/href=["'](?:https?:)?\/\/(?:www\.)?(?:inspire3\.com|affiliates\.inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s)) return false;
  if (!nativeDisabled(s)) return false;
  if (!s.includes('may earn a commission') || !s.includes('no additional cost to you')) return false;
  if (!s.includes('https://finalvestige.com/focus/')) return false;
  if (!s.includes(':focus-visible') || !s.includes('prefers-reduced-motion')) return false;
  if (/dataLayer|googletagmanager|gtag\(|fbq\(|localStorage|sessionStorage|affiliate_click\s*[:=]/i.test(s)) return false;
  const buttonEnd = s.indexOf('</button>');
  const disclosureIndex = s.indexOf('may earn a commission');
  if (buttonEnd === -1 || disclosureIndex < buttonEnd || disclosureIndex - buttonEnd > 600) return false;
  return true;
}
for (const [name,s] of [['A',a],['B',b],['hub',hub]]) {
  pass(guardedHtml(s), name + ': protection baseline');
  pass(buttons(s).length === 1, name + ': exactly one native held purchase control');
  pass(!s.includes('rel="sponsored"'), name + ': no falsely active paid link');
}
const withoutFilm = s => s.replace(/<section class="film" data-optional-film[\s\S]*?<\/section>/, '');
pass(withoutFilm(a) === withoutFilm(b), 'A/B copy identical outside optional film');
pass(!a.includes('data-optional-film'), 'A has no film');
pass(b.includes('data-optional-film') && b.includes('<svg') && b.includes('Timed original transcript'), 'B has original poster and timed transcript only');
pass(!/<video\b/i.test(b), 'B does not pretend to be playable');
pass(article.trim().split(/\s+/).length >= 1800, 'deep original investigation');
for (const term of ['Raymond','Hommel','Slagter','three months','not an attentional-blink test']) pass(article.includes(term), 'article evidence qualifier: '+term);
pass(reg.sources.length >= 15, 'source URL matrix');
pass(reg.claims.length >= 25, 'claim matrix');
pass(Object.keys(reg.authorization_gates).length === 18, 'authorization gate count');
pass(Object.values(reg.authorization_gates).every(x=>x==='HARD_HOLD'), 'authorization gates really held');
pass(reg.claims.every(x=>x.source_ids.every(id=>reg.sources.some(y=>y.id===id))), 'claim source-ID integrity');
pass(reg.creator_to_offer_fit.every(x=>x.grok_asset_id===null), 'no invented Grok media identifiers');
pass(plan.includes('NOT COMPUTABLE') && plan.includes('cleared') && plan.includes('refund'), 'commercial outcome is not clicks');
pass(!/\$\d+[.,]?\d*/.test(a+b+hub), 'no frozen selling price');
const mutations = [
  ['remove-native-disabled', s=>s.replace(' disabled aria-describedby=', ' aria-describedby=')],
  ['seller-url-injection', s=>s.replace('</button>', '</button><a href="https://zen12.com/getstarted">Buy</a>')],
  ['affiliate-pixel', s=>s.replace('</body>','<img src="https://tracking.example/pixel"></body>')],
  ['external-script', s=>s.replace('</body>', '<script src="https://example.com/a.js"></script></body>')],
  ['new-signup-form', s=>s.replace('</body>', '<form><input type="email"></form></body>')],
  ['third-party-iframe', s=>s.replace('</body>','<iframe src="https://example.com"></iframe></body>')],
  ['hidden-autoplay-video', s=>s.replace('</body>', '<video autoplay></video></body>')],
  ['remove-prospective-disclosure', s=>s.replace('may earn a commission', 'may see the result')],
  ['remove-free-option', s=>s.replaceAll('https://finalvestige.com/focus/', '/unknown/')],
  ['turn-on-indexing', s=>s.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"')],
  ['strip-language', s=>s.replace('<html lang="en">', '<html>')],
  ['strip-keyboard-focus', s=>s.replaceAll(':focus-visible', ':hover')],
  ['strip-reduced-motion', s=>s.replaceAll('prefers-reduced-motion','prefers-any-motion')],
  ['add-inline-event', s=>s.replace('</body>','<div onload="steal()">x</div></body>')],
  ['paid-event-spoof', s=>s.replace('</body>','<div affiliate_click="paid_order">x</div></body>')],
  ['CSS-import', s=>s.replace('</style>','@import url(https://example.com/x.css);</style>')],
  ['extra-email-input', s=>s.replace('</body>','<input type="email"></body>')]
];
for (const [name, mutate] of mutations) {
  for (const original of [a,b,hub]) {
    const bad = mutate(original);
    if (bad === original) continue;
    assert.equal(guardedHtml(bad), false, 'unsafe mutation passed guard: '+name);
    rejected++;
  }
}
const fakeClaims = JSON.parse(JSON.stringify(reg));
fakeClaims.claims[0].source_ids = ['S99-NOT-A-REAL-SOURCE'];
pass(!fakeClaims.claims.every(x=>x.source_ids.every(id=>fakeClaims.sources.some(y=>y.id===id))), 'mutated orphan source rejected');
const fakeGates=JSON.parse(JSON.stringify(reg));
fakeGates.authorization_gates.publisher_account_approval = 'APPROVED';
pass(!Object.values(fakeGates.authorization_gates).every(x=>x==='HARD_HOLD'), 'fake affiliate approval rejected');
const fakeKpi = plan.replace('NOT COMPUTABLE', 'PROVEN NET REVENUE');
pass(!fakeKpi.includes('NOT COMPUTABLE'), 'missing-data KPI mutation identifiable');
console.log('R312 native source checks PASS:',passed,'baseline/structural assertions,',rejected,'deliberately unsafe HTML mutations rejected.');
console.log('UNTESTED: real browser/axe/WCAG, WordPress CSS/CSP, actual video, affiliate approval, payments, revenue.');
