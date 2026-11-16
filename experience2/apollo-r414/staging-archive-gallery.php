<?php
/**
 * Plugin Name: FV Apollo Archive Gallery R414 (STAGING ONLY)
 * Description: Text-only NASA archive catalog with provenance; no imagery or commerce.
 * Version: 0.0.1-r414
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R414_SOURCE_BLOB = 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1';
const FV_R414_CSS_BLOB = 'a5eeb96aeebe5569db4cef0d3d0a0e05fdf99c5f';
const FV_R414_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R414_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
function fv_r414_blob(string $v): string { return sha1('blob ' . strlen($v) . "\0" . $v); }
function fv_r414_verified(string $root = __DIR__): bool {
    $source = dirname($root) . '/apollo-r411/staging-source-drawer.php';
    $css = $root . '/assets/archive-gallery.css';
    if (!is_file($source) || !is_readable($source) || !is_file($css) || !is_readable($css)) return false;
    $src = file_get_contents($source); $style = file_get_contents($css);
    return is_string($src) && is_string($style)
        && hash_equals(FV_R414_SOURCE_BLOB, fv_r414_blob($src))
        && hash_equals(FV_R414_CSS_BLOB, fv_r414_blob($style));
}
function fv_r414_allowed(): bool {
    return defined('FV_R414_ENABLED') && FV_R414_ENABLED === true
        && defined('FV_R414_STAGING_PAGE_ID') && (int) FV_R414_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_R414_STAGING_PAGE_ID;
}
function fv_r414_escape(string $v): string { return htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r414_fallback(): string {
    return '<p class="fv-r414-fallback">Archive gallery not available. <a href="' . FV_R414_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r414_catalog(): array {
    if (!fv_r414_verified()) return array();
    if (!function_exists('fv_r411_catalog')) require_once dirname(__DIR__) . '/apollo-r411/staging-source-drawer.php';
    return fv_r411_catalog();
}
/** Validates all records before constructing any markup: never renders a partial ledger. */
function fv_r414_validate(array $catalog): bool {
    if (count($catalog) !== 6) return false;
    foreach ($catalog as $index => $r) {
        if (!is_array($r) || count($r) !== 6 || array_keys($r) !== range(0, 5)) return false;
        foreach ($r as $v) if (!is_string($v) || trim($v) === '') return false;
        if ($r[0] !== sprintf('%02d', $index + 1)) return false;
        foreach (array(3, 4) as $link) {
            $url = parse_url($r[$link]);
            if (!is_array($url) || ($url['scheme'] ?? '') !== 'https' || ($url['host'] ?? '') !== 'www.nasa.gov'
                || isset($url['port']) || !empty($url['user']) || !empty($url['pass']) || !empty($url['query']) || !empty($url['fragment'])
                || !preg_match('~^/[A-Za-z0-9/_\-.]+/$~', $url['path'] ?? '')) return false;
        }
    }
    return true;
}
function fv_r414_markup(int $instance, array $catalog): string {
    if ($instance < 1 || !fv_r414_validate($catalog)) return fv_r414_fallback();
    $prefix = 'fv-r414-gallery-' . $instance;
    $out = '<section class="fv-r414" aria-labelledby="' . $prefix . '-title" data-fv-r414-gallery><div class="fv-r414__inner">';
    $out .= '<header><p class="fv-r414__kicker">APOLLO 1 / ARCHIVE GALLERY</p><h2 id="' . $prefix . '-title">Six records. Six limits.</h2>';
    $out .= '<p>Browse a curated catalog of original NASA record pages, not reproduced photographs. The evidence is public; the individual imagery and its commercial reuse require separate review.</p></header>';
    $out .= '<nav class="fv-r414__index" aria-label="Gallery record shortcuts">';
    foreach ($catalog as $r) {
        $out .= '<a href="#' . $prefix . '-' . $r[0] . '">Source ' . $r[0] . '</a>';
    }
    $out .= '</nav><ol class="fv-r414__track" aria-label="Apollo 1 NASA source cards">';
    foreach ($catalog as $r) {
        list($num, $title, $claim, $archive, $research, $boundary) = $r;
        $id = $prefix . '-' . $num;
        $out .= '<li class="fv-r414__card" id="' . $id . '"><article aria-labelledby="' . $id . '-title">';
        $out .= '<p class="fv-r414__counter">RECORD ' . $num . ' / 06</p><div class="fv-r414__folio" aria-hidden="true">' . $num . '</div>';
        $out .= '<h3 id="' . $id . '-title">' . fv_r414_escape($title) . '</h3>';
        $out .= '<p class="fv-r414__context">' . fv_r414_escape($claim) . '</p>';
        $out .= '<details><summary>What this source cannot establish</summary><p>' . fv_r414_escape($boundary) . '</p></details>';
        $out .= '<p class="fv-r414__status">External NASA record · image rights not cleared for reuse</p>';
        $out .= '<div class="fv-r414__links"><a href="' . fv_r414_escape($archive) . '">Inspect NASA archive page</a>';
        $out .= '<a href="' . fv_r414_escape($research) . '">Read NASA investigation text</a></div>';
        $out .= '</article></li>';
    }
    $out .= '</ol><footer><p>This is an independent research index, not a NASA gallery, endorsement, image licence, or map. No NASA photos, insignia, or astronaut likenesses are hosted here. <a href="' . FV_R414_RIGHTS . '">Review NASA media-use guidance</a>.</p>';
    $out .= '<p><a class="fv-r414__next" href="' . FV_R414_ARTICLE . '">Continue to the free Apollo 1 investigation</a></p></footer></div></section>';
    return $out;
}
function fv_r414_shortcode(): string {
    if (!fv_r414_allowed() || !fv_r414_verified()) return fv_r414_fallback();
    if (!isset($GLOBALS['fv_r414_instance'])) $GLOBALS['fv_r414_instance'] = 0;
    ++$GLOBALS['fv_r414_instance'];
    return fv_r414_markup((int) $GLOBALS['fv_r414_instance'], fv_r414_catalog());
}
function fv_r414_enqueue(): void {
    if (!fv_r414_allowed() || !fv_r414_verified()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r414-gallery', plugins_url('assets/archive-gallery.css', __FILE__), array(), '0.0.1-r414');
    }
}
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_archive_gallery_r414', 'fv_r414_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r414_enqueue', 20);
