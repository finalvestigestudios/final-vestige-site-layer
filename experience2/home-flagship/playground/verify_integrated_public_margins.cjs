'use strict';
/**
 * WordPress Playground source admission for a public-only Page 6 Margins copy.
 * Run: node experience2/home-flagship/playground/verify_integrated_public_margins.cjs
 * This is NOT an actual WordPress, browser, axe, or Jetpack acceptance test.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const bpPath = path.join(__dirname, 'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json');

function verify(blueprintText) {
  const bp = JSON.parse(blueprintText);
  assert.equal(bp.steps.length, 5, 'Unexpected Playground run steps');
  const plugin = bp.steps[2].data;
  const admission = bp.steps[4].code;
  assert.equal(bp.steps[2].path, '/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php');
  assert.match(plugin, /if \(!is_page\('fv-ex2-review'\)\) \{ return ''; \}/);
  const start = plugin.indexOf("return <<<'FVPG_HTML_END'");
  const stop = plugin.indexOf('\nFVPG_HTML_END;', start);
  assert.ok(start > 0 && stop > start, 'Shortcode HTML here-document missing');
  const html = plugin.slice(start, stop);
  assert.equal((html.match(/class="fv-margin-strip fv-margin-strip--rotator"/g) || []).length, 1,
    'Public Margins block must appear exactly once');
  assert.ok(html.indexOf('class="fv-margin-strip') < html.indexOf('data-fv-home-flagship'),
    'Real published Margins must precede the source-controlled seven-chapter flagship');
  const entries = [...html.matchAll(/<span class="fv-margin-strip__item" style="--i:(\d+)">([\s\S]*?)<\/span>/g)];
  assert.equal(entries.length, 72, 'All 72 published fragments must survive');
  entries.forEach(([_, num, text], idx) => {
    assert.equal(Number(num), idx, 'Missing, duplicated or reordered record ' + idx);
    assert.ok(text.trim().length >= 28, 'Empty/truncated record ' + idx);
  });
  for (const id of ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence',
                   'fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']) {
    assert.ok(html.includes('id="' + id + '"'), 'Lost flagship chapter ' + id);
  }
  assert.equal((html.match(/<img /g) || []).length, 2, 'Only Apollo/Franklin may be in isolated candidate');
  assert.ok(html.includes('https://finalvestige.com/focus/'), 'Preserve existing Focus journey');
  assert.ok(!html.includes('wp:jetpack/subscriptions'), 'Do not fabricate a working Jetpack form');
  // The original production reduced-motion rule hides 71 records. The later
  // PR #1062 reviewed overlay is REQUIRED to override that staging-only.
  assert.match(plugin, /Reviewed reduced-motion remedy from draft PR #1062/);
  assert.match(plugin, /@media \(prefers-reduced-motion: reduce\) \{/);
  assert.match(plugin, /\.fv-margin-strip__item,\s*\.fv-margin-strip__item:nth-child\(1\)\s*\{\s*display: block;/);
  assert.match(plugin, /overflow-x: auto;/);
  assert.match(admission, /substr_count\(\$markup, 'class="fv-margin-strip__item"'\) !== 72/);
  assert.match(admission, /FV_EX2_WORDPRESS_IMPORT_ADMISSION_PASS/);
  assert.equal(bp.steps[0].options.targetFolderName, 'assembler');
  return {records:entries.length, chapters:7, previewImages:2};
}

if (require.main === module) {
  const raw = fs.readFileSync(bpPath,'utf8');
  console.log('PASS: integrated public Margins source admission', JSON.stringify(verify(raw)));
  let negative = 0;
  const mutate = (before, after) => {
    assert.ok(raw.includes(before), 'Negative-test source marker changed');
    const trial = raw.replace(before, after);
    assert.throws(() => verify(trial));
    negative++;
  };
  mutate('style=\\"--i:71\\"', 'style=\\"--i:999\\"');
  mutate('Reviewed reduced-motion remedy from draft PR #1062','Removed reviewed overlay');
  mutate('targetFolderName\\": \\"assembler\\"', 'targetFolderName\\": \\"another-theme\\ "');
  console.log('PASS: negative-source variants rejected:', negative);
}
module.exports = { verify };
