<?php
/**
 * Plugin Name: FV Apollo R411 Source Drawer — STAGING ONLY
 * Description: Native, source-linked evidence disclosure; opt-in staging, no JS, no media or tracking.
 * Version: 0.0.1-r411
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R411_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R411_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R411_AFTER = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R411_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';

/** Source catalog: archive reference URLs copied exactly from #158 ledger; no media embedded. */
function fv_r411_catalog(): array {
    return array(
        array('01', 'Test circumstances', 'The rocket was unfueled; the cabin still presented hazards.', 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/', FV_R411_BOARD, 'Ground-test context does not establish the ignition source.'),
        array('02', 'Cabin atmosphere', 'Elevated-pressure pure oxygen contributed to the severe fire risk.', 'https://www.nasa.gov/image-detail/amf-s67-15717/', FV_R411_BOARD, 'An oxygen-rich atmosphere is not itself evidence of the first spark.'),
        array('03', 'Recorded sequence', 'The Board describes a rapid fire and pressure sequence from surviving signals.', 'https://www.nasa.gov/image-detail/amf-s66-58038/', FV_R411_BOARD, 'Recorded markers do not prove an interpolated frame-by-frame reconstruction.'),
        array('04', 'The hatch', 'The original pressure hatch opened inward, obstructing emergency egress.', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/', FV_R411_BOARD, 'Hatch geometry explains an escape constraint, not the cause of ignition.'),
        array('05', 'Unresolved ignition', 'The initiating failure was never positively identified by the Board.', 'https://www.nasa.gov/image-detail/amf-s67-21294/', FV_R411_BOARD, 'A probable electrical arc must never be described as conclusive proof.'),
        array('06', 'Changes after the fire', 'The redesign included a faster outward-opening hatch and flammability testing.', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/', FV_R411_AFTER, 'The 102 deliberate Command Module tests occurred later, in December 1967–February 1968; they cannot identify the January 1967 initiator.'),
    );
}
function fv_r411_html(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
/** Exact reviewed local CSS identity is a required render gate, not a runtime fetch. */
function fv_r411_css_ok(string $root = __DIR__): bool {
    $path = $root . '/assets/source-drawer.css';
    if (!is_file($path) || !is_readable($path)) return false;
    $raw = file_get_contents($path);
    if (!is_string($raw)) return false;
    $expected = '2ed53b254dd9cfd4b27e56a2ace2c68bf05a8118';
    $actual = sha1('blob ' . strlen($raw) . "\0" . $raw);
    return hash_equals($expected, $actual);
}
function fv_r411_authorized(): bool {
    return defined('FV_R411_ENABLED') && FV_R411_ENABLED === true
        && defined('FV_R411_STAGING_PAGE_ID') && (int) FV_R411_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_R411_STAGING_PAGE_ID;
}
function fv_r411_fallback(): string {
    return '<p class="fv-r411-fallback">Source view unavailable. <a href="' . FV_R411_ARTICLE . '">Read the existing Apollo investigation</a>.</p>';
}
/** No authored media, external scripts, cookies, analytics, outbound affiliates or new forms. */
function fv_r411_markup(int $instance): string {
    if ($instance < 1) throw new InvalidArgumentException('Instance must be positive');
    $id = 'fv-r411-sources-' . $instance;
    $out = '<section class="fv-r411" data-fv-r411-sources aria-labelledby="' . $id . '-heading">';
    $out .= '<div class="fv-r411__heading"><p class="fv-r411__eyebrow">APOLLO 1 / SOURCE CUSTODY</p><h2 id="' . $id . '-heading">Inspect the documents. Keep the limits.</h2>';
    $out .= '<p>Six questions, six separately attributed source trails. The source and the interpretation are not the same thing. The link to a NASA archive record does not mean we reproduce or license its photograph.</p></div>';
    $out .= '<ol class="fv-r411__list">';
    foreach (fv_r411_catalog() as $row) {
        list($num, $title, $claim, $archive, $report, $limitation) = $row;
        $out .= '<li class="fv-r411__item"><details class="fv-r411__disclosure">';
        $out .= '<summary><span class="fv-r411__number">' . fv_r411_html($num) . ' / 06</span><span>' . fv_r411_html($title) . '</span></summary>';
        $out .= '<div class="fv-r411__contents"><p class="fv-r411__claim">' . fv_r411_html($claim) . '</p>';
        $out .= '<p><strong>Evidence boundary:</strong> ' . fv_r411_html($limitation) . '</p>';
        $out .= '<div class="fv-r411__sources"><a href="' . fv_r411_html($report) . '">NASA research text (original publisher)</a>';
        $out .= '<a href="' . fv_r411_html($archive) . '">NASA archive record (external)</a></div>';
        $out .= '</div></details></li>';
    }
    $out .= '</ol><div class="fv-r411__footer"><p>Sources belong to NASA. Final Vestige is independent, and NASA has not endorsed this interpretation or any commercial product. No archival photos are reproduced in this component. <a href="' . FV_R411_RIGHTS . '">NASA media-use guidance</a>.</p>';
    $out .= '<p><a class="fv-r411__next" href="' . FV_R411_ARTICLE . '">Continue to the free Apollo 1 investigation</a></p></div></section>';
    return $out;
}
function fv_r411_shortcode(): string {
    if (!fv_r411_authorized() || !fv_r411_css_ok()) return fv_r411_fallback();
    if (!isset($GLOBALS['fv_r411_instance'])) $GLOBALS['fv_r411_instance'] = 0;
    $GLOBALS['fv_r411_instance']++;
    return fv_r411_markup((int) $GLOBALS['fv_r411_instance']);
}
/** Early enqueue handles shortcode blocks, nested/reusable blocks and independently placed component. */
function fv_r411_enqueue(): void {
    if (!fv_r411_authorized() || !fv_r411_css_ok()) return;
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) return;
    wp_enqueue_style('fv-apollo-r411-source-drawer', plugins_url('assets/source-drawer.css', __FILE__), array(), '0.0.1-r411');
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r411_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_source_drawer_r411', 'fv_r411_shortcode');
