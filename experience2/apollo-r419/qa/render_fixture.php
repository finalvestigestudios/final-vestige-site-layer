<?php
/** Read-only WordPress staging context simulation: executes the exact PHP shortcode. */
define('ABSPATH', __DIR__);
define('FV_R419_ENABLED', getenv('FV_R419_MODE') !== 'disabled');
define('FV_R419_STAGING_PAGE_ID', 19019);
function wp_get_environment_type(): string { return getenv('FV_R419_MODE') === 'production' ? 'production' : 'staging'; }
function is_singular(): bool { return getenv('FV_R419_MODE') !== 'archive'; }
function get_queried_object_id(): int { return getenv('FV_R419_MODE') === 'wrong-page' ? 9000 : 19019; }
function add_action(string $name, string $callback, int $priority): void {}
function add_shortcode(string $tag, string $callback): void {}
require dirname(__DIR__) . '/staging-evidence-concordance.php';
$mode = getenv('FV_R419_MODE') ?: 'staging';
$css = file_get_contents(dirname(__DIR__) . '/assets/concordance.css');
$body = fv_r419_shortcode();
if ($mode === 'double') $body .= fv_r419_shortcode();
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R419 offline fixture · NOT INSTALLED WORDPRESS</title><style>' . $css . '</style></head><body style="margin:0;background:#191b1c">' . $body . '</body></html>';
