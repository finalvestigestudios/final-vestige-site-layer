<?php
/**
 * Plugin Name: FV Apollo Chronology Evidence Boundary R418 (STAGING ONLY)
 * Description: Separates contemporary accident evidence from later safety testing and retrospective photographs.
 * Version: 0.0.1-r418
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

const FV_R418_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R418_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R418_TESTS = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R418_MIXED = 'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/';
const FV_R418_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
// Pin reviewed upstream evidence and chronology; never edit the legacy or homepage lane.
const FV_R418_SOURCE_BLOBS = array(
    '../apollo-r411/staging-source-drawer.php' => 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
    '../apollo-r415/staging-journey.php' => '18d20114af2a854bc06f1b265026860f6ccee30c',
    'assets/chronology-bridge.css' => '08cd991db94f368b173e04013842d4dcde7e3e4b',
);
function fv_r418_blob(string $raw): string { return sha1('blob ' . strlen($raw) . "\0" . $raw); }
function fv_r418_verified(string $root = __DIR__): bool {
    if (realpath($root) !== realpath(__DIR__)) return false;
    foreach (FV_R418_SOURCE_BLOBS as $rel => $sha) {
        $file = $root . '/' . $rel;
        if (!is_file($file) || !is_readable($file)) return false;
        $bytes = file_get_contents($file);
        if (!is_string($bytes) || !hash_equals($sha, fv_r418_blob($bytes))) return false;
    }
    return true;
}
function fv_r418_allowed(): bool {
    return defined('FV_R418_ENABLED') && FV_R418_ENABLED === true
        && defined('FV_R418_STAGING_PAGE_ID') && (int)FV_R418_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && (int)get_queried_object_id() === (int)FV_R418_STAGING_PAGE_ID;
}
function fv_r418_fallback(): string {
    return '<p class="fv-r418-fallback">The source chronology is unavailable. <a href="' . FV_R418_ARTICLE . '">Read the existing free Apollo 1 investigation</a>.</p>';
}
function fv_r418_e(string $text): string { return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
/** Each row identifies a separate historical interval, source and evidence boundary.
 * Photographs are deliberately NOT linked as proof of fire-test results or of the 1967 ignition.
 */
function fv_r418_events(): array {
    return array(
        array('1967-01-27', '27 January 1967', 'The ground-test fire',
            'Three Apollo 1 astronauts died during the ground test. The Review Board could not conclusively identify the initial ignition source.',
            'An electrical arc was the most probable initiator, not a conclusively established cause.',
            FV_R418_BOARD, '1967 Review Board findings',
            'No photograph of the burned capsule establishes the initial ignition source.'),
        array('1967-12–1968-02', 'December 1967 – February 1968', 'Subsequent fire-safety testing',
            'Engineers conducted 102 deliberate ignitions in a Command Module test article to examine fire risks after redesign.',
            'These controlled tests occurred months after the accident and did not recreate or identify its original ignition.',
            FV_R418_TESTS, '2018 NASA history of later tests',
            'A photograph of a 2017 museum tribute does not document these 1967–1968 experimental ignitions.'),
        array('1968-03-14', '14 March 1968', 'Launch-pad cabin atmosphere decision',
            'NASA announced a mixed-gas atmosphere for launch-pad operations as part of its post-fire safety redesign.',
            'This later policy decision does not retrospectively prove the initiating mechanism of the January 1967 fire.',
            FV_R418_MIXED, '2018 NASA anniversary history',
            'An image of a hatch on display in 2017 is not a contemporaneous record of this 1968 decision.'),
    );
}
function fv_r418_markup(int $instance): string {
    if ($instance < 1 || $instance > 1000 || !fv_r418_verified()) return fv_r418_fallback();
    $base = 'fv-r418-' . $instance;
    $out = '<section class="fv-r418" data-fv-r418-chronology aria-labelledby="' . $base . '-heading"><div class="fv-r418__wrap">';
    $out .= '<header><p class="fv-r418__eyebrow">APOLLO 1 / PROVENANCE-FIRST CHRONOLOGY</p>';
    $out .= '<h2 id="' . $base . '-heading">After the fire is not evidence from the fire.</h2>';
    $out .= '<p>Three documented stages. The fatal ground test, subsequent fire-risk experiments and the later atmosphere decision must not be merged into a fictitious continuous record. NASA publications are linked directly, without geographic pins or inferred photo-to-claim links.</p></header>';
    $out .= '<ol class="fv-r418__rail">';
    foreach (fv_r418_events() as $idx => $item) {
        list($date, $displayDate, $title, $finding, $limit, $source, $sourceLabel, $photoNote) = $item;
        $id = $base . '-stage-' . ($idx + 1);
        $out .= '<li class="fv-r418__stage" id="' . $id . '"><p class="fv-r418__label">STAGE ' . ($idx + 1) . ' / 03</p>';
        $out .= '<p><time>' . fv_r418_e($displayDate) . '</time></p><h3>' . fv_r418_e($title) . '</h3>';
        $out .= '<p class="fv-r418__finding">' . fv_r418_e($finding) . '</p>';
        $out .= '<p class="fv-r418__limit"><strong>Evidence boundary:</strong> ' . fv_r418_e($limit) . '</p>';
        $out .= '<p><a href="' . fv_r418_e($source) . '">Read ' . fv_r418_e($sourceLabel) . '</a></p>';
        $out .= '<details><summary>Why a photograph cannot settle this stage</summary><p>' . fv_r418_e($photoNote) . '</p></details></li>';
    }
    $out .= '</ol><footer class="fv-r418__footer"><p>We reproduce no archival photographs, NASA insignia or media. This independent guide is not endorsed by NASA. Any future use of archival media or astronaut likenesses requires asset-specific rights review. <a href="' . FV_R418_RIGHTS . '">NASA media-use guidance</a>.</p>';
    $out .= '<p><a class="fv-r418__next" href="' . FV_R418_ARTICLE . '">Continue to the free Apollo 1 investigation</a></p></footer></div></section>';
    return $out;
}
function fv_r418_shortcode(): string {
    if (!fv_r418_allowed() || !fv_r418_verified()) return fv_r418_fallback();
    if (!isset($GLOBALS['fv_r418_instance'])) $GLOBALS['fv_r418_instance'] = 0;
    return fv_r418_markup(++$GLOBALS['fv_r418_instance']);
}
function fv_r418_enqueue(): void {
    if (!fv_r418_allowed() || !fv_r418_verified()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url'))
        wp_enqueue_style('fv-apollo-r418-chronology', plugins_url('assets/chronology-bridge.css', __FILE__), array(), '0.0.1-r418');
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r418_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_chronology_r418', 'fv_r418_shortcode');
