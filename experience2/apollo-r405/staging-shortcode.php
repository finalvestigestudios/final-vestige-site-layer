<?php
/**
 * Plugin Name: Final Vestige Apollo Research Desk R405 (Staging Gate Only)
 * Description: Offline-assembled, immutable Research Desk shortcode pilot. Never install without reviewed staging approval.
 * Version: 0.0.1-r405
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/** Git object identities from PR #158 and R404; do not replace with generated fixture hashes. */
function fv_ex2_r405_expected_blobs(): array {
    return array(
        'templates/ledger.html' => '403d128c57b9bc82dac7c619651689070edef86c',
        'assets/source-ledger.css' => 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
        'assets/research-desk-resilient.js' => '4f2d41dc1dc3d5e321b36a422cefd06a0ecd6760',
        'assets/research-desk-resilient.css' => '2c99fdeecd4d4245908c0f52f6a679c6f5d7718a',
    );
}

function fv_ex2_r405_git_blob(string $file): ?string {
    if (!is_file($file) || !is_readable($file)) { return null; }
    $bytes = file_get_contents($file);
    if (!is_string($bytes)) { return null; }
    return sha1('blob ' . strlen($bytes) . "\0" . $bytes);
}

/** Reject absent and modified NASA evidence and style/JS bytes, with no partial enqueue. */
function fv_ex2_r405_assets_valid(string $base): bool {
    foreach (fv_ex2_r405_expected_blobs() as $path => $expected) {
        if (!hash_equals($expected, fv_ex2_r405_git_blob($base . '/' . $path) ?? '')) { return false; }
    }
    return true;
}

/** Staging and explicit founder-approved staging page gate; defaults OFF. */
function fv_ex2_r405_authorized(): bool {
    return defined('FV_EX2_R405_ENABLE') && FV_EX2_R405_ENABLE === true
        && defined('FV_EX2_R405_STAGING_PAGE_ID') && (int) FV_EX2_R405_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_EX2_R405_STAGING_PAGE_ID;
}

/**
 * The reviewed R158 template uses one fixed ID prefix everywhere.
 * Server-side remapping works with no JS, nested shortcodes and repeated blocks.
 */
function fv_ex2_r405_namespace_markup(string $markup, int $instance): string {
    if ($instance <= 1) { return $markup; }
    return str_replace('fv-ex2-ledger-apollo1-', 'fv-ex2-ledger-apollo1-instance-' . $instance . '-', $markup);
}

function fv_ex2_r405_fallback(): string {
    return '<p>Research source viewer unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
}

/**
 * Enqueue on a fixed, approved STAGING page before nested/reusable blocks render.
 * Never enqueue original source-ledger.js alongside the R404 replacement.
 */
function fv_ex2_r405_enqueue(): void {
    $GLOBALS['fv_ex2_r405_ready'] = false;
    if (!fv_ex2_r405_authorized() || !fv_ex2_r405_assets_valid(__DIR__)) { return; }
    if ((function_exists('wp_script_is') && wp_script_is('fv-ex2-research-desk', 'enqueued'))
        || (function_exists('wp_style_is') && wp_style_is('fv-ex2-research-desk', 'enqueued'))) { return; }
    if (!function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script') || !function_exists('plugins_url')) { return; }
    wp_enqueue_style('fv-ex2-r405-core', plugins_url('assets/source-ledger.css', __FILE__), array(), '0.0.1-r405');
    wp_enqueue_style('fv-ex2-r405-access', plugins_url('assets/research-desk-resilient.css', __FILE__), array('fv-ex2-r405-core'), '0.0.1-r405');
    wp_enqueue_script('fv-ex2-r405-access', plugins_url('assets/research-desk-resilient.js', __FILE__), array(), '0.0.1-r405', true);
    $GLOBALS['fv_ex2_r405_ready'] = true;
}

function fv_ex2_r405_shortcode($atts = array()): string {
    static $instance = 0;
    if (!fv_ex2_r405_authorized() || empty($GLOBALS['fv_ex2_r405_ready'])) { return fv_ex2_r405_fallback(); }
    // Recheck after head render: edits between enqueue and shortcode must not pass.
    if (!fv_ex2_r405_assets_valid(__DIR__)) { return fv_ex2_r405_fallback(); }
    $markup = file_get_contents(__DIR__ . '/templates/ledger.html');
    if (!is_string($markup) || $markup === '') { return fv_ex2_r405_fallback(); }
    $instance++;
    return fv_ex2_r405_namespace_markup($markup, $instance);
}

if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_ex2_r405_enqueue', 99); }
if (function_exists('add_shortcode')) { add_shortcode('fv_ex2_research_desk_r405', 'fv_ex2_r405_shortcode'); }
