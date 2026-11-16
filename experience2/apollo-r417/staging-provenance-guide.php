<?php
/**
 * Plugin Name: FV Apollo Source Provenance Guide R417 (STAGING CANDIDATE)
 * Description: Independently labels each archive photograph's actual date and evidentiary role. No media, analytics or commercial CTA.
 * Version: 0.0.1-r417
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R417_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R417_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R417_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
const FV_R417_DEPENDENCIES = array(
    '../apollo-r411/staging-source-drawer.php' => 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
    '../apollo-r415/staging-journey.php' => '18d20114af2a854bc06f1b265026860f6ccee30c',
    'assets/provenance.css' => '921f50a471fad20ee3562e60333cba8f6c84a74d',
);
function fv_r417_blob(string $source): string { return sha1('blob ' . strlen($source) . "\0" . $source); }
function fv_r417_verified(string $root = __DIR__): bool {
    if (realpath($root) !== realpath(__DIR__)) return false;
    foreach (FV_R417_DEPENDENCIES as $rel => $expected) {
        $file = $root . '/' . $rel;
        if (!is_file($file) || !is_readable($file)) return false;
        $raw = file_get_contents($file);
        if (!is_string($raw) || !hash_equals($expected, fv_r417_blob($raw))) return false;
    }
    return true;
}
function fv_r417_allowed(): bool {
    return defined('FV_R417_ENABLED') && FV_R417_ENABLED === true
        && defined('FV_R417_STAGING_PAGE_ID') && (int) FV_R417_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && (int)get_queried_object_id() === (int)FV_R417_STAGING_PAGE_ID;
}
function fv_r417_fallback(): string {
    return '<p class="fv-r417-fallback">Source provenance guide unavailable. <a href="' . FV_R417_ARTICLE . '">Read the existing Apollo 1 investigation</a>.</p>';
}
function fv_r417_escape(string $v): string { return htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
/** NASA caption metadata, not inferred proof. Record 03 is earlier training, not telemetry;
 * 04 and 06 are 2017 tribute photos, not 1967 accident evidence.
 */
