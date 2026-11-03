<?php
/**
 * Plugin Name: Final Vestige Apollo R99 PRIVATE Review Only
 * Description: Authenticated, read-only, hash-pinned seven-view staging preview. Do not activate on production.
 * Version: 0.0.99-staging
 */
if (!defined('ABSPATH')) { exit; }

/** Explicit private configuration flag + editorial capability; disabled by default. */
function fv_apollo_r99_permitted(): bool {
    return defined('FV_APOLLO_R99_PRIVATE_PREVIEW')
        && FV_APOLLO_R99_PRIVATE_PREVIEW === true
        && function_exists('current_user_can') && current_user_can('edit_posts');
}

/** Compiled-in, immutable SHA-256 source custody; no mutable manifest is trusted at runtime. */
function fv_apollo_r99_pins(): array {
    return /*R99_PIN_MANIFEST*/;
}

/** Return only pinned bytes inside the physical package; never remote fetch or DB access. */
function fv_apollo_r99_resource($name): ?array {
    if (!is_string($name) || !preg_match('/^[A-Za-z0-9_]+\.(?:html|css|js|json|txt)$/D', $name)) { return null; }
    $pins = fv_apollo_r99_pins();
    if (!array_key_exists($name, $pins)) { return null; }
    $root = __DIR__ . '/review';
    $path = $root . '/' . $name;
    if (is_link($root) || is_link($path) || !is_dir($root) || !is_file($path) || !is_readable($path)) { return null; }
    $bytes = file_get_contents($path);
    if (!is_string($bytes) || !hash_equals($pins[$name], hash('sha256', $bytes))) { return null; }
    $extension = pathinfo($name, PATHINFO_EXTENSION);
    $type = array('html'=>'text/html; charset=UTF-8','css'=>'text/css; charset=UTF-8','js'=>'text/javascript; charset=UTF-8','txt'=>'text/plain; charset=UTF-8','json'=>'application/json; charset=UTF-8');
    if (!array_key_exists($extension, $type)) { return null; }
    return array('bytes'=>$bytes,'type'=>$type[$extension]);
}

/** No rewrite rules, plugin options, posts, themes, redirects, uploads, or CMS mutation. */
function fv_apollo_r99_private_endpoint(): void {
    if (!array_key_exists('fv_apollo_r99', $_GET)) { return; }
    if (!fv_apollo_r99_permitted()) {
        if (function_exists('status_header')) { status_header(404); }
        exit;
    }
    $file = $_GET['fv_apollo_r99'];
    $resource = fv_apollo_r99_resource($file);
    if ($resource === null) {
        if (function_exists('status_header')) { status_header(404); }
        exit;
    }
    if (function_exists('nocache_headers')) { nocache_headers(); }
    header('Content-Type: ' . $resource['type']);
    header('X-Content-Type-Options: nosniff');
    header('Cache-Control: private, no-store, max-age=0');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    header('Referrer-Policy: no-referrer');
    if (substr($file,-5) === '.html') {
        header("Content-Security-Policy: default-src 'none'; base-uri 'none'; form-action 'none'; style-src 'self'; script-src 'self'; img-src 'none'; connect-src 'none'; frame-ancestors 'self'");
    }
    echo $resource['bytes'];
    exit;
}
add_action('template_redirect', 'fv_apollo_r99_private_endpoint', 0);

/** Review surface only. Full meaning is always available in the source documents with JS off. */
function fv_apollo_r99_review_shortcode($atts = array()): string {
    $fallback = '<p>Private research preview is unavailable. Read the <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">published Apollo 1 investigation</a>.</p>';
    if (!fv_apollo_r99_permitted() || !function_exists('home_url') || !function_exists('add_query_arg')) {
        return $fallback;
    }
    $url = add_query_arg('fv_apollo_r99', 'R89_REVIEW_HUB.html', home_url('/'));
    $safe = function_exists('esc_url') ? esc_url($url) : htmlspecialchars($url, ENT_QUOTES, 'UTF-8');
    return '<section class="fv-apollo-r99-private" aria-label="Private Apollo source review">'
        . '<h2>Apollo 1 — private evidence review</h2><p><strong>Staging hold.</strong> Six NASA photographic-use assessments are pending. No photos are reproduced; dates and catalog associations retain their uncertainty.</p>'
        . '<p><a href="' . $safe . '">Open the complete research review in a separate page</a></p>'
        . '<iframe title="Apollo source review — private staging" loading="lazy" referrerpolicy="no-referrer" src="' . $safe . '" style="display:block;width:100%;height:760px;border:1px solid #777"></iframe>'
        . '<p>All evidence is accessible with JavaScript disabled. This embedded review is not a verified hosted WordPress.com release.</p></section>';
}
add_shortcode('fv_apollo_r99_review', 'fv_apollo_r99_review_shortcode');
