<?php
/**
 * Plugin Name: FV Apollo R379 — Template-Part CSS Custody (Staging Research)
 * Description: Optional read-only companion for R377/R378 on an approved staging host. Not production approved.
 * Version: 0.0.1-r379-research
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/** Read only the actual resolved block template, never crawl unrelated site templates. */
function fv_r379_current_template(): ?object {
    if (!function_exists('get_stylesheet') || !function_exists('get_block_template')) { return null; }
    $theme = get_stylesheet();
    $id = $GLOBALS['_wp_current_template_id'] ?? null;
    if (!is_string($theme) || !preg_match('/^[a-zA-Z0-9_-]{1,80}$/D', $theme)
        || !is_string($id) || !preg_match('/^[a-zA-Z0-9_-]{1,80}\/\/[a-zA-Z0-9_-]{1,100}$/D', $id)
        || strpos($id, $theme . '//') !== 0) { return null; }
    $template = get_block_template($id, 'wp_template');
    return fv_r379_verified_template($template, $id, $theme, 'wp_template') ? $template : null;
}

/** Trust the resolved WordPress identity, not only an untrusted slug or block attribute. */
function fv_r379_verified_template($t, string $id, string $theme, string $type): bool {
    if (!is_object($t) || ($t->id ?? null) !== $id || ($t->theme ?? null) !== $theme
        || ($t->type ?? null) !== $type || !is_string($t->content ?? null)
        || strlen($t->content) > 1024 * 1024 || ($t->status ?? 'publish') !== 'publish') { return false; }
    return true;
}

/**
 * Bounded, read-only graph walk over *renderable block contents* in one resolved template.
 * WordPress dynamic blocks and arbitrary PHP/template render callbacks are intentionally not guessed.
 */
function fv_r379_template_contains_shortcode(object $template): bool {
    if (!function_exists('parse_blocks') || !function_exists('get_block_template')
        || !function_exists('get_stylesheet') || !function_exists('has_shortcode')
        || !function_exists('get_post')) { return false; }
    $theme = get_stylesheet();
    $visited = array(); $nodes = 0; $bytes = 0; $invalid = false; $found = false;
    $inspect = static function (string $content, int $depth) use (&$inspect, &$visited, &$nodes, &$bytes, &$invalid, &$found, $theme): bool {
        $bytes += strlen($content);
        if ($invalid || $depth > 7 || $bytes > 1024 * 1024) { $invalid = true; return false; }
        $blocks = parse_blocks($content);
        if (!is_array($blocks)) { $invalid = true; return false; }
        $walk = static function (array $parts, int $level) use (&$walk, &$inspect, &$visited, &$nodes, &$invalid, &$found, $theme): bool {
            if ($invalid || $level > 7) { $invalid = true; return false; }
            foreach ($parts as $block) {
                if (!is_array($block) || ++$nodes > 200) { $invalid = true; return false; }
                $name = $block['blockName'] ?? null;
                // A markup sample inside core/code/preformatted isn't an executable shortcode.
                if (!in_array($name, array('core/code', 'core/preformatted'), true)) {
                    $html = $block['innerHTML'] ?? '';
                    if (is_string($html) && has_shortcode($html, FV_R377_TAG)) { $found = true; }
                }
                if ($name === 'core/block') {
                    $ref = $block['attrs']['ref'] ?? null;
                    if (!is_int($ref) || $ref <= 0) { continue; }
                    $key = 'b:' . $ref;
                    if (isset($visited[$key])) { continue; }
                    $visited[$key] = true;
                    $post = get_post($ref);
                    if (is_object($post) && ($post->post_type ?? null) === 'wp_block'
                        && ($post->post_status ?? null) === 'publish'
                        && is_string($post->post_content ?? null)
                         ) { $inspect($post->post_content, $level + 1); }
                }
                if ($name === 'core/template-part') {
                    $attrs = $block['attrs'] ?? array();
                    if (!is_array($attrs)) { $invalid = true; return false; }
                    $slug = $attrs['slug'] ?? null;
                    if (!is_string($slug) || !preg_match('/^[a-zA-Z0-9_-]{1,100}$/D', $slug)
                        || (isset($attrs['theme']) && $attrs['theme'] !== $theme)) { continue; }
                    $id = $theme . '//' . $slug; $key = 't:' . $id;
                    if (isset($visited[$key])) { continue; }
                    $visited[$key] = true;
                    $part = get_block_template($id, 'wp_template_part');
                    if (fv_r379_verified_template($part, $id, $theme, 'wp_template_part')
                         ) { $inspect($part->content, $level + 1); }
                }
                $children = $block['innerBlocks'] ?? array();
                if (!is_array($children)) { $invalid = true; return false; }
                $walk($children, $level + 1);
            }
            return false;
        };
        $walk($blocks, $depth);
        return $found;
    };
    $inspect((string)$template->content, 0);
    return $found && !$invalid;
}

/** Idempotent, pre-head asset handling, shared with the reviewed R377/R378 handle. */
function fv_r379_prehead_enqueue(): void {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()
        || !function_exists('fv_r378_r377_owner') || !fv_r378_r377_owner()
        || !function_exists('fv_r378_css_asset') || fv_r378_css_asset() === null
        || !function_exists('fv_r377_records') || fv_r377_records() === null
        || !function_exists('is_singular') || !is_singular()
        || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    $template = fv_r379_current_template();
    if ($template === null || !fv_r379_template_contains_shortcode($template)) { return; }
    if (function_exists('wp_style_is') && wp_style_is('fv-apollo-r377-source-role', 'enqueued')) { return; }
    wp_enqueue_style('fv-apollo-r377-source-role',
        plugins_url('assets/source-role.css', dirname(__DIR__) . '/apollo-r377/source-role-desk.php'),
        array(), 'r377-sealed-' . substr(FV_R378_SHA256_CSS, 0, 12));
}

if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (function_exists('fv_r377_environment') && fv_r377_environment()
            && function_exists('fv_r378_r377_owner') && fv_r378_r377_owner()) {
            add_action('wp_enqueue_scripts', 'fv_r379_prehead_enqueue', 3);
        }
    }, 70);
}
