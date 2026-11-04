import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

/**
 * Fail-closed editorial/source custody for the EXISTING unpublished homepage.
 * Deliberately does not make remote requests, perform CMS writes or certify
 * copyright, image transfer bytes, WordPress parity or WCAG.
 */
const path = fileURLToPath(new URL('../../index.html', import.meta.url));
const html = readFileSync(path, 'utf8');
const NASA = 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp';
const FRANKLIN = 'https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg';
function images(document) {
  return Array.from(document.matchAll(/<img\b[^>]*>/gi), match => {
    const tag = match[0];
    const attr = name => tag.match(new RegExp('(?:\\s)' + name + '="([^"]*)"', 'i'))?.[1];
    return { src: attr('src') ?? '', alt: attr('alt'), role: attr('role') ?? '', hidden: attr('aria-hidden') ?? '' };
  });
}
function check(document) {
  const im = images(document);
  const count = (src) => im.filter(x => x.src === src);
  const correctPair = src => count(src).length === 2
    && count(src).filter(x => x.alt && x.alt.trim().length >= 25).length === 1
    && count(src).filter(x => x.alt === '' && x.role === 'presentation' && x.hidden === 'true').length === 1;
  return {
    twoSourcesOnly: im.length === 4 && im.every(x => x.src === NASA || x.src === FRANKLIN),
    distinctAccessibleVariants: correctPair(NASA) && correctPair(FRANKLIN),
    nasaAttribution: document.includes('https://www.nasa.gov/image-detail/apollo-1-crew-honored/')
      && document.includes('NASA does not endorse Final Vestige'),
    franklinAttribution: document.includes('https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg')
      && document.includes('Wikimedia Commons file marked public domain')
      && document.includes('https://www.rmg.co.uk/collections/objects/rmgc-object-504898'),
    nyplNonReproduction: !im.some(x => /nypl|5003296|edit-017/i.test(x.src))
      && document.includes('IMAGE NOT REPRODUCED')
      && document.includes('https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0'),
    focusPreserved: document.includes('https://finalvestige.com/focus/'),
  };
}
test('exact-source archival image custody and contextual disclosures', () => {
  const result = check(html);
  assert.deepEqual(result, Object.fromEntries(Object.keys(result).map(k => [k,true])), JSON.stringify(result));
});
test('negative control: an unreviewed embedded photo fails the source allowlist', () => {
  assert.equal(check(html.replace('</body>', '<img src="https://example.com/sponsored.webp" alt="unreviewed"></body>')).twoSourcesOnly, false);
});
test('negative control: missing NASA editorial/no-endorsement credit fails', () => {
  assert.equal(check(html.replace('NASA does not endorse Final Vestige', 'NASA content')).nasaAttribution, false);
});
test('negative control: Franklin Commons-rights basis removed fails', () => {
  assert.equal(check(html.replace('Wikimedia Commons file marked public domain', 'image')).franklinAttribution, false);
});
test('negative control: NYPL map newly embedded requires fresh rights admission', () => {
  assert.equal(check(html.replace('</body>', '<img src="https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg" alt="map"></body>')).nyplNonReproduction, false);
});
test('negative control: accessible photograph replaced with decorative alt fails', () => {
  assert.equal(check(html.replace('alt="Apollo 1 astronauts Gus Grissom', 'alt="" data-comment="Apollo 1 astronauts Gus Grissom')).distinctAccessibleVariants, false);
});
