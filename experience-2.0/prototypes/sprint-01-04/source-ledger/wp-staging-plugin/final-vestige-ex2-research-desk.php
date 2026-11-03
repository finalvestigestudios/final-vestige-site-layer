<?php
/**
 * Plugin Name: Final Vestige Experience 2.0 — Research Desk (Staging Candidate)
 * Description: Isolated static-first source-ledger prototype. Not authorized for production deployment.
 * Version: 0.0.3-research
 * Requires PHP: 7.4
 * License: Proprietary research prototype; source-photo credits retained in content.
 */
if (!defined('ABSPATH')) { exit; }

if (!defined('FV_EX2_RD_VERSION')) {
    define('FV_EX2_RD_VERSION', '0.0.3-research');
}

/**
 * WordPress adapter proof-of-concept. This standalone module is intentionally NOT added to the
 * existing Site Layer plugin, not bundled into PR #49, and has no background/admin actions.
 */
function fv_ex2_rd_assets(): void {
    if (!is_singular()) { return; }
    $post = get_post();
    if (!$post || !has_shortcode((string) $post->post_content, 'fv_ex2_research_desk')) { return; }
    wp_enqueue_style(
        'fv-ex2-research-desk',
        plugins_url('assets/source-ledger.css', __FILE__),
        array(),
        FV_EX2_RD_VERSION
    );
    wp_enqueue_script(
        'fv-ex2-research-desk',
        plugins_url('assets/source-ledger.js', __FILE__),
        array(),
        FV_EX2_RD_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'fv_ex2_rd_assets', 20);

function fv_ex2_rd_shortcode($atts = array()): string {
    $path = plugin_dir_path(__FILE__) . 'templates/ledger.html';
    if (!is_readable($path)) {
        return '<p>Research source viewer unavailable. <a href="' . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') . '">Read the original Apollo 1 investigation</a>.</p>';
    }
    $markup = file_get_contents($path);
    if (!is_string($markup) || $markup === '') {
        return '<p><a href="' . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') . '">Read the original Apollo 1 investigation</a>.</p>';
    }
    // Trust boundary: this is a release-reviewed, immutable, bundled file, NOT shortcode input.
    // No user-supplied attributes or remote content are injected into the returned markup.
    return $markup;
}
add_shortcode('fv_ex2_research_desk', 'fv_ex2_rd_shortcode');
