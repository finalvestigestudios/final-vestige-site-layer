<?php
/** Native R421 component PHP rendered under a controlled staging-context shim; NOT WordPress. */
define('ABSPATH', __DIR__);
$mode = getenv('FV_R421_MODE') ?: 'staging';
define('FV_R421_ENABLED', $mode !== 'disabled');
define('FV_R421_STAGING_PAGE_ID', 19021);
function wp_get_environment_type(): string { return getenv('FV_R421_MODE') === 'production' ? 'production' : 'staging'; }
function is_singular(): bool { return getenv('FV_R421_MODE') !== 'archive'; }
function get_queried_object_id(): int { return getenv('FV_R421_MODE') === 'wrong-page' ? 44 : 19021; }
function add_action(string $hook, string $cb, int $priority): void {}
function add_shortcode(string $tag, string $cb): void {}
require dirname(__DIR__) . '/staging-source-receipts.php';
$body = fv_r421_shortcode();
if ($mode === 'double') $body .= fv_r421_shortcode();
$css = file_get_contents(dirname(__DIR__) . '/assets/source-receipts.css');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">';
echo '<title>FV Apollo R421 offline fixture — not installed WordPress</title><style>' . $css . '</style></head>';
echo '<body style="margin:0;background:#0e1510">' . $body . '</body></html>';
