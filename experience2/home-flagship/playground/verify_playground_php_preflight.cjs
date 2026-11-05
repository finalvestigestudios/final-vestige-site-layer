'use strict';
/**
 * Independent, native PHP preflight for the complete sealed WordPress Playground import.
 * Run with: node experience2/home-flagship/playground/verify_playground_php_preflight.cjs
 *
 * This validates syntax and accidental-copy behavior, NOT a WordPress/Assembler
 * integration, and is NOT permission to install this MU-plugin on production.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const blueprint = JSON.parse(fs.readFileSync(path.join(__dirname, 'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json'), 'utf8'));
const pluginStep = blueprint.steps.find(s => s.step === 'writeFile' && /mu-plugins\/fv-ex2-playground-review\.php$/.test(s.path));
const runnerStep = blueprint.steps.find(s => s.step === 'runPHP');
const admissionStep = blueprint.steps.filter(s => s.step === 'runPHP')[1];
assert.ok(pluginStep, 'Missing local-only MU-plugin');
assert.ok(runnerStep, 'Missing local page-creation step');
assert.ok(admissionStep, 'Missing fresh WordPress runtime admission step');

const markerKey = 'fv_ex2_playground_review_only';
const markerValue = 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1';
const guard = "if (get_option('" + markerKey + "', '') !== '" + markerValue + "') { return; }";
const plugin = pluginStep.data;
const runPHP = runnerStep.code;
assert.ok(plugin.startsWith('<?php\n'), 'Expected PHP source');
assert.equal(plugin.split(guard).length - 1, 1, 'Exactly one complete activation guard required');
assert.ok(plugin.indexOf(guard) < plugin.indexOf("add_action('wp_enqueue_scripts'"), 'Must fail closed before registering page assets');
assert.ok(plugin.indexOf(guard) < plugin.indexOf("add_shortcode('fv_ex2_playground'"), 'Must fail closed before registering the shortcode');
assert.ok(runPHP.includes("update_option('" + markerKey + "', '" + markerValue + "', false);"), 'Local Blueprint must initialize exact marker');
assert.ok(runPHP.indexOf("update_option('" + markerKey) > runPHP.indexOf("wp_insert_post("), 'Do not authorize activation before local page creation');
assert.ok(plugin.includes("if (!is_page('fv-ex2-review'))"), 'Assets and shortcode must remain scoped to review page');
assert.ok(!/wp_remote_(?:post|request)\s*\(/.test(plugin), 'No backend outbound calls permitted');
assert.ok(!/fetch\s*\(\s*['\"]https?:/.test(plugin), 'No newly added remote JS calls permitted');

function recognizesGuard(source) {
  return source.includes(guard) &&
    source.indexOf(guard) < source.indexOf("add_action('wp_enqueue_scripts'") &&
    source.indexOf(guard) < source.indexOf("add_shortcode('fv_ex2_playground'");
}
assert.equal(recognizesGuard(plugin), true);
assert.equal(recognizesGuard(plugin.replace(guard, '')), false, 'negative: deleted guard rejected');
assert.equal(recognizesGuard(plugin.replace(markerValue, 'MISMATCHED_MARKER')), false, 'negative: mismatched marker rejected');
assert.equal(recognizesGuard(plugin.replace(guard, '').replace("add_shortcode('fv_ex2_playground'", guard + "\nadd_shortcode('fv_ex2_playground'")), false, 'negative: late guard rejected');

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'fv-ex2-playground-php-'));
try {
  const phpFile = path.join(temp, 'fv-ex2-playground-review.php');
  const harnessFile = path.join(temp, 'guard-harness.php');
  const admissionFile = path.join(temp, 'wordpress-runtime-admission.php');
  fs.writeFileSync(admissionFile, admissionStep.code, { mode: 0o600 });
  fs.writeFileSync(phpFile, plugin, { mode: 0o600 });
  const phpHarness = String.raw`<?php
define('ABSPATH', __DIR__ . '/');
$GLOBALS['fv_actions'] = array();
$GLOBALS['fv_codes'] = array();
function get_option($key, $fallback = '') {
    if ($key !== 'fv_ex2_playground_review_only') { return $fallback; }
    return ($GLOBALS['argv'][2] ?? '') === 'valid'
        ? 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1'
        : $fallback;
}
function add_action($hook, $callback) { $GLOBALS['fv_actions'][] = $hook; }
function add_shortcode($name, $callback) { $GLOBALS['fv_codes'][] = $name; }
require $argv[1];
echo json_encode(array('actions' => $GLOBALS['fv_actions'], 'shortcodes' => $GLOBALS['fv_codes']));
`;
  fs.writeFileSync(harnessFile, phpHarness, { mode: 0o600 });

  function php(args) {
    const out = spawnSync('php', args, { encoding: 'utf8', timeout: 15000, maxBuffer: 1024 * 1024 });
    assert.ifError(out.error);
    assert.equal(out.status, 0, 'Native PHP failure: ' + out.stderr);
    return out.stdout;
  }
  assert.match(php(['-l', phpFile]), /No syntax errors detected/, 'PHP parser must accept the real generated plugin');
  assert.match(php(['-l', admissionFile]), /No syntax errors detected/, 'PHP parser must accept the fresh WordPress runtime admission');
  const inactive = JSON.parse(php([harnessFile, phpFile, 'missing']));
  assert.deepEqual(inactive, { actions: [], shortcodes: [] }, 'Plugin must do nothing if imported without local marker');
  const active = JSON.parse(php([harnessFile, phpFile, 'valid']));
  assert.deepEqual(active, { actions: ['wp_enqueue_scripts'], shortcodes: ['fv_ex2_playground'] }, 'Plugin should register exactly the expected local callbacks');
  const wrong = JSON.parse(php([harnessFile, phpFile, 'wrong']));
  assert.deepEqual(wrong, inactive, 'Wrong marker must also fail closed');
  console.log('PASS: native plugin and WordPress-admission PHP syntax; inactive/active/invalid-marker behavior; exact Blueprint marker; 3 adversarial structural cases');
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}
