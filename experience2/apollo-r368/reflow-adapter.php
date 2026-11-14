<?php
/**
 * Apollo R368: opt-in sealed-chronology reflow and asset adapter.
 * STAGING ONLY. Load in the same plugin as R365 and R367, never from production
 * without installed WordPress/Assembler, security, accessibility and QD gates.
 * No data edits, network services, images, tracking, purchases or e-mail.
 */
if (!defined('ABSPATH')) { exit; }
function fv_apollo_r368_shortcode($atts = array()): string {
    // R367's complete-sequence gate is mandatory. Do NOT fall back to the
    // individually validated, but sequence-unsealed, R365 shortcode.
    if (function_exists('fv_apollo_r367_shortcode')) {
        return fv_apollo_r367_shortcode($atts);
    }
    return '<section class="fv-apollo-r367__unavailable" aria-label="Apollo evidence availability">'
         . '<h2>Evidence chronology temporarily unavailable</h2>'
         . '<p>Source-custody verification is unavailable. The historical sequence and NASA citations are withheld.</p>'
         . '<p><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the existing free Apollo 1 investigation</a></p>'
         . '</section>';
}
function fv_apollo_r368_enqueue(): void {
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    // This adapter is installed only on an isolated staging surface. WordPress
    // theme/template lifecycle acceptance is a separate blocked release gate.
    $r367_file = dirname(__DIR__) . '/apollo-r367/sealed-chronology.php';
    wp_enqueue_style(
        'fv-apollo-r367-sequence',
        plugins_url('assets/sequence-gate.css', $r367_file),
        array('fv-apollo-r365-chronology'),
        'r368-stage-1'
    );
    wp_enqueue_style(
        'fv-apollo-r368-reflow',
        plugins_url('assets/reflow.css', __FILE__),
        array('fv-apollo-r367-sequence'),
        'r368-stage-1'
    );
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_chronology_r368', 'fv_apollo_r368_shortcode');
}
if (function_exists('add_action')) {
    add_action('wp_enqueue_scripts', 'fv_apollo_r368_enqueue', 30);
}
