<?php
/**
 * Apollo R357 — staging-only WordPress template-part-aware asset discovery.
 * Read-only. Does not publish, add tracking, change options, or initiate commerce.
 * Complements, never modifies, frozen homepage PR #49 or Research Desk PR #158.
 */
if (!defined('ABSPATH')) { exit; }
$upstream = dirname(__DIR__) . '/apollo-r355/postfire-ledger.php';
if (is_readable($upstream)) { require_once $upstream; }

function fv_apollo_r357_full($atts = array()): string {
    return function_exists('fv_apollo_r355_experience_shortcode')
        ? fv_apollo_r355_experience_shortcode($atts)
        : '<p>Evidence components are unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_apollo_r357_note($atts = array()): string {
    return function_exists('fv_apollo_r355_postfire_shortcode')
        ? fv_apollo_r355_postfire_shortcode($atts)
        : '<p>Later NASA evidence is unavailable pending editorial review.</p>';
}

/**
 * Return [full experience, later-source note, traversal complete].
 * Only a literal approved shortcode, saved wp_block, or same-theme template part can
 * authorize assets. No guesses based on page topic, URL, or adjacent site content.
 * Never use this as proof that a full WP template/Assembler has been accepted.
 */
function fv_apollo_r357_usage(string $content, array &$seen = array(), int $depth = 0, ?array &$budget = null): array {
    if ($budget === null) { $budget = array('nodes' => 0, 'bytes' => 0); }
    $budget['bytes'] += strlen($content);
    if ($depth > 6 || $budget['bytes'] > 500000 || $budget['nodes'] > 128) {
        return array(false, false, false);
    }
    $match = static function(string $tag) use ($content): bool {
        if (function_exists('has_shortcode')) { return (bool)has_shortcode($content, $tag); }
        return (bool)preg_match('/\[' . preg_quote($tag, '/') . '(?=[\s\]\/])/', $content);
    };
    $found = array($match('fv_apollo_experience_r357'), $match('fv_apollo_postfire_r357'), true);
    if ($found[0] && $found[1]) { return $found; }
    if (!function_exists('parse_blocks')) { return $found; }
    $theme = function_exists('get_stylesheet') ? (string)get_stylesheet() : '';
    $walk = static function(array $blocks, int $level) use (&$walk, &$seen, &$budget, $theme, &$found): void {
        foreach ($blocks as $block) {
            ++$budget['nodes'];
            if ($budget['nodes'] > 128 || $level > 6) { $found[2] = false; return; }
            if (!is_array($block)) { continue; }
            $type = (string)($block['blockName'] ?? '');
            $nestedContent = null; $key = '';
            if ($type === 'core/block' && function_exists('get_post')) {
                $ref = $block['attrs']['ref'] ?? null;
                if (is_numeric($ref) && (int)$ref > 0 && (int)$ref <= 2147483647) {
                    $key = 'block:' . (int)$ref;
                    if (!isset($seen[$key]) && count($seen) < 48) {
                        $p = get_post((int)$ref);
                        if (is_object($p) && ($p->post_type ?? '') === 'wp_block') {
                            $nestedContent = (string)($p->post_content ?? '');
                        }
                    }
                }
            } elseif ($type === 'core/template-part' && function_exists('get_block_template') && $theme !== '') {
                $slug = (string)($block['attrs']['slug'] ?? '');
                $declaredTheme = (string)($block['attrs']['theme'] ?? $theme);
                // Reject arbitrary IDs, traversal, foreign themes and unbounded slugs.
                if (strlen($slug) <= 80 && preg_match('/\A[a-zA-Z0-9_-]+\z/D', $slug)
                    && $declaredTheme === $theme) {
                    $key = 'part:' . $theme . '//' . $slug;
                    if (!isset($seen[$key]) && count($seen) < 48) {
                        $p = get_block_template($theme . '//' . $slug, 'wp_template_part');
                        if (is_object($p) && isset($p->content)) {
                            $nestedContent = (string)$p->content;
                        }
                    }
                }
            }
            if ($nestedContent !== null) {
                $seen[$key] = true;
                $child = fv_apollo_r357_usage($nestedContent, $seen, $level + 1, $budget);
                $found[0] = $found[0] || $child[0];
                $found[1] = $found[1] || $child[1];
                $found[2] = $found[2] && $child[2];
            }
            if (isset($block['innerBlocks']) && is_array($block['innerBlocks'])) {
                $walk($block['innerBlocks'], $level + 1);
            }
            if ($found[0] && $found[1]) { return; }
        }
    };
    $walk(parse_blocks($content), $depth);
    return $found;
}

function fv_apollo_r357_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')
        || !function_exists('wp_enqueue_style')) { return; }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content)) { return; }
    $seen = array(); $budget = null;
    $usage = fv_apollo_r357_usage((string)$post->post_content, $seen, 0, $budget);
    if (!$usage[0] && !$usage[1]) { return; }
    $root = dirname(__DIR__);
    $assets = array(
        array('fv-apollo-r355-postfire', 'apollo-r355/postfire-ledger.css'),
        array('fv-apollo-r356-print-proof', 'apollo-r356/assets/print-proof.css'),
    );
    if ($usage[0]) {
        $assets = array_merge(array(
            array('fv-apollo-r339-chronology', 'apollo-r339/assets/chronology-rail.css'),
            array('fv-apollo-r340-gallery', 'apollo-r340/assets/accession-gallery.css'),
            array('fv-apollo-r345-evidence-plate', 'apollo-r345/evidence-plate.css'),
            array('fv-apollo-r347-index', 'apollo-r347/assets/source-index.css'),
            array('fv-apollo-r348-custody', 'apollo-r348/assets/source-custody.css'),
        ), $assets);
    }
    foreach ($assets as $asset) {
        $absolute = $root . '/' . $asset[1];
        if (is_readable($absolute)) {
            wp_enqueue_style($asset[0], plugins_url('../' . $asset[1], __FILE__), array(), '0.0.1-research');
        }
    }
    if ($usage[0] && function_exists('wp_enqueue_script')
        && is_readable($root . '/apollo-r347/assets/source-index.js')) {
        wp_enqueue_script('fv-apollo-r347-index', plugins_url('../apollo-r347/assets/source-index.js', __FILE__), array(), '0.0.1-research', true);
    }
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_experience_r357', 'fv_apollo_r357_full');
    add_shortcode('fv_apollo_postfire_r357', 'fv_apollo_r357_note');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_apollo_r357_enqueue', 18); }
