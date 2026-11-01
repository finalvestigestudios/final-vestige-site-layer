<?php
/* CLI-only function probe; NOT an installed WordPress environment. */
define('ABSPATH', '/tmp/fv-r50-test/');
function add_action($name, $fn, $priority = 10) { }
function add_shortcode($name, $fn) { }
function esc_url($value) { return htmlspecialchars($value, ENT_QUOTES, 'UTF-8'); }
require dirname(__DIR__) . '/integration/fv-ex2-apollo-suite.php';
$input = json_decode(stream_get_contents(STDIN), true);
if (!is_array($input)) { fwrite(STDERR, "Invalid probe input\n"); exit(2); }
$desk = (string) ($input['desk'] ?? '');
$atlas = (string) ($input['atlas'] ?? '');
$markup = fv_ex2_apollo_suite_markup($desk, $atlas);
if (($input['mode'] ?? '') === 'markup') { echo $markup === null ? '' : $markup; exit($markup === null ? 3 : 0); }
$result = array(
    'has_markup' => is_string($markup),
    'heading_count' => is_string($markup) ? substr_count($markup, 'id="fv-ex2-apollo-suite-heading"') : 0,
    'research_link' => is_string($markup) && strpos($markup, 'href="#fv-ex2-ledger-apollo1-title"') !== false,
    'atlas_link' => is_string($markup) && strpos($markup, 'href="#fva-title"') !== false,
    'desk_unmodified' => is_string($markup) && strpos($markup, $desk) !== false,
    'atlas_unmodified' => is_string($markup) && strpos($markup, $atlas) !== false,
    'missing_plugin_guard' => fv_ex2_apollo_verified_desk() === null,
    'safe_fallback' => strpos(fv_ex2_apollo_suite_shortcode(), 'Read the original Apollo 1 investigation') !== false,
    'git_blob_hello' => fv_ex2_apollo_git_blob("hello\n"),
);
echo json_encode($result, JSON_UNESCAPED_SLASHES), "\n";
