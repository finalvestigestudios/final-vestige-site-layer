<?php
/**
 * Plugin Name: Final Vestige Experience 2.0 — Private Staging Preview
 * Description: Non-public, source-custody-verified preview rendered only to staging editors.
 * Version: 0.2.0
 * Requires PHP: 8.0
 * License: All rights reserved by Final Vestige Studios
 *
 * HOLD: staging QA artifact; never activate on finalvestige.com production.
 */
if (!defined('ABSPATH')) { http_response_code(403); exit; }

function fv_ex2_private_authorized(): bool {
    return defined('FV_EX2_ALLOW_PREVIEW') && FV_EX2_ALLOW_PREVIEW === true
        && function_exists('wp_get_environment_type')
        && in_array(wp_get_environment_type(), ['staging', 'development', 'local'], true)
        && is_user_logged_in() && current_user_can('edit_pages');
}

function fv_ex2_private_shortcode($atts = []): string {
    if (!fv_ex2_private_authorized()) { return ''; }
    $url = add_query_arg(
        ['action' => 'fv_ex2_private_render', '_wpnonce' => wp_create_nonce('fv_ex2_private_render')],
        admin_url('admin-ajax.php')
    );
    return '<section aria-label="Unpublished Final Vestige homepage design preview" data-fv-ex2-staging="private">'
        . '<p><strong>Private staging preview only.</strong> This illustration is not the live homepage or a release approval.</p>'
        . '<iframe title="Final Vestige Experience 2.0, unpublished editorial preview" src="' . esc_url($url) . '"'
        . ' loading="lazy" referrerpolicy="no-referrer" sandbox="allow-scripts allow-popups"'
        . ' style="display:block;width:100%;min-height:85vh;border:1px solid #5d4b31;background:#090a0a"></iframe>'
        . '<p>Source links open their original records; this preview collects no visitor information.</p></section>';
}
add_shortcode('fv_ex2_homepage_preview_private', 'fv_ex2_private_shortcode');

/**
 * Embed every version-pinned stylesheet and script into ONE authenticated HTML response.
 * There are no public static source files, no public Ajax handler and no external JS.
 * Return an error before output if a hash, required tag or source contract is broken.
 */
function fv_ex2_private_compose(): ?array {
    $file = plugin_dir_path(__FILE__) . 'fv-ex2-private-payload.php';
    if (!is_readable($file)) { return null; }
    $payload = require $file;
    if (!is_array($payload) || !isset($payload['sha256'], $payload['data'])
        || !is_array($payload['sha256']) || !is_array($payload['data'])) { return null; }
    $styles = ['flagship.css', 'chronicle.css', 'chronicle-lens.css', 'inquiry.css', 'observer-lab.css', 'reading-trail.css'];
    $scripts = ['flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js'];
    $expected = ['index.html', ...$styles, ...$scripts];
    $keys = array_keys($payload['data']); sort($keys);
    $reference = $expected; sort($reference);
    if ($keys !== $reference) { return null; }
    $hashKeys = array_keys($payload['sha256']); sort($hashKeys);
    if ($hashKeys !== $reference) { return null; }
    $raw = [];
    foreach ($expected as $name) {
        if (!is_string($payload['data'][$name]) || !is_string($payload['sha256'][$name])) { return null; }
        $bytes = base64_decode($payload['data'][$name], true);
        if ($bytes === false || !hash_equals($payload['sha256'][$name], hash('sha256', $bytes))) { return null; }
        $raw[$name] = $bytes;
    }
    $html = $raw['index.html'];
    if (strpos($html, 'DO NOT DEPLOY AS THE WORDPRESS HOME PAGE') === false
        || strpos($html, 'data-fv-home-flagship') === false
        || strpos($html, 'DESIGN STUDY · NOT LIVE') === false) { return null; }
    $nonce = base64_encode(random_bytes(18));
    foreach ($styles as $name) {
        $old = '<link rel="stylesheet" href="./' . $name . '">';
        if (substr_count($html, $old) !== 1 || stripos($raw[$name], '</style') !== false) { return null; }
        $html = str_replace($old, '<style nonce="' . $nonce . '" data-fv-private-asset="' . $name . '">' . "\n" . $raw[$name] . "\n</style>", $html);
    }
    $scriptsAtEnd = ''; // Inline scripts cannot be 'defer' in HTML. Run after body is parsed.
    foreach ($scripts as $name) {
        $old = '<script src="./' . $name . '" defer></script>';
        if (substr_count($html, $old) !== 1 || stripos($raw[$name], '</script') !== false) { return null; }
        $html = str_replace($old, '', $html);
        $scriptsAtEnd .= '<script nonce="' . $nonce . '" data-fv-private-asset="' . $name . '">' . "\n" . $raw[$name] . "\n</script>";
    }
    if (substr_count($html, '</body>') !== 1) { return null; }
    $html = str_replace('</body>', $scriptsAtEnd . '</body>', $html);
    // No passive execution or outbound executable assets. Fail closed on unexpected refs.
    if (preg_match('~<script[^>]+\bsrc\s*=|<link[^>]+rel=["\']stylesheet["\']~i', $html)) { return null; }
    return ['html' => $html, 'nonce' => $nonce, 'index_sha256' => hash('sha256', $raw['index.html'])];
}

function fv_ex2_private_render(): void {
    if (!fv_ex2_private_authorized()) { status_header(403); exit; }
    check_ajax_referer('fv_ex2_private_render');
    $page = fv_ex2_private_compose();
    if ($page === null) { status_header(503); exit; }
    nocache_headers();
    header('Content-Type: text/html; charset=UTF-8');
    header('X-FV-EX2-Index-SHA256: ' . $page['index_sha256']);
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    header('Cache-Control: private, no-store, max-age=0');
    header('Content-Security-Policy: default-src \'none\'; base-uri \'none\'; object-src \'none\'; frame-ancestors \'self\'; script-src \'nonce-' . $page['nonce'] . '\'; style-src \'unsafe-inline\'; img-src https://finalvestige.com https://i0.wp.com data:; font-src \'none\'; connect-src \'none\'; form-action \'none\'');
    echo $page['html'];
    exit;
}
add_action('wp_ajax_fv_ex2_private_render', 'fv_ex2_private_render');
// Deliberately NO wp_ajax_nopriv handler, public stylesheet, script, document or template route.
