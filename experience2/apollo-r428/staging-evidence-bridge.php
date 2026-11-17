<?php
/**
 * Final Vestige Apollo R428: opt-in staging-only evidence-to-investigation bridge.
 * Not a WordPress plugin installer and not enabled by default.
 * Archival media are linked to NASA rather than embedded or relicensed.
 */
if (!defined('ABSPATH')) { exit; }

const FV_R428_INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R428_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R428_TRIBUTE = 'https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/';
const FV_R428_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/';

function fv_r428_e(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv_r428_allowed(): bool {
    return defined('FV_R428_ENABLED') && FV_R428_ENABLED === true
        && defined('FV_R428_STAGING_PAGE_ID') && is_int(FV_R428_STAGING_PAGE_ID)
        && FV_R428_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R428_STAGING_PAGE_ID;
}
function fv_r428_fallback(): string {
    return '<p class="fv-r428-fallback">The evidence review is unavailable. <a href="' . FV_R428_INVESTIGATION . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r428_entries(): array {
    return [
        [
            '1967-01-27', 'The ground-test fire', 'Contemporaneous event',
            'The crew died during the launch rehearsal test on January 27, 1967.',
            'The event date is not the date of a later museum photograph.',
            FV_R428_BOARD, 'Read the Apollo 204 Review Board report',
        ],
        [
            '1967-04-05', 'What the Review Board established', 'Primary investigation',
            'The Board found an electrical arc the most probable initiator, but did not conclusively identify a single ignition source. The test atmosphere was 100-percent oxygen at 16.7 psia.',
            'A probable electrical initiator is not a conclusively located initiating spark; this is the Board’s written finding, not a photographic measurement.',
            FV_R428_BOARD, 'Review the original findings and determinations',
        ],
        [
            '2017-01-27', 'The 50-year tribute', 'Retrospective display',
            'The Apollo 1 tribute opened in 2017, displaying the original spacecraft hatch for the first time in public.',
            'A 2017 exhibit photo documents the exhibit; it does not independently establish the emergency procedure used in 1967.',
            FV_R428_TRIBUTE, 'Inspect NASA’s 2017 exhibit announcement',
        ],
    ];
}
/** Visitor-readable content is delivered by PHP. Native details survive disabled JS. */
function fv_r428_render(int $instance): string {
    if ($instance < 1 || $instance > 100) return fv_r428_fallback();
    $key = 'fv-r428-' . $instance;
    $out = '<section class="fv-r428" data-fv-r428 aria-labelledby="' . $key . '-heading">';
    $out .= '<header class="fv-r428__header"><p class="fv-r428__kicker">APOLLO 1 / ORIGINAL SOURCE REVIEW</p><h2 id="' . $key . '-heading">Three dates. Two kinds of evidence. One unresolved question.</h2>';
    $out .= '<p>A primary report and a retrospective museum announcement answer different questions. Inspect each source before treating a photograph as proof of an event.</p></header>';
    $out .= '<ol class="fv-r428__rail" aria-label="Three dated evidence stages">';
    foreach (fv_r428_entries() as $n => $entry) {
        [$date, $title, $kind, $claim, $limitation, $url, $source_label] = $entry;
        $out .= '<li class="fv-r428__plate"><span class="fv-r428__index">RECORD ' . ($n + 1) . ' / 03</span>';
        $out .= '<time datetime="' . fv_r428_e($date) . '">' . fv_r428_e($date) . '</time>';
        $out .= '<h3>' . fv_r428_e($title) . '</h3><p class="fv-r428__kind">' . fv_r428_e($kind) . '</p>';
        $out .= '<p>' . fv_r428_e($claim) . '</p><details><summary>What this source cannot establish</summary><p>' . fv_r428_e($limitation) . '</p></details>';
        $out .= '<p class="fv-r428__source"><a href="' . fv_r428_e($url) . '">' . fv_r428_e($source_label) . '</a></p></li>';
    }
    $out .= '</ol><aside class="fv-r428__method" aria-labelledby="' . $key . '-method">';
    $out .= '<h3 id="' . $key . '-method">An educator’s evidence question</h3>';
    $out .= '<p>Which account can establish the suspected ignition mechanism—and which image can only establish what was displayed in a museum decades later?</p>';
    $out .= '<details><summary>Show a source-based response</summary><p>The 1967 Review Board supports a probable electrical arc, while leaving the exact initiator unresolved. The 2017 announcement supports the museum display date, not the accident’s initiating mechanism.</p></details>';
    $out .= '<p class="fv-r428__rights">These are links to NASA publications, not copies of NASA media. NASA does not endorse FV or any FV product. Check <a href="' . FV_R428_RIGHTS . '">NASA image and brand guidance</a> before media reuse.</p>';
    $out .= '<p class="fv-r428__next"><a href="' . FV_R428_INVESTIGATION . '">Continue to the free Apollo 1 investigation</a></p></aside></section>';
    return $out;
}
function fv_r428_shortcode(): string {
    if (!fv_r428_allowed()) return fv_r428_fallback();
    $next = ($GLOBALS['fv_r428_instances'] ?? 0) + 1;
    if (!is_int($next) || $next > 100) return fv_r428_fallback();
    $GLOBALS['fv_r428_instances'] = $next;
    return fv_r428_render($next);
}
function fv_r428_enqueue(): void {
    if (!fv_r428_allowed()) return;
    if (function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r428-evidence', plugins_url('assets/evidence-bridge.css', __FILE__), [], 'r428');
    }
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_evidence_bridge_r428', 'fv_r428_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r428_enqueue', 20);
