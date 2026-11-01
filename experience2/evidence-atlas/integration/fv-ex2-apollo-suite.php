<?php
/**
 * Plugin Name: Final Vestige — Apollo Research Suite (STAGING ONLY)
 * Description: Fail-closed, exact-source Research Desk + Evidence Atlas co-host shortcode; no CMS writes.
 * Version: 0.0.51-staging
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
if (!defined('FV_EX2_APOLLO_SUITE_VERSION')) { define('FV_EX2_APOLLO_SUITE_VERSION', '0.0.51-staging'); }

/** Git *blob* SHA-1 (not the SHA-1 of bare file bytes). */
function fv_ex2_apollo_git_blob(string $bytes): string {
    return sha1('blob ' . strlen($bytes) . "\0" . $bytes);
}

/** Only exact, source-reviewed PR #158 files are admitted. Do not touch that plugin's branch. */
function fv_ex2_apollo_verified_desk(): ?string {
    if (!function_exists('fv_ex2_rd_shortcode') || !function_exists('fv_ex2_atlas_shortcode')) { return null; }
    $origin = (new ReflectionFunction('fv_ex2_rd_shortcode'))->getFileName();
    if (!is_string($origin) || basename($origin) !== 'final-vestige-ex2-research-desk.php') { return null; }
    $dir = dirname($origin);
    $pins = array(
        'final-vestige-ex2-research-desk.php' => 'd1879a90101b5475990132369178f42743f4b57c',
        'templates/ledger.html' => '403d128c57b9bc82dac7c619651689070edef86c',
        'assets/source-ledger.css' => 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
        'assets/source-ledger.js' => '32e757cc4dc8708397ff65ac21e89dd319781d78',
    );
    foreach ($pins as $relative => $expected) {
        $path = $dir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
        if (!is_file($path) || !is_readable($path)) { return null; }
        $data = file_get_contents($path);
        if (!is_string($data) || !hash_equals($expected, fv_ex2_apollo_git_blob($data))) { return null; }
    }
    return $origin;
}

/** Explicit enqueue fixes PR #158's top-level-post-only asset assumption for nested shortcodes. */
function fv_ex2_apollo_suite_enqueue(): bool {
    $origin = fv_ex2_apollo_verified_desk();
    if ($origin === null) { return false; }
    wp_enqueue_style('fv-ex2-research-desk', plugins_url('assets/source-ledger.css', $origin), array(), FV_EX2_RD_VERSION);
    wp_enqueue_script('fv-ex2-research-desk', plugins_url('assets/source-ledger.js', $origin), array(), FV_EX2_RD_VERSION, true);
    wp_enqueue_style('fv-ex2-apollo-suite', plugins_url('apollo-suite.css', __FILE__), array(), FV_EX2_APOLLO_SUITE_VERSION);
    return true;
}
function fv_ex2_apollo_suite_pre_enqueue(): void {
    if (!is_singular()) { return; }
    $post = get_queried_object();
    if ($post instanceof WP_Post && is_string($post->post_content)
        && has_shortcode($post->post_content, 'fv_ex2_apollo_suite')) {
        fv_ex2_apollo_suite_enqueue();
    }
}
add_action('wp_enqueue_scripts', 'fv_ex2_apollo_suite_pre_enqueue', 22);

function fv_ex2_apollo_suite_fallback(): string {
    return '<p class="fv-ex2-apollo-suite-fallback">Research components are unavailable. <a href="'
        . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')
        . '">Read the original Apollo 1 investigation</a>.</p>';
}

/** No shortcode attributes or remote data. Renders both existing components unchanged. */
function fv_ex2_apollo_suite_shortcode($atts = array()): string {
    static $rendered = false;
    if ($rendered) {
        return '<p class="fv-ex2-apollo-suite-duplicate">Research suite already appears on this page. <a href="#fv-ex2-apollo-suite-heading">Return to research sources</a>.</p>';
    }
    if (fv_ex2_apollo_verified_desk() === null || !function_exists('shortcode_exists')
        || !shortcode_exists('fv_ex2_research_desk') || !shortcode_exists('fv_ex2_evidence_atlas')) {
        return fv_ex2_apollo_suite_fallback();
    }
    $desk = fv_ex2_rd_shortcode();
    $atlas = fv_ex2_atlas_shortcode();
    $markup = fv_ex2_apollo_suite_markup($desk, $atlas);
    if ($markup === null) { return fv_ex2_apollo_suite_fallback(); }
    $rendered = true;
    fv_ex2_apollo_suite_enqueue();
    return $markup;
}

/** Deterministic, side-effect-free HTML assembly, separately unit-testable. */
function fv_ex2_apollo_suite_markup(string $desk, string $atlas): ?string {
    // Fail closed if either source collection is absent or repeated.
    if (substr_count($desk, 'data-fvx-record ') !== 6 || substr_count($desk, 'data-fvx-ledger') !== 1
        || substr_count($atlas, 'data-fva-record ') !== 6 || substr_count($atlas, 'data-fva-atlas') !== 1) {
        return null;
    }
    return '<section class="fv-ex2-apollo-suite" aria-labelledby="fv-ex2-apollo-suite-heading">'
        . '<header class="fv-ex2-apollo-suite__head"><p>FINAL VESTIGE / EVIDENCE, NOT SPECULATION</p>'
        . '<h2 id="fv-ex2-apollo-suite-heading">Apollo 1: the research sources</h2>'
        . '<p>Six documented findings and six NASA photographic-source references. The dates of the photographs are not an event timeline; no image-use rights are asserted.</p>'
        . '<p class="fv-ex2-apollo-suite__provenance">Source custody notice: record 01 uses an unconfirmed S67-19766 catalog-to-photo association; the linked NASA page does not state the catalog number. See its source notes.</p>'
        . '<nav aria-label="Apollo research sections"><a href="#fv-ex2-ledger-apollo1-title">Review Research Desk</a>'
        . '<a href="#fva-title">Inspect photographic Evidence Atlas</a></nav></header>'
        . $desk . $atlas . '</section>';
}
add_shortcode('fv_ex2_apollo_suite', 'fv_ex2_apollo_suite_shortcode');
