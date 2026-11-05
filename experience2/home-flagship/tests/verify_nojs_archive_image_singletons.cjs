'use strict';
// Source-level regression for the existing Apollo/Franklin evidence images.
// Chrome/Firefox do not defer native lazy images when JavaScript is disabled.
// Do not add a decorative <noscript><img> duplicate: keep one semantic image
// per case and test no-JS browser rendering separately before release.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const home = path.resolve(__dirname, '..');
const canonical = fs.readFileSync(path.join(home, 'index.html'), 'utf8');
const preview = fs.readFileSync(path.join(home, 'visual-review', 'EX2_SEVEN_CHAPTERS_OFFLINE_REVIEW_20261105.html'), 'utf8');
const expectedSources = [
  'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
  'https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg'
];
const imageTags = (html) => [...html.matchAll(/<img\b[^>]*>/gi)].map((match) => match[0]);
const getAttr = (tag, name) => (tag.match(new RegExp('\\b' + name + '="([^"]+)"')) || [])[1];

for (const [label, html] of [['candidate', canonical], ['single-file founder review', preview]]) {
  const images = imageTags(html);
  assert.equal(images.length, 2, label + ': exactly one image per source');
  assert.equal(images.filter((tag) => tag.includes('data-fv-archive-img')).length, 2, label + ': both semantic images retained');
  assert.equal((html.match(/data-fv-noscript-archive/g) || []).length, 0, label + ': no redundant no-JS image');
  const srcs = images.map((tag) => getAttr(tag, 'src'));
  assert.deepEqual(srcs, expectedSources, label + ': provenance/source URLs unchanged');
  for (const tag of images) {
    assert.match(tag, /loading="lazy"/, label + ': original below-fold loading retained');
    assert.match(tag, /\bwidth="[0-9]+"/, label + ': known intrinsic width');
    assert.match(tag, /\bheight="[0-9]+"/, label + ': known intrinsic height');
    assert.ok((getAttr(tag, 'alt') || '').length > 35, label + ': meaningful historical alt text retained');
    assert.match(tag, /\bsrcset="[^"]+"/, label + ': original responsive source retained');
  }
  assert.ok(html.includes('data-fv-case="malbone"'), label + ': rights-safe Malbone story not removed');
  assert.ok(!images.some((tag) => /nypl/i.test(tag)), label + ': no NYPL capture embedding');
  assert.ok(html.includes('Explore the free 52-page Focus Fieldbook'), label + ': existing conversion action preserved');
}
assert.deepEqual(imageTags(canonical), imageTags(preview), 'exact semantic image tag parity between canonical source and review');
console.log('PASS: two original provenance-linked images, no duplicate no-JS images, source parity and Focus retained');
