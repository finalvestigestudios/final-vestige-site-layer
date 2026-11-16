<?php
/**
 * Plugin Name: FV Apollo EvidencePlate R413 (STAGING ONLY)
 * Description: Pure-PHP source/limitation comparison, default disabled and source pinned.
 * Version: 0.0.1-r413
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R413_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R413_SOURCE_SHA = 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1';
const FV_R413_CSS_SHA = '95aa879a118f15de35b7fd82d3f1e182fead002c';
function fv_r413_git_blob(string $source): string {
    return sha1('blob ' . strlen($source) . "\0" . $source);
}
function fv_r413_dependency_ok(string $root = __DIR__): bool {
    $r411 = dirname($root) . '/apollo-r411/staging-source-drawer.php';
    $css = $root . '/assets/evidence-plate.css';
    if (!is_readable($r411) || !is_readable($css)) return false;
    $src = file_get_contents($r411);
    $style = file_get_contents($css);
    return is_string($src) && is_string($style)
        && hash_equals(FV_R413_SOURCE_SHA, fv_r413_git_blob($src))
        && hash_equals(FV_R413_CSS_SHA, fv_r413_git_blob($style));
}
function fv_r413_authorized(): bool {
    return defined('FV_R413_ENABLED') && FV_R413_ENABLED === true
        && defined('FV_R413_STAGING_PAGE_ID') && (int)FV_R413_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int)get_queried_object_id() === (int)FV_R413_STAGING_PAGE_ID;
}
function fv_r413_fallback(): string {
    return '<p class="fv-r413-fallback">Evidence plate unavailable. <a href="' . FV_R413_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r413_escape(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
/** The six rows come directly from exact R411 NASA custody source, never shortcode input. */
function fv_r413_catalog(): array {
    if (!fv_r413_dependency_ok()) return array();
    $path = dirname(__DIR__) . '/apollo-r411/staging-source-drawer.php';
    if (!function_exists('fv_r411_catalog')) require_once $path;
    return fv_r411_catalog();
}
function fv_r413_markup(int $instance, array $catalog): string {
    if ($instance < 1 || count($catalog) !== 6) return fv_r413_fallback();
    $prefix = 'fv-r413-evidence-' . $instance;
    $out = '<section class="fv-r413" data-fv-r413-plate aria-labelledby="' . $prefix . '-title"><div class="fv-r413__inner">';
    $out .= '<header><p class="fv-r413__eyebrow">APOLLO 1 / EVIDENCE PLATES</p><h2 class="fv-r413__title" id="' . $prefix . '-title">What the record shows. What it cannot prove.</h2>';
    $out .= '<p class="fv-r413__intro">Six documented questions from NASA records. The evidence and its limitations appear side by side. This is independent interpretation, not a NASA endorsement or an image licence.</p></header>';
    $out .= '<nav class="fv-r413__jump" aria-label="Evidence questions"><strong>Jump to a record</strong>';
    foreach ($catalog as $row) {
        $out .= '<a href="#' . $prefix . '-' . fv_r413_escape($row[0]) . '">' . fv_r413_escape($row[0] . ' ' . $row[1]) . '</a>';
    }
    $out .= '</nav><ol class="fv-r413__list">';
    foreach ($catalog as $row) {
        if (count($row) !== 6) return fv_r413_fallback();
        list($number, $title, $claim, $archive, $report, $boundary) = $row;
        if (!preg_match('/^0[1-6]$/', $number) || !preg_match('~^https://www\.nasa\.gov/[A-Za-z0-9/_\-.]+/$~', $archive)
            || !preg_match('~^https://www\.nasa\.gov/[A-Za-z0-9/_\-.]+/$~', $report)) return fv_r413_fallback();
        $id = $prefix . '-' . $number;
        $out .= '<li class="fv-r413__card" id="' . $id . '"><div class="fv-r413__head"><span class="fv-r413__number">EVIDENCE ' . fv_r413_escape($number) . ' / 06</span><h3>' . fv_r413_escape($title) . '</h3></div>';
        $out .= '<div class="fv-r413__columns"><div class="fv-r413__claim"><span class="fv-r413__label">WHAT THE RECORD SUPPORTS</span><p>' . fv_r413_escape($claim) . '</p></div>';
        $out .= '<div class="fv-r413__limit"><span class="fv-r413__label">WHAT IT DOES NOT PROVE</span><p>' . fv_r413_escape($boundary) . '</p></div></div>';
        $out .= '<div class="fv-r413__sources"><a href="' . fv_r413_escape($report) . '">NASA research account</a><a href="' . fv_r413_escape($archive) . '">NASA archive record</a></div></li>';
    }
    $out .= '</ol><footer class="fv-r413__footer"><p>Publicly accessible NASA source links do not grant image reuse rights. No photographs, insignia or invented map locations are included.</p>';
    $out .= '<p><a class="fv-r413__next" href="' . FV_R413_ARTICLE . '">Continue with the free Apollo 1 investigation</a></p></footer></div></section>';
    return $out;
}
function fv_r413_shortcode(): string {
    if (!fv_r413_authorized() || !fv_r413_dependency_ok()) return fv_r413_fallback();
    $catalog = fv_r413_catalog();
    if (!isset($GLOBALS['fv_r413_instance'])) $GLOBALS['fv_r413_instance'] = 0;
    $GLOBALS['fv_r413_instance']++;
    return fv_r413_markup((int)$GLOBALS['fv_r413_instance'], $catalog);
}
function fv_r413_enqueue(): void {
    if (!fv_r413_authorized() || !fv_r413_dependency_ok()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r413-plate', plugins_url('assets/evidence-plate.css', __FILE__), array(), '0.0.1-r413');
    }
}
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_evidence_plate_r413', 'fv_r413_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r413_enqueue', 20);
