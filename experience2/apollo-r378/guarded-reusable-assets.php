<?php
/**
 * Plugin Name: Final Vestige Apollo R378 — Reusable Block CSS Custody (Staging Only)
 * Description: Optional read-only companion for R377. Never activate without approved WordPress staging.
 * Version: 0.0.1-r378-research
 * Requires PHP: 7.4
 *
 * Apollo R378, isolated *optional* WordPress staging companion for R377.
 * Problem: the R377 enqueue hook only checks post_content and misses a shortcode
 * inside a core/block reusable pattern, even while WordPress renders that pattern.
 * This file adds no shortcode, does not override R377's owners, and does not write
 * posts, settings, transients or anything else. No production activation permitted.
 */
if (!defined('ABSPATH')) { exit; }

const FV_R378_SHA256_CSS = '7a900dc0bf5e42fd527ccadddbed4d8f58138c87745ea96f55a991cda13bd8b3';
const FV_R378_TARGET = 'fv_apollo_source_role_desk_r377';

function fv_r378_css_asset(): ?string {
    // Fixed adjacent reviewed file, never a user-controlled path.
    $parent = dirname(__DIR__) . '/apollo-r377';
    $p = $parent . '/assets/source-role.css';
    if (!is_dir($parent) || is_link($parent) || is_link($parent . '/assets') || is_link($p)
        || realpath($parent) !== $parent || realpath($p) !== $p
        || !is_file($p) || !is_readable($p)) { return null; }
    $data = file_get_contents($p);
    return is_string($data) && hash_equals(FV_R378_SHA256_CSS, hash('sha256', $data)) ? $p : null;
}

/** Read-only bounded discovery; return false, not a guessed match, on malformed/cyclic references. */
function fv_r378_has_shortcode_in_blocks(string $content): bool {
    if (!function_exists('has_shortcode') || !function_exists('parse_blocks') || !function_exists('get_post')) {
        return false;
    }
    $seen = array(); $nodes = 0;
    $visit = static function (string $fragment, int $depth) use (&$visit, &$seen, &$nodes): bool {
        if ($depth > 6 || strlen($fragment) > 1024 * 1024) { return false; }
        // Preserve ordinary shortcodes, including core/shortcode and classic content.
        if (has_shortcode($fragment, FV_R378_TARGET)) { return true; }
        $blocks = parse_blocks($fragment);
        if (!is_array($blocks)) { return false; }
        $walk = static function (array $blocks, int $level) use (&$walk, &$visit, &$seen, &$nodes): bool {
            if ($level > 6) { return false; }
            foreach ($blocks as $block) {
                if (++$nodes > 200) { return false; }
                if (!is_array($block)) { return false; }
                if (($block['blockName'] ?? null) === 'core/block') {
                    $ref = $block['attrs']['ref'] ?? null;
                    if (!is_int($ref) || $ref <= 0 || isset($seen[$ref])) { continue; }
                    $seen[$ref] = true;
                    $post = get_post($ref);
                    if (is_object($post) && ($post->post_type ?? null) === 'wp_block'
                        && ($post->post_status ?? null) === 'publish'
                        && is_string($post->post_content ?? null)
                        && $visit($post->post_content, $level + 1)) { return true; }
                }
                if (isset($block['innerBlocks']) && is_array($block['innerBlocks'])
                    && $walk($block['innerBlocks'], $level + 1)) { return true; }
            }
            return false;
        };
        return $walk($blocks, $depth);
    };
    return $visit($content, 0);
}

function fv_r378_r377_owner(): bool {
    // wp shortcode ownership is global; avoid styling another plugin's identically named tag.
    return function_exists('shortcode_exists') && shortcode_exists(FV_R378_TARGET)
        && isset($GLOBALS['shortcode_tags'][FV_R378_TARGET])
        && $GLOBALS['shortcode_tags'][FV_R378_TARGET] === 'fv_r377_shortcode';
}

function fv_r378_prehead_enqueue(): void {
    // R377's exact host + environment gate is authoritative. No fallback guesses.
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()
        || !fv_r378_r377_owner()
        || !function_exists('is_singular') || !is_singular()
        || !function_exists('get_queried_object_id') || !function_exists('get_post')
        || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    $post = get_post((int) get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null)
        || !fv_r378_has_shortcode_in_blocks($post->post_content)) { return; }
    $asset = fv_r378_css_asset();
    if ($asset === null) { return; }
    if (function_exists('wp_style_is') && wp_style_is('fv-apollo-r377-source-role','enqueued')) { return; }
    wp_enqueue_style('fv-apollo-r377-source-role',
        plugins_url('assets/source-role.css', dirname(__DIR__) . '/apollo-r377/source-role-desk.php'),
        array(), 'r377-sealed-' . substr(FV_R378_SHA256_CSS, 0, 12));
}

// Register only after R377's own shortcode registration. Does not claim a shortcode name.
if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (function_exists('fv_r377_environment') && fv_r377_environment()
            && fv_r378_r377_owner()) {
            add_action('wp_enqueue_scripts', 'fv_r378_prehead_enqueue', 2);
        }
    }, 60);
}
