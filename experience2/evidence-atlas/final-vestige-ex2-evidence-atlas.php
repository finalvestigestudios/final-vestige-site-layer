<?php
/**
 * Plugin Name: Final Vestige — Apollo Evidence Atlas (STAGING ONLY)
 * Description: NASA-custody source-reference gallery; not approved for production.
 * Version: 0.0.58-staging
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
if (!defined('FV_EX2_ATLAS_VERSION')) { define('FV_EX2_ATLAS_VERSION', '0.0.58-staging'); }
// R72 reviewed source-custody HTML fragment: six citation-copy buttons now
// satisfy visible-first accessible names. SHA must match exact compiled HTML.
if (!defined('FV_EX2_ATLAS_TEMPLATE_SHA256')) { define('FV_EX2_ATLAS_TEMPLATE_SHA256', 'f2cf346ab5801729fada99643168be7878d9f83237c038e3f9dd638d49613250'); }

/** Register once. Preload for a top-level shortcode; dynamically rendered shortcodes
 * enqueue in the callback, so reusable blocks and template parts are not excluded.
 * Late-rendered blocks can cause footer CSS / flash of unstyled content until WP
 * prints late styles; validate in authentic Assembler/WordPress before approval.
 */
function fv_ex2_atlas_enqueue_assets(): void {
    wp_enqueue_style('fv-ex2-evidence-atlas');
    wp_enqueue_script('fv-ex2-evidence-atlas');
}
function fv_ex2_atlas_register_assets(): void {
    wp_register_style('fv-ex2-evidence-atlas', plugins_url('assets/atlas.css', __FILE__), array(), FV_EX2_ATLAS_VERSION);
    wp_register_script('fv-ex2-evidence-atlas', plugins_url('assets/atlas.js', __FILE__), array(), FV_EX2_ATLAS_VERSION, true);
    if (!is_singular()) { return; }
    $post = get_queried_object();
    if ($post instanceof WP_Post && is_string($post->post_content)
        && has_shortcode($post->post_content, 'fv_ex2_evidence_atlas')) {
        fv_ex2_atlas_enqueue_assets();
    }
}
add_action('wp_enqueue_scripts', 'fv_ex2_atlas_register_assets', 20);

function fv_ex2_atlas_fallback(): string {
    return '<p class="fv-ex2-atlas-fallback">Evidence Atlas is unavailable. <a href="' . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') . '">Read the Apollo 1 investigation</a>.</p>';
}

/** Only compiled, source-reviewed local markup; no shortcode attributes or remote input. */
function fv_ex2_atlas_shortcode($atts = array()): string {
    static $rendered = false;
    if ($rendered) {
        // The underlying R39 JS supports a single Atlas root. Never silently duplicate IDs.
        return '<p class="fv-ex2-atlas-duplicate">The Atlas is already on this page. <a href="#fva-title">Jump to its evidence records</a>.</p>';
    }
    $path = plugin_dir_path(__FILE__) . 'templates/atlas-fragment.html';
    if (!is_readable($path)) { return fv_ex2_atlas_fallback(); }
    $markup = file_get_contents($path);
    if (!is_string($markup) || substr_count($markup, 'data-fva-record ') !== 6
        || strpos($markup, 'data-fva-atlas') === false
        || strpos($markup, '<script') !== false || strpos($markup, '<img') !== false
        || !hash_equals(FV_EX2_ATLAS_TEMPLATE_SHA256, hash('sha256', $markup))) {
        return fv_ex2_atlas_fallback();
    }
    $rendered = true;
    fv_ex2_atlas_enqueue_assets();
    return $markup;
}
add_shortcode('fv_ex2_evidence_atlas', 'fv_ex2_atlas_shortcode');
