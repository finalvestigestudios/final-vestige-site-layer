<?php
/**
 * Final Vestige Apollo R395 — isolated, explicitly opted-in STAGING CSS prepaint.
 *
 * Keeps the R384 gallery shortcode and reviewed base CSS untouched. Adds the
 * reviewed 400%-text mobile-fit rules to <head> after the base asset, before
 * any gallery can paint, even when the shortcode is in a reusable block.
 * This does not activate itself and never changes a WordPress option or post.
 */
if (!defined('ABSPATH')) { exit; }

const FV_R395_BASE_SHA256 = '4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9';
const FV_R395_FIT_SHA256 = '93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756';

function fv_r395_reviewed_file(string $path, string $expected): bool {
    return is_file($path) && !is_link($path) && is_readable($path)
      && hash_equals($expected, hash_file('sha256', $path));
}

/** Fail closed unless *all* deployment, canonical-content and custody guards pass. */
function fv_r395_prepaint_eligible(): bool {
    if (!defined('FV_R395_APOLLO_QA_ENABLE') || FV_R395_APOLLO_QA_ENABLE !== true
        || !function_exists('wp_get_environment_type') || wp_get_environment_type() !== 'staging'
        || !function_exists('is_page') || !is_page('apollo-1-evidence-atlas')
        || !function_exists('fv_r384_records') || fv_r384_records() === false
        || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return false; }
    $base = dirname(__DIR__) . '/apollo-r384/assets/gallery.css';
    $fit = __DIR__ . '/assets/mobile-fit.css';
    return fv_r395_reviewed_file($base, FV_R395_BASE_SHA256)
       && fv_r395_reviewed_file($fit, FV_R395_FIT_SHA256);
}

function fv_r395_enqueue_prepaint(): void {
    if (!fv_r395_prepaint_eligible()) { return; }
    // Original shortcode's handle is deliberately reused. WordPress deduplicates
    // it when R384 has already enqueued the base at wp_enqueue_scripts priority 5.
    // The dependency pins fit CSS *after* base CSS in the original head queue.
    wp_enqueue_style('fv-apollo-r384-gallery',
        plugins_url('../apollo-r384/assets/gallery.css', __FILE__), array(), 'r384-reviewed-1', 'all');
    wp_enqueue_style('fv-apollo-r395-mobile-fit',
        plugins_url('assets/mobile-fit.css', __FILE__), array('fv-apollo-r384-gallery'),
        'r395-reviewed-1', 'screen');
}

if (function_exists('add_action')) {
    // Enqueue BEFORE wp_head. Priority 99 follows the original gallery's 5.
    add_action('wp_enqueue_scripts', 'fv_r395_enqueue_prepaint', 99);
}
