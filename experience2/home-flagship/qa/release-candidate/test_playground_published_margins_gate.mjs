/** Regression contract for real publicly published page-6 Margins in
 * disposable Gutenberg/Assembler browser fixture. No network/CMS access.
 * Execute: node --test test_playground_published_margins_gate.mjs
 */
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {
  PUBLISHED_MARGINS_LABEL,
  validatePublishedMarginsFixture,
  firstMarginMismatch
} from './playground_assembler_render_gate.mjs';

const fixture=JSON.parse(readFileSync(
  new URL('./public_page6_margins_20261102.json',import.meta.url),'utf8'));
const clone=()=>structuredClone(fixture);

test('actual published source yields 72 ordered, unique and nonempty records',()=>{
  const texts=validatePublishedMarginsFixture(fixture);
  assert.equal(texts.length,72);
  assert.equal(new Set(texts).size,72);
  assert.match(texts[0],/^Nearly 4,000 years ago, Nanni/);
  assert.match(texts[71],/JFK/);
});
test('browser source-label contract exactly matches the serialized builder',()=>{
  assert.equal(PUBLISHED_MARGINS_LABEL,
    '72 published historical fragments in isolated review');
  const builder=readFileSync(new URL('./write_source_flagship_playground_candidate.py',
    import.meta.url),'utf8');
  assert.ok(builder.includes('aria-label="'+PUBLISHED_MARGINS_LABEL+'" tabindex="0"'),
    'WordPress-saved markup must expose the same label as browser QA');
});
test('exact rendering and no-JS text arrays must match all published records',()=>{
  const texts=validatePublishedMarginsFixture(fixture);
  assert.equal(firstMarginMismatch([...texts],texts),-1);
  for(const i of [0,19,35,71]){
    const changed=[...texts];changed[i]+=' edited';
    assert.equal(firstMarginMismatch(changed,texts),i);
  }
});
test('missing or extra published DOM nodes are rejected',()=>{
  const texts=validatePublishedMarginsFixture(fixture);
  assert.equal(firstMarginMismatch(texts.slice(0,71),texts),71);
  assert.equal(firstMarginMismatch([...texts,'unreviewed'],texts),72);
});
test('reordered or duplicated published DOM nodes are rejected',()=>{
  const texts=validatePublishedMarginsFixture(fixture);
  const swapped=[...texts];[swapped[4],swapped[5]]=[swapped[5],swapped[4]];
  assert.equal(firstMarginMismatch(swapped,texts),4);
  const doubled=[...texts];doubled[20]=doubled[19];
  assert.equal(firstMarginMismatch(doubled,texts),20);
});
test('wrong production site, page or source status fails closed',()=>{
  for(const [field,value] of [
    ['source_site_id',1],['source_page_id',7],
    ['source_url','https://untrusted.invalid/'],['status','PRODUCTION'],
    ['fragment_count',71]
  ]){
    const bad=clone();bad[field]=value;
    assert.throws(()=>validatePublishedMarginsFixture(bad),undefined,field);
  }
});
test('missing, duplicated and reordered fixture indices fail closed',()=>{
  for(const mutate of [
    d=>d.items.pop(),
    d=>{d.items[8].index=7;},
    d=>{d.items[3].text=d.items[2].text;},
    d=>{d.items[1].text='';}
  ]){
    const bad=clone();mutate(bad);
    assert.throws(()=>validatePublishedMarginsFixture(bad));
  }
});
test('unexpected rendered margin input cannot be silently accepted',()=>{
  const texts=validatePublishedMarginsFixture(fixture);
  assert.throws(()=>firstMarginMismatch(null,texts));
  assert.throws(()=>firstMarginMismatch(texts,'not an array'));
});
