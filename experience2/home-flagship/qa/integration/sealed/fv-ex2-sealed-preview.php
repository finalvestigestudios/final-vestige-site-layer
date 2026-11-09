<?php
/**
 * Plugin Name: Final Vestige EX2 — Sealed Staging Preview
 * Description: Reviewer-only Experience 2 homepage prototype; no public static preview assets.
 * Version: 0.2.0
 * Requires PHP: 8.0
 * License: All rights reserved
 */
if (!defined('ABSPATH')) { exit; }

// The builder replaces this marker with compressed, SHA-pinned source bytes.
/* FV_EX2_SEALED_ASSET_DEFINITIONS */

function fv_ex2_sealed_authorized(): bool {
    return defined('FV_EX2_ALLOW_PREVIEW') && FV_EX2_ALLOW_PREVIEW === true
        && function_exists('wp_get_environment_type')
        && in_array(wp_get_environment_type(), ['staging','development','local'], true)
        && is_user_logged_in() && current_user_can('edit_pages');
}

function fv_ex2_sealed_asset(string $name): ?string {
    if (!defined('FV_EX2_PACKED_ASSETS') || !defined('FV_EX2_ASSET_SHA256')) { return null; }
    if (!array_key_exists($name, FV_EX2_PACKED_ASSETS) || !array_key_exists($name, FV_EX2_ASSET_SHA256)) { return null; }
    $encoded = base64_decode(FV_EX2_PACKED_ASSETS[$name], true);
    if ($encoded === false) { return null; }
    $value = @gzuncompress($encoded);
    if ($value === false || !hash_equals(FV_EX2_ASSET_SHA256[$name], hash('sha256', $value))) { return null; }
    return $value;
}

function fv_ex2_sealed_shortcode($atts = []): string {
    if (!fv_ex2_sealed_authorized()) { return ''; }
    $url = add_query_arg(
        ['action' => 'fv_ex2_sealed_render', '_wpnonce' => wp_create_nonce('fv_ex2_sealed_render')],
        admin_url('admin-ajax.php')
    );
    return '<div data-fv-ex2-sealed="true">'
        . '<p><strong>PRIVATE STAGING STUDY — NOT LIVE.</strong> Authenticated reviewer preview; do not publish on the production homepage.</p>'
        // The sandboxed iframe intentionally has an opaque origin; this explicit
        // top-level fallback avoids session-cookie failures in private review.
        // Keep the same authenticated, nonce-checked AJAX route and noindex CSP.
        . '<p><a href="' . esc_url($url) . '" target="_blank" rel="noopener noreferrer" '
        . 'referrerpolicy="no-referrer">Open the private full-page preview in a new tab</a>'
        . ' <small>(reviewers only; use if the embedded frame cannot authenticate)</small></p>'
        . '<iframe src="' . esc_url($url) . '" title="Private Final Vestige Experience 2 homepage preview" '
        . 'sandbox="allow-scripts allow-popups" loading="lazy" referrerpolicy="no-referrer" '
        . 'style="display:block;width:100%;min-height:85vh;border:1px solid #5d4b31;background:#090a0a"></iframe>'
        . '</div>';
}
add_shortcode('fv_ex2_sealed_homepage_preview', 'fv_ex2_sealed_shortcode');

function fv_ex2_sealed_render(): void {
    if (!fv_ex2_sealed_authorized()) { status_header(403); exit; }
    check_ajax_referer('fv_ex2_sealed_render');
    $html = fv_ex2_sealed_asset('index.html');
    if (!is_string($html) || strpos($html, 'DO NOT DEPLOY AS THE WORDPRESS HOME PAGE') === false
        || strpos($html, 'data-fv-home-flagship') === false) { status_header(503); exit; }
    $nonce = base64_encode(random_bytes(18));
    $cssFiles = ['flagship.css', 'chronicle.css', 'chronicle-lens.css', 'inquiry.css', 'observer-lab.css', 'reading-trail.css'];
    $jsFiles = ['flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js'];
    foreach ($cssFiles as $file) {
        $css = fv_ex2_sealed_asset($file);
        if (!is_string($css)) { status_header(503); exit; }
        $tag = '<link rel="stylesheet" href="./' . $file . '">';
        if (substr_count($html, $tag) !== 1) { status_header(503); exit; }
        $html = str_replace($tag, '<style nonce="' . $nonce . '" data-ex2-style="' . $file . '">' . $css . '</style>', $html);
    }
    $inlineJs = '';
    foreach ($jsFiles as $file) {
        $js = fv_ex2_sealed_asset($file);
        if (!is_string($js)) { status_header(503); exit; }
        $tag = '<script src="./' . $file . '" defer></script>';
        if (substr_count($html, $tag) !== 1) { status_header(503); exit; }
        $html = str_replace($tag, '', $html);
        // Move defer-scripts to the document tail, preserving their original ordered execution.
        $inlineJs .= '<script nonce="' . $nonce . '" data-ex2-script="' . $file . '">' . str_replace('</script', '<\/script', $js) . '</script>';
    }
    if (substr_count($html, '</body>') !== 1 || str_contains($html, 'src="./') || str_contains($html, 'href="./')) {
        status_header(503); exit;
    }
    $html = str_replace('</body>', $inlineJs . '</body>', $html);
    nocache_headers();
    header('Content-Type: text/html; charset=UTF-8');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
    header("Content-Security-Policy: default-src 'none'; script-src 'nonce-{$nonce}'; style-src 'nonce-{$nonce}' 'unsafe-inline'; img-src https://finalvestige.com https://i0.wp.com data:; object-src 'none'; frame-ancestors 'self'; base-uri 'none'; connect-src 'none'; form-action 'none'");
    echo $html;
    exit;
}
add_action('wp_ajax_fv_ex2_sealed_render', 'fv_ex2_sealed_render');
// Intentionally no public Ajax handler, static HTML/CSS/JS files, settings writes, or activation hooks.
