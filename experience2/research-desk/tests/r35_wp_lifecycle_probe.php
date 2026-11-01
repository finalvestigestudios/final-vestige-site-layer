<?php
/** Fake WP lifecycle, intentionally NOT WordPress certification.
 * Usage: php r35_wp_lifecycle_probe.php /path/to/plugin.php case_name
 */
if ($argc !== 3) { fwrite(STDERR, "Usage: php probe.php plugin.php case\n"); exit(2); }
$plugin = $argv[1];
$case = $argv[2];
if (!is_file($plugin)) { fwrite(STDERR, 'Missing plugin'); exit(2); }
define('ABSPATH', '/isolated/research-staging/');
$GLOBALS['wp_actions'] = array();
$GLOBALS['wp_shortcodes'] = array();
$GLOBALS['styles'] = array();
$GLOBALS['scripts'] = array();
$GLOBALS['singular'] = ($case !== 'archive');
$GLOBALS['post'] = (object) array('post_content' => ($case === 'direct' ? '[fv_ex2_research_desk]' : '<!-- wp:block {"ref":153} /-->'));
function add_action($name, $func, $priority = 10) { $GLOBALS['wp_actions'][$name] = $func; }
function add_shortcode($name, $func) { $GLOBALS['wp_shortcodes'][$name] = $func; }
function is_singular() { return $GLOBALS['singular']; }
function get_post() { return $GLOBALS['post']; }
function has_shortcode($content, $tag) { return strpos($content, '[' . $tag . ']') !== false; }
function plugins_url($rel, $file) { return 'https://staging.example.test/wp-content/plugins/research-desk/' . $rel; }
function plugin_dir_path($file) { return dirname($file) . '/'; }
function wp_enqueue_style($handle, $url, $deps, $version) { $GLOBALS['styles'][$handle] = array('url' => $url, 'version' => $version); }
function wp_enqueue_script($handle, $url, $deps, $version, $footer) { $GLOBALS['scripts'][$handle] = array('url' => $url, 'version' => $version, 'footer' => $footer); }
function esc_url($url) { return htmlspecialchars($url, ENT_QUOTES, 'UTF-8'); }
require $plugin;
if (!isset($GLOBALS['wp_actions']['wp_enqueue_scripts']) || !isset($GLOBALS['wp_shortcodes']['fv_ex2_research_desk'])) { fwrite(STDERR, 'Missing WP registrations'); exit(1); }
// Important: enqueue (head) before a nested dynamic block renders (content).
($GLOBALS['wp_actions']['wp_enqueue_scripts'])();
$before_render = count($GLOBALS['styles']) === 1 && count($GLOBALS['scripts']) === 1;
$rendered = ($GLOBALS['wp_shortcodes']['fv_ex2_research_desk'])(array('unknown_input' => 'ignored'));
$result = array(
 'case' => $case,
 'singular' => $GLOBALS['singular'],
 'direct_literal_shortcode' => has_shortcode($GLOBALS['post']->post_content, 'fv_ex2_research_desk'),
 'early_css_and_js' => $before_render,
 'styles' => $GLOBALS['styles'],
 'scripts' => $GLOBALS['scripts'],
 'has_static_ledger' => strpos($rendered, 'data-fvx-ledger') !== false,
 'fallback_url' => strpos($rendered, 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') !== false,
 'rendered_sha256' => hash('sha256', $rendered),
 'content_length' => strlen($rendered),
);
echo json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
