<?php
/**
 * Plugin Name: FV Apollo Source-to-Investigation Journey R415 (STAGING ONLY)
 * Description: Integrates the verified R411 custody catalog with R414 gallery and a NASA-sourced chronology. Disabled by default.
 * Version: 0.0.1-r415
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R415_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R415_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R415_LATER = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R415_MIXED = 'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/';
const FV_R415_SOURCE_BLOBS = array(
    '../apollo-r411/staging-source-drawer.php' => 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
    '../apollo-r414/staging-archive-gallery.php' => '41540268014b4a792b2e52685ebe8c471a35c3da',
    '../apollo-r414/assets/archive-gallery.css' => 'a5eeb96aeebe5569db4cef0d3d0a0e05fdf99c5f',
    'assets/journey.css' => '8861287fa3e565963454f7a524a60cafe23bd797',
);
function fv_r415_hash(string $data): string { return sha1('blob ' . strlen($data) . "\0" . $data); }
function fv_r415_verified(string $root = __DIR__): bool {
    foreach (FV_R415_SOURCE_BLOBS as $relative => $blob) {
        $path = $root . '/' . $relative;
        if (!is_file($path) || !is_readable($path)) return false;
        $data = file_get_contents($path);
        if (!is_string($data) || !hash_equals($blob, fv_r415_hash($data))) return false;
    }
    return true;
}
function fv_r415_authorized(): bool {
    return defined('FV_R415_ENABLED') && FV_R415_ENABLED === true
        && defined('FV_R415_STAGING_PAGE_ID') && (int) FV_R415_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_R415_STAGING_PAGE_ID;
}
function fv_r415_fallback(): string {
    return '<p class="fv-r415-fallback">The source-guided experience is unavailable. <a href="' . FV_R415_ARTICLE . '">Read the existing Apollo 1 investigation</a>.</p>';
}
/** Load only reviewed dependencies. The gallery itself performs a second source validation. */
function fv_r415_catalog(string $root = __DIR__): ?array {
    if (!fv_r415_verified($root) || realpath($root) !== realpath(__DIR__)) return null;
    if (!function_exists('fv_r411_catalog')) require_once dirname(__DIR__) . '/apollo-r411/staging-source-drawer.php';
    if (!function_exists('fv_r414_markup')) require_once dirname(__DIR__) . '/apollo-r414/staging-archive-gallery.php';
    $rows = fv_r411_catalog();
    if (!fv_r414_validate($rows)) return null;
    return $rows;
}
function fv_r415_chronology(int $instance): string {
    $base = 'fv-r415-' . $instance;
    $events = array(
        array('1967-01-27', '27 January 1967', 'Ground test and fire', 'The Apollo 204 ground test ended in a fatal cabin fire. The Review Board did not conclusively identify its ignition initiator.', FV_R415_BOARD, '05'),
        array('1967-12/1968-02', 'December 1967 – February 1968', 'Deliberate Command Module tests', 'Engineers conducted 102 separate, later deliberate ignitions to assess changes in spacecraft fire risk. These were not reconstructions identifying the 1967 ignition.', FV_R415_LATER, '06'),
        array('1968-03-14', '14 March 1968', 'Changed launch-pad atmosphere announced', 'NASA announced a mixed-gas cabin atmosphere for launch-pad operations, alongside other fire-safety redesigns.', FV_R415_MIXED, '06'),
    );
    $out = '<section class="fv-r415__chronology" aria-labelledby="' . $base . '-chronology"><h3 id="' . $base . '-chronology">Three documented milestones</h3><p>Later tests and design choices are separate evidence from the original fire. Select a milestone to read the primary publication or its related source card.</p><ol class="fv-r415__rail">';
    foreach ($events as $e) {
        list($iso, $label, $title, $claim, $url, $card) = $e;
        $target = 'fv-r414-gallery-' . $instance . '-' . $card;
        $out .= '<li><span class="fv-r415__date">' . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . '</span>';
        $out .= '<h4>' . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '</h4>';
        $out .= '<p>' . htmlspecialchars($claim, ENT_QUOTES, 'UTF-8') . '</p>';
        $out .= '<div class="fv-r415__rail-links"><a href="#' . $target . '">Related evidence ' . $card . '</a><a href="' . htmlspecialchars($url, ENT_QUOTES, 'UTF-8') . '">NASA original publication</a></div></li>';
    }
    return $out . '</ol></section>';
}
function fv_r415_markup(int $instance, array $catalog): string {
    if ($instance < 1 || $instance > 1000 || !function_exists('fv_r414_validate') || !fv_r414_validate($catalog)) return fv_r415_fallback();
    $base = 'fv-r415-' . $instance;
    $out = '<section class="fv-r415" data-fv-r415-journey aria-labelledby="' . $base . '-heading"><div class="fv-r415__wrap">';
    $out .= '<nav aria-label="Apollo research guide navigation" class="fv-r415__nav"><a href="#' . $base . '-chronology">Evidence chronology</a><a href="#' . $base . '-gallery">Inspect six records</a></nav>';
    $out .= '<header class="fv-r415__hero"><p class="fv-r415__kicker">FINAL VESTIGE / APOLLO 1 / SOURCE GUIDE</p><h2 id="' . $base . '-heading">What the records establish — and what they cannot.</h2>';
    $out .= '<p>For history educators and careful readers: follow the documented sequence, examine the original NASA publications and make your own distinction between evidence, later safety improvements and unproven ignition theories.</p>';
    $out .= '<p class="fv-r415__notice">Independent historical research. No archival imagery is reproduced or licensed here; NASA has not approved or endorsed this guide.</p></header>';
    $out .= fv_r415_chronology($instance);
    $out .= '<div id="' . $base . '-gallery" class="fv-r415__gallery">' . fv_r414_markup($instance, $catalog) . '</div>';
    $out .= '</div></section>';
    return $out;
}
function fv_r415_shortcode(): string {
    if (!fv_r415_authorized()) return fv_r415_fallback();
    $catalog = fv_r415_catalog();
    if ($catalog === null) return fv_r415_fallback();
    if (!isset($GLOBALS['fv_r415_instance'])) $GLOBALS['fv_r415_instance'] = 0;
    $GLOBALS['fv_r415_instance']++;
    return fv_r415_markup((int) $GLOBALS['fv_r415_instance'], $catalog);
}
function fv_r415_enqueue(): void {
    if (!fv_r415_authorized() || fv_r415_catalog() === null) return;
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) return;
    wp_enqueue_style('fv-apollo-r414-gallery', plugins_url('../apollo-r414/assets/archive-gallery.css', __FILE__), array(), '0.0.1-r414');
    wp_enqueue_style('fv-apollo-r415-journey', plugins_url('assets/journey.css', __FILE__), array('fv-apollo-r414-gallery'), '0.0.1-r415');
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r415_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_journey_r415', 'fv_r415_shortcode');
