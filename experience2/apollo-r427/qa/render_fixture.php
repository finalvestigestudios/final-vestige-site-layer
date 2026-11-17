<?php
// Genuine byte-verified R426 rendering through the R427 shortcode. OFFLINE ONLY: not WordPress staging.
define('ABSPATH', __DIR__);
define('FV_R427_ENABLED', true);
define('FV_R427_STAGING_PAGE_ID', 427);
define('FV_R427_UPSTREAM_ROOT', dirname(__DIR__, 3) . '/checkout_r426/experience2/apollo-r426');
function wp_get_environment_type(){return 'staging';}
function is_singular(){return true;}
function get_queried_object_id(){return 427;}
function add_shortcode($name,$fn){}
function add_action($name,$fn,$priority=10){}
require_once dirname(__DIR__) . '/staging-source-chain.php';
$root = fv_r427_upstream_root();
if (!$root || !fv_r427_valid_upstream($root)) {fwrite(STDERR,"R426 byte identity gate failed\n");exit(2);}
$css = file_get_contents($root . '/assets/source-comparison.css') . "\n" . file_get_contents(dirname(__DIR__) . '/assets/source-chain.css');
$first = fv_r427_shortcode();
$second = fv_r427_shortcode();
if (str_contains($first,'source-chain research viewer unavailable') || str_contains($second,'source-chain research viewer unavailable')) {fwrite(STDERR,"Renderer HOLD\n");exit(2);}
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R427 exact-source offline fixture</title><style>' . $css . '</style></head><body style="margin:0">' . $first . $second . '</body></html>';
