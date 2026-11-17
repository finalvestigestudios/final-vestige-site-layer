<?php
/**
 * FV Experience 2.0 R430 — original educator evidence worksheet (staging only).
 * No network calls, form submissions, visitor storage, media copies or merchant links.
 * Every inherited documentary statement is rendered by the exact-reviewed R429 PHP.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R430_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R430_EXPECTED_PHP_BLOB = 'c604bccf9873688ec1d9b64187d1a9a7fdcf89ac';
const FV_R430_EXPECTED_CSS_BLOB = '15942f8ef27d82695c8d2af8bdc8a807396da33e';
function fv_r430_fallback(): string {
    return '<p class="fv-r430-fallback">The evidence worksheet is unavailable. <a href="' . FV_R430_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r430_path(string $part): string {
    return dirname(__DIR__) . '/apollo-r429/' . $part;
}
function fv_r430_git_blob(string $bytes): string {
    return sha1('blob ' . strlen($bytes) . "\0" . $bytes);
}
function fv_r430_verified_sources(): bool {
    foreach ([
        ['staging-attribution-bridge.php', FV_R430_EXPECTED_PHP_BLOB],
        ['assets/bridge.css', FV_R430_EXPECTED_CSS_BLOB],
    ] as $expected) {
        [$part, $sha] = $expected;
        $file = fv_r430_path($part);
        if (is_link($file) || !is_file($file) || !is_readable($file)) return false;
        $bytes = file_get_contents($file);
        if (!is_string($bytes) || !hash_equals($sha, fv_r430_git_blob($bytes))) return false;
    }
    return true;
}
function fv_r430_allowed(): bool {
    return defined('FV_R430_ENABLED') && FV_R430_ENABLED === true
        && defined('FV_R430_STAGING_PAGE_ID') && is_int(FV_R430_STAGING_PAGE_ID) && FV_R430_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R430_STAGING_PAGE_ID;
}
function fv_r430_questions(): array {
    return [
        [
            'An unfueled launch vehicle', '1967-01-27',
            'Does an unfueled Saturn IB mean that the Apollo 1 cabin was free of fire hazards?',
            'Identify the difference between launch-vehicle fueling and conditions inside Command Module 012.',
            'No. The Board recorded 100 percent oxygen at 16.7 psia, combustible materials and possible ignition sources. The rocket\'s fuel status did not eliminate cabin hazards.',
            'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
            'Primary investigation — Apollo 204 Review Board',
        ],
        [
            'A probable initiator, not a proven wire', '1967-04-05',
            'Did the Review Board identify the exact initiating spark or individual wire?',
            'Separate the Board\'s probable electrical-arc finding from a conclusively established origin.',
            'No. The Board considered an electrical arc the most probable initiator, but said that no single ignition source was conclusively identified.',
            'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
            'Primary investigation — findings and determinations',
        ],
        [
            'Experiments after the accident', '2018-02-14',
            'Do the 102 deliberate Command Module ignitions establish what sparked the January 1967 fire?',
            'Identify the date of the historical events described and the date NASA published its retrospective.',
            'No. The 102 deliberate ignitions occurred in three test series between December 1967 and February 1968. NASA published the retrospective February 14, 2018. Neither date places those tests inside the January 1967 accident.',
            'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
            'Later NASA institutional history — not a contemporary accident finding',
        ],
    ];
}
/** Add the original worksheet AFTER the audited R429 evidence trail, retaining its single CTA. */
function fv_r430_render(int $instance, array $query): string {
    if ($instance < 1 || $instance > 40 || !fv_r430_verified_sources()) return fv_r430_fallback();
    // Reject a preloaded unknown R429 implementation, but allow repeated trusted R430 instances.
    if (empty($GLOBALS['fv_r430_trusted_loaded'])) {
        if (function_exists('fv_r429_render')) return fv_r430_fallback();
        require_once fv_r430_path('staging-attribution-bridge.php');
        if (!function_exists('fv_r429_render')) return fv_r430_fallback();
        $GLOBALS['fv_r430_trusted_loaded'] = true;
    }
    $id = 'fv-r430-' . $instance;
    $out = '<div class="fv-r430" data-fv-r430>';
    // The inherited evidence trail includes the *only* next-action CTA.
    $out .= fv_r429_render(60 + $instance, $query);
    $out .= '<section class="fv-r430__worksheet" aria-labelledby="' . $id . '-title">';
    $out .= '<p class="fv-r430__eyebrow">CLASSROOM / ORIGINAL EVIDENCE REASONING</p>';
    $out .= '<h2 id="' . $id . '-title">Three questions to take back to the source</h2>';
    $out .= '<p>For educators and independent researchers: compare each claim with its cited NASA record. Write an answer, then expand the instructor reasoning to check your interpretation. Your writing stays in this browser; nothing is saved or submitted.</p>';
    $out .= '<ol class="fv-r430__questions">';
    foreach (fv_r430_questions() as $index => $q) {
        [$title, $date, $prompt, $guidance, $answer, $url, $source] = $q;
        $questionId = $id . '-q' . ($index + 1);
        $out .= '<li class="fv-r430__question"><p class="fv-r430__date">RECORD DATE <time datetime="' . htmlspecialchars($date, ENT_QUOTES, 'UTF-8') . '">' . htmlspecialchars($date, ENT_QUOTES, 'UTF-8') . '</time></p>';
        $out .= '<h3>' . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '</h3>';
        $out .= '<label for="' . $questionId . '">' . htmlspecialchars($prompt, ENT_QUOTES, 'UTF-8') . '</label>';
        $out .= '<p id="' . $questionId . '-hint" class="fv-r430__hint">' . htmlspecialchars($guidance, ENT_QUOTES, 'UTF-8') . '</p>';
        $out .= '<textarea rows="3" id="' . $questionId . '" aria-describedby="' . $questionId . '-hint" autocomplete="off" spellcheck="true"></textarea>';
        $out .= '<p class="fv-r430__source"><a href="' . htmlspecialchars($url, ENT_QUOTES, 'UTF-8') . '">' . htmlspecialchars($source, ENT_QUOTES, 'UTF-8') . '</a></p>';
        $out .= '<details class="fv-r430__reason"><summary>Instructor reasoning — reveal after answering</summary><p>' . htmlspecialchars($answer, ENT_QUOTES, 'UTF-8') . '</p></details>';
        $out .= '</li>';
    }
    $out .= '</ol><p class="fv-r430__note">NASA sources are credited for historical facts; these classroom prompts and explanations are original Final Vestige text. No NASA logo, photographic reproduction, endorsement or paid product is implied. This worksheet is free and requires no account.</p>';
    $out .= '</section></div>';
    return $out;
}
function fv_r430_shortcode(): string {
    if (!fv_r430_allowed() || !fv_r430_verified_sources()) return fv_r430_fallback();
    $next = ($GLOBALS['fv_r430_instances'] ?? 0) + 1;
    if (!is_int($next) || $next > 40) return fv_r430_fallback();
    $GLOBALS['fv_r430_instances'] = $next;
    return fv_r430_render($next, $_GET);
}
function fv_r430_enqueue(): void {
    if (!fv_r430_allowed() || !fv_r430_verified_sources() || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) return;
    wp_enqueue_style('fv-apollo-r430-source', plugins_url('../apollo-r429/assets/bridge.css', __FILE__), [], FV_R430_EXPECTED_CSS_BLOB);
    wp_enqueue_style('fv-apollo-r430-worksheet', plugins_url('assets/educator-case-lab.css', __FILE__), ['fv-apollo-r430-source'], 'r430');
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_educator_lab_r430', 'fv_r430_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r430_enqueue', 20);
