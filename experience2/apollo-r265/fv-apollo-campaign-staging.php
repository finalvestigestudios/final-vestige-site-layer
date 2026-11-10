<?php
/**
 * Plugin Name: FV Apollo Campaign Continuity (STAGING ONLY — DO NOT ACTIVATE)
 * Description: Optional source-gated DOM campaign handoff hints, with unchanged links and no tracking.
 * Version: 0.1.0-r265
 * Requires PHP: 8.0
 */
if (!defined('ABSPATH')) { exit; }
function fv_apollo_r265_assets_ok(): bool {
    $script = __DIR__ . '/assets/campaign-continuity.js';
    return is_readable($script) && hash_file('sha256', $script) === 'afec1e65191d4df1655a557dca70c92d76922799c0c20d5fb14a6c992ad12c3e';
}
function fv_apollo_r265_enqueue(): void {
    if (is_admin() || !is_singular()) return;
    if (!function_exists('fv_ex2_r224_assets_ok') || !fv_ex2_r224_assets_ok()) return;
    if (!function_exists('fv_apollo_r262_assets_ok') || !fv_apollo_r262_assets_ok()) return;
    if (!wp_style_is('fv-apollo-r224', 'enqueued') || !wp_style_is('fv-apollo-r262-overlays', 'enqueued')) return;
    if (!fv_apollo_r265_assets_ok()) return;
    wp_enqueue_script('fv-apollo-r265-campaign', plugins_url('assets/campaign-continuity.js', __FILE__), array(), '0.1.0-r265', true);
}
add_action('wp_enqueue_scripts', 'fv_apollo_r265_enqueue', 30);
