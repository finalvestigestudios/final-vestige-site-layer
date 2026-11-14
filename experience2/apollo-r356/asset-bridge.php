<?php
/**
 * Apollo R356 — research-only, demand-scoped shortcode asset bridge.
 * No WordPress writes, live deployment, tracking, network access or commerce.
 * Prevents a standalone post-fire source note from loading the entire Atlas.
 */
if (!defined('ABSPATH')) { exit; }
$upstream = dirname(__DIR__) . '/apollo-r355/postfire-ledger.php';
if (is_readable($upstream)) { require_once $upstream; }

function fv_apollo_r356_experience($atts = array()): string {
    if (function_exists('fv_apollo_r355_experience_shortcode')) {
        return fv_apollo_r355_experience_shortcode($atts);
    }
    return '<p>The evidence experience is temporarily unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_apollo_r356_postfire($atts = array()): string {
    if (function_exists('fv_apollo_r355_postfire_shortcode')) {
        return fv_apollo_r355_postfire_shortcode($atts);
    }
    return '<p>Post-fire source details are unavailable pending review.</p>';
}
/** Returns [composite, note] for direct and bounded reusable-block content. */
function fv_apollo_r356_usage(string $content, array &$seen = array(), int $depth = 0): array {
    if (strlen($content) > 500000 || $depth > 5) { return array(false, false); }
    $has = static function(string $tag) use ($content): bool {
        return function_exists('has_shortcode')
            ? (bool)has_shortcode($content, $tag)
            : (bool)preg_match('/\[' . preg_quote($tag, '/') . '(?=[\s\]\/])/', $content);
    };
    $usage = array($has('fv_apollo_experience_r356'), $has('fv_apollo_postfire_r356'));
    if ($usage[0] && $usage[1]) { return $usage; }
    if (!function_exists('parse_blocks') || $depth >= 5) { return $usage; }
    $walk = static function(array $blocks) use (&$walk, &$usage, &$seen, $depth): void {
        foreach ($blocks as $block) {
            if (!is_array($block)) { continue; }
            if (($block['blockName'] ?? '') === 'core/block' && function_exists('get_post')) {
                $ref = (int)($block['attrs']['ref'] ?? 0);
                if ($ref > 0 && !isset($seen[$ref]) && count($seen) < 24) {
                    $seen[$ref] = true;
                    $post = get_post($ref);
                    if (is_object($post) && ($post->post_type ?? '') === 'wp_block') {
                        $nested = fv_apollo_r356_usage((string)($post->post_content ?? ''), $seen, $depth + 1);
                        $usage[0] = $usage[0] || $nested[0];
                        $usage[1] = $usage[1] || $nested[1];
                    }
                }
            }
            if (isset($block['innerBlocks']) && is_array($block['innerBlocks'])) {
                $walk($block['innerBlocks']);
            }
        }
    };
    $walk(parse_blocks($content));
    return $usage;
}
function fv_apollo_r356_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post') || !function_exists('wp_enqueue_style')) { return; }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content)) { return; }
    $seen = array(); $usage = fv_apollo_r356_usage((string)$post->post_content, $seen);
    if (!$usage[0] && !$usage[1]) { return; }
    $root = dirname(__DIR__);
    $note = array('fv-apollo-r355-postfire', 'apollo-r355/postfire-ledger.css');
    $composite = array(
        array('fv-apollo-r339-chronology', 'apollo-r339/assets/chronology-rail.css'),
        array('fv-apollo-r340-gallery', 'apollo-r340/assets/accession-gallery.css'),
        array('fv-apollo-r345-evidence-plate', 'apollo-r345/evidence-plate.css'),
        array('fv-apollo-r347-index', 'apollo-r347/assets/source-index.css'),
        array('fv-apollo-r348-custody', 'apollo-r348/assets/source-custody.css'),
    );
    $print = array('fv-apollo-r356-print-proof', 'apollo-r356/assets/print-proof.css');
    $assets = $usage[0] ? array_merge($composite, array($note, $print)) : array($note, $print);
    foreach ($assets as $asset) {
        $absolute = $root . '/' . $asset[1];
        if (is_readable($absolute)) {
            wp_enqueue_style($asset[0], plugins_url('../' . $asset[1], __FILE__), array(), '0.0.1-research');
        }
    }
    if ($usage[0] && function_exists('wp_enqueue_script') && is_readable($root . '/apollo-r347/assets/source-index.js')) {
        wp_enqueue_script('fv-apollo-r347-index', plugins_url('../apollo-r347/assets/source-index.js', __FILE__), array(), '0.0.1-research', true);
    }
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_experience_r356', 'fv_apollo_r356_experience');
    add_shortcode('fv_apollo_postfire_r356', 'fv_apollo_r356_postfire');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_apollo_r356_enqueue', 18); }
