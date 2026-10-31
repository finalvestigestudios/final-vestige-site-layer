<?php
/** PHP CLI simulates WP auth/env/nonce, not an actual site or HTTP headers. */
if ($argc < 4) { fwrite(STDERR, "USAGE php mock_wordpress.php plugin.php MODE ACTION [file]\n"); exit(70); }
$plugin = $argv[1];
$mode = $argv[2];
$action = $argv[3];
$GLOBALS['ENV'] = ($mode === 'production') ? 'production' : 'staging';
$GLOBALS['LOGIN'] = $mode !== 'guest';
$GLOBALS['CAP'] = $mode !== 'reader';
if ($mode !== 'off') { define('FV_EX2_APOLLO_STAGING_ALLOW', true); }
define('ABSPATH', '/staging/wp/');
$GLOBALS['shortcodes'] = array(); $GLOBALS['actions'] = array();
function wp_get_environment_type() { return $GLOBALS['ENV']; }
function is_user_logged_in() { return $GLOBALS['LOGIN']; }
function current_user_can($cap) { return $GLOBALS['CAP'] && $cap === 'edit_pages'; }
function wp_create_nonce($what) { return 'fixed-cli-test-nonce'; }
function check_ajax_referer($action, $query_arg = false, $stop = true) {
    $field = $query_arg ? $query_arg : (isset($_REQUEST['_ajax_nonce']) ? '_ajax_nonce' : '_wpnonce');
    $token = $_REQUEST[$field] ?? null;
    $result = ($action === 'fv_ex2_apollo_sealed' && is_string($token)
        && $token === wp_create_nonce($action)) ? 1 : false;
    if ($action === 'fv_ex2_apollo_sealed' && is_string($token)
        && $token === 'fixed-cli-old-nonce') { $result = 2; }
    if ($stop && $result === false) {
        status_header(403);
        echo '-1';
        exit;
    }
    return $result;
}
function add_shortcode($shortcode, $handler) { $GLOBALS['shortcodes'][$shortcode] = $handler; }
function add_action($action, $handler) { $GLOBALS['actions'][$action] = $handler; }
function admin_url($path) { return 'https://staging.invalid/wp-admin/' . $path; }
function add_query_arg($items, $url) { return $url . '?' . http_build_query($items, '', '&', PHP_QUERY_RFC3986); }
function esc_url($url) { return htmlspecialchars($url, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function nocache_headers() {}
function status_header($code) { fwrite(STDERR, 'STATUS:' . $code); }
$_GET = array('_wpnonce' => $mode === 'badnonce' ? 'wrong' : 'fixed-cli-test-nonce');
$_REQUEST = $_GET;
if ($action === 'download') { $_GET['file'] = $argv[4] ?? ''; }
require $plugin;
if ($action === 'shortcode') { echo fv_ex2_apollo_sealed_shortcode(); }
elseif ($action === 'page') { fv_ex2_apollo_sealed_page(); }
elseif ($action === 'download') { fv_ex2_apollo_sealed_download(); }
elseif ($action === 'registrations') { echo json_encode(array('shortcodes'=>array_keys($GLOBALS['shortcodes']),'actions'=>array_keys($GLOBALS['actions']))); }
else { fwrite(STDERR, 'UNKNOWN_ACTION'); exit(71); }