function fv_r417_provenance(): array {
    return array(
        '01' => array('January 1967, crew training portrait', 'The astronauts near Launch Complex 34 during Apollo 1 training.', 'Context photograph, not evidence about the hazard of the unfueled ground test or ignition.'),
        '02' => array('3 January 1967, preparation photograph', 'Apollo Spacecraft 012 being moved for assembly preparations.', 'Context photograph, not a measurement of oxygen pressure or an atmospheric test.'),
        '03' => array('18 October 1966, training photograph', 'Crew entering the command module in a KSC altitude chamber.', 'This is not telemetry from 27 January 1967 or a recording of the fatal sequence.'),
        '04' => array('24 January 2017, tribute photograph', 'A museum display of Apollo 1 spacecraft/hatch artifacts at Kennedy Space Center.', 'The 2017 museum view is not a contemporaneous recording of hatch operation or escape.'),
        '05' => array('28 January 1967, aftermath photograph', 'The fire-damaged interior of Apollo Spacecraft 012, one day after the accident.', 'Visible damage does not establish the original ignition initiator.'),
        '06' => array('24 January 2017, tribute photograph', 'A redesigned hatch on display in the 2017 Apollo 1 tribute.', 'This later display is not a photograph of the 1967–1968 deliberate flammability tests.'),
    );
}
function fv_r417_catalog(): ?array {
    if (!fv_r417_verified()) return null;
    if (!function_exists('fv_r411_catalog')) require_once dirname(__DIR__) . '/apollo-r411/staging-source-drawer.php';
    $rows = fv_r411_catalog();
    $notes = fv_r417_provenance();
    if (count($rows) !== 6 || count($notes) !== 6) return null;
    foreach ($rows as $i => $row) {
        if (!is_array($row) || count($row) !== 6 || !isset($notes[$row[0]]) || $row[0] !== sprintf('%02d', $i+1)) return null;
        foreach ($row as $v) if (!is_string($v) || trim($v) === '') return null;
        if ($row[4] !== FV_R417_BOARD && $row[0] !== '06') return null;
        if (!filter_var($row[3], FILTER_VALIDATE_URL) || strpos($row[3], 'https://www.nasa.gov/image-detail/') !== 0) return null;
    }
    return $rows;
}
function fv_r417_markup(int $instance, array $records): string {
    if ($instance < 1 || $instance > 1000 || !fv_r417_verified() || !function_exists('fv_r411_catalog') || $records !== fv_r411_catalog()) return fv_r417_fallback();
    $notes = fv_r417_provenance(); $base = 'fv-r417-' . $instance;
    $out = '<section class="fv-r417" aria-labelledby="' . $base . '-heading" data-fv-r417-provenance><div class="fv-r417__wrap">';
    $out .= '<header><p class="fv-r417__kicker">APOLLO 1 / IMAGE-TO-EVIDENCE CUSTODY</p><h2 id="' . $base . '-heading">A photograph is not the same as proof.</h2>';
    $out .= '<p class="fv-r417__intro">Each link below points to an actual NASA image catalog page. Some pictures were taken before the fire, some afterward, and two depict a museum tribute photographed fifty years later. The historical conclusions belong to the Review Board and other cited research, not to these photographs alone.</p></header>';
    $out .= '<p class="fv-r417__legend"><strong>How to use:</strong> Compare a question to the picture’s date and subject. Open “Photo date and limits” to see why an image does — or does not — support the interpretation. The full textual findings remain available in NASA’s report.</p>';
    $out .= '<ol class="fv-r417__list">';
    foreach ($records as $row) {
        list($number,$title,$claim,$photo,$research,$limit) = $row;
        if (!isset($notes[$number]) || !is_string($photo) || !is_string($research)) return fv_r417_fallback();
        list($classification,$depiction,$warning) = $notes[$number];
        $id = $base . '-record-' . $number;
        $out .= '<li class="fv-r417__item" id="' . $id . '"><p class="fv-r417__number">SOURCE ' . fv_r417_escape($number) . ' / 06</p>';
        $out .= '<h3>' . fv_r417_escape($title) . '</h3><p>' . fv_r417_escape($claim) . '</p>';
        $out .= '<p class="fv-r417__type"><strong>Image role:</strong> ' . fv_r417_escape($classification) . '</p>';
        $out .= '<p class="fv-r417__limit"><strong>What it cannot prove:</strong> ' . fv_r417_escape($warning) . '</p>';
        $out .= '<details><summary>Photo date and limits</summary><div class="fv-r417__details"><p><strong>NASA caption:</strong> ' . fv_r417_escape($depiction) . '</p><p><strong>Review limitation:</strong> ' . fv_r417_escape($limit) . '</p></div></details>';
        $out .= '<div class="fv-r417__links"><a href="' . fv_r417_escape($photo) . '">NASA image catalog</a><a href="' . fv_r417_escape($research) . '">NASA research text</a></div></li>';
    }
    $out .= '</ol><footer class="fv-r417__footer"><p>No images are reproduced here. A link does not license its photograph for resale. Final Vestige is independent; NASA does not endorse this guide or a future paid product. <a href="' . FV_R417_RIGHTS . '">Review NASA media-use terms</a>.</p>';
    $out .= '<p><a href="' . FV_R417_ARTICLE . '" class="fv-r417__next">Continue to the free Apollo 1 investigation</a></p></footer></div></section>';
    return $out;
}
function fv_r417_shortcode(): string {
    if (!fv_r417_allowed()) return fv_r417_fallback();
    $catalog = fv_r417_catalog();
    if ($catalog === null) return fv_r417_fallback();
    if (!isset($GLOBALS['fv_r417_instance'])) $GLOBALS['fv_r417_instance'] = 0;
    return fv_r417_markup(++$GLOBALS['fv_r417_instance'], $catalog);
}
function fv_r417_enqueue(): void {
    if (!fv_r417_allowed() || !fv_r417_verified()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r417-provenance', plugins_url('assets/provenance.css', __FILE__), array(), '0.0.1-r417');
    }
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r417_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_provenance_r417', 'fv_r417_shortcode');
