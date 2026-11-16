<?php
/**
 * Plugin Name: FV Apollo R406 Research Desk — isolated staging candidate
 * Description: Default-OFF, immutable NASA-ledger integration; NEVER deploy unreviewed.
 * Version: 0.0.1-r406
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

function fv_ex2_r406_expected_blobs(): array {
    return array(
        'templates/ledger.html' => '403d128c57b9bc82dac7c619651689070edef86c',
        'assets/source-ledger.css' => 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
        'assets/research-desk-resilient.css' => '2c99fdeecd4d4245908c0f52f6a679c6f5d7718a',
        'assets/research-desk-r406.js' => 'a925ef792a4f894208f88d8edb3a7b4620b3028f',
    );
}
function fv_ex2_r406_git_blob(string $file): ?string {
    if (!is_file($file) || !is_readable($file)) { return null; }
    $data = file_get_contents($file);
    if (!is_string($data)) { return null; }
    return sha1('blob ' . strlen($data) . "\0" . $data);
}
function fv_ex2_r406_assets_valid(string $root): bool {
    foreach (fv_ex2_r406_expected_blobs() as $name => $expected) {
        if (!hash_equals($expected, fv_ex2_r406_git_blob($root . '/' . $name) ?? '')) { return false; }
    }
    return true;
}
function fv_ex2_r406_authorized(): bool {
    return defined('FV_EX2_R406_ENABLE') && FV_EX2_R406_ENABLE === true
        && defined('FV_EX2_R406_STAGING_PAGE_ID') && (int) FV_EX2_R406_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_EX2_R406_STAGING_PAGE_ID;
}
/** Every desk, including the first, must have unique server IDs; no JS needed. */
function fv_ex2_r406_namespace_markup(string $markup, int $instance): string {
    if ($instance < 1) { throw new InvalidArgumentException('Instance must be positive'); }
    return str_replace('fv-ex2-ledger-apollo1-',
        'fv-ex2-ledger-apollo1-r406-i' . $instance . '-', $markup);
}
function fv_ex2_r406_fallback(): string {
    return '<p>Research Desk unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_ex2_r406_legacy_conflict(): bool {
    return (function_exists('wp_script_is') &&
        (wp_script_is('fv-ex2-research-desk', 'enqueued') || wp_script_is('fv-ex2-research-desk', 'done') ||
         wp_script_is('fv-ex2-r405-access', 'enqueued') || wp_script_is('fv-ex2-r405-access', 'done')))
        || (function_exists('wp_style_is') &&
        (wp_style_is('fv-ex2-research-desk', 'enqueued') || wp_style_is('fv-ex2-research-desk', 'done')));
}
/** Pre-enqueue only on authorized staging page; never mutate WP settings/content. */
function fv_ex2_r406_enqueue(): void {
    $GLOBALS['fv_ex2_r406_ready'] = false;
    if (!fv_ex2_r406_authorized() || !fv_ex2_r406_assets_valid(__DIR__) || fv_ex2_r406_legacy_conflict()) { return; }
    if (!function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script') || !function_exists('plugins_url')) { return; }
    wp_enqueue_style('fv-ex2-r406-core', plugins_url('assets/source-ledger.css', __FILE__), array(), '0.0.1-r406');
    wp_enqueue_style('fv-ex2-r406-access', plugins_url('assets/research-desk-resilient.css', __FILE__), array('fv-ex2-r406-core'), '0.0.1-r406');
    wp_enqueue_script('fv-ex2-r406-access', plugins_url('assets/research-desk-r406.js', __FILE__), array(), '0.0.1-r406', true);
    $GLOBALS['fv_ex2_r406_ready'] = true;
}
function fv_ex2_r406_shortcode($atts = array()): string {
    static $instance = 0;
    if (!fv_ex2_r406_authorized() || empty($GLOBALS['fv_ex2_r406_ready']) ||
        fv_ex2_r406_legacy_conflict() || !fv_ex2_r406_assets_valid(__DIR__)) {
        return fv_ex2_r406_fallback();
    }
    $markup = file_get_contents(__DIR__ . '/templates/ledger.html');
    if (!is_string($markup) || $markup === '') { return fv_ex2_r406_fallback(); }
    $instance++;
    return fv_ex2_r406_namespace_markup($markup, $instance);
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_ex2_r406_enqueue', 99); }
if (function_exists('add_shortcode')) { add_shortcode('fv_ex2_research_desk_r406', 'fv_ex2_r406_shortcode'); }
