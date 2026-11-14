<?php
/**
 * Apollo R370: pre-head, read-only WordPress asset discovery for the R369 bridge.
 * STAGING ONLY; include explicitly in an approved staging plugin, not in production.
 * No page edits, remote calls, output buffering, cache writes, or analytics.
 */
if (!defined('ABSPATH')) { exit; }

/** Scan only WordPress-authored shortcode payloads, not untrusted remote input. */
function fv_apollo_r370_has_tag(string $text): bool {
    return function_exists('has_shortcode')
        ? has_shortcode($text, 'fv_apollo_educator_bridge_r369')
        : preg_match('/\[fv_apollo_educator_bridge_r369(?:\s|\]|\/)/i', $text) === 1;
}

/** Bounded parser for reusable blocks and same-theme template parts. */
function fv_apollo_r370_scan(string $content, array &$seen, int $depth=0, int &$budget=128): bool {
    if ($depth > 7 || $budget <= 0 || strlen($content) > 250000) { return false; }
    $budget--;
    if (fv_apollo_r370_has_tag($content)) { return true; }
    if (!function_exists('parse_blocks')) { return false; }
    $blocks = parse_blocks($content);
    if (!is_array($blocks)) { return false; }
    $walk = static function (array $items, int $level) use (&$walk, &$seen, &$budget): bool {
        if ($level > 7 || $budget <= 0) { return false; }
        foreach ($items as $block) {
            if (--$budget < 0) { return false; }
            if (!is_array($block)) { continue; }
            if (isset($block['innerHTML']) && is_string($block['innerHTML'])
                && fv_apollo_r370_has_tag($block['innerHTML'])) { return true; }
            $name = $block['blockName'] ?? '';
            $attrs = is_array($block['attrs'] ?? null) ? $block['attrs'] : array();
            if ($name === 'core/block' && isset($attrs['ref']) && is_numeric($attrs['ref'])
                && function_exists('get_post')) {
                $id = (int)$attrs['ref'];
                if ($id > 0 && !isset($seen['block:'.$id])) {
                    $seen['block:'.$id] = true;
                    $post = get_post($id);
                    if (is_object($post) && ($post->post_type ?? '') === 'wp_block'
                        && is_string($post->post_content ?? null)
                        && fv_apollo_r370_scan($post->post_content, $seen, $level+1, $budget)) { return true; }
                }
            }
            if ($name === 'core/template-part' && function_exists('get_block_template')
                && function_exists('get_stylesheet')) {
                $slug = $attrs['slug'] ?? null;
                $theme = $attrs['theme'] ?? get_stylesheet();
                if (is_string($slug) && preg_match('/^[a-z0-9][a-z0-9_-]{0,95}$/D', $slug)
                    && is_string($theme) && $theme === get_stylesheet()) {
                    $id = $theme . '//' . $slug;
                    if (!isset($seen['part:'.$id])) {
                        $seen['part:'.$id] = true;
                        $tpl = get_block_template($id, 'wp_template_part');
                        if (is_object($tpl) && ($tpl->id ?? '') === $id
                            && is_string($tpl->content ?? null)
                            && fv_apollo_r370_scan($tpl->content, $seen, $level+1, $budget)) { return true; }
                    }
                }
            }
            if (is_array($block['innerBlocks'] ?? null)
                && $walk($block['innerBlocks'], $level+1)) { return true; }
        }
        return false;
    };
    return $walk($blocks, $depth);
}

/** Only the resolved template identity is accepted; never guess hierarchy. */
function fv_apollo_r370_needs_assets(): bool {
    if ((function_exists('is_admin') && is_admin())
        || (function_exists('is_singular') && !is_singular())
        || !function_exists('get_queried_object_id') || !function_exists('get_post')) { return false; }
    $id = (int)get_queried_object_id();
    $post = $id > 0 ? get_post($id) : null;
    if (!is_object($post) || !is_string($post->post_content ?? null)) { return false; }
    $seen = array(); $budget = 128;
    if (fv_apollo_r370_scan($post->post_content, $seen, 0, $budget)) { return true; }
    // WordPress sets this once it has selected a real block template. If absent,
    // do not invent a `page`, `single`, `front-page`, or `index` match.
    $resolved = $GLOBALS['_wp_current_template_id'] ?? null;
    if (!is_string($resolved) || !function_exists('get_stylesheet')
        || !function_exists('get_block_template')) { return false; }
    $prefix = get_stylesheet() . '//';
    if (strpos($resolved, $prefix) !== 0 || strlen($resolved) <= strlen($prefix)) { return false; }
    $tpl = get_block_template($resolved, 'wp_template');
    if (!is_object($tpl) || ($tpl->id ?? '') !== $resolved
        || !is_string($tpl->content ?? null)) { return false; }
    return fv_apollo_r370_scan($tpl->content, $seen, 0, $budget);
}

/** All CSS in wp_head, not during a potentially late shortcode rendering. */
function fv_apollo_r370_prehead(): void {
    if (!fv_apollo_r370_needs_assets() || !function_exists('wp_enqueue_style')
        || !function_exists('plugins_url')) { return; }
    $root = dirname(__DIR__);
    $files = array(
        'fv-apollo-r365-chronology' => array('apollo-r365/chrono-rail.php','assets/chrono-rail.css',array()),
        'fv-apollo-r367-sequence' => array('apollo-r367/sealed-chronology.php','assets/sequence-gate.css',array('fv-apollo-r365-chronology')),
        'fv-apollo-r368-reflow' => array('apollo-r368/reflow-adapter.php','assets/reflow.css',array('fv-apollo-r367-sequence')),
        'fv-apollo-r369-educator-bridge' => array('apollo-r369/evidence-bridge.php','assets/evidence-bridge.css',array('fv-apollo-r368-reflow')),
    );
    foreach ($files as $handle=>$def) {
        if (function_exists('wp_style_is') && (wp_style_is($handle, 'enqueued') || wp_style_is($handle, 'done'))) { continue; }
        $source = $root . '/' . $def[0];
        if (!is_readable($source) || !is_readable(dirname($source) . '/' . $def[1])) { return; }
        wp_enqueue_style($handle, plugins_url($def[1], $source), $def[2], 'r370-stage-1');
    }
}
if (function_exists('add_action')) {
    add_action('wp_enqueue_scripts', 'fv_apollo_r370_prehead', 1);
}
