'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { inspect, evaluate } = require('./gate.cjs');
const wrap = (saved, rendered=saved, status='draft') => ({ pages: [{ id: 2017, status, saved_html: saved, rendered_html: rendered }] });
const js = s => `<script>${s}</script>`;
test('valid inline syntax survives save/render', () => assert.equal(evaluate(wrap(js('if (true && false) {}'))).status, 'PASS'));
test('encoded && in rendered HTML is detected without printing script source', () => {
  const r=evaluate(wrap(js('if (a && b) {}'), js('if (a &#038;&#038; b) {}')));
  assert.equal(r.status, 'HOLD'); assert.equal(r.failures[0].kind, 'rendered_syntax_invalid');
  assert.equal(JSON.stringify(r).includes('a &#038;'), false);
});
test('broken saved source is different from rendering defect', () => {
  const r=evaluate(wrap(js('if (a &#038;&#038; b) {}')));
  assert.equal(r.failures[0].kind, 'saved_syntax_invalid');
});
test('jsonld is validated as JSON, not JS', () => {
  assert.equal(evaluate(wrap('<script type="application/ld+json">{"@context":"https://schema.org"}</script>')).status, 'PASS');
});
test('invalid JSON-LD fails closed', () => assert.equal(evaluate(wrap('<script type="application/ld+json">{</script>')).status, 'HOLD'));
test('src-only scripts are not claimed to be downloaded/verified', () => {
  assert.equal(inspect('<script src="https://example.org/a.js"></script>')[0].result, 'external_unverified');
});
test('dropped script between saved and rendered fails', () => assert.equal(evaluate(wrap(js('let x=1'), '')).failures[0].kind, 'script_count_changed'));
test('non-JS template is not parsed as JS', () => assert.equal(evaluate(wrap('<script type="text/x-template">{{ template }}</script>')).status, 'PASS'));
test('modules fail closed, not falsely syntax-approved', () => assert.equal(evaluate(wrap('<script type="module">export const a=1</script>')).failures[0].kind, 'module_unverified'));
test('unclosed script is rejected', () => assert.throws(() => inspect('<script>let a=1'), /unclosed/));
test('oversized page is rejected', () => assert.throws(() => inspect('x'.repeat(2*1024*1024+1)), /oversized/));
test('published page is excluded by design', () => assert.throws(() => evaluate(wrap('', '', 'publish')), /draft_metadata/));
test('empty draft set fails closed', () => assert.throws(() => evaluate({pages:[]}), /page_set/));
test('multiple scripts and pages preserve counts', () => {
  const r=evaluate({pages:[{id:1,status:'draft',saved_html:js('let a=1')+js('let b=2'),rendered_html:js('let a=1')+js('let b=2')},{id:2,status:'draft',saved_html:'',rendered_html:''}]});
  assert.equal(r.status,'PASS');assert.equal(r.draft_pages,2);assert.equal(r.inline_scripts_checked,2);
});
test('differing type flags source classification drift', () => assert.equal(evaluate(wrap('<script type="application/json">{}</script>',js('{}'))).failures[0].kind,'script_type_changed'));
