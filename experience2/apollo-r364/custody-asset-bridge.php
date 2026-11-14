<?php
/**
 * Apollo R364 — pre-head nested custody asset discovery, STAGING ONLY.
 * Handles post content, reusable WP blocks, same-theme template parts,
 * explicitly assigned block templates and the verified R359 captured resolved canvas.
 * READ ONLY. Never modifies content/settings, enqueues tracking or gates evidence.
 * This is a companion adapter, not a replacement for the WordPress release gates.
 */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r364_is_audit(string $content): bool {
    foreach (array('fv_apollo_custody_guard_r363') as $tag) {
        if (function_exists('has_shortcode')) {
            if (has_shortcode($content, $tag)) { return true; }
        } elseif (preg_match('/\[' . preg_quote($tag, '/') . '(?=[\s\]\/])/', $content)) {
            return true;
        }
    }
    return false;
}
/**
 * Return [contains source custody, complete bounded traversal]. A traversal error
 * cannot authorize an asset. Shared node/byte/reference budgets stop loops.
 */
function fv_apollo_r364_scan(string $content, array &$seen, array &$budget, int $depth = 0): array {
    $budget['bytes'] += strlen($content);
    if ($depth > 6 || $budget['bytes'] > 500000 || $budget['nodes'] > 128 || count($seen) > 48) {
        return array(false, false);
    }
    $found = fv_apollo_r364_is_audit($content);
    if (!function_exists('parse_blocks')) { return array($found, true); }
    $blocks = parse_blocks($content);
    if (!is_array($blocks)) { return array(false, false); }
    $theme = function_exists('get_stylesheet') ? (string)get_stylesheet() : '';
    $walk = static function(array $nodes, int $depth) use (&$walk, &$seen, &$budget, &$found, $theme): bool {
        if ($depth > 6) { return false; }
        foreach ($nodes as $b) {
            ++$budget['nodes'];
            if ($budget['nodes'] > 128 || !is_array($b)) { return false; }
            $type = $b['blockName'] ?? '';
            $nested = null; $key = null;
            if ($type === 'core/block' && function_exists('get_post')) {
                $ref = $b['attrs']['ref'] ?? null;
                if (is_int($ref) && $ref > 0 && $ref <= 2147483647) {
                    $key = 'block:' . $ref;
                    if (!isset($seen[$key])) {
                        $post = get_post($ref);
                        if (is_object($post) && ($post->post_type ?? '') === 'wp_block'
                            && isset($post->post_content) && is_string($post->post_content)) {
                            $nested = $post->post_content;
                        }
                    }
                }
            } elseif ($type === 'core/template-part' && function_exists('get_block_template')
                && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $theme)) {
                $slug = $b['attrs']['slug'] ?? null;
                $declaredTheme = $b['attrs']['theme'] ?? $theme;
                if (is_string($slug) && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $slug)
                    && $declaredTheme === $theme) {
                    $id = $theme . '//' . $slug;
                    $key = 'part:' . $id;
                    if (!isset($seen[$key])) {
                        $part = get_block_template($id, 'wp_template_part');
                        if (is_object($part) && isset($part->content) && is_string($part->content)
                            && (!isset($part->id) || $part->id === $id)
                            && (!isset($part->slug) || $part->slug === $slug)
                            && (!isset($part->theme) || $part->theme === $theme)) {
                            $nested = $part->content;
                        }
                    }
                }
            }
            if ($nested !== null && $key !== null) {
                if (count($seen) >= 48) { return false; }
                $seen[$key] = true; // revisiting a reference must never recurse infinitely
                [$childFound, $complete] = fv_apollo_r364_scan($nested, $seen, $budget, $depth + 1);
                if (!$complete) { return false; }
                $found = $found || $childFound;
            }
            if (isset($b['innerBlocks']) && is_array($b['innerBlocks'])
                && !$walk($b['innerBlocks'], $depth + 1)) { return false; }
        }
        return true;
    };
    if (!$walk($blocks, $depth)) { return array(false, false); }
    return array($found, true);
}
/** Do not confuse a detected shortcode with actual release/editorial approval. */
function fv_apollo_r364_usage(): array {
    if (!function_exists('is_singular') || !is_singular()
        || !function_exists('get_post')) { return array(false, 'ineligible'); }
    $p = get_post();
    if (!is_object($p) || !isset($p->post_content) || !is_string($p->post_content)) {
        return array(false, 'post-unavailable');
    }
    $sources = array($p->post_content);
    // Already-resolved canvas is recorded and attested by R359; no hierarchy guessing.
    if (function_exists('fv_apollo_r359_resolved_usage')) {
        $r359 = fv_apollo_r359_resolved_usage();
        if (!empty($r359[2]) && isset($GLOBALS['fv_apollo_r359_snapshot']['content'])
            && ($GLOBALS['fv_apollo_r359_snapshot']['theme'] ?? null) === get_stylesheet()
            && ($GLOBALS['_wp_current_template_id'] ?? null) === ($GLOBALS['fv_apollo_r359_snapshot']['id'] ?? null)
            && ($GLOBALS['_wp_current_template_content'] ?? null) === $GLOBALS['fv_apollo_r359_snapshot']['content']
            && hash('sha256', (string)$GLOBALS['fv_apollo_r359_snapshot']['content']) === ($GLOBALS['fv_apollo_r359_snapshot']['digest'] ?? null)) {
            $sources[] = $GLOBALS['fv_apollo_r359_snapshot']['content'];
        }
    }
    // Explicitly assigned custom template: verify same-theme slug, ID and content.
    if (function_exists('get_page_template_slug') && function_exists('fv_apollo_r358_template_slug')
        && function_exists('get_stylesheet') && function_exists('get_block_template')) {
        $slug = fv_apollo_r358_template_slug(get_page_template_slug($p));
        $theme = (string)get_stylesheet();
        if ($slug !== null && preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $theme)) {
            $id = $theme . '//' . $slug;
            $tpl = get_block_template($id, 'wp_template');
            if (is_object($tpl) && isset($tpl->content) && is_string($tpl->content)
                && ($tpl->id ?? null) === $id && ($tpl->slug ?? null) === $slug
                && ($tpl->theme ?? null) === $theme) {
                $sources[] = $tpl->content;
            }
        }
    }
    $seen = array(); $budget = array('bytes' => 0, 'nodes' => 0);
    $found = false;
    foreach ($sources as $source) {
        [$has, $complete] = fv_apollo_r364_scan($source, $seen, $budget);
        if (!$complete) { return array(false, 'bounded-traversal-incomplete'); }
        $found = $found || $has;
    }
    return array($found, $found ? 'reviewed-shortcode-found' : 'not-present');
}
function fv_apollo_r364_enqueue(): void {
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    [$found] = fv_apollo_r364_usage();
    if (!$found) { return; }
    $file = dirname(__DIR__) . '/apollo-r362/assets/research-crosswalk.css';
    if (!is_readable($file)) { return; }
    // Same handle as R363: native WordPress dedupes direct-post and embedded requests.
    wp_enqueue_style('fv-apollo-r362-crosswalk', plugins_url('../apollo-r362/assets/research-crosswalk.css', __FILE__), array(), '0.0.1-research');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_apollo_r364_enqueue', 19); }
