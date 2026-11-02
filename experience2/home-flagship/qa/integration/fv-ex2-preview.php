<?php
/**
 * Plugin Name: Final Vestige Experience 2.0 — Staging Preview Only
 * Description: Capability-gated, explicitly opt-in, source-controlled iframe preview. Never replaces the live homepage.
 * Version: 0.1.0
 * Requires PHP: 8.0
 * License: All rights reserved by Final Vestige Studios
 */
if (!defined('ABSPATH')) { exit; }

/** Explicit fail-closed gate: only on correctly configured non-production WordPress environments. */
function fv_ex2_preview_authorized(): bool {
    if (!defined('FV_EX2_ALLOW_PREVIEW') || FV_EX2_ALLOW_PREVIEW !== true) { return false; }
    if (!function_exists('wp_get_environment_type') || !in_array(wp_get_environment_type(), ['staging', 'development', 'local'], true)) { return false; }
    return is_user_logged_in() && current_user_can('edit_pages');
}

/** Display ONLY inside an unpublished WordPress draft or a staging-only private page. */
function fv_ex2_preview_shortcode($atts = []): string {
    if (!fv_ex2_preview_authorized()) { return ''; }
    $href = add_query_arg(
        [ 'action' => 'fv_ex2_render_preview', '_wpnonce' => wp_create_nonce('fv_ex2_render_preview') ],
        admin_url('admin-ajax.php')
    );
    return '<div class="fv-ex2-staging-shell" data-fv-ex2-staging="true">'
        . '<p><strong>Unpublished Experience 2.0 staging study.</strong> This is an iframe preview, not WordPress homepage integration or production approval.</p>'
        . '<iframe src="' . esc_url($href) . '" loading="lazy" title="Final Vestige Experience 2.0 — unpublished full-homepage interactive preview"'
        . ' style="display:block;width:100%;min-height:82vh;border:1px solid #5d4b31;background:#090a0a"'
        . ' sandbox="allow-scripts allow-popups" referrerpolicy="no-referrer"></iframe>'
        . '<p><small>Scroll inside the preview frame. Original source records remain linked for verification; no data is submitted.</small></p></div>';
}
add_shortcode('fv_ex2_homepage_preview', 'fv_ex2_preview_shortcode');

/** Serve static checked-in HTML only to a logged-in staging editor. Not via public plugin assets. */
function fv_ex2_preview_ajax_render(): void {
    if (!fv_ex2_preview_authorized()) { status_header(403); exit; }
    check_ajax_referer('fv_ex2_render_preview');
    $file = plugin_dir_path(__FILE__) . 'assets/index.html.txt';
    if (!is_readable($file)) { status_header(503); exit; }
    $html = file_get_contents($file);
    if (!is_string($html) || strpos($html, 'DO NOT DEPLOY AS THE WORDPRESS HOME PAGE') === false
        || strpos($html, 'data-fv-home-flagship') === false) { status_header(503); exit; }
    // Self-contained relative CSS/JS resolve to this plugin's source-controlled files.
    $base = '<base href="' . esc_url(plugins_url('assets/', __FILE__)) . '">';
    $html = str_replace('<head>', '<head>' . "\n" . $base, $html);
    nocache_headers();
    header('Content-Type: text/html; charset=UTF-8');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    header('Referrer-Policy: no-referrer');
    header('Content-Security-Policy: default-src \'none\'; base-uri \'self\'; style-src \'self\' \'unsafe-inline\'; script-src \'self\'; img-src https://finalvestige.com https://i0.wp.com data:; font-src \'self\'; frame-ancestors \'self\'; connect-src \'none\'; form-action \'none\'');
    echo $html;
    exit;
}
add_action('wp_ajax_fv_ex2_render_preview', 'fv_ex2_preview_ajax_render');
// Intentionally no wp_ajax_nopriv handler, no activation hooks and no page/theme/settings writes.
