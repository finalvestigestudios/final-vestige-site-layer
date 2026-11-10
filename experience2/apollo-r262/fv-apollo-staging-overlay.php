<?php
/**
 * Plugin Name: FV Apollo Experience 2 — Overlay Preview Bridge (STAGING ONLY)
 * Description: Safe opt-in staging adapter for the separately source-sealed R224 Apollo Atlas.
 * Version: 0.1.0-r262
 * Requires PHP: 8.0
 * Not a standalone renderer. Never install publicly before release approval.
 */
if (!defined('ABSPATH')) { exit; }
function fv_apollo_r262_assets_ok(): bool {
    $assets = __DIR__ . '/assets/';
    return is_readable($assets . 'apollo-overlays.css')
        && hash_file('sha256', $assets . 'apollo-overlays.css') === '18115eab49504bc5dc0b59373456b78f590b7816e052046d4379cb4b109cc108'
        && is_readable($assets . 'source-drawer-focus.js')
        && hash_file('sha256', $assets . 'source-drawer-focus.js') === '0f1c8feeecf40c79c0b5e9d41025e7a4fd7806eac92a7d612aed3ecd4aaededa';
}
/** Priority 25 follows source-sealed R224 preflight at 20. No WP writes. */
function fv_apollo_r262_enqueue(): void {
    if (is_admin() || !is_singular()) return;
    if (!function_exists('fv_ex2_r224_assets_ok') || !fv_ex2_r224_assets_ok()) return;
    if (!wp_style_is('fv-apollo-r224', 'enqueued')) return;
    if (!fv_apollo_r262_assets_ok()) return;
    wp_enqueue_style('fv-apollo-r262-overlays',
        plugins_url('assets/apollo-overlays.css', __FILE__),
        array('fv-apollo-r224'), '18115eab4950');
    wp_enqueue_script('fv-apollo-r262-drawer-focus',
        plugins_url('assets/source-drawer-focus.js', __FILE__),
        array(), '0f1c8feeecf4', true);
}
add_action('wp_enqueue_scripts', 'fv_apollo_r262_enqueue', 25);
