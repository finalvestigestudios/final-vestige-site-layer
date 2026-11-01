<?php
/* CLI-only R52 manifest probe. It cannot enqueue or modify WordPress. */
define('ABSPATH', '/tmp/fv-ex2-r52-probe/');
function add_action($hook, $callback, $priority = 10) { }
function add_shortcode($tag, $callback) { }
function esc_url($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }
require dirname(__DIR__) . '/integration/fv-ex2-apollo-suite.php';
$input = json_decode(stream_get_contents(STDIN), true);
if (!is_array($input)) { fwrite(STDERR, "Invalid JSON\n"); exit(2); }
$mode = $input['mode'] ?? 'match';
if ($mode === 'profiles') { echo json_encode(fv_ex2_apollo_desk_profiles(), JSON_UNESCAPED_SLASHES), "\n"; exit(0); }
$dir = $input['dir'] ?? '';
$pins = $input['pins'] ?? array();
if (!is_string($dir) || !is_array($pins)) { fwrite(STDERR, "Invalid path or pins\n"); exit(2); }
echo json_encode(array('matched' => fv_ex2_apollo_match_desk_pins($dir, $pins)), JSON_UNESCAPED_SLASHES), "\n";
