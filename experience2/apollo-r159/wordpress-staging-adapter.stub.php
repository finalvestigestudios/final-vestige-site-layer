<?php
/**
 * Plugin Name: FV Apollo R159 Research Desk — CSP Staging Candidate ONLY
 * Description: Provenance-pinned Research Desk with same-origin external assets. Not production approved.
 * Version: 0.0.1-r159-staging
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Emit link/script URLs directly where the shortcode is rendered, including
 * nested/reusable blocks after wp_head. Do not depend on has_shortcode(post_content).
 * Server checks SHA-256; browser enforces SRI. No remote libraries or analytics.
 * Review late styles, strict-dynamic CSP, theme and cache behavior in WP staging.
 */
function fv_apollo_r159_shortcode($atts = array()): string {
    static $rendered = false;
    $investigation = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
    $fallback = '<p>Research Desk preview unavailable. <a href="' . esc_url($investigation) . '">Read the original Apollo 1 investigation</a>.</p>';
    if ($rendered) {
        return '<p><a href="#fv-apollo-r159-root">Return to Apollo Research Desk</a></p>';
    }
    $files = array(
        'html' => array(__DIR__ . '/templates/ledger.html', '@@HTML_SHA256@@'),
        'css'  => array(__DIR__ . '/assets/research-desk.css', '@@CSS_SHA256@@'),
        'js'   => array(__DIR__ . '/assets/research-desk.js', '@@JS_SHA256@@')
    );
    $raw = array();
    foreach ($files as $kind => $entry) {
        if (!is_readable($entry[0])) { return $fallback; }
        $bytes = file_get_contents($entry[0]);
        if (!is_string($bytes) || $bytes === '' || !hash_equals($entry[1], hash('sha256', $bytes))) {
            return $fallback;
        }
        $raw[$kind] = $bytes;
    }
    // HTML is a fixed, reviewed template. No shortcode arguments, visitor
    // parameters, or remote values are interpolated into the trusted source.
    $css_url = esc_url(plugins_url('assets/research-desk.css', __FILE__));
    $js_url = esc_url(plugins_url('assets/research-desk.js', __FILE__));
    if ($css_url === '' || $js_url === '') { return $fallback; }
    $css_sri = 'sha256-' . base64_encode(hash('sha256', $raw['css'], true));
    $js_sri = 'sha256-' . base64_encode(hash('sha256', $raw['js'], true));
    $rendered = true;
    return '<link id="fv-apollo-r159-css" rel="stylesheet" href="' . $css_url . '" integrity="' . esc_attr($css_sri) . '" crossorigin="anonymous">'
         . '<div id="fv-apollo-r159-root">' . $raw['html'] . '</div>'
         . '<script id="fv-apollo-r159-js" src="' . $js_url . '" integrity="' . esc_attr($js_sri) . '" crossorigin="anonymous" defer></script>';
}
add_shortcode('fv_ex2_research_desk', 'fv_apollo_r159_shortcode');
