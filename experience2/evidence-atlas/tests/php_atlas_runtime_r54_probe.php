<?php
/* R54 isolated, mutation-resistant fixture probe; no WordPress or network. */
if (!defined('ABSPATH')) { define('ABSPATH', '/tmp/fv-r54-qa/'); }
function add_action($hook, $fn, $priority=10) { return true; }
function add_shortcode($tag, $fn) { return true; }
$dir = getenv('FV_R54_ATLAS_PLUGIN_ROOT');
if (!is_string($dir) || !is_dir($dir)) { fwrite(STDERR, "Exact fixture path required\n"); exit(2); }
require $dir . '/final-vestige-ex2-evidence-atlas.php';
require dirname(__DIR__) . '/integration/fv-ex2-apollo-suite.php';
function r54_admitted() { return fv_ex2_apollo_verified_atlas() !== null; }
function r54_mutate_file($path) {
    $bytes = file_get_contents($path);
    if (!is_string($bytes)) { throw new Exception('Missing fixture ' . $path); }
    try {
        if (file_put_contents($path, $bytes . "\n<!-- R54 drift -->\n") === false) { throw new Exception('write failed'); }
        return !r54_admitted();
    } finally { file_put_contents($path, $bytes); }
}
$results = array();
$results['exact_reviewed_bundle_accepted'] = r54_admitted();
foreach (array('final-vestige-ex2-evidence-atlas.php','assets/atlas.css','assets/atlas.js','templates/atlas-fragment.html') as $relative) {
    $results['drift_rejected_' . $relative] = r54_mutate_file($dir . '/' . $relative);
    $results['recovery_' . $relative] = r54_admitted();
}
$template = $dir . '/templates/atlas-fragment.html';
$hidden = $template . '.r54-hidden';
if (file_exists($hidden)) { throw new Exception('Unsafe fixture state'); }
if (!rename($template, $hidden)) { throw new Exception('Cannot rename fixture'); }
try { $results['missing_template_rejected'] = !r54_admitted(); }
finally { rename($hidden, $template); }
$results['post_missing_template_recovered'] = r54_admitted();
$results['bad_reuse_guard'] = fv_ex2_apollo_suite_enqueue() === false; // Desk is not included.
$results['template_hash_is_exact'] = hash_file('sha256',$template) === FV_EX2_ATLAS_TEMPLATE_SHA256;
$results['pins_are_whole_runtime_files'] = count(fv_ex2_apollo_atlas_runtime_pins()) === 3;
echo json_encode($results, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), "\n";
if (in_array(false, array_values($results), true)) { exit(1); }
