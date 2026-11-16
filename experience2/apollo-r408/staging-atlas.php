<?php
/**
 * Plugin Name: FV Apollo R408 Curated Evidence Atlas (STAGING ONLY)
 * Description: Independent no-geo source index requiring approved R407. OFF by default.
 * Version: 0.0.1-r408
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

const FV_R408_SOURCE_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R408_SOURCE_LATER = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R408_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';

function fv_r408_authorized(): bool {
    return defined('FV_R408_ENABLED') && FV_R408_ENABLED === true
        && defined('FV_R408_STAGING_PAGE_ID') && (int) FV_R408_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_R408_STAGING_PAGE_ID;
}
function fv_r408_fallback(): string {
    return '<p>The interactive source index is unavailable. <a href="' . FV_R408_ARTICLE . '">Read the original Apollo 1 investigation</a>.</p>';
}
function fv_r408_parent_ready(): bool {
    return function_exists('fv_r407_shortcode') && function_exists('fv_r407_authorized')
        && fv_r407_authorized() && function_exists('fv_r407_assets_valid')
        && !empty($GLOBALS['fv_r407_ready']);
}
/** In PHP and with JS disabled, every source question and native disclosure is readable. */
function fv_r408_questions(): array {
    return array(
        array('01', 'conditions', 'Test circumstances', 'Three men. One ground test.', 'What test was underway, and why was the absence of fuel not enough to remove cabin risk?', 'The test setting does not identify the specific cause of ignition.'),
        array('02', 'conditions', 'Cabin atmosphere', 'An atmosphere built for a different risk.', 'What were the oxygen and material conditions during the ground test?', 'An oxygen-rich environment explains propagation risk, not which wire or object first ignited.'),
        array('03', 'sequence', 'Fire and communications', 'Fourteen seconds changed the system.', 'What can the surviving communications and instrumentation place in sequence?', 'Recorded markers are not a frame-by-frame simulation or a complete witness account.'),
        array('04', 'conditions', 'Hatch and escape', 'The hatch opened inward.', 'How did the hatch design affect emergency egress?', 'A safety-design constraint should not be treated as a proven ignition mechanism.'),
        array('05', 'investigation', 'Unresolved ignition', 'The spark was never conclusively identified.', 'What could the Review Board establish, and what remained uncertain?', 'Do not present one proposed ignition site or circuit as conclusively proven.'),
        array('06', 'aftermath', 'Design response', 'Inward became outward.', 'What design and test programs followed the tragedy?', 'The later deliberate fire tests cannot retroactively identify the 1967 ignition source.'),
    );
}
function fv_r408_markup(int $instance): string {
    if ($instance < 1) throw new InvalidArgumentException('Instance must be positive.');
    $root = 'fv-r408-atlas-' . $instance;
    $source_prefix = 'fv-ex2-ledger-apollo1-r407-i' . $instance . '-record-';
    $out = '<section class="fv-r408" data-fv-r408-atlas aria-labelledby="' . $root . '-title">';
    $out .= '<div class="fv-r408__intro"><p class="fv-r408__eyebrow">FINAL VESTIGE / EVIDENCE ATLAS</p>';
    $out .= '<h2 id="' . $root . '-title">Six questions. An inspectable source trail.</h2>';
    $out .= '<p>This is an independent, non-geospatial index to the six evidence records below. Each record distinguishes an observed claim from a limitation. No map pins, location relationships or reconstructed motion are asserted.</p></div>';
    $out .= '<div class="fv-r408__filters" data-fv-r408-filters hidden role="group" aria-label="Filter evidence questions">';
    foreach (array('all'=>'All six','conditions'=>'Conditions','sequence'=>'Sequence','investigation'=>'Investigation','aftermath'=>'Aftermath') as $key=>$label) {
        $out .= '<button type="button" data-fv-r408-filter="' . $key . '" aria-pressed="' . ($key==='all'?'true':'false') . '">' . $label . '</button>';
    }
    $out .= '</div><p class="fv-r408__status" data-fv-r408-status role="status" aria-live="polite">All six evidence questions are available.</p>';
    $out .= '<ol class="fv-r408__grid" data-fv-r408-list>';
    foreach (fv_r408_questions() as $row) {
        list($number, $kind, $label, $record_heading, $question, $caveat) = $row;
        $source = $number === '06' ? FV_R408_SOURCE_LATER : FV_R408_SOURCE_BOARD;
        $out .= '<li class="fv-r408__card" data-fv-r408-card data-fv-r408-kind="' . $kind . '">';
        $out .= '<div class="fv-r408__meta"><span>RECORD ' . $number . '/06</span><span>' . ucfirst($kind) . '</span></div>';
        $out .= '<h3>' . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . '</h3>';
        $out .= '<p>' . htmlspecialchars($question, ENT_QUOTES, 'UTF-8') . '</p>';
        $out .= '<a class="fv-r408__jump" href="#' . $source_prefix . $number . '">Inspect evidence ' . $number . ' — ' . htmlspecialchars($record_heading, ENT_QUOTES, 'UTF-8') . '</a>';
        $out .= '<details class="fv-r408__drawer"><summary>Source and evidence limit</summary>';
        $out .= '<p>' . htmlspecialchars($caveat, ENT_QUOTES, 'UTF-8') . '</p>';
        $out .= '<p><a href="' . $source . '">Inspect original NASA publication</a> (external primary-source reference; NASA has not reviewed or endorsed this index).</p></details>';
        $out .= '</li>';
    }
    $out .= '</ol><p class="fv-r408__boundary">Research context only. This is a curated question index, not a precise geospatial atlas. The free investigation link appears after the underlying six records; no paid offer is inserted here.</p></section>';
    return $out;
}
/** Only trust the parent's server-generated, source-locked six-card ledger. */
function fv_r408_extract_parent_instance(string $html): ?int {
    if (!preg_match('/id="fv-r407-rail-([1-9][0-9]*)"/', $html, $m)) return null;
    $n = (int)$m[1];
    if ($n < 1 || $n > 1000 || substr_count($html, 'data-fvx-record') !== 6) return null;
    for ($i=1; $i<=6; $i++) {
        $id = 'id="fv-ex2-ledger-apollo1-r407-i' . $n . '-record-' . sprintf('%02d', $i) . '"';
        if (substr_count($html, $id) !== 1) return null;
    }
    if (substr_count($html, FV_R408_ARTICLE) !== 1) return null;
    return $n;
}
function fv_r408_shortcode($atts=array()): string {
    if (!fv_r408_authorized() || !fv_r408_parent_ready()) return fv_r408_fallback();
    $parent = fv_r407_shortcode(array());
    $n = fv_r408_extract_parent_instance($parent);
    if ($n === null) return fv_r408_fallback();
    return '<div class="fv-r408__experience">' . fv_r408_markup($n) . $parent . '</div>';
}
function fv_r408_enqueue(): void {
    if (!fv_r408_authorized() || !fv_r408_parent_ready()) return;
    if (!function_exists('plugins_url') || !function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script')) return;
    wp_enqueue_style('fv-r408-atlas', plugins_url('assets/evidence-atlas.css', __FILE__), array('fv-r407-chronology'), '0.0.1-r408');
    wp_enqueue_script('fv-r408-atlas', plugins_url('assets/evidence-atlas.js', __FILE__), array('fv-r407-script'), '0.0.1-r408', true);
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r408_enqueue', 100);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_evidence_atlas_r408', 'fv_r408_shortcode');
