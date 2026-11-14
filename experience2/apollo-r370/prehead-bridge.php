<?php
/**
 * Apollo R370: early, opt-in, read-only CSS discovery for R369's educator bridge.
 * STAGING ONLY. Does not activate content, modify WordPress, create requests, or
 * override theme selection. Never assume a default template's shortcode content.
 * Requires separately included R365/R367/R368/R369 modules before registration.
 */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r370_has_shortcode(string $content): bool {
    if (strlen($content) > 500000) { return false; }
    if (function_exists('has_shortcode')) {
        return has_shortcode($content, 'fv_apollo_educator_bridge_r369');
    }
    // Conservative test-only substitute if WP helper is absent.
    return preg_match('/\[fv_apollo_educator_bridge_r369(?=[\s\]\/])/i', $content) === 1;
}

/** [present, complete] — all claims require a complete bounded traversal. */
function fv_apollo_r370_scan(string $content, array &$seen, array &$budget, int $depth = 0): array {
    $budget['bytes'] += strlen($content);
    if ($depth > 6 || $budget['bytes'] > 500000 || $budget['nodes'] > 128 || count($seen) > 48) {
        return array(false, false);
    }
    $found = fv_apollo_r370_has_shortcode($content);
    if (!function_exists('parse_blocks')) { return array($found, true); }
    $blocks = parse_blocks($content);
    if (!is_array($blocks)) { return array(false, false); }
    $theme = function_exists('get_stylesheet') ? (string)get_stylesheet() : '';
    $walk = static function(array $blocks, int $depth) use (&$walk, &$seen, &$budget, &$found, $theme): bool {
        if ($depth > 6) { return false; }
        foreach ($blocks as $block) {
            ++$budget['nodes'];
            if ($budget['nodes'] > 128 || !is_array($block)) { return false; }
            $kind = $block['blockName'] ?? null;
            $attrs = is_array($block['attrs'] ?? null) ? $block['attrs'] : array();
            $target = null; $key = null;
            if ($kind === 'core/block' && function_exists('get_post')) {
                $ref = $attrs['ref'] ?? null;
                if (is_int($ref) && $ref > 0 && $ref <= 2147483647) {
                    $key = 'block:' . $ref;
                    if (($seen[$key] ?? null) === 'active') { return false; } // Genuine cycle.
                    if (($seen[$key] ?? null) === 'complete') { continue; }
                    $p = get_post($ref);
                    if (is_object($p) && ($p->post_type ?? '') === 'wp_block'
                        && ($p->post_status ?? '') === 'publish' && is_string($p->post_content ?? null)) {
                        $target = $p->post_content;
                    }
                }
            } elseif ($kind === 'core/template-part' && function_exists('get_block_template')
                && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $theme)) {
                $slug = $attrs['slug'] ?? null;
                if (is_string($slug) && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $slug)
                    && ($attrs['theme'] ?? $theme) === $theme) {
                    $id = $theme . '//' . $slug;
                    $key = 'part:' . $id;
                    if (($seen[$key] ?? null) === 'active') { return false; }
                    if (($seen[$key] ?? null) === 'complete') { continue; }
                    $p = get_block_template($id, 'wp_template_part');
                    if (is_object($p) && ($p->id ?? null) === $id
                        && ($p->slug ?? null) === $slug && ($p->theme ?? null) === $theme
                        && is_string($p->content ?? null)) {
                        $target = $p->content;
                    }
                }
            }
            if ($target !== null && $key !== null) {
                if (count($seen) >= 48) { return false; }
                $seen[$key] = 'active';
                [$subFound, $complete] = fv_apollo_r370_scan($target, $seen, $budget, $depth + 1);
                if (!$complete) { return false; }
                $seen[$key] = 'complete';
                $found = $found || $subFound;
            }
            if (isset($block['innerBlocks'])) {
                if (!is_array($block['innerBlocks']) || !$walk($block['innerBlocks'], $depth + 1)) {
                    return false;
                }
            }
        }
        return true;
    };
    return $walk($blocks, $depth) ? array($found, true) : array(false, false);
}

function fv_apollo_r370_usage(): array {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')) {
        return array(false, 'not-singular');
    }
    $post = get_post();
    if (!is_object($post) || !is_string($post->post_content ?? null)) {
        return array(false, 'post-missing');
    }
    $sources = array($post->post_content);
    // Explicit custom template, exact theme/slug/content verified; never guess hierarchy.
    if (function_exists('get_page_template_slug') && function_exists('get_stylesheet')
        && function_exists('get_block_template')) {
        $raw = get_page_template_slug($post);
        $slug = is_string($raw) ? preg_replace('~^(?:templates/)?([a-zA-Z0-9_-]{1,80})(?:\.html)?$~D', '$1', $raw) : null;
        $theme = (string)get_stylesheet();
        if (is_string($slug) && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $slug)
            && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $theme)) {
            $id = $theme . '//' . $slug;
            $template = get_block_template($id, 'wp_template');
            if (is_object($template) && ($template->id ?? null) === $id
                && ($template->slug ?? null) === $slug && ($template->theme ?? null) === $theme
                && is_string($template->content ?? null)) {
                $sources[] = $template->content;
            }
        }
    }
    // R359's independently resolved block canvas is usable only when identity and
    // content still match the exact snapshot from template_include.
    $snapshot = $GLOBALS['fv_apollo_r359_snapshot'] ?? null;
    if (is_array($snapshot) && function_exists('get_stylesheet')
        && ($snapshot['theme'] ?? null) === get_stylesheet()
        && ($GLOBALS['_wp_current_template_id'] ?? null) === ($snapshot['id'] ?? null)
        && ($GLOBALS['_wp_current_template_content'] ?? null) === ($snapshot['content'] ?? null)
        && is_string($snapshot['content'] ?? null)
        && hash('sha256', $snapshot['content']) === ($snapshot['digest'] ?? null)) {
        $sources[] = $snapshot['content'];
    }
    $seen = array(); $budget = array('bytes' => 0, 'nodes' => 0); $found = false;
    foreach ($sources as $source) {
        [$contains, $complete] = fv_apollo_r370_scan($source, $seen, $budget);
        if (!$complete) { return array(false, 'incomplete-scan'); }
        $found = $found || $contains;
    }
    return array($found, $found ? 'verified-shortcode-present' : 'not-found');
}

function fv_apollo_r370_enqueue(): void {
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    [$present] = fv_apollo_r370_usage();
    if (!$present) { return; }
    $assets = array(
        array('fv-apollo-r365-chronology', 'apollo-r365/assets/chrono-rail.css', array()),
        array('fv-apollo-r367-sequence', 'apollo-r367/assets/sequence-gate.css', array('fv-apollo-r365-chronology')),
        array('fv-apollo-r368-reflow', 'apollo-r368/assets/reflow.css', array('fv-apollo-r367-sequence')),
        array('fv-apollo-r369-educator-bridge', 'apollo-r369/assets/evidence-bridge.css', array('fv-apollo-r368-reflow')),
    );
    $root = dirname(__DIR__);
    // All-or-nothing source asset availability: avoid partially styled evidence.
    foreach ($assets as $asset) { if (!is_readable($root . '/' . $asset[1])) { return; } }
    foreach ($assets as $asset) {
        wp_enqueue_style($asset[0], plugins_url('../' . $asset[1], __FILE__), $asset[2], 'r370-staging-1');
    }
}
if (function_exists('add_action')) {
    // Before inherited R365 (20) and R368 (30) enqueue; all handles are deduped by WP.
    add_action('wp_enqueue_scripts', 'fv_apollo_r370_enqueue', 12);
}
