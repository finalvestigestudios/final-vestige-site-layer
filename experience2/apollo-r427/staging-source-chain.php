<?php
/**
 * FV Apollo Source Chain R427: opt-in staging adapter for reviewed R426, never self-activating.
 * Reuses exactly the reviewed Evidence Atlas implementation; adds source/rights custody context.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R427_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R427_FILES = [
    'staging-source-comparison.php' => '36ecba01c84d13bf2546d0bd650e9f95ac50d7d9',
    'assets/source-comparison.css' => 'e76decc769e811a59f71c1cf459478d747676eb3',
];
function fv_r427_escape(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r427_blob(string $s): string { return sha1('blob ' . strlen($s) . "\0" . $s); }
function fv_r427_fallback(): string {
    return '<p class="fv-r427-fallback">Source-chain research viewer unavailable. <a href="' . FV_R427_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r427_allowed(): bool {
    return defined('FV_R427_ENABLED') && FV_R427_ENABLED === true
        && defined('FV_R427_STAGING_PAGE_ID') && is_int(FV_R427_STAGING_PAGE_ID)
        && FV_R427_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && get_queried_object_id() === FV_R427_STAGING_PAGE_ID;
}
/** No remote fetch, inherited images, external scripts, dynamic user parameters or editable source. */
function fv_r427_upstream_root(): ?string {
    if (!defined('FV_R427_UPSTREAM_ROOT') || !is_string(FV_R427_UPSTREAM_ROOT)
        || FV_R427_UPSTREAM_ROOT === '' || is_link(FV_R427_UPSTREAM_ROOT)) return null;
    $root = realpath(FV_R427_UPSTREAM_ROOT);
    return ($root && is_dir($root)) ? $root : null;
}
function fv_r427_valid_upstream(?string $root): bool {
    if ($root === null || !is_dir($root)) return false;
    foreach (FV_R427_FILES as $relative => $expected) {
        $requested = $root . DIRECTORY_SEPARATOR . $relative;
        if (is_link($requested) || !is_file($requested) || !is_readable($requested)) return false;
        $actual = realpath($requested);
        if ($actual === false || strncmp($actual, $root . DIRECTORY_SEPARATOR, strlen($root) + 1) !== 0) return false;
        $bytes = file_get_contents($actual);
        if (!is_string($bytes) || !hash_equals($expected, fv_r427_blob($bytes))) return false;
    }
    return true;
}
function fv_r427_verified_load(string $root): bool {
    if (!fv_r427_valid_upstream($root)) return false;
    if (isset($GLOBALS['fv_r427_loaded_root'])) {
        return $GLOBALS['fv_r427_loaded_root'] === $root && function_exists('fv_r426_render');
    }
    // Refuse to adopt a previously loaded implementation whose provenance is unknown.
    if (function_exists('fv_r426_render')) return false;
    require_once $root . '/staging-source-comparison.php';
    if (!function_exists('fv_r426_render')) return false;
    $GLOBALS['fv_r427_loaded_root'] = $root;
    return true;
}
function fv_r427_shortcode(): string {
    if (!fv_r427_allowed()) return fv_r427_fallback();
    $root = fv_r427_upstream_root();
    if ($root === null || !fv_r427_verified_load($root)) return fv_r427_fallback();
    $id = ($GLOBALS['fv_r426_instances'] ?? 0) + 1;
    if (!is_int($id) || $id < 1 || $id > 100) return fv_r427_fallback();
    $GLOBALS['fv_r426_instances'] = $id;
    $markup = fv_r426_render($id);
    if (substr_count($markup, FV_R427_ARTICLE) !== 1 || substr_count($markup, '<details>') !== 6) return fv_r427_fallback();
    $key = 'fv-r427-' . $id;
    $context = '<aside class="fv-r427__context" aria-labelledby="' . $key . '-title">'
      . '<p class="fv-r427__eyebrow">RESEARCH DESK / SOURCE CUSTODY / STAGING</p>'
      . '<h2 id="' . $key . '-title">Claims require records, not just adjacent photographs.</h2>'
      . '<p>In the gallery below, dates describe the NASA photograph or later museum exhibit. Historical conclusions come from separate written research and must be interpreted with their limits. The original ignition initiator was not conclusively established.</p>'
      . '<p>No original NASA media are embedded here or licensed for resale. <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Inspect the Apollo 204 Review Board</a>. NASA does not endorse Final Vestige.</p>'
      . '</aside>';
    return '<div class="fv-r427" data-fv-r427>' . $context . $markup . '</div>';
}
function fv_r427_enqueue(): void {
    if (!fv_r427_allowed()) return;
    $root = fv_r427_upstream_root();
    if ($root === null || !fv_r427_valid_upstream($root)) return;
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) return;
    wp_enqueue_style('fv-r426-comparison', plugins_url('assets/source-comparison.css', $root . '/staging-source-comparison.php'), [], '0.0.1-r426');
    wp_enqueue_style('fv-r427-source-chain', plugins_url('assets/source-chain.css', __FILE__), ['fv-r426-comparison'], '0.0.1-r427');
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_source_chain_r427', 'fv_r427_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r427_enqueue', 20);
