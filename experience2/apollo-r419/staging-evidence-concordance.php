<?php
/**
 * Plugin Name: FV Apollo Evidence Concordance R419 (STAGING ONLY)
 * Description: Exact-source custody for claims, historical stages and NASA photo-date boundaries; zero commerce, JS, or media.
 * Version: 0.0.1-r419
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R419_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R419_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
const FV_R419_BLOBS = array(
    '../apollo-r411/staging-source-drawer.php' => 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
    '../apollo-r418/staging-chronology-bridge.php' => '2936eaac30cfe8a1c9016ca9298d98cb78ce9f7d',
    'assets/concordance.css' => '42bcc4e606b035f0b52519fb97acb5d3fefd7352',
);
function fv_r419_blob(string $raw): string { return sha1('blob ' . strlen($raw) . "\0" . $raw); }
function fv_r419_verified(): bool {
    foreach (FV_R419_BLOBS as $relative => $expected) {
        $file = __DIR__ . '/' . $relative;
        if (!is_file($file) || !is_readable($file)) return false;
        $raw = file_get_contents($file);
        if (!is_string($raw) || !hash_equals($expected, fv_r419_blob($raw))) return false;
    }
    return true;
}
function fv_r419_allowed(): bool {
    return defined('FV_R419_ENABLED') && FV_R419_ENABLED === true
        && defined('FV_R419_STAGING_PAGE_ID') && (int)FV_R419_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && (int)get_queried_object_id() === (int)FV_R419_STAGING_PAGE_ID;
}
function fv_r419_escape(string $text): string { return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r419_fallback(): string {
    return '<p class="fv-r419-fallback">The evidence concordance is unavailable. <a href="' . FV_R419_ARTICLE . '">Read the existing free Apollo 1 investigation</a>.</p>';
}
/**
 * Catalogue URLs are evidence *contexts*, not documentation of the adjacent claim.
 * 01-03 precede fire, 04/06 are 2017 museum images, 05 post-fire damage.
 * These are editorial classifications, not media licenses.
 */
