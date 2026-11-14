<?php
/**
 * FV Apollo R369 — source-sealed educator evidence bridge (STAGING ONLY).
 * Opt-in shortcode [fv_apollo_educator_bridge_r369]. No tracking, photos,
 * payment links, forms, background requests, new geo claims or CMS writes.
 * Requires the R365 chronology and the complete R367 sequence seal.
 */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r369_fallback(): string {
    return '<section class="fv-apollo-r369__unavailable" aria-label="Apollo evidence unavailable">'
         . '<h2>Apollo evidence temporarily unavailable</h2>'
         . '<p>The independent chronology custody check is unavailable or did not pass. The evidence and source citations are withheld.</p>'
         . '<p><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the existing free Apollo 1 investigation</a></p>'
         . '</section>';
}

/** Accepts a test candidate only to let tests demonstrate fail-closed behavior. */
function fv_apollo_r369_render($candidate): string {
    if (!function_exists('fv_apollo_r367_is_sealed') ||
        !function_exists('fv_apollo_r367_render') ||
        !fv_apollo_r367_is_sealed($candidate)) {
        return fv_apollo_r369_fallback();
    }
    static $instance = 0;
    $instance++;
    $title_id = 'fv-apollo-r369-' . $instance . '-title';
    $lenses_id = 'fv-apollo-r369-' . $instance . '-lenses';
    $chronology = fv_apollo_r367_render($candidate);
    // This is FV-original pedagogical scaffolding, not a replacement for the
    // NASA sources and not a sellable product, confirmed lead or purchase.
    return '<section class="fv-apollo-r369" aria-labelledby="' . $title_id . '">'
         . '<div class="fv-apollo-r369__intro">'
         . '<p class="fv-apollo-r369__eyebrow">APOLLO 1 · RESEARCH DESK / EVIDENCE ATLAS</p>'
         . '<h2 id="' . $title_id . '">Follow the evidence before drawing the conclusion.</h2>'
         . '<p>Use the original Apollo 204 investigation to distinguish a supported finding from an exact cause that investigators could not establish. The timeline below then separates the 1967 investigation from subsequent tests and decisions.</p>'
         . '</div><section class="fv-apollo-r369__lenses" aria-labelledby="' . $lenses_id . '">'
         . '<h3 id="' . $lenses_id . '">Three questions to bring to the record</h3>'
         . '<div class="fv-apollo-r369__gallery">'
         . '<details class="fv-apollo-r369__lens"><summary>01 · What did investigators actually determine?</summary>'
         . '<p>Compare the Board’s probable initiating mechanism with its explicit limits. Do not turn “most probable” into an identified individual wire or a proven exact ignition point.</p></details>'
         . '<details class="fv-apollo-r369__lens"><summary>02 · Which evidence came later?</summary>'
         . '<p>The later flammability-test series is engineering evidence, not a contemporaneous observation of the fire. Read its publication and evidence classification before citing it.</p></details>'
         . '<details class="fv-apollo-r369__lens"><summary>03 · Which operational change applied where?</summary>'
         . '<p>Distinguish the launch-pad atmosphere decision from atmospheric conditions during orbital flight. A ground-test response is not a claim that all flight conditions changed identically.</p></details>'
         . '</div><p class="fv-apollo-r369__note">Free editorial research preview. No Apollo educator product, license, checkout or paid offer is represented as currently available. NASA does not endorse this resource.</p>'
         . '</section>' . $chronology . '</section>';
}

function fv_apollo_r369_shortcode($atts = array()): string {
    fv_apollo_r369_enqueue();
    return fv_apollo_r369_render(function_exists('fv_apollo_r365_rows') ? fv_apollo_r365_rows() : null);
}

function fv_apollo_r369_enqueue(): void {
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    wp_enqueue_style('fv-apollo-r369-educator-bridge', plugins_url('assets/evidence-bridge.css', __FILE__),
        array('fv-apollo-r368-reflow'), 'r369-staging-1');
}

if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_educator_bridge_r369', 'fv_apollo_r369_shortcode');
}
// On-demand at shortcode execution, with static HTML fallback if assets arrive late.
// Pre-head asset detection and installed Assembler style ordering remain open gates.
