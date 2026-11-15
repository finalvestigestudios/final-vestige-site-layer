<?php
/**
 * Apollo R385: optional read-only pre-head asset guard for R384 source gallery.
 * Staging-only; never registers or replaces a shortcode, writes WP data, or tracks users.
 */
if (!defined('ABSPATH')) { exit; }

/** Inspect the *entire* bounded WordPress block graph, even after finding a match. */
function fv_r385_gallery_in_blocks(string $content): bool {
    if (!function_exists('parse_blocks') || !function_exists('get_post')
      || !function_exists('has_shortcode') || !defined('FV_R384_TAG')) { return false; }
    $active = array(); $visited = array(); $nodes = 0; $bytes = 0;
    $found = false; $invalid = false;
    $scan = static function (string $fragment, int $depth) use (&$scan, &$active, &$visited, &$nodes, &$bytes, &$found, &$invalid): void {
        $bytes += strlen($fragment);
        if ($invalid || $depth > 7 || $bytes > 1048576) { $invalid = true; return; }
        try { $blocks = parse_blocks($fragment); } catch (Throwable $e) { $invalid = true; return; }
        if (!is_array($blocks)) { $invalid = true; return; }
        $walk = static function (array $parts, int $depth) use (&$walk, &$scan, &$active, &$visited, &$nodes, &$found, &$invalid): void {
            if ($invalid || $depth > 7) { $invalid = true; return; }
            foreach ($parts as $block) {
                if (!is_array($block) || ++$nodes > 200) { $invalid = true; return; }
                $kind = $block['blockName'] ?? null;
                $inner = $block['innerHTML'] ?? null;
                if (!is_string($inner)) { $invalid = true; return; }
                // Examples and raw code cannot authorize the stylesheet.
                if (!in_array($kind, array('core/code','core/preformatted','core/html'), true)
                  && has_shortcode($inner, FV_R384_TAG)) { $found = true; }
                if ($kind === 'core/block') {
                    $ref = $block['attrs']['ref'] ?? null;
                    if (!is_int($ref) || $ref < 1 || isset($active[$ref])) { $invalid = true; return; }
                    if (!isset($visited[$ref])) {
                        $post = get_post($ref);
                        if (!is_object($post) || ($post->post_type ?? '') !== 'wp_block'
                          || ($post->post_status ?? '') !== 'publish'
                          || !is_string($post->post_content ?? null)) { $invalid = true; return; }
                        $active[$ref] = true;
                        $scan($post->post_content, $depth + 1);
                        unset($active[$ref]);
                        if ($invalid) { return; }
                        $visited[$ref] = true;
                    }
                }
                $children = $block['innerBlocks'] ?? array();
                if (!is_array($children)) { $invalid = true; return; }
                $walk($children, $depth + 1);
                if ($invalid) { return; }
            }
        };
        $walk($blocks, $depth);
    };
    $scan($content, 0);
    return $found && !$invalid;
}

function fv_r385_gallery_owner(): bool {
    return defined('FV_R384_TAG') && function_exists('shortcode_exists')
      && shortcode_exists(FV_R384_TAG) && isset($GLOBALS['shortcode_tags'][FV_R384_TAG])
      && $GLOBALS['shortcode_tags'][FV_R384_TAG] === 'fv_r384_shortcode';
}

function fv_r385_prehead_assets(): void {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()
      || !function_exists('fv_r384_records') || fv_r384_records() === false
      || !function_exists('fv_r384_assets_verified') || !fv_r384_assets_verified()
      || !fv_r385_gallery_owner() || !function_exists('is_singular') || !is_singular()
      || !function_exists('get_queried_object_id') || !function_exists('get_post')
      || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    $post = get_post((int) get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null)
      || !fv_r385_gallery_in_blocks($post->post_content)) { return; }
    $gallery = dirname(__DIR__) . '/apollo-r384/document-gallery.php';
    $css = dirname(__DIR__) . '/apollo-r384/assets/gallery.css';
    if (!is_file($gallery) || is_link($gallery) || !is_file($css) || is_link($css)) { return; }
    if (!function_exists('wp_style_is') || !wp_style_is('fv-apollo-r384-gallery','enqueued')) {
        wp_enqueue_style('fv-apollo-r384-gallery',plugins_url('assets/gallery.css',$gallery),array(),'r384-reviewed-1');
    }
}

if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (function_exists('fv_r377_environment') && fv_r377_environment()
          && fv_r385_gallery_owner()) {
            add_action('wp_enqueue_scripts','fv_r385_prehead_assets',2);
        }
    },90);
}
