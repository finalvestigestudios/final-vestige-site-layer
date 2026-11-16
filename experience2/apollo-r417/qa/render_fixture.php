<?php
/** Offline harness only; never load this fixture as a WordPress plugin or live route. */
define('ABSPATH', __DIR__);
define('FV_R417_ENABLED', getenv('FV_TEST_MODE') !== 'disabled');
define('FV_R417_STAGING_PAGE_ID', 41717);
function wp_get_environment_type(): string { return getenv('FV_TEST_MODE') === 'production' ? 'production' : 'staging'; }
function is_singular(): bool { return getenv('FV_TEST_MODE') !== 'archive'; }
function get_queried_object_id(): int { return getenv('FV_TEST_MODE') === 'wrong-page' ? 23 : 41717; }
function add_action($a, $b, $c = null): void {}
function add_shortcode($a, $b): void {}
function wp_enqueue_style(...$args): void { $GLOBALS['r417_assets'][] = $args; }
function plugins_url($path, $file): string { return '/staging/' . $path; }
require dirname(__DIR__) . '/staging-provenance-guide.php';
$css = file_get_contents(dirname(__DIR__) . '/assets/provenance.css');
$mode = getenv('FV_TEST_MODE') ?: 'staging';
// No actual remote scripts/fonts, no media. CSS inlined exclusively in offline test document.
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo Provenance R417 Offline Fixture</title><style>' . $css . '</style></head><body style="margin:0">';
echo fv_r417_shortcode();
if ($mode === 'double') echo fv_r417_shortcode();
echo '</body></html>';
