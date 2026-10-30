'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {pageCounts, checkFocusMetadata} = require('./focus_metadata_guard.cjs');
function page(body = 'Get the 52-page Complete Edition', desc = 'A free 52-page fieldbook', status = 'publish') {
  return {id: 1579, slug: 'focus', status, content: body, meta: {advanced_seo_description: desc}};
}
test('detects real October 29 CMS mismatch: 52-page hero vs 7-page SEO description', () => {
  const r = checkFocusMetadata(page('Get the complete 52-page fieldbook', 'A free 7-page fieldbook'));
  assert.equal(r.code, 'FOCUS_EDITION_PAGE_COUNT_MISMATCH');
  assert.equal(r.status, 'MISMATCH_CMS');
  assert.deepEqual(r.body_pages, [52]); assert.deepEqual(r.seo_description_pages, [7]);
  assert.equal(r.source_only, true);
});
test('passes matching 52-page source and description', () => {
  assert.equal(checkFocusMetadata(page()).status, 'PASS_CMS');
});
test('handles en dash and whitespace before pages', () => {
  assert.deepEqual(pageCounts('52–page PDF, 7 pages, 52-page edition'), [7, 52]);
});
test('ignores seven days, twelve minutes, and other unrelated numerals', () => {
  assert.deepEqual(pageCounts('seven days and 12 minutes, then 30 day log'), []);
});
test('does not mark an unpublished page as production mismatch', () => {
  assert.equal(checkFocusMetadata(page('52 pages', '7 pages', 'draft')).code, 'NOT_PUBLISHED');
});
test('refuses a different page or route', () => {
  assert.equal(checkFocusMetadata({...page(), id: 29}).code, 'UNEXPECTED_PAGE');
  assert.equal(checkFocusMetadata({...page(), slug: '72-hours-without-the-tap'}).status, 'INCONCLUSIVE');
});
test('does not invent a mismatch where SEO description omits counts', () => {
  assert.equal(checkFocusMetadata(page('52 pages', 'A free workbook')).status, 'REVIEW');
});
test('does not select a count when body mentions multiple editions', () => {
  assert.equal(checkFocusMetadata(page('Original 7-page guide now expanded to 52 pages', '7 pages')).code, 'BODY_EDITION_AMBIGUOUS');
});
test('accepts Gutenberg-style raw content and nested page', () => {
  const p = page(); p.content = {raw: '<p>52-page Complete Edition</p>'};
  assert.equal(checkFocusMetadata({page: p}).status, 'PASS_CMS');
});
test('fails safely on missing/malformed data', () => {
  assert.equal(checkFocusMetadata(null).status, 'INCONCLUSIVE');
  assert.equal(checkFocusMetadata({page: {...page(), content: null}}).status, 'INCONCLUSIVE');
  assert.equal(checkFocusMetadata({...page(), meta: null}).status, 'REVIEW');
});
