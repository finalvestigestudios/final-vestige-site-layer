<?php
// WordPress function shim ONLY. No installed WordPress, user data or network.
define('ABSPATH', '/mock/');
class WP_Post { public $post_content = '[fv_ex2_apollo_atlas]'; }
function plugin_dir_path($file) { return dirname($file) . '/'; }
function plugins_url($file, $plugin) { return 'https://example.test/plugin/' . $file; }
function wp_enqueue_style(...$args) { $GLOBALS['styles'][$args[0]] = true; }
function wp_enqueue_script(...$args) { $GLOBALS['scripts'][$args[0]] = true; }
function wp_style_is($handle, $what) { return isset($GLOBALS['styles'][$handle]); }
function did_action($hook) { return 0; }
function add_action(...$args) { }
function add_shortcode(...$args) { }
function is_admin() { return false; }
function is_singular() { return true; }
function has_shortcode($content, $name) { return strpos($content, '['.$name) !== false; }
function get_queried_object() { return new WP_Post(); }
function parse_blocks($content) { return array(); }
function get_post($id=null) { return new WP_Post(); }
if ($argc < 3) { exit(2); }
parse_str($argv[2], $_GET);
require $argv[1];
$fn = str_contains(basename($argv[1]), 'r189') ? 'fv_ex2_r189_render' : 'fv_ex2_r188_render';
echo $fn();
