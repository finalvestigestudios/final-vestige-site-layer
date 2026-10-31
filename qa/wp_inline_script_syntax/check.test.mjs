import test from 'node:test';
import assert from 'node:assert/strict';
import { inspectRenderedHtml, extractRestRendered } from './check.mjs';

const wrap = source => `<main>visitor-facing content</main><script>${source}</script>`;

test('valid raw ampersand expression parses', () => {
  const r = inspectRenderedHtml(wrap('if (a && b) { alert("ok"); }'));
  assert.equal(r.status, 'PASS');
  assert.equal(r.checked, 1);
  assert.equal(r.errors, 0);
});

test('WordPress-rendered decimal entity in JS operator fails compile', () => {
  const r = inspectRenderedHtml(wrap('if (c&#038;&#038;other) { show(); }'));
  assert.equal(r.status, 'FAIL');
  assert.equal(r.errors, 1);
  assert.equal(r.scripts[0].entityAmpersands, 2);
});

test('WordPress-rendered amp entity also fails compile', () => {
  assert.equal(inspectRenderedHtml(wrap('if (c&amp;&amp;x) {}')).errors, 1);
});

test('realistic Focus subscriber class conditional is caught', () => {
  const raw = 'function check(){if(c&&/\bis-subscriber\b/.test(c.className)){show();}}';
  const rendered = raw.replaceAll('&', '&#038;');
  assert.equal(inspectRenderedHtml(wrap(raw)).errors, 0);
  assert.equal(inspectRenderedHtml(wrap(rendered)).errors, 1);
});

test('one invalid script makes overall result FAIL while preserving other passes', () => {
  const r = inspectRenderedHtml(wrap('let ok = 1;') + wrap('if(x&#038;&#038;y){}'));
  assert.deepEqual(r.scripts.map(x => x.status), ['PASS','SYNTAX_ERROR']);
  assert.equal(r.checked, 2);
});

test('skips JSON-LD instead of incorrectly parsing JSON as JS', () => {
  const r = inspectRenderedHtml('<script type="application/ld+json">{"@context":"https://schema.org"}</script>');
  assert.equal(r.errors, 0);
  assert.equal(r.scripts[0].status, 'SKIP_NON_JS');
});

test('skips external scripts without trying to fetch URLs', () => {
  const r = inspectRenderedHtml('<script src="https://cdn.invalid/app.js"></script>');
  assert.equal(r.scripts[0].status, 'SKIP_EXTERNAL');
});

test('skips ES modules explicitly rather than misgrading them', () => {
  const r = inspectRenderedHtml('<script type="module">import {foo} from "./foo.js";</script>');
  assert.equal(r.scripts[0].status, 'SKIP_MODULE_BROWSER_REQUIRED');
});

test('handles case-insensitive tags and unquoted JavaScript type', () => {
  const r = inspectRenderedHtml('<SCRIPT TYPE=text/javascript>const x = 1;</SCRIPT>');
  assert.equal(r.errors, 0);
  assert.equal(r.checked, 1);
});

test('does not execute inline code while checking syntax', () => {
  globalThis.__fv_test_unexpected_execution = false;
  inspectRenderedHtml(wrap('globalThis.__fv_test_unexpected_execution = true;'));
  assert.equal(globalThis.__fv_test_unexpected_execution, false);
  delete globalThis.__fv_test_unexpected_execution;
});

test('parses canonical WordPress REST content.rendered string', () => {
  const html = wrap('if(x&&y){}');
  assert.equal(extractRestRendered(JSON.stringify({ content: { rendered: html } })), html);
});

test('accepts connector data wrapper while requiring rendered not raw', () => {
  assert.equal(extractRestRendered(JSON.stringify({data:{content:{rendered:wrap('const ok=true;')}}})).includes('<script>'),true);
  assert.throws(()=>extractRestRendered(JSON.stringify({content:{raw:'<script>ok()</script>'}})),/content\.rendered/);
});

test('invalid JSON input refuses gracefully', () => {
  assert.throws(()=>extractRestRendered('{broken'),SyntaxError);
});

test('pages with no inline JavaScript produce a clean zero-check report', () => {
  const r = inspectRenderedHtml('<div>text only</div>');
  assert.equal(r.checked,0);
  assert.equal(r.status,'PASS');
});

test('rejects non-string HTML', () => {
  assert.throws(()=>inspectRenderedHtml(null),TypeError);
});
