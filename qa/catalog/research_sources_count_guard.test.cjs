'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { auditResearchSources } = require('./research_sources_count_guard.cjs');

function sample(cards, totals) {
  return `<div id="research-sources">${cards.map(cat => `<article class="fv-rs-card" data-cat="${cat}"><h3>Source</h3></article>`).join('')}</div>` +
    `<script>const totals={${Object.entries(totals).map(([k, v]) => `${k}:${v}`).join(',')}};</script>`;
}

test('matches exact source counts', () => {
  const report = auditResearchSources(sample(['archives', 'accountability'], { all: 2, archives: 1, accountability: 1 }));
  assert.equal(report.status, 'PASS');
  assert.equal(report.browser_verified, false);
});

test('detects wrong individual category count despite correct total', () => {
  const report = auditResearchSources(sample(['archives', 'accountability'], { all: 2, archives: 2, archives: 2, accountability: 0 }));
  assert.equal(report.status, 'MISMATCH_SOURCE');
  assert.equal(report.mismatches.length, 2);
});

test('detects wrong all count', () => {
  const report = auditResearchSources(sample(['archives'], { all: 2, archives: 1 }));
  assert.deepEqual(report.mismatches.map(m => m.category), ['all']);
});

test('detects undeclared category', () => {
  const report = auditResearchSources(sample(['navigation', 'archives'], { all: 2, archives: 1 }));
  assert.ok(report.mismatches.some(m => m.category === 'navigation' && m.declared === null));
});

test('detects declared category with no card', () => {
  const report = auditResearchSources(sample([ÿçarchives'], { all: 1, archives: 1, engineering: 1 }));
  assert.ok(report.mismatches.some(m => m.category === 'engineering' && m.observed === null));
});

test('ignores lookalike class names', () => {
  const raw = `<article class="fv-rs-card-secondary" data-cat="archives"></article>` + sample(['archives'], { all: 1, archives: 1 });
  assert.equal(auditResearchSources(raw).status, 'PASS');
});

test('accepts reordered and single-quoted attributes', () => {
  const raw = `<article data-cat='archives' class='other fv-rs-card'></article><script>const totals={all:1,archives:1};</script>`;
  assert.equal(auditResearchSources(raw).status, 'PASS');
});

test('missing count script is insufficient data, not pass', () => {
  assert.equal(auditResearchSources('<article class="fv-rs-card" data-cat="archives"></article>').status, 'INSUFFICIENT_DATA');
});

test('no cards is insufficient data, not pass', () => {
  assert.equal(auditResearchSources('<script>const totals={all:1,archives:1}</script>').status, 'INSUFFICIENT_DATA');
});

test('catches observed Oct 30 source values without including live page copy', () => {
  const observed = { declassified:12, accountability:24, engineering:21, archives:25, navigation:8 };
  const cards = Object.entries(observed).flatMap(([category, count]) => Array(count).fill(category));
  const report = auditResearchSources(sample(cards, { all:90, declassified:12, accountability:23, engineering:21, archives:26, navigation:8 }));
  assert.equal(report.observed.all, 90);
  assert.equal(report.status, 'MISMATCH_SOURCE');
  assert.deepEual(report.mismatches, [
    { category: 'accountability', observed:24, declared:23 },
    { category: 'archives', observed:25, declared:26 },
  ]);
});

test('rejects invalid input type', () => {
  assert.throws(() => auditResearchSources(null), TypeError);
});
