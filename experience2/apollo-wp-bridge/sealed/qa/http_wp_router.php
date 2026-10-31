<?php
/** Synthetic WordPress function stub, test-only. All routes served from this file; no static asset exposure. */
if (!defined('FV_TEST_APOLLO_PLUGIN')) { http_response_code(500); exit; }
$route = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
if (!in_array($route, array('/review', '/wp-admin/admin-ajax.php', '/health'), true)) { http_response_code(404); exit; }
if ($route === '/health') { header('Content-Type: text/plain'); echo 'ready'; exit; }
$GLOBALS['FV_TEST_MODE'] = $_COOKIE['fv_test_mode'] ?? 'guest';
if (!in_array($GLOBALS['FV_TEST_MODE'], array('editor','guest','reader','production','off'), true)) { http_response_code(403); exit; }
if ($GLOBALS['FV_TEST_MODE'] !== 'off') { define('FV_EX2_APOLLO_STAGING_ALLOW', true); }
define('ABSPATH', __DIR__ . '/');
$GLOBALS['shortcodes'] = array(); $GLOBALS['actions'] = array();
function wp_get_environment_type() { return $GLOBALS['FV_TEST_MODE'] === 'production' ? 'production' : 'staging'; }
function is_user_logged_in() { return in_array($GLOBALS['FV_TEST_MODE'], array('editor','reader','production'), true); }
function current_user_can($cap) { return $GLOBALS['FV_TEST_MODE'] !== 'reader' && $cap === 'edit_pages'; }
function wp_create_nonce($action) { return $action === 'fv_ex2_apollo_sealed' ? 'http-stub-fixed-nonce' : ''; }
function check_ajax_referer($action, $query_arg = false, $stop = true) {
    // Emulate WordPress core: default stop=true emits -1 on an invalid nonce.
    $field = $query_arg ? $query_arg : (isset($_REQUEST['_ajax_nonce']) ? '_ajax_nonce' : '_wpnonce');
    $token = $_REQUEST[$field] ?? null;
    $result = ($action === 'fv_ex2_apollo_sealed' && is_string($token)
        && $token === wp_create_nonce($action)) ? 1 : false;
    if ($action === 'fv_ex2_apollo_sealed' && is_string($token)
        && $token === 'http-stub-old-nonce') { $result = 2; }
    if ($stop && $result === false) {
        status_header(403);
        echo '-1';
        exit;
    }
    return $result;
}
function add_shortcode($name, $handler) { $GLOBALS['shortcodes'][$name] = $handler; }
function add_action($name, $handler) { $GLOBALS['actions'][$name] = $handler; }
function admin_url($path) { return 'http://127.0.0.1:' . $_SERVER['SERVER_PORT'] . '/wp-admin/' . $path; }
function add_query_arg($args, $url) { return $url . '?' . http_build_query($args, '', '&', PHP_QUERY_RFC3986); }
function esc_url($url) { return htmlspecialchars($url, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function nocache_headers() { header('Cache-Control: no-store, private, no-cache, must-revalidate, max-age=0'); header('Expires: Wed, 11 Jan 1984 05:00:00 GMT'); }
function status_header($status) { http_response_code($status); }
require FV_TEST_APOLLO_PLUGIN;
if ($route === '/review') {
    header('Content-Type: text/html; charset=UTF-8'); header('Cache-Control: no-store');
    echo '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo 1 Private WordPress HTTP Stub</title></head><body><main><h1>Staging editorial review</h1>';
    echo fv_ex2_apollo_sealed_shortcode();
    echo '</main></body></html>'; exit;
}
$action = $_GET['action'] ?? '';
$handler = $GLOBALS['actions']['wp_ajax_' . $action] ?? null;
if (!is_callable($handler)) { http_response_code(404); exit; }
$handler();
