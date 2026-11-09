<?php
/** R238 WordPress-function-simulator smoke, NOT installed WordPress acceptance. */
if ($argc !== 2) { fwrite(STDERR, "Usage: php r238_php_smoke.php <generated-staging-dir>\n"); exit(2); }
$root = realpath($argv[1]);
if ($root === false) { fwrite(STDERR, "Missing stage\n"); exit(2); }
define('ABSPATH', $root);
function plugin_dir_path($file) { return dirname($file) . DIRECTORY_SEPARATOR; }
function add_action($name, $callback, $priority = 10) { return true; }
function add_shortcode($tag, $callback) { return true; }
function wp_style_is($name, $mode) { return true; }
function did_action($name) { return 1; }
function wp_enqueue_style($handle, $src, $deps = array(), $ver = null) { return true; }
function plugins_url($name, $file) { return '/staging/' . $name; }
require $root . '/fv-ex2-apollo-r224.php';
function ok($cond, $message) { if (!$cond) throw new RuntimeException($message); }
ok(fv_ex2_r224_assets_ok(), 'asset integrity should pass');
$html = fv_ex2_r224_render();
ok($html === file_get_contents($root.'/templates/atlas-fragment.html'), 'render source differs');
ok(substr_count($html, 'class="cta"') === 1, 'exactly one free CTA required');
$second = fv_ex2_r224_render();
ok(strpos($second, 'Read the original investigation') !== false, 'second shortcode should fail open');
$css = $root . '/assets/atlas-scoped.css';
$original = file_get_contents($css);
try {
    file_put_contents($css, $original . "\n/* unauthorized mutation */\n");
    ok(!fv_ex2_r224_assets_ok(), 'modified CSS must be rejected');
    ok(strpos(fv_ex2_r224_fallback(), 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') !== false,
        'fallback must link to free historical article');
} finally {
    file_put_contents($css, $original);
}
ok(fv_ex2_r224_assets_ok(), 'restored asset integrity should pass');
echo json_encode(array('source' => 'staging-r238', 'php_assets' => 'PASS',
 'duplicate_shortcode_fallback' => 'PASS', 'corrupt_css_rejection' => 'PASS',
 'original_article_fallback' => 'PASS', 'installed_wordpress' => 'NOT_TESTED'), JSON_UNESCAPED_SLASHES) . "\n";
