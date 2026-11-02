<?php
/**
 * Plugin Name: Final Vestige — Apollo Research Suite (STAGING ONLY)
 * Description: Fail-closed, exact-source Research Desk + Evidence Atlas co-host shortcode; no CMS writes.
 * Version: 0.0.66-staging
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
if (!defined('FV_EX2_APOLLO_SUITE_VERSION')) { define('FV_EX2_APOLLO_SUITE_VERSION', '0.0.66-staging'); }

/** Git *blob* SHA-1 (not the SHA-1 of bare file bytes). */
function fv_ex2_apollo_git_blob(string $bytes): string {
    return sha1('blob ' . strlen($bytes) . "\0" . $bytes);
}

/**
 * Immutable, mutually exclusive release profiles. PR #158 is the original pilot;
 * R38 is the later custody/search version already present in the R51 ancestry.
 * Never combine file hashes from different profiles or accept arbitrary upgrades.
 */
function fv_ex2_apollo_desk_profiles(): array {
    return array(
        'pr158-original' => array(
            'final-vestige-ex2-research-desk.php' => 'd1879a90101b5475990132369178f42743f4b57c',
            'templates/ledger.html' => '403d128c57b9bc82dac7c619651689070edef86c',
            'assets/source-ledger.css' => 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
            'assets/source-ledger.js' => '32e757cc4dc8708397ff65ac21e89dd319781d78',
        ),
        'r38-custody-search' => array(
            'final-vestige-ex2-research-desk.php' => '44a43c63ba262de4193295563f5762df6e731077',
            'templates/ledger.html' => '4842afb84b4c993cfc4861ce7f5a7a4d7b451871',
            'assets/source-ledger.css' => '7b0972fc3a920ded08f9783fddcfc9c609c7ff06',
            'assets/source-ledger.js' => '57f4a639d4c37fc4355b10fe7dec085bf87c6eb7',
            'sources/R37_PHOTO_CUSTODY_CROSSWALK.json' => 'ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea',
        ),
    );
}

/** Check a whole pinned profile, not an independently mixed list of approved files. */
function fv_ex2_apollo_match_desk_pins(string $dir, array $pins): bool {
    if (count($pins) < 4) { return false; }
    foreach ($pins as $relative => $expected) {
        if (!is_string($relative) || !preg_match('~^[a-zA-Z0-9_./-]+$~D', $relative)
            || fv_ex2_apollo_unsafe_relative($relative) || !is_string($expected)
            || !preg_match('/^[0-9a-f]{40}$/D', $expected)) { return false; }
        $path = $dir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
        if (!is_file($path) || !is_readable($path)) { return false; }
        $bytes = file_get_contents($path);
        if (!is_string($bytes) || !hash_equals($expected, fv_ex2_apollo_git_blob($bytes))) { return false; }
    }
    return true;
}
function fv_ex2_apollo_unsafe_relative(string $relative): bool {
    foreach (explode('/', $relative) as $segment) { if ($segment === '..' || $segment === '.') { return true; } }
    return false;
}

/** Admit only a complete, exact original PR #158 or R38 Research Desk plugin. */
function fv_ex2_apollo_verified_desk(): ?string {
    if (!function_exists('fv_ex2_rd_shortcode') || !function_exists('fv_ex2_atlas_shortcode')) { return null; }
    $origin = (new ReflectionFunction('fv_ex2_rd_shortcode'))->getFileName();
    if (!is_string($origin) || basename($origin) !== 'final-vestige-ex2-research-desk.php') { return null; }
    foreach (fv_ex2_apollo_desk_profiles() as $pins) {
        if (fv_ex2_apollo_match_desk_pins(dirname($origin), $pins)) { return $origin; }
    }
    return null;
}

/**
 * Reviewed Atlas *runtime* files. The generated HTML template is validated
 * against the constant defined by the exact pinned Atlas PHP plugin itself.
 * This is a custody / accidental-drift gate, NOT a hostile-server security boundary.
 * Keep the Atlas and Research Desk profiles mutually independent.
 */
