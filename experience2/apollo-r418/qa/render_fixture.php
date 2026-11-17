<?php
// Offline PHP-rendered fixture only. This is NOT installed WordPress staging.
define('ABSPATH', __DIR__);
$mode = getenv('FV_TEST_MODE') ?: 'staging';
define('FV_R418_ENABLED', $mode !== 'disabled');
define('FV_R418_STAGING_PAGE_ID', 418);
function wp_get_environment_type() { return getenv('FV_TEST_MODE') === 'production' ? 'production' : 'staging'; }
function is_singular() { return getenv('FV_TEST_MODE') !== 'archive'; }
function get_queried_object_id() { return getenv('FV_TEST_MODE') === 'wrong-page' ? 888 : 418; }
function add_shortcode($name, $cb) { /* No runtime WordPress mutations */ }
function add_action($name, $cb, $priority = 10) { /* No runtime WordPress mutations */ }
require dirname(__DIR__) . '/staging-chronology-bridge.php';
$css = file_get_contents(dirname(__DIR__) . '/assets/chronology-bridge.css');
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R418 offline acceptance fixture</title><style>html{font:16px/1.55 system-ui,sans-serif}body{margin:0;max-width:100%;background:#e8e6e0;padding:6px}*{box-sizing:border-box}<?php echo $css;?></style></head><body><main><?php echo fv_r418_shortcode(); if ($mode === 'double') echo fv_r418_shortcode(); ?></main></body></html>
