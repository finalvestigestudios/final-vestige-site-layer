<?php
// This is *not* installed WordPress. It executes the exact R428 PHP functions.
define('ABSPATH', __DIR__ . '/');
define('FV_R428_ENABLED', true);
define('FV_R428_STAGING_PAGE_ID', 2001);
function wp_get_environment_type() { return 'staging'; }
function is_singular() { return true; }
function get_queried_object_id() { return 2001; }
function add_shortcode($name, $callback) { $GLOBALS['fv_test_shortcode'] = $callback; }
function add_action($hook, $callback, $priority) { /* fixture */ }
require dirname(__DIR__) . '/staging-evidence-bridge.php';
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">';
echo '<title>R428 source bridge—PHP fixture</title><style>' . file_get_contents(dirname(__DIR__) . '/assets/evidence-bridge.css') . '</style></head><body style="margin:0;background:#111">';
echo fv_r428_shortcode();
echo fv_r428_shortcode();
echo '</body></html>';
