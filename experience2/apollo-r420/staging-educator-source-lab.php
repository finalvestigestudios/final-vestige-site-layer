<?php
/**
 * Plugin Name: FV Apollo Source Reasoning Lab R420 (STAGING ONLY)
 * Description: Evidence-reading educator preview. Requires pinned R419 custody; no JS, forms, sales, geo or media.
 * Version: 0.0.1-r420
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R420_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R420_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
const FV_R420_BLOBS = array(
    '../apollo-r419/staging-evidence-concordance.php' => '0d300360c6614be9c189ef5d555e1f497c844582',
    'assets/educator-lab.css' => 'f1a9a99571589697d313002b0daab534a93b305d',
);
function fv_r420_blob(string $raw): string { return sha1('blob ' . strlen($raw) . "\0" . $raw); }
function fv_r420_verified(): bool {
    foreach (FV_R420_BLOBS as $rel => $sha) {
        $path = __DIR__ . '/' . $rel;
        if (!is_readable($path) || !is_file($path)) return false;
        $raw = file_get_contents($path);
        if (!is_string($raw) || !hash_equals($sha, fv_r420_blob($raw))) return false;
    }
    return true;
}
function fv_r420_allowed(): bool {
    return defined('FV_R420_ENABLED') && FV_R420_ENABLED === true
        && defined('FV_R420_STAGING_PAGE_ID') && (int) FV_R420_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && (int)get_queried_object_id() === (int) FV_R420_STAGING_PAGE_ID;
}
function fv_r420_e(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r420_fallback(): string {
    return '<p class="fv-r420-fallback">The source activity is unavailable. <a href="' . FV_R420_ARTICLE . '">Read the existing free Apollo 1 investigation</a>.</p>';
}
/**
 * Every exercise draws its original historical finding, evidence boundary, photo date and source URL
 * from upstream immutable R419 -> R418/R411 structures. Narrative prompts are FV-authored pedagogy.
 */