function fv_r419_photo_roles(): array {
    return array(
        '01' => array('January 1967', 'Contemporary crew context', 'The crew image does not document an ignition, an unfueled rocket hazard or the hatch operation.'),
        '02' => array('3 January 1967', 'Preparation context', 'A spacecraft preparation image cannot measure the cabin oxygen concentration or pressure.'),
        '03' => array('18 October 1966', 'Earlier altitude-chamber training', 'This photograph is not accident-day pressure or communications telemetry.'),
        '04' => array('24 January 2017', 'Retrospective museum display', 'A 2017 exhibit photograph cannot show the hatch being operated during the 1967 fire.'),
        '05' => array('28 January 1967', 'Post-fire damage context', 'Visible damage is not conclusive identification of the initial electrical fault.'),
        '06' => array('24 January 2017', 'Retrospective hatch exhibit', 'A 2017 museum photograph cannot document experiments run in 1967–1968.'),
    );
}
function fv_r419_records(): ?array {
    if (!fv_r419_verified()) return null;
    if (!function_exists('fv_r411_catalog')) require_once dirname(__DIR__) . '/apollo-r411/staging-source-drawer.php';
    if (!function_exists('fv_r418_events')) require_once dirname(__DIR__) . '/apollo-r418/staging-chronology-bridge.php';
    $cards = fv_r411_catalog(); $events = fv_r418_events();
    $roles = fv_r419_photo_roles();
    $texts = array(
        'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
        'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
        'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
    );
    if (count($cards) !== 6 || count($roles) !== 6 || count($events) !== 3) return null;
    foreach ($cards as $i => $card) {
        if (!is_array($card) || count($card) !== 6 || $card[0] !== sprintf('%02d', $i + 1)) return null;
        foreach ($card as $part) if (!is_string($part) || trim($part) === '') return null;
        if (!isset($roles[$card[0]]) || strpos($card[3], 'https://www.nasa.gov/image-detail/') !== 0) return null;
        if (!in_array($card[4], array_slice($texts, 0, 2), true)) return null;
    }
    foreach ($events as $i => $event) {
        if (!is_array($event) || count($event) !== 8 || $event[5] !== $texts[$i]) return null;
        foreach ($event as $part) if (!is_string($part) || trim($part) === '') return null;
    }
    return array($cards, $events);
}
function fv_r419_markup(int $instance, array $records): string {
    if ($instance < 1 || $instance > 1000 || !fv_r419_verified() || fv_r419_records() !== $records) return fv_r419_fallback();
    list($cards, $events) = $records;
    $roles = fv_r419_photo_roles();
    $base = 'fv-r419-' . $instance;
    $out = '<section class="fv-r419" data-fv-r419-concordance aria-labelledby="' . $base . '-title"><div class="fv-r419__shell">';
    $out .= '<header><p class="fv-r419__kicker">FINAL VESTIGE / APOLLO 1 / EDITORIAL PROVENANCE</p><h2 id="' . $base . '-title">An image is not proof of the claim beside it.</h2>';
    $out .= '<p class="fv-r419__intro">For educators and careful readers: compare what NASA documented about the fire with the dates and subjects of associated archive photographs. The photograph is context; the original textual record supports or limits the historical claim.</p></header>';
    $out .= '<nav class="fv-r419__nav" aria-label="Apollo evidence sections"><a href="#' . $base . '-chronology">Three dated findings</a><a href="#' . $base . '-sources">Six source checks</a></nav>';
    $out .= '<section aria-labelledby="' . $base . '-chronology"><h3 id="' . $base . '-chronology">Three different historical moments</h3><ol class="fv-r419__rail">';
    $dates = array(
        '<time datetime="1967-01-27">27 January 1967</time>',
        '<time datetime="1967-12">December 1967</time> – <time datetime="1968-02">February 1968</time>',
        '<time datetime="1968-03-14">14 March 1968</time>',
    );
    foreach ($events as $i => $event) {
        $out .= '<li><span class="fv-r419__meta">STAGE ' . ($i + 1) . ' / 03</span><span class="fv-r419__date">' . $dates[$i] . '</span>';
        $out .= '<h3>' . fv_r419_escape($event[2]) . '</h3><p>' . fv_r419_escape($event[3]) . '</p>';
        $out .= '<p class="fv-r419__boundary"><strong>Evidence limitation: </strong>' . fv_r419_escape($event[4]) . '</p>';
        $out .= '<p><a href="' . fv_r419_escape($event[5]) . '">Read the NASA textual publication</a></p></li>';
    }
    $out .= '</ol></section>';
    $out .= '<section aria-labelledby="' . $base . '-sources"><h3 id="' . $base . '-sources">Six sources: distinguish photograph from finding</h3><ol class="fv-r419__grid">';
    foreach ($cards as $card) {
        list($num, $title, $claim, $photoUrl, $researchUrl, $limitation) = $card;
        list($photoDate, $role, $warning) = $roles[$num];
        $out .= '<li class="fv-r419__card" id="' . $base . '-record-' . $num . '"><p class="fv-r419__meta">RECORD ' . $num . ' / 06</p><h3>' . fv_r419_escape($title) . '</h3>';
        $out .= '<p><strong>Historical finding:</strong> ' . fv_r419_escape($claim) . '</p>';
        $out .= '<p class="fv-r419__boundary"><strong>Source limitation:</strong> ' . fv_r419_escape($limitation) . '</p>';
        $out .= '<p><strong>Photo date:</strong> ' . fv_r419_escape($photoDate) . '<span class="fv-r419__role"> · ' . fv_r419_escape($role) . '</span></p>';
        $out .= '<p><strong>What the image cannot establish:</strong> ' . fv_r419_escape($warning) . '</p>';
        $out .= '<details><summary>Inspect distinct evidence links</summary><p>These are different source types. Neither NASA image-catalog access nor this editorial summary licenses the photograph for a future product.</p>';
        $out .= '<div class="fv-r419__sources"><a href="' . fv_r419_escape($researchUrl) . '">NASA historical text</a><a href="' . fv_r419_escape($photoUrl) . '">NASA image catalogue</a></div></details></li>';
    }
    $out .= '</ol></section><footer class="fv-r419__footer"><p>No archival photographs, NASA logos or astronaut likenesses are reproduced here. The guide is independent, not NASA-endorsed, and does not establish commercial image permissions. <a href="' . FV_R419_RIGHTS . '">NASA rights and non-endorsement rules</a>.</p>';
    $out .= '<p><a class="fv-r419__next" href="' . FV_R419_ARTICLE . '">Continue to the free Apollo 1 investigation</a></p></footer></div></section>';
    return $out;
}
function fv_r419_shortcode(): string {
    if (!fv_r419_allowed()) return fv_r419_fallback();
    $records = fv_r419_records();
    if ($records === null) return fv_r419_fallback();
    if (!isset($GLOBALS['fv_r419_instance'])) $GLOBALS['fv_r419_instance'] = 0;
    return fv_r419_markup(++$GLOBALS['fv_r419_instance'], $records);
}
function fv_r419_enqueue(): void {
    if (!fv_r419_allowed() || !fv_r419_verified()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r419-concordance', plugins_url('assets/concordance.css', __FILE__), array(), '0.0.1-r419');
    }
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r419_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_concordance_r419', 'fv_r419_shortcode');
