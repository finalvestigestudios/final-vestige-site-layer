<?php
/**
 * Plugin Name: Final Vestige Experience 2 — Apollo casefile (STAGING ONLY)
 * Description: Integrity-checked, source-first Apollo Research Desk/Chronology/Atlas shortcode. Do not activate on production.
 * Version: 0.1.0-staging
 * License: Proprietary — Final Vestige Studios
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/** Only the vetted deterministic source-control outputs may be served. */
function fv_ex2_apollo_bridge_valid_manifest() {
    $root = plugin_dir_path(__FILE__) . 'generated/';
    $manifest_path = $root . 'manifest.json';
    if (!is_file($manifest_path)) { return false; }
    $manifest = json_decode(file_get_contents($manifest_path), true);
    if (!is_array($manifest) || ($manifest['schema_version'] ?? null) !== 1 ||
        ($manifest['status'] ?? '') !== 'STAGING_ONLY_UNREVIEWED_FOR_PUBLICATION') {
        return false;
    }
    // Never serve a bridge built from a different upstream revision on a real site.
    // The CLI-only test override is expressly prohibited in HTTP/WordPress requests.
    if (($manifest['source_matches_pr215'] ?? false) !== true &&
        !(PHP_SAPI === 'cli' && defined('FV_EX2_BRIDGE_TEST_FIXTURE') && FV_EX2_BRIDGE_TEST_FIXTURE === true)) {
        return false;
    }
    $required = array('fragment.html', 'apollo.css', 'apollo.js',
        'evidence-export.csv', 'evidence-export.json',
        'response-export.csv', 'response-export.json');
    $hashes = $manifest['outputs_sha256'] ?? null;
    if (!is_array($hashes) || count($hashes) !== count($required)) { return false; }
    foreach ($required as $file) {
        $expected = $hashes[$file] ?? null;
        if (!is_string($expected) || !preg_match('/^[a-f0-9]{64}$/D', $expected)) { return false; }
        $file_path = $root . $file;
        if (!is_file($file_path) || !hash_equals($expected, hash_file('sha256', $file_path))) {
            return false;
        }
    }
    return $manifest;
}

/**
 * Shortcode: [fv_ex2_apollo_casefile].
 * No WordPress database writes; no remote fetches; no file uploads.
 * Self-hosted stylesheet/script URLs work even when shortcode executes from a
 * dynamic template/reusable block after wp_head. A staging CSP must permit
 * same-origin CSS and JS. Assets and HTML are checked BEFORE external links.
 */
function fv_ex2_apollo_casefile_shortcode($attrs = array()) {
    static $rendered = false;
    $fallback_url = esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/');
    $fallback = '<p class="fv-ex2-apollo-unavailable">Apollo Research Desk staging component unavailable. '
        . '<a href="' . $fallback_url . '">Read the original documented investigation</a>.</p>';
    if ($rendered) {
        return '<p class="fv-ex2-apollo-repeat"><a href="#fv-ex2-apollo-top">Go to the Apollo Research Desk above</a>.</p>';
    }
    if (!fv_ex2_apollo_bridge_valid_manifest()) { return $fallback; }
    $fragment = file_get_contents(plugin_dir_path(__FILE__) . 'generated/fragment.html');
    if (!is_string($fragment) || strpos($fragment, '{{FV_EX2_ASSET_BASE}}') === false) {
        return $fallback;
    }
    $base = plugin_dir_url(__FILE__) . 'generated/';
    // URLs here are supplied by WordPress, not by user content. No external/CDN links.
    $fragment = str_replace('{{FV_EX2_ASSET_BASE}}/', esc_url($base), $fragment);
    $css_url = esc_url($base . 'apollo.css');
    $js_url = esc_url($base . 'apollo.js');
    $rendered = true;
    return '<link rel="stylesheet" href="' . $css_url . '" media="all" data-fv-ex2-staging-style>'
        . '<section class="fv-ex2-apollo" aria-label="Apollo 1 evidence investigation">'
        . $fragment . '</section>'
        . '<script defer src="' . $js_url . '" data-fv-ex2-staging-script></script>';
}
add_shortcode('fv_ex2_apollo_casefile', 'fv_ex2_apollo_casefile_shortcode');
