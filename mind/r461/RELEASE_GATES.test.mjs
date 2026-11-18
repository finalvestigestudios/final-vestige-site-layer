// Execute locally: node --test mind/r461/RELEASE_GATES.test.mjs
// Standard Node.js built-ins only; no network, analytics, WordPress or merchant actions.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = name => readFileSync(new URL(name, import.meta.url), 'utf8');
const A = source('ZEN12_A_TEXT_ONLY.html');
const B = source('ZEN12_B_OPTIONAL_42S.html');
const hub = source('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');
const article = source('THE_GORILLA_IN_THE_SCAN.md');
const vtt = source('ZEN12_R461_CAPTIONS.vtt');
const poster = source('ZEN12_R461_POSTER.svg');
const matrix = JSON.parse(source('SOURCE_CLAIM_PARTNER_MATRIX.json'));
function core(s) {
  const begin = s.indexOf('<article class="guide-core"');
  const end = s.indexOf('</article>', begin);
  assert.ok(begin >= 0 && end > begin, 'core article region missing');
  return s.slice(begin, end + '</article>'.length);
}
function disabled(s) {
  return /<button[^>]*\bdisabled\b[^>]*>Review approved Zen12 offer — not available<\/button>/.test(s);
}
test('A and B contain the identical substantive guide', () => assert.equal(core(A), core(B)));
test('purchase CTA is natively disabled and not anchor cloaked', () => {
  assert.ok(disabled(A));
  assert.ok(disabled(B));
});
test('FTC earning disclosure precedes each inactive CTA in the same offer region', () => {
  for (const s of [A, B]) {
    const section = s.match(/<aside class="offer"[\s\S]*?<\/aside>/)?.[0];
    assert.ok(section);
    const d = section.indexOf('Affiliate disclosure:');
    const b = section.indexOf('<button');
    assert.ok(d >= 0 && b > d && b - d < 750);
  }
});
test('no affiliate merchant anchor or merchant tracking link in source pages', () => {
  for (const s of [A, B, hub]) {
    assert.doesNotMatch(s, /<a\s[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i);
  }
});
test('no extra signup form, tracker or executable scripts', () => {
  for (const s of [A, B, hub]) {
    assert.doesNotMatch(s, /<form\b|<script\b|gtag\s*\(|fbq\s*\(|googletagmanager|<iframe\b/i);
  }
});
test('all prototypes are unpublished and search-disabled', () => {
  for (const s of [A, B, hub]) {
    assert.match(s, /name="robots" content="noindex,nofollow"/);
  }
});
test('no guaranteed outcomes or invented numerical checkout prices', () => {
  for (const s of [A, B]) {
    assert.doesNotMatch(s, /\$\s*[0-9]+(?:\.[0-9]{2})?|guaranteed wealth|i (?:used|purchased|personally tested) zen12/i);
  }
});
test('video variant is optional source concept, not fake playable player', () => {
  assert.match(B, /42-second visual explanation/);
  assert.match(B, /not a playable encode/);
  assert.doesNotMatch(B, /<video\b|autoplay="|<iframe\b/i);
  assert.doesNotMatch(A, /class="film" id="film"/);
});
test('six nonoverlapping WebVTT cues span exactly forty-two seconds', () => {
  assert.match(vtt, /^WEBVTT/m);
  const cues = [...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
  assert.equal(cues.length, 6);
  const toMs = t => { const [h,m,s] = t.split(':'); return ((Number(h)*60+Number(m))*60+Number(s))*1000; };
  assert.equal(toMs(cues[0][1]), 0);
  assert.equal(toMs(cues.at(-1)[2]), 42000);
  for (let i = 0; i < cues.length; i++) {
    assert.ok(toMs(cues[i][2]) > toMs(cues[i][1]));
    if (i) assert.equal(toMs(cues[i-1][2]), toMs(cues[i][1]));
  }
});
test('poster is original, accessible and has no linked remote asset', () => {
  assert.match(poster, /<svg\b/);
  assert.match(poster, /<title\b/);
  assert.match(poster, /<desc\b/);
  assert.doesNotMatch(poster, /<(?:image|script|foreignObject)\b|xlink:href\s*=/i);
});
test('no claims turn original research into retail efficacy guarantee', () => {
  assert.match(article, /not the effectiveness of those recordings/);
  assert.match(article, /2023 systematic review/);
  assert.match(article, /Puységur/);
});
test('source and seller claim categories are explicitly separate', () => {
  const kinds = new Set(matrix.claims.map(c => c.class));
  assert.ok(kinds.has('INDEPENDENT_RESEARCH'));
  assert.ok(kinds.has('EFFICACY_SELLER_UNSUBSTANTIATED'));
  assert.ok(kinds.has('COMPLIANCE'));
});
test('unsubstantiated seller efficacy claims are never endorsed', () => {
  for (const claim of matrix.claims.filter(c => c.class === 'EFFICACY_SELLER_UNSUBSTANTIATED')) {
    assert.equal(claim.decision, 'DO_NOT_ENDORSE');
  }
});
test('every one of the merchant-release gates is still closed', () => {
  assert.equal(matrix.commercialStatus, 'HARD_HOLD');
  assert.ok(matrix.releaseGates.length >= 25);
  assert.ok(matrix.releaseGates.every(g => g.status === 'HOLD'));
});
test('no fabricated paid outcome or known denominator', () => {
  assert.equal(matrix.commerce.settledSales, null);
  assert.equal(matrix.commerce.qualifiedHumanSessions, null);
  assert.equal(matrix.commerce.netRevenuePer1000, null);
  assert.equal(matrix.commerce.url, null);
  assert.equal(matrix.measurement.implementation, 'NOT_DEPLOYED');
});
test('all internal hub links use actual verified live paths', () => {
  for (const path of ['2026/11/02/change-blindness/','2026/11/02/mesmerism/','free-resources/puysegurs-animal-magnetism-files/','finalvestige.com/focus/']) {
    assert.ok(hub.includes(path));
  }
  assert.match(hub, /UNPUBLISHED/);
});
test('prototypes retain accessible no-JS responsive layout', () => {
  for (const s of [A, B, hub]) {
    assert.match(s, /<html lang="en">/);
    assert.match(s, /name="viewport"/);
    assert.match(s, /:focus-visible/);
    assert.match(s, /@media\(max-width:/);
  }
});
