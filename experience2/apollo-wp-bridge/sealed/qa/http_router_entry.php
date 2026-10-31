<?php
/** Test-only PHP built-in server router. It cannot expose unpublished static source. */
if (PHP_SAPI !== 'cli-server' || !isset($_SERVER['REMOTE_ADDR']) || $_SERVER['REMOTE_ADDR'] !== '127.0.0.1') {
    http_response_code(403); exit;
}
$plugin = getenv('FV_TEST_APOLLO_PLUGIN');
if (!$plugin || !is_file($plugin)) { http_response_code(500); exit; }
define('FV_TEST_APOLLO_PLUGIN', $plugin);
require __DIR__ . '/http_wp_router.php';
