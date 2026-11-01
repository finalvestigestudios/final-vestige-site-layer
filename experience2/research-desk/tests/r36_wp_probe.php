<?php
/**
 * Isolated WordPress-function test double, NOT an installed WordPress test.
 * Run: php r36_wp_probe.php /absolute/path/to/research-desk-plugin.php
 * The production NASA ledger template is read from the adjacent templates folder.
 */
if ($argc !== 2 || !is_readable($argv[1])) { fwrite(STDERR, "Expected readable plugin filename\n"); exit(2); }
define('ABSPATH', '/isolated/apollo-r36/');
$GLOBALS['actions'] = array(); $GLOBALS['shortcodes'] = array();
function add_action($tag, $cb, $priority=10) { $GLOBALS['actions'][$tag]=$cb; }
function add_shortcode($tag, $cb) { $GLOBALS['shortcodes'][$tag]=$cb; }
function is_singular() { return true; }
function wp_enqueue_style(...$args) {}
function wp_enqueue_script(...$args) {}
function plugins_url($rel, $file) { return 'https://staging.example.test/' . $rel; }
function plugin_dir_path($file) { return dirname($file) . '/'; }
function esc_url($str) { return htmlspecialchars($str, ENT_QUOTES, 'UTF-8'); }
require $argv[1];
$cb=$GLOBALS['shortcodes']['fv_ex2_research_desk'] ?? null;
if (!is_callable($cb)) { fwrite(STDERR, "Research Desk shortcode not registered\n"); exit(1); }
$out=array();
for ($i=0;$i<3;$i++) $out[]=$cb(array('unsafe'=>'must-not-render'));
echo json_encode(array('html'=>$out), JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR);
