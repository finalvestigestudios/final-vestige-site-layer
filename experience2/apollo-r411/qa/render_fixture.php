<?php
/** CLI-only real-PHP fixture; no WordPress network, no data writes. */
define('ABSPATH', __DIR__);
define('FV_R411_ENABLED', true);
define('FV_R411_STAGING_PAGE_ID', 411);
$GLOBALS['fv_r411_env'] = 'staging';
$GLOBALS['fv_r411_page'] = 411;
function wp_get_environment_type(): string { return $GLOBALS['fv_r411_env']; }
function is_singular(): bool { return true; }
function get_queried_object_id(): int { return $GLOBALS['fv_r411_page']; }
function add_action($hook,$fn,$priority=10): void {}
function add_shortcode($name,$fn): void {}
function wp_enqueue_style($handle,$src,$deps,$version): void { $GLOBALS['fv_r411_styles'][]=$handle; }
function plugins_url($path,$file): string { return 'https://staging.example.test/'.$path; }
require dirname(__DIR__).'/staging-source-drawer.php';
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R411 offline fixture</title></head><body><main>'; 
echo fv_r411_shortcode();
echo '</main></body></html>';