function fv_ex2_apollo_atlas_runtime_pins(): array {
    return array(
        'final-vestige-ex2-evidence-atlas.php' => '8f5a21b42cbd00acf0e390aaeb22e55f3bb216f8',
        'assets/atlas.css' => '079f2ef9785184a098ec7686f5018a474181031b',
        'assets/atlas.js' => '1bfde47e00abc522f5af0b125c5668f8c7617256',
    );
}
function fv_ex2_apollo_verified_atlas(): ?string {
    if (!function_exists('fv_ex2_atlas_shortcode') || !defined('FV_EX2_ATLAS_TEMPLATE_SHA256')) { return null; }
    $origin = (new ReflectionFunction('fv_ex2_atlas_shortcode'))->getFileName();
    if (!is_string($origin) || basename($origin) !== 'final-vestige-ex2-evidence-atlas.php') { return null; }
    $dir = dirname($origin);
    foreach (fv_ex2_apollo_atlas_runtime_pins() as $relative => $expected) {
        $path = $dir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
        if (!is_file($path) || !is_readable($path)) { return null; }
        $bytes = file_get_contents($path);
        if (!is_string($bytes) || !hash_equals($expected, fv_ex2_apollo_git_blob($bytes))) { return null; }
    }
    $expectedTemplate = FV_EX2_ATLAS_TEMPLATE_SHA256;
    if (!is_string($expectedTemplate) || !preg_match('/^[0-9a-f]{64}$/D', $expectedTemplate)) { return null; }
    $template = $dir . DIRECTORY_SEPARATOR . 'templates/atlas-fragment.html';
    if (!is_file($template) || !is_readable($template)) { return null; }
    $actualTemplate = hash_file('sha256', $template);
    if (!is_string($actualTemplate) || !hash_equals($expectedTemplate, $actualTemplate)) { return null; }
    return $origin;
}

/** Explicit enqueue fixes PR #158's top-level-post-only asset assumption for nested shortcodes. */
function fv_ex2_apollo_suite_enqueue(): bool {
    $origin = fv_ex2_apollo_verified_desk();
    if ($origin === null || fv_ex2_apollo_verified_atlas() === null) { return false; }
    wp_enqueue_style('fv-ex2-research-desk', plugins_url('assets/source-ledger.css', $origin), array(), FV_EX2_RD_VERSION);
    wp_enqueue_script('fv-ex2-research-desk', plugins_url('assets/source-ledger.js', $origin), array(), FV_EX2_RD_VERSION, true);
    wp_enqueue_style('fv-ex2-apollo-suite', plugins_url('apollo-suite.css', __FILE__), array(), FV_EX2_APOLLO_SUITE_VERSION);
    // Important: Atlas registers its assets at priority 20. Enqueue the already-
    // registered handles NOW, before wp_head, for predeclared nested blocks.
    // Otherwise Atlas CSS can arrive only after the shortcode renders.
    if (function_exists('fv_ex2_atlas_enqueue_assets')) {
        fv_ex2_atlas_enqueue_assets();
    }
    return true;
}
/**
 * For a nested Gutenberg/reusable-block/template-part shortcode, the page's raw
 * post_content may not contain the shortcode. An explicitly configured staging
 * page ID preloads assets before wp_head, without site-wide JS/CSS overhead.
 * Define FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS as an array of positive int IDs
 * in PRIVATE staging configuration only. This is not a WordPress setting.
 */
function fv_ex2_apollo_suite_page_opted_in($post): bool {
    if (!($post instanceof WP_Post) || !isset($post->ID) || !is_int($post->ID) || $post->ID < 1) { return false; }
    if (!defined('FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS')) { return false; }
    $ids = FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS;
    if (!is_array($ids)) { return false; }
    foreach ($ids as $id) {
        if (is_int($id) && $id > 0 && $id === $post->ID) { return true; }
    }
    return false;
}
function fv_ex2_apollo_suite_pre_enqueue(): void {
    if (!is_singular()) { return; }
    $post = get_queried_object();
    if ($post instanceof WP_Post &&
        ((is_string($post->post_content) && has_shortcode($post->post_content, 'fv_ex2_apollo_suite'))
         || fv_ex2_apollo_suite_page_opted_in($post))) {
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
    if (fv_ex2_apollo_verified_desk() === null || fv_ex2_apollo_verified_atlas() === null
        || !function_exists('shortcode_exists')
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
