'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { headingsFromMarkup, auditPages } = require('./heading_order_audit.cjs');
const page = (id, content, status='publish') => ({id, content, status, url:`https://finalvestige.com/example-${id}/`});

test('normal h1 before h2 passes source review', () => {
  assert.equal(auditPages([page(1, '<h1>Library</h1><h2>Sources</h2>')])[0].status, 'PASS_SOURCE_ONLY');
});
test('featured h2 above main h1 flags semantic review', () => {
  const r=auditPages([page(525,'<section><h2>Featured source</h2></section><h1>Explore</h1>')])[0];
  assert.deepEqual(r.reviewReasons,['HEADING_BEFORE_CONTENT_H1']);
  assert.equal(r.beforeH1Count,1);
});
test('two pages with similar featured banners are detected separately',()=>{
  const input=[page(525,'<h2>Puységur</h2><h1>Explore</h1>'),page(77,'<h2>Puységur</h2><h1>The Library</h1>')];
  assert.equal(auditPages(input).filter(x=>x.status==='REVIEW_SOURCE_ONLY').length,2);
});
test('Gutenberg comments containing fake headings are ignored',()=>{
  assert.equal(headingsFromMarkup('<!-- <h2>Template</h2> --><h1>Real</h1>').length,1);
});
test('CSS and script text containing headings are ignored',()=>{
  assert.deepEqual(headingsFromMarkup('<style>content:"<h2>Fake</h2>"</style><script>"<h3>Fake</h3>"</script><h1>Main</h1>'),[{level:1,text:'Main'}]);
});
test('inline HTML in heading is stripped for readable diagnostics',()=>{
  assert.deepEqual(headingsFromMarkup('<h2 id="a"><em>The</em> Library</h2>'),[{level:2,text:'The Library'}]);
});
test('multiple first-level headings are flagged but not called browser failures',()=>{
  const result=auditPages([page(4,'<h1>One</h1><h1>Two</h1>')])[0];
  assert.deepEqual(result.reviewReasons,['MULTIPLE_CONTENT_H1']);
  assert.equal(result.status,'REVIEW_SOURCE_ONLY');
});
test('missing content h1 is review only',()=>{
  const result=auditPages([page(5,'<h2>Orphan</h2>')])[0];
  assert.deepEqual(result.reviewReasons,['NO_CONTENT_H1','HEADING_BEFORE_CONTENT_H1']);
});
test('unpublished pages are excluded',()=>{
  assert.equal(auditPages([page(6,'<h2>A</h2><h1>B</h1>','draft')]).length,0);
});
test('bad input fails closed without network',()=>{
  assert.throws(()=>auditPages({foo:1}),/array/);
  assert.throws(()=>auditPages([page(7,null)]),/string/);
});
test('source check never treats its output as a public browser verdict',()=>{
  for(const result of auditPages([page(8,'<h2>Top</h2><h1>Bottom</h1>')]))assert.match(result.status,/SOURCE_ONLY/);
});
