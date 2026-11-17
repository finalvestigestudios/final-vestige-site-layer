<?php
/**
 * Apollo Evidence Atlas / Source Comparison R426 — staging candidate, never self-activating.
 * No NASA images are embedded. All gallery entries are links to the originating NASA records.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R426_STORY = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R426_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R426_MEDIA = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
function fv_r426_escape(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv_r426_records(): array {
    // Photo date is not necessarily the claim/event date. NASA source links from PR #158.
    return [
        ['01','1967','Crew portrait','Crew and mission context','Does not depict the hatch, cabin pressure or initiating spark.','https://www.nasa.gov/image-detail/apollo-1-crew-honored/'],
        ['02','1967-01-03','Spacecraft preparation','Preparation context','Cannot measure cabin oxygen concentration or test pressure.','https://www.nasa.gov/image-detail/amf-s67-15717/'],
        ['03','1966-10-18','Altitude-chamber training','Earlier training context','Not the January 27, 1967 accident instrument chronology.','https://www.nasa.gov/image-detail/amf-s66-58038/'],
        ['04','2017-01-24','Museum hatch exhibit','Retrospective exhibit','Not a contemporary photograph of hatch operation during the fire.','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/'],
        ['05','1967-01-28','Post-fire damage','Documented aftermath','Damage alone does not establish one conclusive ignition initiator.','https://www.nasa.gov/image-detail/amf-s67-21294/'],
        ['06','2017-01-24','Museum redesigned-hatch exhibit','Retrospective exhibit','Not a photograph of the 1967–1968 flammability experiments.','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'],
    ];
}
function fv_r426_stages(): array {
    return [
        ['1967-01-27','Ground-test fire','NASA documented a rapidly developing fire and multiple interacting hazards. The Board could not conclusively identify the original ignition source.'],
        ['1967','Post-fire investigation','The Review Board distinguished fire circumstances, possible ignition mechanisms and wider organizational/design hazards. This is a report, not a photographic measurement.'],
        ['1968-03-14','Revised atmosphere decision','NASA later approved a different launch-pad atmosphere. Do not mistake retrospective exhibits for original 1968 engineering test data.'],
    ];
}
/** Two shortcode instances must never reuse IDs; all content survives disabled JS. */
function fv_r426_render(int $instance): string {
    if ($instance < 1 || $instance > 100) return fv_r426_fallback();
    $root = 'fv-r426-' . $instance;
    $out = '<section class="fv-r426" data-fv-r426 aria-labelledby="' . $root . '-title">';
    $out .= '<header class="fv-r426__intro"><p class="fv-r426__eyebrow">APOLLO 1 / THE SOURCE COMPARISON</p><h2 id="' . $root . '-title">A real photograph is not proof of every claim beside it.</h2>';
    $out .= '<p>Six NASA catalogue entries. One official investigation. Compare a photograph’s actual date and subject with the evidence needed for a historical conclusion.</p></header>';
    $out .= '<nav aria-label="Apollo source comparison sections"><a href="#' . $root . '-chronology">Historical chronology</a><a href="#' . $root . '-gallery">Photographic source gallery</a><a href="#' . $root . '-method">Source limits</a></nav>';
    $out .= '<section id="' . $root . '-chronology" aria-labelledby="' . $root . '-chronology-heading"><h3 id="' . $root . '-chronology-heading">Three different moments in the record</h3><ol class="fv-r426__rail">';
    foreach (fv_r426_stages() as $stage) {
        [$date,$title,$text] = $stage;
        $out .= '<li><time datetime="' . fv_r426_escape($date) . '">' . fv_r426_escape($date) . '</time><h4>' . fv_r426_escape($title) . '</h4><p>' . fv_r426_escape($text) . '</p><a href="' . FV_R426_BOARD . '">Read the NASA review report</a></li>';
    }
    $out .= '</ol></section>';
    $out .= '<section id="' . $root . '-gallery" aria-labelledby="' . $root . '-gallery-heading"><h3 id="' . $root . '-gallery-heading">Gallery: linked records, not republished images</h3>';
    $out .= '<p>Photographic catalogue entries remain on NASA’s site. Dates below are the photographed or displayed subjects, not substitutes for a dated instrument record.</p><ol class="fv-r426__gallery">';
    foreach (fv_r426_records() as $record) {
        [$n,$date,$title,$kind,$limit,$url] = $record;
        $out .= '<li class="fv-r426__plate"><span class="fv-r426__number">PHOTO RECORD ' . $n . ' / 06</span><h4>' . fv_r426_escape($title) . '</h4>';
        $out .= '<p><strong>Record date:</strong> <time datetime="' . fv_r426_escape($date) . '">' . fv_r426_escape($date) . '</time></p>';
        $out .= '<p><strong>Evidence type:</strong> ' . fv_r426_escape($kind) . '</p>';
        $out .= '<details><summary>Inspect what this image cannot prove</summary><p>' . fv_r426_escape($limit) . '</p></details>';
        $out .= '<p><a href="' . fv_r426_escape($url) . '" rel="noopener noreferrer" target="_blank">Open NASA image catalogue entry</a></p></li>';
    }
    $out .= '</ol></section>';
    $out .= '<aside id="' . $root . '-method" class="fv-r426__method" aria-labelledby="' . $root . '-method-title"><h3 id="' . $root . '-method-title">What is established—and what stays open</h3>';
    $out .= '<p>NASA’s 1967 review describes dangerous oxygen conditions, combustible material and problems with emergency escape. The precise ignition initiator was not conclusively established.</p>';
    $out .= '<p>Nothing here is a geographic reconstruction. No map pins or connections between unrelated locations are asserted. NASA photographs are not reproduced or licensed for resale; review <a href="' . FV_R426_MEDIA . '">NASA’s media and brand guidance</a> before any downstream reuse. NASA does not endorse Final Vestige or an FV product.</p>';
    $out .= '<p><strong>Continue the investigation:</strong> <a class="fv-r426__cta" href="' . FV_R426_STORY . '">Read the full Apollo 1 investigation</a></p></aside></section>';
    return $out;
}
function fv_r426_fallback(): string {
    return '<p>Source comparison not available on this page. <a href="' . FV_R426_STORY . '">Read the full Apollo 1 investigation</a>.</p>';
}
function fv_r426_allowed(): bool {
    return defined('FV_R426_ENABLED') && FV_R426_ENABLED === true
        && defined('FV_R426_STAGING_PAGE_ID') && (int) FV_R426_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_R426_STAGING_PAGE_ID;
}
function fv_r426_shortcode(): string {
    if (!fv_r426_allowed()) return fv_r426_fallback();
    $GLOBALS['fv_r426_instances'] = ($GLOBALS['fv_r426_instances'] ?? 0) + 1;
    return fv_r426_render((int) $GLOBALS['fv_r426_instances']);
}
function fv_r426_assets(): void {
    if (!fv_r426_allowed()) return;
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) return;
    wp_enqueue_style('fv-r426-comparison', plugins_url('assets/source-comparison.css', __FILE__), [], '0.0.1-r426');
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_source_comparison_r426', 'fv_r426_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r426_assets', 20);
