<?php
/**
 * Apollo R367: sequence-wide source custody gate (STAGING ONLY).
 * Requires a separately loaded R365 chronology; does not activate WordPress,
 * enqueue assets, mutate content, track visitors or use external services.
 */
if (!defined('ABSPATH')) { exit; }
const FV_APOLLO_R367_SHA256 = '522ffa8829d6292b90e2ad115f26412d5ec92ef19423d0f2ab125775c08cf5f3';
const FV_APOLLO_R367_IDS = array('fire', 'findings', 'tests', 'decision');

function fv_apollo_r367_is_sealed($candidate): bool {
    if (!function_exists('fv_apollo_r365_rows') || !function_exists('fv_apollo_r365_render_rows')) { return false; }
    if (!is_array($candidate) || count($candidate) !== count(FV_APOLLO_R367_IDS)
        || array_keys($candidate) !== array(0, 1, 2, 3)) { return false; }
    $canonical = fv_apollo_r365_rows();
    if (!is_array($canonical) || count($canonical) !== 4) { return false; }
    try {
        $digest = hash('sha256', json_encode($canonical, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR));
    } catch (Throwable $error) { return false; }
    if (!hash_equals(FV_APOLLO_R367_SHA256, $digest) || $candidate !== $canonical) { return false; }
    foreach (FV_APOLLO_R367_IDS as $index => $id) {
        if (!isset($candidate[$index]['id']) || $candidate[$index]['id'] !== $id
            || !isset($candidate[$index]['source'])
            || !preg_match('~^https://www\.nasa\.gov/~D', $candidate[$index]['source'])) { return false; }
    }
    return true;
}

function fv_apollo_r367_render($candidate): string {
    if (fv_apollo_r367_is_sealed($candidate)) {
        return fv_apollo_r365_render_rows($candidate);
    }
    // The complete set is withheld; partial or reordered records must not acquire citations.
    return '<section class="fv-apollo-r367__unavailable" aria-label="Apollo evidence availability">'
         . '<h2>Evidence chronology temporarily unavailable</h2>'
         . '<p>The reviewed sequence or one of its source records did not pass the source-custody check. No historical claim or NASA citation from this sequence is displayed.</p>'
         . '<p><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the existing free Apollo 1 investigation</a></p>'
         . '</section>';
}

function fv_apollo_r367_shortcode($atts = array()): string {
    return fv_apollo_r367_render(function_exists('fv_apollo_r365_rows') ? fv_apollo_r365_rows() : null);
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_chronology_r367', 'fv_apollo_r367_shortcode');
}
