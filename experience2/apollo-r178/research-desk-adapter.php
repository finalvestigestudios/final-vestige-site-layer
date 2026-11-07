<?php
/**
 * Apollo Experience 2.0 R178 — REPLACEMENT CANDIDATE for original PR #158 adapter.
 * NOT a standalone plugin, NOT APPROVED for WordPress installation.
 * Reviewed staging overlay: experience2/research-desk/final-vestige-ex2-research-desk.php
 * Expected companion asset: assets/source-ledger.js from R177 (NEVER co-load original).
 * Preserve original templates/ledger.html or separately reviewed R176 candidate.
 */
if (!defined('ABSPATH')) { exit; }
if (!defined('FV_EX2_RD_VERSION')) { define('FV_EX2_RD_VERSION', '0.0.4-r178-review'); }

// Register early: dynamic blocks can render before wp_enqueue_scripts.
function fv_ex2_rd_register_assets(): void {
    wp_register_style('fv-ex2-research-desk', plugins_url('assets/source-ledger.css', __FILE__), array(), FV_EX2_RD_VERSION);
    wp_register_script('fv-ex2-research-desk', plugins_url('assets/source-ledger.js', __FILE__), array(), FV_EX2_RD_VERSION, true);
}
add_action('init', 'fv_ex2_rd_register_assets', 5);

// Fast-path: original direct post shortcodes get CSS in <head>; other pages pay no enqueue cost.
function fv_ex2_rd_preflight_assets(): void {
    if (!is_singular()) { return; }
    $post = get_post();
    if (!$post || !has_shortcode((string) $post->post_content, 'fv_ex2_research_desk')) { return; }
    fv_ex2_rd_register_assets();
    wp_enqueue_style('fv-ex2-research-desk');
    wp_enqueue_script('fv-ex2-research-desk');
}
add_action('wp_enqueue_scripts', 'fv_ex2_rd_preflight_assets', 20);

function fv_ex2_rd_shortcode($atts = array()): string {
    static $rendered = false;
    if ($rendered) {
        // Repeated shortcodes would duplicate six IDs and aria-controls targets.
        return '<p>Research Desk is already shown on this page. <a href="#fv-ex2-ledger-apollo1-title">Return to the evidence records</a>.</p>';
    }
    $path = plugin_dir_path(__FILE__) . 'templates/ledger.html';
    $fallback = '<p>Research source viewer unavailable. <a href="' . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') . '">Read the original Apollo 1 investigation</a>.</p>';
    if (!is_readable($path)) { return $fallback; }
    $markup = file_get_contents($path);
    if (!is_string($markup) || $markup === '') { return $fallback; }

    // Shortcodes in synced patterns or dynamic blocks are not visible to has_shortcode(post_content).
    // Register lazily if necessary, enqueue only on actual renders, and retain no-JS content.
    fv_ex2_rd_register_assets();
    wp_enqueue_style('fv-ex2-research-desk');
    wp_enqueue_script('fv-ex2-research-desk');
    $prefix = '';
    if (did_action('wp_head') > 0 && !wp_style_is('fv-ex2-research-desk', 'done')) {
        // WordPress normally prints styles in wp_head; a late enqueue alone can be silently
        // omitted in dynamic shortcode renders. The first instance gets a same-origin link.
        // REVIEW REQUIRED: test real theme/CSP, FOUS and caching before staging acceptance.
        $prefix = '<link rel="stylesheet" href="' . esc_url(plugins_url('assets/source-ledger.css', __FILE__)) . '?ver=' . rawurlencode(FV_EX2_RD_VERSION) . '" data-fvx-r178-late-style="1">';
    }
    $rendered = true;
    return $prefix . $markup;
}
add_shortcode('fv_ex2_research_desk', 'fv_ex2_rd_shortcode');
