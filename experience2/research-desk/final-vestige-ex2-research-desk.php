<?php
/**
 * Plugin Name: Final Vestige Experience 2.0 — Research Desk (Staging Candidate)
 * Description: Static-first Research Desk. Isolated staging only; no production authorization.
 * Version: 0.0.4-research
 * Requires PHP: 7.4
 * License: Proprietary research prototype; source-photo credits retained in content.
 */
if (!defined('ABSPATH')) { exit; }
if (!defined('FV_EX2_RD_VERSION')) {
    define('FV_EX2_RD_VERSION', '0.0.4-research');
}

/** Only trusted, bundled files are rendered; never accept shortcode HTML, URLs or code. */
function fv_ex2_rd_enqueue_assets(): void {
    wp_enqueue_style('fv-ex2-research-desk', plugins_url('assets/source-ledger.css', __FILE__), array(), FV_EX2_RD_VERSION);
    wp_enqueue_script('fv-ex2-research-desk', plugins_url('assets/source-ledger.js', __FILE__), array(), FV_EX2_RD_VERSION, true);
}

/** Early enqueue is a performance optimization, not a prerequisite for rendering. */
function fv_ex2_rd_assets(): void {
    if (!is_singular()) { return; }
    $post = get_post();
    if (!$post || !has_shortcode((string) $post->post_content, 'fv_ex2_research_desk')) { return; }
    fv_ex2_rd_enqueue_assets();
}
add_action('wp_enqueue_scripts', 'fv_ex2_rd_assets', 20);

function fv_ex2_rd_shortcode($atts = array()): string {
    static $instances = 0;
    static $fallback_style_emitted = false;
    $original = '<p>Research source viewer unavailable. <a href="' . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') . '">Read the original Apollo 1 investigation</a>.</p>';
    $path = plugin_dir_path(__FILE__) . 'templates/ledger.html';
    if (!is_readable($path)) { return $original; }
    $markup = file_get_contents($path);
    if (!is_string($markup) || trim($markup) === '') { return $original; }

    // R246: only the reviewed six-record NASA ledger may be presented as authoritative.
    // The fixed Git blob ID is pinned to PR #158; edit the source only through editorial review.
    // When source custody fails, show the existing free investigation instead of unverified claims.
    $source_blob = sha1('blob ' . strlen($markup) . "\0" . $markup);
    if (!hash_equals('403d128c57b9bc82dac7c619651689070edef86c', $source_blob)) {
        return $original;
    }

    // Shortcodes may occur in reusable patterns or dynamic blocks after wp_head.
    // Enqueue opportunistically; lack of JS must never conceal the six static records.
    fv_ex2_rd_enqueue_assets();
    ++$instances;
    if ($instances > 1) {
        // The bundled template uses this fixed prefix for all ID references, including
        // labels, aria-controls and aria-labelledby. Scoped JS operates per root.
        $markup = str_replace('fv-ex2-ledger-apollo1-', 'fv-ex2-ledger-apollo1-instance-' . $instances . '-', $markup);
    }

    // A late shortcode can miss wp_head styles. Inline *reviewed local CSS* once,
    // never remote CSS or shortcode/user input. If unavailable, HTML stays readable.
    if (!$fallback_style_emitted && !wp_style_is('fv-ex2-research-desk', 'done')) {
        $css_path = plugin_dir_path(__FILE__) . 'assets/source-ledger.css';
        if (is_readable($css_path)) {
            $css = file_get_contents($css_path);
            if (is_string($css) && $css !== '' && !preg_match('~</?\s*(?:script|style)\b|@import\b|url\s*\(~i', $css)) {
                $markup = '<style id="fv-ex2-research-desk-late-style">' . $css . '</style>' . $markup;
                $fallback_style_emitted = true;
            }
        }
    }
    return $markup;
}
add_shortcode('fv_ex2_research_desk', 'fv_ex2_rd_shortcode');
