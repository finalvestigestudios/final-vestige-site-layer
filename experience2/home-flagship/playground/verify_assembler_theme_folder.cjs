'use strict';
/**
 * Verify the actual WordPress theme template directory promised by Playground.
 * This checks the source-level installer contract, not live Playground execution.
 * Run from exact checkout: node experience2/home-flagship/playground/verify_playground_blueprint.cjs
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json'), 'utf8'));

const ASSEMBLER_PIN = '75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f';
function admitThemeContract(bp) {
  assert.ok(Array.isArray(bp.steps) && bp.steps.length >= 5, 'complete review Blueprint required');
  const install = bp.steps[0];
  assert.equal(install.step, 'installTheme', 'theme installation must precede mu-plugin');
  assert.equal(install.themeData.resource, 'git:directory', 'source must remain pinned Git directory');
  assert.equal(install.themeData.url, 'https://github.com/Automattic/themes', 'expected upstream repository');
  assert.equal(install.themeData.path, 'assembler', 'expected upstream theme folder');
  assert.equal(install.themeData.ref, ASSEMBLER_PIN, 'immutable source commit required');
  assert.equal(install.themeData.refType, 'commit', 'Git resolver must treat SHA as a commit');
  assert.equal(install.options.activate, true, 'Assembler must be activated');
  assert.equal(install.options.targetFolderName, 'assembler',
    'Without targetFolderName Playground derives a checkout folder name; WordPress get_template() would not be assembler');
  const admission = bp.steps.find(s => s.step === 'runPHP' && s.code.includes('FV_EX2_WORDPRESS_IMPORT_ADMISSION_PASS'));
  assert.ok(admission, 'fresh WordPress admission is mandatory');
  assert.ok(admission.code.includes("$theme->get_template() !== 'assembler'"), 'WordPress must confirm activated template basename');
  assert.ok(admission.code.includes("shortcode_exists('fv_ex2_playground')"), 'preserve shortcode admission');
  return true;
}
assert.equal(admitThemeContract(fixture), true);
const mutate = (change) => { const bp=JSON.parse(JSON.stringify(fixture)); change(bp); return bp; };
const rejectionCases = [
  ['missing target folder', bp => { delete bp.steps[0].options.targetFolderName; }],
  ['incorrect derived folder', bp => { bp.steps[0].options.targetFolderName = 'https-github-com-Automattic-themes-at-assembler'; }],
  ['non-Assembler directory', bp => { bp.steps[0].options.targetFolderName = 'twentytwentyfive'; }],
  ['deactivated theme', bp => { bp.steps[0].options.activate = false; }],
  ['upstream path drift', bp => { bp.steps[0].themeData.path = 'another-theme'; }],
  ['unpinned source', bp => { bp.steps[0].themeData.ref = 'HEAD'; }],
  ['wrong ref type', bp => { bp.steps[0].themeData.refType = 'branch'; }],
  ['ambiguous ref type', bp => { delete bp.steps[0].themeData.refType; }],
  ['untrusted upstream', bp => { bp.steps[0].themeData.url = 'https://example.com/untrusted'; }],
  ['removed theme runtime check', bp => { const s=bp.steps[4];s.code=s.code.replace("$theme->get_template() !== 'assembler'", 'false'); }],
  ['removed shortcode admission', bp => { const s=bp.steps[4];s.code=s.code.replace("shortcode_exists('fv_ex2_playground')", 'true'); }],
];
for (const [name, change] of rejectionCases) {
  assert.throws(() => admitThemeContract(mutate(change)), undefined, name + ' must fail closed');
}
assert.equal(fixture.steps[1].step, 'mkdir');
assert.equal(fixture.steps[2].step, 'writeFile');
assert.equal(fixture.steps[3].step, 'runPHP');
assert.equal(fixture.steps[4].step, 'runPHP');
console.log('PASS: pinned Assembler Git source, exact WordPress template folder and activation, runtime admission, 11 negative mutations, step order');
