<?php
// TEST FIXTURE ONLY. Emulates WordPress eligibility functions; not a real WP.
if ($_SERVER['REQUEST_URI'] === '/private-payload.php') {
    require getenv('FV_EX2_MOCK_PLUGIN_ROOT') . '/fv-ex2-private-payload.php';
    return true;
}
define('ABSPATH', '/mock-wordpress/');
if (($_GET['mock_optin'] ?? 'no') === 'yes') { define('FV_EX2_ALLOW_PREVIEW', true); }
function wp_get_environment_type(){return $_GET['mock_env'] ?? 'production';}
function is_user_logged_in(){return ($_GET['mock_login'] ?? 'no') === 'yes';}
function current_user_can($cap){return $cap==='edit_pages' && ($_GET['mock_edit'] ?? 'no') === 'yes';}
function plugin_dir_path($f){ return dirname($f) . DIRECTORY_SEPARATOR; }
function add_shortcode($x,$y){}
function add_action($x,$y){}
function admin_url($p){return 'http://127.0.0.1:18941/'.$p;}
function wp_create_nonce($x){return 'TEST_NONCE';}
function add_query_arg($params,$url){return $url.'?'.http_build_query($params);}
function esc_url($x){return htmlspecialchars($x,ENT_QUOTES);}
function nocache_headers(){header('Cache-Control: private,no-cache,no-store');}
function check_ajax_referer($x){if(($_GET['_wpnonce']??'')!=='TEST_NONCE'){http_response_code(403);exit;}}
function status_header($n){http_response_code($n);}
require getenv('FV_EX2_MOCK_PLUGIN_ROOT') . '/fv-ex2-private-preview.php';
$action = $_GET['action'] ?? 'shortcode';
if($action === 'fv_ex2_private_render') { fv_ex2_private_render(); }
if($action === 'shortcode') { echo fv_ex2_private_shortcode(); return true; }
if($action === 'compose') {$x=fv_ex2_private_compose(); echo $x===null?'INVALID':'VALID'; return true;}
http_response_code(404);
