<?php
/** Read-only genuine PHP composition of two R415 instances using original R411 and R414 sources. */
define('ABSPATH', '/tmp/r415-synthetic-staging');
define('FV_R415_ENABLED', true);
define('FV_R415_STAGING_PAGE_ID', 415);
function wp_get_environment_type() { return 'staging'; }
function is_singular() { return true; }
function get_queried_object_id() { return 415; }
require dirname(__DIR__) . '/staging-journey.php';
$main = fv_r415_shortcode();
$second = fv_r415_shortcode();
$css1 = file_get_contents(dirname(__DIR__) . '/../apollo-r414/assets/archive-gallery.css');
$css2 = file_get_contents(dirname(__DIR__) . '/assets/journey.css');
print '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FV R415 offline fixture (NOT WordPress)</title><style>' . $css1 . "\n" . $css2 . '</style></head><body style="margin:0">';
print $main . $second;
print '</body></html>';
