<?php
/**
 * Plugin Name: FV Experience 2.0 Research Desk — R231 Staging Adapter
 * Description: Source-ledger shortcode candidate with nested-block and duplicate-instance safety. NOT FOR PRODUCTION.
 * Version: 0.0.5-r231-source-scope-staging
 * Requires PHP: 7.4
 * License: Proprietary staging candidate; historical sources linked in bundled evidence.
 *
 * MUTUALLY EXCLUSIVE with final-vestige-ex2-research-desk.php and fv-ex2-r230-runtime.php. Never activate together.
 */
if (!defined('ABSPATH')) { exit; }
if (!defined('FV_EX2_R231_VERSION')) { define('FV_EX2_R231_VERSION', '0.0.5-r231-source-scope-staging'); }

function fv_ex2_r231_assets(): void {
    // Register via enqueue; shortcode can be called from nested/reusable/dynamic blocks
    // after wp_enqueue_scripts has finished. No assumptions about post_content.
    wp_enqueue_style('fv-ex2-r231-ledger', plugins_url('assets/source-ledger.css', __FILE__), array(), FV_EX2_R231_VERSION);
    wp_enqueue_script('fv-ex2-r231-ledger', plugins_url('assets/source-ledger-r231.js', __FILE__), array(), FV_EX2_R231_VERSION, true);
}

function fv_ex2_r231_preflight(): void {
    // Fast path: normal top-level shortcodes print stylesheet in <head>.
    if (!is_singular()) { return; }
    $post = get_post();
    if ($post && has_shortcode((string) $post->post_content, 'fv_ex2_research_desk')) {
        fv_ex2_r231_assets();
    }
}
add_action('wp_enqueue_scripts', 'fv_ex2_r231_preflight', 20);

function fv_ex2_r231_fallback(): string {
    return '<p>Research source viewer unavailable. <a href="' . esc_url('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') . '">Read the original Apollo 1 investigation</a>.</p>';
}

function fv_ex2_r231_shortcode($atts = array()): string {
    static $instances = 0;
    static $late_css_emitted = false;
    static $late_js_emitted = false;
    $path = plugin_dir_path(__FILE__) . 'templates/ledger-r231-source-scope.html';
    if (!is_readable($path)) { return fv_ex2_r231_fallback(); }
    $html = file_get_contents($path);
    if (!is_string($html) || trim($html) === '') { return fv_ex2_r231_fallback(); }
    // Pin the reviewed rendered source, not just the approved URL set. This
    // protects labels, photo/technical-proof distinction and the single CTA.
    $git_blob = sha1('blob ' . strlen($html) . "\0" . $html);
    if (!hash_equals('0fd4f9ddadb3473110d2709a52332a78fa4ac04a', $git_blob) || substr_count($html, 'data-fvx-source-scope') !== 3) {
        return fv_ex2_r231_fallback();
    }

    $instances++;
    // The original six-record template uses a constant ID prefix. A second
    // shortcode on the same page otherwise duplicates IDs, labels and ARIA refs.
    // Re-key *all* matching references (id, href, for, aria-labelledby/controls),
    // without rewriting NASA URLs, evidence text, source IDs or editorial prose.
    if ($instances > 1) {
        $html = str_replace('fv-ex2-ledger-apollo1-', 'fv-ex2-ledger-apollo1-copy-' . $instances . '-', $html);
    }

    fv_ex2_r231_assets();
    $resources = '';
    // When the shortcode was introduced after wp_head (e.g. reusable/dynamic
    // pattern), styles enqueued at render time miss the normal head printer.
    // A single external stylesheet link supplies the same approved static CSS.
    if (did_action('wp_head') && !wp_style_is('fv-ex2-r231-ledger', 'done') && !$late_css_emitted) {
        $resources .= '<link rel="stylesheet" href="' . esc_url(plugins_url('assets/source-ledger.css', __FILE__)) . '" />';
        $late_css_emitted = true;
    }
    // Normally JS is printed by WP in the footer. Only recover if a shortcode
    // is rendered *after* footer processing; JS is optional and never required
    // to expose the six records. No inline script, storage, tracking, or fetch.
    if (did_action('wp_footer') && !wp_script_is('fv-ex2-r231-ledger', 'done') && !$late_js_emitted) {
        $resources .= '<script defer src="' . esc_url(plugins_url('assets/source-ledger-r231.js', __FILE__)) . '"></script>';
        $late_js_emitted = true;
    }
    return $resources . $html;
}
add_shortcode('fv_ex2_research_desk', 'fv_ex2_r231_shortcode');
