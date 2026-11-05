'use strict';
/**
 * Source-only archival custody gate. Intentionally does NOT certify image rights,
 * real HTTP image transfers, WordPress rendering, or a release decision.
 * Run: node experience2/home-flagship/review/verify_archive_media_contract.cjs
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const ROOT = path.resolve(__dirname, '..');
const contract = JSON.parse(fs.readFileSync(path.join(__dirname,'archive-media-contract-20261105.json'),'utf8'));
const html = fs.readFileSync(path.join(ROOT,'index.html'),'utf8');
const media = contract.assets;
assert.equal(contract.release_decision, 'HOLD');
assert.equal(media.length, 3);
assert.equal(media.filter(x => x.embedded).length, 2);
assert.equal(media.filter(x => !x.embedded).length, 1);
for (const item of media) {
  assert.ok(item.wp_media_id > 0 && Number.isInteger(item.wp_media_declared_bytes));
  assert.ok(item.wp_media_declared_bytes > 0);
  assert.ok(item.source_reference.startsWith('https://'));
  assert.equal(item.browser_response_status, null, 'Do not invent an HTTP response');
  assert.equal(item.network_body_sha256, null, 'Do not invent a network hash');
}
function validate(text) {
  const images = [...text.matchAll(/<img\b[^>]*>/gi)].map(m => m[0]);
  assert.equal(images.length, 2, 'Exactly two archival images in canonical candidate');
  for (const item of media.filter(x => x.embedded)) {
    const found = images.filter(tag => tag.includes('src="' + item.src + '"'));
    assert.equal(found.length, 1, 'Expected single intact image: ' + item.key);
    const image = found[0];
    assert.match(image, /\balt="[^"]{20,}"/, 'Image alt text must be descriptive');
    assert.match(image, /\bwidth="[0-9]+"/);
    assert.match(image, /\bheight="[0-9]+"/);
    assert.match(image, /\bsrcset="/, 'Responsive source candidates must remain explicit');
    assert.match(image, /\bloading="lazy"/);
  }
  for (const item of media.filter(x => !x.embedded)) {
    assert.ok(!images.some(tag => tag.includes(item.src)), 'No unapproved NYPL image embed');
  }
  assert.ok(text.includes('https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg'));
  assert.ok(text.includes('https://www.rmg.co.uk/collections/objects/rmgc-object-504898'));
  assert.ok(text.includes('href="https://finalvestige.com/focus/"'), 'Existing Focus link must remain');
  return images;
}
const images = validate(html);
assert.ok(images.some(tag => tag.includes('i0.wp.com')), 'Document Jetpack CDN dependency rather than claim first-party-only');
const damaged = [
  ['removed-archive-image', html.replace(images[0], '')],
  ['wrong-image-src', html.replace(media[0].src, 'https://example.invalid/other.webp')],
  ['blank-alt', html.replace(/alt="Apollo 1 astronauts[^"]+"/, 'alt=""')],
  ['unexpected-nypl-image', html.replace(images[1], images[1] + '<img src="' + media[2].src + '" alt="unreviewed">')]
];
for (const [name, mutation] of damaged) {
  assert.throws(() => validate(mutation), undefined, 'Mutation must fail: '+name);
}
console.log('PASS: 2 expected images, 1 explicitly excluded image, source links, Focus preserved; 4/4 negative controls rejected.');
console.log('PENDING: real currentSrc/status/response body/hash, exact NASA photo ID, local Franklin derivative, NYPL rights. RELEASE HOLD.');
