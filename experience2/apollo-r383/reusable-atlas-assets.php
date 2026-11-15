<?php
/**
 * Plugin Name: FV Apollo R383 — Evidence Atlas Reusable Block Assets (staging only)
 * Description: Optional read-only pre-head CSS/JS loader for R381 Atlas nested in reusable WordPress blocks.
 * Version: 0.0.1-r383-research
 * Requires PHP: 7.4
 *
 * Does not register shortcodes, touch WordPress data, alter the homepage, or run on production.
 * Requires the original owner and source-custody contracts; refuses uncertain graphs.
 */
if (!defined('ABSPATH')) { exit; }

/** Return true only when a complete bounded, renderable graph contains the reviewed Atlas shortcode. */
function fv_r383_atlas_in_blocks(string $content): bool {
    if (!function_exists('parse_blocks') || !function_exists('get_post') || !function_exists('has_shortcode')) { return false; }
    $active = array(); $visited = array(); $nodes = 0; $bytes = 0; $found = false; $invalid = false;
    $scan = static function (string $fragment, int $depth) use (&$scan, &$active, &$visited, &$nodes, &$bytes, &$found, &$invalid): void {
        $bytes += strlen($fragment);
        if ($invalid || $depth > 7 || $bytes > 1024 * 1024) { $invalid = true; return; }
        $blocks = parse_blocks($fragment);
        if (!is_array($blocks)) { $invalid = true; return; }
        $walk = static function (array $parts, int $level) use (&$walk, &$scan, &$active, &$visited, &$nodes, &$found, &$invalid): void {
            if ($invalid || $level > 7) { $invalid = true; return; }
            foreach ($parts as $block) {
                if (!is_array($block) || ++$nodes > 200) { $invalid = true; return; }
                $kind = $block['blockName'] ?? null;
                // Code examples must never be treated as executable shortcodes.
                if (!in_array($kind, array('core/code','core/preformatted'), true)) {
                    $html = $block['innerHTML'] ?? null;
                    if (!is_string($html)) { $invalid = true; return; }
                    if (has_shortcode($html, FV_R381_TAG)) { $found = true; }
                }
                if ($kind === 'core/block') {
                    $ref = $block['attrs']['ref'] ?? null;
                    if (!is_int($ref) || $ref < 1) { $invalid = true; return; }
                    if (isset($active[$ref])) { $invalid = true; return; }
                    if (!isset($visited[$ref])) {
                        $post = get_post($ref);
                        if (!is_object($post) || ($post->post_type ?? '') !== 'wp_block'
                          || ($post->post_status ?? '') !== 'publish'
                          || !is_string($post->post_content ?? null)) { $invalid = true; return; }
                        $active[$ref] = true;
                        $scan($post->post_content, $level + 1);
                        unset($active[$ref]);
                        if ($invalid) { return; }
                        $visited[$ref] = true;
                    }
                }
                $children = $block['innerBlocks'] ?? array();
                if (!is_array($children)) { $invalid = true; return; }
                $walk($children, $level + 1);
                if ($invalid) { return; }
            }
        };
        $walk($blocks, $depth);
    };
    $scan($content, 0);
    return $found && !$invalid;
}

function fv_r383_atlas_owner(): bool {
    return function_exists('shortcode_exists') && shortcode_exists(FV_R381_TAG)
      && isset($GLOBALS['shortcode_tags'][FV_R381_TAG])
      && $GLOBALS['shortcode_tags'][FV_R381_TAG] === 'fv_r381_shortcode';
}

/** Enqueue on the normal pre-head hook, even if the shortcode lives inside a core/block ref. */
function fv_r383_prehead_assets(): void {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()
      || !function_exists('fv_r381_assets_verified') || !fv_r381_assets_verified()
      || !function_exists('fv_r377_records') || !function_exists('fv_r381_approved')
      || !fv_r381_approved(fv_r377_records()) || !fv_r383_atlas_owner()
      || !function_exists('is_singular') || !is_singular()
      || !function_exists('get_queried_object_id') || !function_exists('get_post')
      || !function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script')
      || !function_exists('plugins_url')) { return; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null)
      || !fv_r383_atlas_in_blocks($post->post_content)) { return; }
    $source = dirname(__DIR__) . '/apollo-r381/atlas.php';
    $assets = dirname(__DIR__) . '/apollo-r381/assets';
    if (!is_file($source) || is_link($source) || !is_dir($assets) || is_link($assets)) { return; }
    if (!function_exists('wp_style_is') || !wp_style_is('fv-apollo-r381-atlas','enqueued')) {
        wp_enqueue_style('fv-apollo-r381-atlas',plugins_url('assets/atlas.css',$source),array(),'r381-sealed-1');
    }
    if (!function_exists('wp_script_is') || !wp_script_is('fv-apollo-r381-atlas','enqueued')) {
        wp_enqueue_script('fv-apollo-r381-atlas',plugins_url('assets/atlas.js',$source),array(),'r381-sealed-1',true);
    }
}

if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (function_exists('fv_r377_environment') && fv_r377_environment()
          && defined('FV_R381_TAG') && fv_r383_atlas_owner()) {
            add_action('wp_enqueue_scripts','fv_r383_prehead_assets',2);
        }
    },65);
}
