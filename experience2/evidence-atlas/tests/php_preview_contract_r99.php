<?php
/** Contract harness only, NOT actual WordPress or hosted Assembler. Never deploy. */
define('ABSPATH', __DIR__);
define('FV_APOLLO_R99_PRIVATE_PREVIEW', true);
$apollo_routes = [];
function add_action($hook, $callable, $priority=10) { $GLOBALS['apollo_routes'][$hook]=$callable; }
function add_shortcode($shortcode, $callable) { $GLOBALS['apollo_routes'][$shortcode]=$callable; }
function current_user_can($capability) {
    return $capability === 'edit_others_posts' && ($_COOKIE['apollo_r99_fixture_auth'] ?? '') === 'contract-only';
}
function status_header($code) { http_response_code($code); }
function nocache_headers() {}
function home_url($path='/') { return 'http://127.0.0.1:8941/'; }
function esc_url($url) { return htmlspecialchars($url, ENT_QUOTES, 'UTF-8'); }
function add_query_arg($key, $value, $base) { return $base . '?' . rawurlencode($key) . '=' . rawurlencode($value); }
// Test-only same-origin axe endpoint: obey the reviewed document's strict CSP.
// This fixture is NEVER installed with the generated WordPress adapter.
if (isset($_GET['fv_r99_axe'])) {
    $axe=getenv('APOLLO_R99_AXE');
    if (!current_user_can('edit_posts') || !$axe || !is_file($axe)) { http_response_code(404); exit; }
    header('Content-Type: text/javascript; charset=utf-8');
    header('Cache-Control: no-store');
    readfile($axe); exit;
}
$stage=getenv('APOLLO_R99_STAGE');
if (!$stage || !is_file($stage.'/fv-apollo-r99-private-preview.php')) { http_response_code(503); exit; }
require $stage.'/fv-apollo-r99-private-preview.php';
if (isset($_GET['fv_apollo_r99'])) {
    ($apollo_routes['template_redirect'])();
    http_response_code(404);
    exit;
}
header('Content-Type: text/html; charset=utf-8');
echo '<!doctype html><html lang="en"><head><title>R99 PHP Contract Fixture</title></head><body><main>';
echo ($apollo_routes['fv_apollo_r99_review'])();
echo '</main></body></html>';