function fv_r420_cases(): ?array {
    if (!fv_r420_verified()) return null;
    if (!function_exists('fv_r419_records')) require_once dirname(__DIR__) . '/apollo-r419/staging-evidence-concordance.php';
    $records = fv_r419_records();
    if ($records === null) return null;
    list($cards, $events) = $records;
    $roles = fv_r419_photo_roles();
    if (count($cards) !== 6 || count($events) !== 3 || count($roles) !== 6) return null;
    $links = array($events[0][5], $events[1][5], $events[2][5]);
    if (count(array_unique($links)) !== 3) return null;
    return array(
        array('01', 'Uncertain ignition', 'Did NASA determine the exact ignition source in the 27 January 1967 fire?',
              $events[0][3], $events[0][4], $roles['05'][0], $roles['05'][2], $events[0][5], $cards[4][3],
              'Separate a probable explanation from a demonstrated fact.'),
        array('02', 'Retrospective image', 'Can a museum photograph from 2017 establish how the crew operated the hatch in 1967?',
              $cards[3][2], $cards[3][5], $roles['04'][0], $roles['04'][2], $cards[3][4], $cards[3][3],
              'Distinguish the date of a photograph from the date of the event it depicts or interprets.'),
        array('03', 'Tests after the event', 'Did the later 102 deliberate ignitions identify the original 1967 spark?',
              $events[1][3], $events[1][4], $roles['06'][0], $roles['06'][2], $events[1][5], $cards[5][3],
              'Distinguish a later safety experiment from an observation of the original accident.'),
    );
}
function fv_r420_markup(int $instance, array $cases): string {
    if ($instance < 1 || $instance > 1000 || count($cases) !== 3 || !fv_r420_verified() || fv_r420_cases() !== $cases) return fv_r420_fallback();
    $id = 'fv-r420-' . $instance;
    $out = '<section class="fv-r420" data-fv-r420-lab aria-labelledby="' . $id . '-heading"><div class="fv-r420__shell">';
    $out .= '<header><p class="fv-r420__eyebrow">FINAL VESTIGE / APOLLO 1 / ORIGINAL EDUCATOR ACTIVITY</p><h2 id="' . $id . '-heading">Could the evidence actually prove that?</h2>';
    $out .= '<p class="fv-r420__intro">A three-question, printable source-reading preview for history educators and careful readers. Compare a historical claim with a NASA publication and a separately dated image record. The NASA links are evidence references, not a commercial media license.</p>';
    $out .= '<p><strong>Suggested use:</strong> approximately 10–15 minutes; individual or small-group source evaluation. No account or download required. This free activity is not a purchasable product.</p></header>';
    $out .= '<nav class="fv-r420__map" aria-label="Source evaluation questions"><a href="#' . $id . '-case-01">Question 1: uncertainty</a><a href="#' . $id . '-case-02">Question 2: photographs</a><a href="#' . $id . '-case-03">Question 3: later tests</a></nav>';
    $out .= '<ol class="fv-r420__questions">';
    foreach ($cases as $c) {
        list($num, $title, $question, $historical, $limit, $photoDate, $photoLimit, $textUrl, $photoUrl, $teaching) = $c;
        $out .= '<li id="' . $id . '-case-' . fv_r420_e($num) . '" class="fv-r420__card">';
        $out .= '<p class="fv-r420__meta">QUESTION ' . fv_r420_e($num) . ' / 03</p><h3>' . fv_r420_e($title) . '</h3><p class="fv-r420__prompt">' . fv_r420_e($question) . '</p>';
        $out .= '<p><strong>Historical finding:</strong> ' . fv_r420_e($historical) . '</p><p class="fv-r420__boundary"><strong>Evidence limitation:</strong> ' . fv_r420_e($limit) . '</p>';
        $out .= '<p><strong>Related photograph date:</strong> ' . fv_r420_e($photoDate) . '</p><p><strong>Why the photo cannot settle this:</strong> ' . fv_r420_e($photoLimit) . '</p>';
        $out .= '<div class="fv-r420__source"><h4>Inspect original source destinations</h4><p><a href="' . fv_r420_e($textUrl) . '">NASA historical publication</a></p><p><a href="' . fv_r420_e($photoUrl) . '">NASA image catalogue (photo not reproduced)</a></p></div>';
        $out .= '<p><strong>Write your own source-grounded answer:</strong><span aria-hidden="true" class="fv-r420__practice"></span></p>';
        $out .= '<details><summary>Reveal instructor reasoning check</summary><div class="fv-r420__explanation"><p>' . fv_r420_e($teaching) . '</p><p>Check the historical finding, evidence limitation, and photo date above. Do not assert more than the cited source establishes.</p></div></details>';
        $out .= '</li>';
    }
    $out .= '</ol><footer class="fv-r420__footer"><p><strong>Source/rights note:</strong> this independent educational exercise cites NASA but is not NASA endorsed. No NASA photograph, emblem, astronaut likeness or third-party media is embedded, sold or sublicensed. <a href="' . FV_R420_RIGHTS . '">NASA media and non-endorsement guidance</a>. Each linked catalogue item requires its own review before reuse.</p>';
    $out .= '<p><a class="fv-r420__next" href="' . FV_R420_ARTICLE . '">Read the full free Apollo 1 investigation</a></p></footer></div></section>';
    return $out;
}
function fv_r420_shortcode(): string {
    if (!fv_r420_allowed() || !fv_r420_verified()) return fv_r420_fallback();
    $cases = fv_r420_cases();
    if ($cases === null) return fv_r420_fallback();
    if (!isset($GLOBALS['fv_r420_instance'])) $GLOBALS['fv_r420_instance'] = 0;
    return fv_r420_markup(++$GLOBALS['fv_r420_instance'], $cases);
}
function fv_r420_enqueue(): void {
    if (!fv_r420_allowed() || !fv_r420_verified()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r420-source-lab', plugins_url('assets/educator-lab.css', __FILE__), array(), '0.0.1-r420');
    }
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r420_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_educator_lab_r420', 'fv_r420_shortcode');
