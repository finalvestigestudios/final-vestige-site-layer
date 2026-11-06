'use strict';
/**
 * Fail-closed source admission for PR #1282's exact 7-chapter WordPress Playground
 * Blueprint after moving the unchanged 72 public records behind the opening hero.
 * This does NOT execute WordPress, axe, Jetpack, images, or Lighthouse.
 */
const fs = require('node:fs');
const assert = require('node:assert/strict');
const EXPECTED_IDS = [
  'fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
  'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title'
];
function verify(text, previous = null) {
  const bp = JSON.parse(text);
  assert.equal(bp.$schema, 'https://playground.wordpress.net/blueprint-schema.json');
  assert.equal(bp.steps[0].step, 'installTheme');
  assert.equal(bp.steps[0].themeData.path, 'assembler');
  assert.equal(bp.steps[0].themeData.ref, '75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f');
  const plugin = bp.steps[2].data;
  assert.ok(plugin.includes('FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1'));
  function heredoc(type) {
    const start = "<<<'FVPG_" + type + "_END'\\n", end = '\\nFVPG_' + type + '_END';
    assert.equal(plugin.split(start).length, 2, 'missing '+type+' start');
    const tail = plugin.split(start)[1];
    assert.equal(tail.split(end).length, 2, 'missing '+type+' end');
    return tail.split(end)[0];
  }
  const html = heredoc('HTML'), css = heredoc('CSS'), js = heredoc('JS');
  const n = (s,sub) => s.split(sub).length - 1;
  assert.equal(n(html, 'class="fv-margin-strip__item"'), 72, 'source records');
  assert.equal(n(html, 'class="fv-margin-strip fv-margin-strip--rotator"'), 1);
  assert.equal(n(html, 'class="fv-hf__chapter-nav"'), 1);
  assert.equal(n(html, 'href="https://finalvestige.com/focus/"'), 5);
  assert.equal(n(html, '<img '), 2, 'Apollo and Franklin only');
  assert.ok(!html.includes('wp-content/uploads/2026/11/brooklyn-map'));
  for (const anchor of EXPECTED_IDS) assert.ok(html.includes('id="'+anchor+'"'), 'missing '+anchor);
  const opening = html.indexOf('class="fv-hf__opening"');
  const strip = html.indexOf('class="fv-margin-strip fv-margin-strip--rotator"');
  const chronicle = html.indexOf('class="fv-hf__chronicle"');
  const content = html.indexOf('class="fv-hf__wp-content"');
  assert.ok(0 <= content && content < opening && opening < strip && strip < chronicle,
    'evidence rail must follow hero but precede chapter 02');
  assert.ok(html.indexOf('class="fv-hf" data-fv-home-flagship>') < strip);
  assert.ok(html.includes('type="checkbox"'));
  assert.ok(css.includes('.fv-margin-strip__motion-check'));
  assert.ok(css.includes('prefers-reduced-motion: reduce'));
  assert.ok(js.includes('source: flagship.js'));
  if (previous !== null) {
    const old = JSON.parse(previous).steps[2].data;
    function grab(str,type) {
      const start = "<<<'FVPG_"+type+"_END'\\n", end = '\\nFVPG_'+type+'_END';
      return str.split(start)[1].split(end)[0];
    }
    assert.equal(css, grab(old, 'CSS'), 'CSS changed in reorder');
    assert.equal(js, grab(old, 'JS'), 'JS changed in reorder');
    const oldHtml = grab(old,'HTML');
    const extractRecords = h => [...h.matchAll(/<span class="fv-margin-strip__item"[^>]*>([\\s\\S]*?)<\\/span>/g)]
      .map(m => m[1]);
    assert.deepEqual(extractRecords(html), extractRecords(oldHtml), 'historical record text changed');
    assert.equal(html.replace(/<!-- All 72 source-preserved public records follow the opening promise, and remain readable without JavaScript. -->/g,'')
      .match(/https:\\/\\/finalvestige\\.com\\/focus\\//g)?.length,
      oldHtml.match(/https:\\/\\/finalvestige\\.com\\/focus\\//g)?.length);
  }
  return {records:72,chapters:7,images:2,focusLinks:5,opening,strip,chronicle};
}
if (require.main === module) {
  const current = fs.readFileSync(process.argv[2] || 'experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json','utf8');
  const old = process.argv[3] && fs.readFileSync(process.argv[3], 'utf8');
  console.log(JSON.stringify({result:'SOURCE_ADMISSION_PASS',...verify(current,old||null)}));
}
module.exports = {verify};
