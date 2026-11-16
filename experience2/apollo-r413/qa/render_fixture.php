<?php
/** Staging-only offline PHP fixture; no WordPress writes or live traffic. */
define('ABSPATH', __DIR__);
define('FV_R413_ENABLED', true);
define('FV_R413_STAGING_PAGE_ID', 413);
$GLOBALS['fv_r413_env'] = 'staging';
$GLOBALS['fv_r413_page'] = 413;
function wp_get_environment_type(): string { return $GLOBALS['fv_r413_env']; }
function is_singular(): bool { return true; }
function get_queried_object_id(): int { return $GLOBALS['fv_r413_page']; }
function add_shortcode($tag,$callback): void {}
function add_action($hook,$callback,$priority=10): void {}
function wp_enqueue_style($handle,$src,$deps,$version): void { $GLOBALS['fv_r413_styles'][] = $handle; }
function plugins_url($path,$file): string { return 'https://staging.invalid/' . $path; }
require dirname(__DIR__) . '/staging-evidence-plate.php';
$style = file_get_contents(dirname(__DIR__) . '/assets/evidence-plate.css');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R413 evidence plate staging fixture</title><style>' . $style . '</style></head><body style="margin:0"><main>';
echo fv_r413_shortcode();
echo fv_r413_shortcode();
echo '</main></body></html>';
