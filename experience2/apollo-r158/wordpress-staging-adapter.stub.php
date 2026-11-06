<?php
/**
 * Plugin Name: FV Apollo R158 Research Desk — Offline Staging ONLY
 * Description: Source-pinned, bundled Apollo Research Desk preview; never install without governed approval.
 * Version: 0.0.1-r158-staging
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Deliberate preview adapter: inline, source-pinned CSS + JS ensure shortcode output
 * works in nested dynamic/reusable blocks after wp_head. No analytics, remote
 * fetches, settings, admin writes, or dependencies on an active theme.
 * Inline assets and a possible restrictive CSP require real WP/theme review.
 */
function fv_apollo_r158_shortcode($atts = array()): string {
    static $rendered = false;
    $investigation = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
    $fallback = '<p>Research Desk preview unavailable. <a href="' . esc_url($investigation) . '">Read the original Apollo 1 investigation</a>.</p>';
    // Repeated shortcode instances must never duplicate document IDs or event listeners.
    if ($rendered) {
        return '<p><a href="#fv-apollo-r158-root">Return to Apollo Research Desk</a></p>';
    }
    $sources = array(
        'html' => array(__DIR__ . '/templates/ledger.html', '@@HTML_SHA256@@'),
        'css'  => array(__DIR__ . '/assets/research-desk.css', '@@CSS_SHA256@@'),
        'js'   => array(__DIR__ . '/assets/research-desk.js', '@@JS_SHA256@@')
    );
    $raw = array();
    foreach ($sources as $kind => $file) {
        if (!is_readable($file[0])) { return $fallback; }
        $bytes = file_get_contents($file[0]);
        if (!is_string($bytes) || $bytes === '' || !hash_equals($file[1], hash('sha256', $bytes))) { return $fallback; }
        $raw[$kind] = $bytes;
    }
    // These files are immutable and reviewed at release; no shortcode attributes
    // or remote values are ever interpolated. Reject premature close tags.
    if (stripos($raw['css'], '</style') !== false || stripos($raw['js'], '</script') !== false) {
        return $fallback;
    }
    $rendered = true;
    return '<style id="fv-apollo-r158-css">' . $raw['css'] . '</style>'
         . '<div id="fv-apollo-r158-root">' . $raw['html'] . '</div>'
         . '<script id="fv-apollo-r158-js">' . $raw['js'] . '</script>';
}
add_shortcode('fv_ex2_research_desk', 'fv_apollo_r158_shortcode');
