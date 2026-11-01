<?php
// Deliberately minimal WordPress API lifecycle contract shim. NOT real WordPress.
define('ABSPATH', '/qa-wordpress-stub/');
$GLOBALS['fv_actions'] = array();
$GLOBALS['fv_shortcodes'] = array();
$GLOBALS['fv_assets'] = array();
function add_action($hook, $callback, $priority = 10) { $GLOBALS['fv_actions'][$hook][] = array($callback, $priority); }
function add_shortcode($name, $callback) { $GLOBALS['fv_shortcodes'][$name] = $callback; }
function is_singular() { return getenv('FV_SINGULAR') !== '0'; }
function plugins_url($path, $file) { return '/assets/' . basename($path); }
function plugin_dir_path($file) { return dirname($file) . DIRECTORY_SEPARATOR; }
function esc_url($url) { return htmlspecialchars($url, ENT_QUOTES, 'UTF-8'); }
function wp_enqueue_style($h, $url, $deps, $version) { $GLOBALS['fv_assets']['styles'][$h] = array($url, $version); }
function wp_enqueue_script($h, $url, $deps, $version, $footer) { $GLOBALS['fv_assets']['scripts'][$h] = array($url, $version, $footer); }
require $argv[1];
foreach (($GLOBALS['fv_actions']['wp_enqueue_scripts'] ?? array()) as $handler) { call_user_func($handler[0]); }
$callback = $GLOBALS['fv_shortcodes']['fv_ex2_evidence_atlas'];
$primary = call_user_func($callback);
$secondary = call_user_func($callback);
echo json_encode(array('shortcode_registered'=>true,'assets'=>$GLOBALS['fv_assets'],
  'markup'=>$primary,'duplicate'=>$secondary,'hooks'=>$GLOBALS['fv_actions']['wp_enqueue_scripts'] ?? array()),
  JSON_UNESCAPED_SLASHES|JSON_INVALID_UTF8_SUBSTITUTE);
