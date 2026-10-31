<?php
/** Deterministic CLI-only WordPress function stubs; NOT a WordPress installation. */
define('ABSPATH', '/mock/wp/');
// CLI-only fixture override: the supplied offline response files predate PR #215.
define('FV_EX2_BRIDGE_TEST_FIXTURE', true);
$GLOBALS['shortcodes'] = array();
function add_shortcode($name, $callback) { $GLOBALS['shortcodes'][$name] = $callback; }
function plugin_dir_path($path) { return dirname($path) . '/'; }
function plugin_dir_url($path) { return 'https://staging.invalid/wp-content/plugins/fv-ex2-apollo-casefile/'; }
function esc_url($value) { return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
require dirname(__DIR__) . '/fv-ex2-apollo-casefile.php';
$callback = $GLOBALS['shortcodes']['fv_ex2_apollo_casefile'];
$first = $callback();
$second = $callback();
$mode = $argv[1] ?? 'html';
if ($mode === 'html') { echo $first; }
elseif ($mode === 'once') {
    echo json_encode(array('first_bytes' => strlen($first),
        'second_bytes' => strlen($second),
        'first_has_sources' => strpos($first, 'id="documentary-trails"') !== false,
        'second_is_anchor' => strpos($second, 'href="#fv-ex2-apollo-top"') !== false,
        'no_remote_css' => strpos($first, 'https://staging.invalid/wp-content/plugins/') !== false,
        'asset_base_replaced' => strpos($first, '{{FV_EX2_ASSET_BASE}}') === false,
    ), JSON_PRETTY_PRINT);
} else { exit(2); }
