<?php
/**
 * Plugin Name: FV Apollo review custody — R277 staging adapter
 * Description: STAGING/REVIEW ONLY. Native shortcode for Apollo editorial custody; no approvals or tracking.
 * Version: 0.1.0
 * License: GPL-2.0-or-later
 *
 * Release gate: this file must not be activated on production without founder approval.
 * The authoritative evidence presentation lives in ../apollo-r273/review-custody.php.
 */
if (!defined('ABSPATH')) { return; }

const FV_R277_SHORTCODE = 'fv_apollo_review_custody';
const FV_R277_STYLE = 'fv-apollo-r277-review-custody';

/** Deliberately pinned to a *same-origin* sibling asset; no external scripts. */
function fv_r277_style_url(): string {
    return plugins_url('../apollo-r273/assets/review-custody.css', __FILE__);
}

/**
 * Read-only, bounded block walk for normal and reusable shortcode blocks.
 * Visibility is a *preload hint*, never an authorization or publication decision.
 * Dynamic/third-party blocks may be impossible to discover before wp_head;
 * the shortcode renderer supplies a late-loading, same-origin fallback link.
 */
function fv_r277_contains_shortcode(string $content, int $depth = 0, array &$seen = []): bool {
    if ($depth > 8) { return false; }
    if (has_shortcode($content, FV_R277_SHORTCODE)) { return true; }
    if (!function_exists('parse_blocks')) { return false; }
    foreach (parse_blocks($content) as $block) {
        if (fv_r277_block_contains($block, $depth, $seen)) { return true; }
    }
    return false;
}

function fv_r277_block_contains(array $block, int $depth, array &$seen): bool {
    if ($depth > 8) { return false; }
    foreach (['innerHTML', 'innerContent'] as $key) {
        $value = $block[$key] ?? null;
        if (is_string($value) && has_shortcode($value, FV_R277_SHORTCODE)) { return true; }
        if (is_array($value)) {
            foreach ($value as $segment) {
                if (is_string($segment) && has_shortcode($segment, FV_R277_SHORTCODE)) { return true; }
            }
        }
    }
    if (($block['blockName'] ?? null) === 'core/block') {
        $ref = $block['attrs']['ref'] ?? null;
        if (is_int($ref) && $ref > 0 && !isset($seen[$ref])) {
            $seen[$ref] = true; // cycles cannot recurse indefinitely
            $post = get_post($ref);
            if ($post && $post->post_type === 'wp_block' && $post->post_status === 'publish'
                && is_string($post->post_content)
                && fv_r277_contains_shortcode($post->post_content, $depth + 1, $seen)) { return true; }
        }
    }
    foreach (($block['innerBlocks'] ?? []) as $child) {
        if (is_array($child) && fv_r277_block_contains($child, $depth + 1, $seen)) { return true; }
    }
    return false;
}

/** WP head preflight; does not traverse unrelated posts or call external services. */
function fv_r277_enqueue_preflight(): void {
    if (!function_exists('is_singular') || !is_singular()) { return; }
    $id = get_queried_object_id();
    if (!$id) { return; }
    $post = get_post($id);
    if (!$post || !isset($post->post_content) || !is_string($post->post_content)) { return; }
    $seen = [];
    if (fv_r277_contains_shortcode($post->post_content, 0, $seen)) {
        wp_enqueue_style(FV_R277_STYLE, fv_r277_style_url(), [], 'r277');
    }
}

/**
 * All data shown here are *pending*. Unauthenticated shortcode attributes cannot
 * set review state, pass rights checks, change sources, or introduce merchant links.
 */
function fv_r277_render_shortcode($attributes = [], $unused_content = null): string {
    $source = __DIR__ . '/../apollo-r273/review-custody.php';
    if (!is_readable($source)) {
        return '<aside aria-label="Apollo 1 research custody"><p>The review panel is unavailable. The original records remain accessible.</p>'
            . '<p><a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">NASA Apollo 204 Review Board report</a></p>'
            . '<p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Free Apollo 1 investigation</a></p></aside>';
    }
    require_once $source;
    if (!function_exists('fv_ex2_r273_review_panel')) { return ''; }
    $html = fv_ex2_r273_review_panel([]); // Never trust client/user-controlled approval metadata.
    // Dynamic templates may render after wp_head. A static stylesheet link in the
    // shortcode body is HTML body-ok and works without JS under same-origin CSP.
    // Output only once, even if the shortcode is repeated on a page.
    static $fallback_printed = false;
    if (!$fallback_printed && (!function_exists('wp_style_is') || !wp_style_is(FV_R277_STYLE, 'done'))) {
        $fallback_printed = true;
        $href = htmlspecialchars(fv_r277_style_url(), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $html = '<link rel="stylesheet" href="' . $href . '">' . $html;
    }
    return $html;
}

add_action('wp_enqueue_scripts', 'fv_r277_enqueue_preflight', 20);
add_action('init', static function (): void {
    add_shortcode(FV_R277_SHORTCODE, 'fv_r277_render_shortcode');
});
