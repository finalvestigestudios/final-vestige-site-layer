<?php
/**
 * Disposable WordPress Playground ONLY: install and activate an official
 * downloaded Assembler theme ZIP inside a loopback, synthetic fixture site.
 * NEVER mount on, upload to or execute against a hosted/production WordPress.
 */
header('Content-Type: application/json; charset=utf-8');
require_once __DIR__ . '/wp-load.php';
function fv_ex2_assembler_reply($status, $message) {
    http_response_code($status);
    echo wp_json_encode($message);
    exit;
}
function fv_ex2_assembler_fail($why) {
    fv_ex2_assembler_reply(422, array('result'=>'FAIL','reason'=>$why,'release'=>'HOLD'));
}
function fv_ex2_assembler_is_loopback($url) {
    $host = wp_parse_url($url, PHP_URL_HOST);
    return in_array(strtolower((string)$host), array('localhost','127.0.0.1','::1'), true);
}
$marker = __DIR__ . '/wp-content/fv-ex2-synthetic-only.marker';
$token_file = __DIR__ . '/wp-content/fv-ex2-editor-token';
$zip_path = __DIR__ . '/wp-content/fv-ex2-assembler.zip';
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fv_ex2_assembler_fail('POST only');
if (!fv_ex2_assembler_is_loopback('http://' . ($_SERVER['HTTP_HOST'] ?? ''))
    || !fv_ex2_assembler_is_loopback(home_url())) fv_ex2_assembler_fail('Non-loopback WordPress refused');
if (!is_file($marker) || trim((string)file_get_contents($marker)) !== 'SYNTHETIC_TEST_FIXTURE_ONLY')
    fv_ex2_assembler_fail('Synthetic marker missing');
if (!is_file($token_file)) fv_ex2_assembler_fail('Ephemeral token missing');
$expected = trim((string)file_get_contents($token_file));
$received = (string)($_SERVER['HTTP_X_FV_EX2_EDITOR_TOKEN'] ?? '');
if (strlen($expected) !== 64 || !ctype_xdigit($expected) || !hash_equals($expected,$received))
    fv_ex2_assembler_fail('Invalid ephemeral token');
if (($_GET['action'] ?? '') !== 'install') fv_ex2_assembler_fail('Unsupported action');
if (!is_file($zip_path) || filesize($zip_path) < 10000 || filesize($zip_path) > 10000000)
    fv_ex2_assembler_fail('Expected official theme package missing or oversized');
if (is_dir(WP_CONTENT_DIR . '/themes/assembler'))
    fv_ex2_assembler_fail('Theme was already installed: refuse ambiguous state');
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/theme.php';
if (!WP_Filesystem()) fv_ex2_assembler_fail('Disposable filesystem unavailable');
$unzip = unzip_file($zip_path, WP_CONTENT_DIR . '/themes');
if (is_wp_error($unzip)) fv_ex2_assembler_fail('Theme unzip error: ' . $unzip->get_error_code());
$theme = wp_get_theme('assembler');
if (!$theme->exists() || $theme->get_stylesheet() !== 'assembler')
    fv_ex2_assembler_fail('Official Assembler theme folder missing');
switch_theme('assembler');
wp_clean_themes_cache();
if (get_stylesheet() !== 'assembler' || get_template() !== 'assembler')
    fv_ex2_assembler_fail('Assembler theme activation not confirmed');
fv_ex2_assembler_reply(200, array(
    'result'=>'ASSEMBLER_ACTIVE', 'release'=>'HOLD', 'theme'=>'assembler',
    'version'=>(string)wp_get_theme()->get('Version'),
    'source'=>'official WordPress.com Assembler download, isolated local PHP only'
));
