import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareReview, fnv32Utf16, BEFORE, AFTER, CHAPTER_IDS } from './prepare_focus_hero_review.mjs';

const margins = Array.from({ length:72 }, (_,i) => '<span class="fv-margin-strip__item" style="--i:' + i + '">Source ' + i + '</span>').join('');
const chapters = CHAPTER_IDS.map(id => '<section id="' + id + '"></section>').join('');
function fixture(content) {
  return {
    id:6, status:'publish', modified:'2026-11-05T12:07:24',
    content:content ?? '<!-- wp:html -->' + margins
      + '<div class="fv-hf__opening-actions"><a class="fv-hf__button fv-hf__button--gold" href="#fv-hf-evidence">Enter the evidence room</a>'
      + BEFORE + '</div>' + chapters
      + '<img src="edit-017-v02-nypl-5003296-original.jpg">'
      + '<!-- wp:jetpack/subscriptions /-->',
  };
}
const options = { enforceSnapshot:false };
test('changes only intended secondary hero anchor and maintains entire rest of source', () => {
  const input=fixture(); const result=prepareReview(input,options);
  assert.equal(result.report.changed_anchor_count,1);
  assert.equal(result.html, input.content.replace(BEFORE,AFTER));
  assert.equal(result.report.production_writes,false);
  assert.notEqual(result.report.source_sha256, result.report.candidate_sha256);
});
test('accepts connector structuredContent.data and edit-context content.raw', () => {
  const wrapped = { structuredContent:{data:{...fixture(), content:{raw:fixture().content}}}};
  assert.match(prepareReview(wrapped,options).html,/Focus Fieldbook/);
});
test('strict snapshot refuses representative fixture', () => assert.throws(()=>prepareReview(fixture()),/drift/));
test('rejects page-id mismatch',()=>assert.throws(()=>prepareReview({...fixture(),id:7},options),/Page 6/));
test('rejects unpublished input',()=>assert.throws(()=>prepareReview({...fixture(),status:'draft'},options),/Page 6/));
test('rejects rendered-content export',()=>assert.throws(()=>prepareReview({...fixture(),content:'<main>'+BEFORE+'</main>'},options),/raw Gutenberg/));
test('rejects duplicate CTA',()=>assert.throws(()=>prepareReview(fixture(fixture().content+BEFORE),options),/exactly once/));
test('rejects already applied CTA',()=>assert.throws(()=>prepareReview(fixture(fixture().content.replace(BEFORE,AFTER)),options),/exactly once/));
test('rejects missing Margins',()=>assert.throws(()=>prepareReview(fixture(fixture().content.replace(margins.split('</span>')[0]+'</span>','')),options),/72 historical/));
test('rejects missing Jetpack',()=>assert.throws(()=>prepareReview(fixture(fixture().content.replace('<!-- wp:jetpack/subscriptions /-->','')),options),/Jetpack/));
test('rejects missing chapter',()=>assert.throws(()=>prepareReview(fixture(fixture().content.replace('id="fv-hf-observer"','id="missing"')),options),/seven unique/));
test('rejects missing unreviewed NYPL original',()=>assert.throws(()=>prepareReview(fixture(fixture().content.replace('edit-017-v02-nypl-5003296-original.jpg','removed.jpg')),options),/NYPL image/));
test('rejects missing evidence CTA',()=>assert.throws(()=>prepareReview(fixture(fixture().content.replace('Enter the evidence room','Go elsewhere')),options),/primary evidence/));
test('utf16 FNV32 stable for basic source',()=>assert.equal(fnv32Utf16('abc'),'1a47e90b'));
