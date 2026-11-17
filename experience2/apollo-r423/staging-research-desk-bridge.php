<?php
/**
 * Plugin Name: FV Apollo Research Desk Source Bridge R423 (STAGING ONLY)
 * Description: Opt-in, source-pinned Research Desk + image custody context. No publication, tracking or media copies.
 * Version: 0.0.1-r423
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

const FV_R423_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R423_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R423_MEDIA = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
const FV_R423_FILES = [
    'templates/ledger.html' => '403d128c57b9bc82dac7c619651689070edef86c',
    'assets/source-ledger.css' => 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
    'assets/source-ledger.js' => '32e757cc4dc8708397ff65ac21e89dd319781d78',
];

function fv_r423_git_blob(string $source): string {
    return sha1('blob ' . strlen($source) . "\0" . $source);
}
function fv_r423_valid_files(string $root, array $expected = FV_R423_FILES): bool {
    $base = realpath($root);
    if (!$base || !is_dir($base)) return false;
    foreach ($expected as $relative => $sha) {
        if (!preg_match('~^(?:templates|assets)/[a-z0-9-]+\.(?:html|css|js)$~D', $relative)
            || !preg_match('/^[0-9a-f]{40}$/D', $sha)) return false;
        $file = realpath($base . DIRECTORY_SEPARATOR . $relative);
        if (!$file || strpos($file, $base . DIRECTORY_SEPARATOR) !== 0 || !is_file($file) || !is_readable($file)) return false;
        $bytes = file_get_contents($file);
        if (!is_string($bytes) || !hash_equals($sha, fv_r423_git_blob($bytes))) return false;
    }
    return true;
}
function fv_r423_root(): ?string {
    if (!defined('FV_R423_RESEARCH_DESK_ROOT') || !is_string(FV_R423_RESEARCH_DESK_ROOT)) return null;
    return realpath(FV_R423_RESEARCH_DESK_ROOT) ?: null;
}
function fv_r423_allowed(): bool {
    return defined('FV_R423_ENABLED') && FV_R423_ENABLED === true
        && defined('FV_R423_STAGING_PAGE_ID') && (int)FV_R423_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && (int)get_queried_object_id() === (int)FV_R423_STAGING_PAGE_ID;
}
function fv_r423_fallback(): string {
    return '<p class="fv-r423-fallback">Research Desk unavailable. <a href="' . FV_R423_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r423_escape(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

/** Independent photographic custody annotations; each image link is contextual, not dispositive. */
function fv_r423_photo_notes(): array {
    return [
        ['01', '1967 · crew portrait', 'The image documents the crew. It does not depict the ignition or spacecraft wiring.'],
        ['02', 'January 3, 1967 · preparation', 'The image shows spacecraft preparation; it is not an oxygen-pressure measurement.'],
        ['03', 'October 18, 1966 · training', 'An altitude-chamber training photograph is not the January 27, 1967 instrument record.'],
        ['04', 'January 24, 2017 · museum exhibit', 'A later tribute exhibit is not a contemporaneous record of hatch operation during the fire.'],
        ['05', 'January 28, 1967 · aftermath', 'Damage documents the aftermath, not the exact initiating spark.'],
        ['06', 'January 24, 2017 · museum exhibit', 'This redesigned-hatch display is not a photograph of the 1967–1968 flammability tests.'],
    ];
}
/** Render only a pinned template, never shortcode user input. Unique IDs eliminate collisions between instances. */
function fv_r423_render(string $template, int $instance): string {
    if ($instance < 1 || $instance > 100 || substr_count($template, 'data-fvx-record') !== 6
        || substr_count($template, 'data-fvx-ledger') !== 1
        || substr_count($template, 'fv-ex2-ledger-apollo1-record-') !== 6
        || strpos($template, FV_R423_ARTICLE) === false) return fv_r423_fallback();
    $prefix = 'fv-r423-' . $instance . '-';
    $desk = str_replace('fv-ex2-ledger-apollo1-', $prefix, $template);
    $out = '<div class="fv-r423" data-fv-r423-bridge><section class="fv-r423__custody" aria-labelledby="' . $prefix . 'custody-heading">';
    $out .= '<p class="fv-r423__eyebrow">APOLLO 1 / RESEARCH DESK / SOURCE CUSTODY</p>';
    $out .= '<h2 id="' . $prefix . 'custody-heading">What the photograph shows is not everything the report establishes.</h2>';
    $out .= '<p>These are six NASA archive image references. Claims about conditions, timing and engineering decisions must be checked against NASA’s textual investigation, not inferred from pictures. Dates below describe the photographs, not necessarily the events discussed alongside them.</p>';
    $out .= '<ol class="fv-r423__notes">';
    foreach (fv_r423_photo_notes() as $record) {
        [$number, $date, $limit] = $record;
        $out .= '<li><a href="#' . $prefix . 'record-' . $number . '">Record ' . $number . ': ' . fv_r423_escape($date) . '</a>';
        $out .= '<details><summary>What this image cannot prove</summary><p>' . fv_r423_escape($limit) . '</p></details></li>';
    }
    $out .= '</ol><p class="fv-r423__notice">Historical conclusions: <a href="' . FV_R423_BOARD . '">Apollo 204 Review Board</a>. ';
    $out .= 'NASA’s report did not conclusively identify one ignition source. ';
    $out .= 'No NASA media are copied here; linked images are subject to <a href="' . FV_R423_MEDIA . '">NASA media-use conditions</a>. NASA does not endorse Final Vestige.</p></section>';
    $out .= $desk . '</div>';
    return $out;
}
function fv_r423_shortcode(): string {
    if (!fv_r423_allowed()) return fv_r423_fallback();
    $root = fv_r423_root();
    if ($root === null || !fv_r423_valid_files($root)) return fv_r423_fallback();
    $template = file_get_contents($root . '/templates/ledger.html');
    if (!is_string($template)) return fv_r423_fallback();
    $GLOBALS['fv_r423_instances'] = ($GLOBALS['fv_r423_instances'] ?? 0) + 1;
    return fv_r423_render($template, (int)$GLOBALS['fv_r423_instances']);
}
function fv_r423_enqueue(): void {
    if (!fv_r423_allowed()) return;
    $root = fv_r423_root();
    if ($root === null || !fv_r423_valid_files($root)) return;
    if (!function_exists('plugins_url') || !function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script')) return;
    $existing_file = $root . '/final-vestige-ex2-research-desk.php';
    if (!is_file($existing_file)) return;
    wp_enqueue_style('fv-ex2-research-desk', plugins_url('assets/source-ledger.css', $existing_file), [], '0.0.3-research');
    wp_enqueue_style('fv-r423-bridge', plugins_url('assets/bridge.css', __FILE__), ['fv-ex2-research-desk'], '0.0.1-r423');
    wp_enqueue_script('fv-ex2-research-desk', plugins_url('assets/source-ledger.js', $existing_file), [], '0.0.3-research', true);
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r423_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_research_bridge_r423', 'fv_r423_shortcode');
