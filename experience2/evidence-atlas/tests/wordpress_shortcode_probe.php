<?php
// R42 mock lifecycle only. NOT actual WordPress. Models top-level vs nested render.
define('ABSPATH', '/qa-wordpress-stub/');
$GLOBALS['fv_actions'] = array();
$GLOBALS['fv_shortcodes'] = array();
$GLOBALS['fv_assets'] = array();
$GLOBALS['fv_registered'] = array();
class WP_Post { public $post_content; public function __construct($content) { $this->post_content = $content; } }
function add_action($hook, $callback, $priority = 10) { $GLOBALS['fv_actions'][$hook][] = array($callback, $priority); }
function add_shortcode($name, $callback) { $GLOBALS['fv_shortcodes'][$name] = $callback; }
function is_singular() { return getenv('FV_SINGULAR') !== '0'; }
function get_queried_object() {
    $mode = getenv('FV_POST_MODE') ?: 'direct';
    if ($mode === 'not-post') { return new stdClass(); }
    return new WP_Post($mode === 'direct' ? 'Text [fv_ex2_evidence_atlas] Text' : 'Ordinary page content');
}
function has_shortcode($content,$tag) { return strpos($content, '[' . $tag . ']') !== false; }
function plugins_url($path, $file) { return '/assets/' . basename($path); }
function plugin_dir_path($file) { return dirname($file) . DIRECTORY_SEPARATOR; }
function esc_url($url) { return htmlspecialchars($url, ENT_QUOTES, 'UTF-8'); }
function wp_register_style($h,$url,$deps,$version) { $GLOBALS['fv_registered']['styles'][$h]=array($url,$version); }
function wp_register_script($h,$url,$deps,$version,$footer) { $GLOBALS['fv_registered']['scripts'][$h]=array($url,$version,$footer); }
function wp_enqueue_style($h) { $GLOBALS['fv_assets']['styles'][$h]=$GLOBALS['fv_registered']['styles'][$h] ?? 'NOT_REGISTERED'; }
function wp_enqueue_script($h) { $GLOBALS['fv_assets']['scripts'][$h]=$GLOBALS['fv_registered']['scripts'][$h] ?? 'NOT_REGISTERED'; }
require $argv[1];
foreach (($GLOBALS['fv_actions']['wp_enqueue_scripts'] ?? array()) as $handler) { call_user_func($handler[0]); }
$early = $GLOBALS['fv_assets'];
$callback = $GLOBALS['fv_shortcodes']['fv_ex2_evidence_atlas'];
$primary = getenv('FV_RENDER_SHORTCODE') === '0' ? '' : call_user_func($callback);
$secondary = $primary ? call_user_func($callback) : '';
echo json_encode(array('shortcode_registered'=>true,'registered'=>$GLOBALS['fv_registered'],
 'early_assets'=>$early,'assets'=>$GLOBALS['fv_assets'],'markup'=>$primary,'duplicate'=>$secondary,
 'hooks'=>$GLOBALS['fv_actions']['wp_enqueue_scripts'] ?? array()),
 JSON_UNESCAPED_SLASHES|JSON_INVALID_UTF8_SUBSTITUTE);
