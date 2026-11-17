<?php
/** Staging context shim: real component PHP, but NOT WordPress or installed staging. */
define('ABSPATH', __DIR__);
$mode = getenv('FV_R420_MODE') ?: 'staging';
define('FV_R420_ENABLED', $mode !== 'disabled');
define('FV_R420_STAGING_PAGE_ID', 19020);
function wp_get_environment_type(): string { return getenv('FV_R420_MODE') === 'production' ? 'production' : 'staging'; }
function is_singular(): bool { return getenv('FV_R420_MODE') !== 'archive'; }
function get_queried_object_id(): int { return getenv('FV_R420_MODE') === 'wrong-page' ? 999 : 19020; }
function add_action(string $hook, string $callback, int $priority): void {}
function add_shortcode(string $tag, string $callback): void {}
require dirname(__DIR__) . '/staging-educator-source-lab.php';
$body = fv_r420_shortcode();
if ($mode === 'double') $body .= fv_r420_shortcode();
$css = file_get_contents(dirname(__DIR__) . '/assets/educator-lab.css');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R420 local PHP fixture (not WordPress)</title><style>' . $css . '</style></head><body style="margin:0;background:#1c2021">' . $body . '</body></html>';
