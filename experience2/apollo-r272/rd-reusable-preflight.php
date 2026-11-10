<?php
/**
 * Plugin Name: FV Experience 2.0 Apollo Research Desk Reusable Block Asset Preflight (STAGING ONLY)
 * Description: Bounded read-only asset discovery for reusable core/block patterns; R272 draft, not activation approved.
 * Version: 0.0.1-r272
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/** Look through parsed blocks without executing render callbacks or altering content. */
function fv_ex2_r272_blocks_have_desk(array $blocks, array &$visited, int &$budget, int $depth = 0): bool {
    if ($depth > 8) { return false; }
    foreach ($blocks as $block) {
        if (--$budget < 0) { return false; }
        if (!is_array($block)) { continue; }
        $name = isset($block['blockName']) ? $block['blockName'] : null;
        $attrs = isset($block['attrs']) && is_array($block['attrs']) ? $block['attrs'] : array();
        if ($name === 'core/block' && isset($attrs['ref'])) {
            $ref = $attrs['ref'];
            if ((is_int($ref) || (is_string($ref) && ctype_digit($ref))) &&
                (int) $ref > 0 && !isset($visited[(int) $ref]) && count($visited) < 32) {
                $visited[(int) $ref] = true;
                $post = get_post((int) $ref);
                if (is_object($post) && isset($post->post_type, $post->post_status, $post->post_content) &&
                    $post->post_type === 'wp_block' && $post->post_status === 'publish' &&
                    is_string($post->post_content) &&
                    fv_ex2_r272_content_has_desk($post->post_content, $visited, $budget, $depth + 1)) {
                    return true;
                }
            }
        }
        if (isset($block['innerBlocks']) && is_array($block['innerBlocks']) &&
            fv_ex2_r272_blocks_have_desk($block['innerBlocks'], $visited, $budget, $depth + 1)) {
            return true;
        }
    }
    return false;
}

function fv_ex2_r272_content_has_desk(string $content, array &$visited, int &$budget, int $depth = 0): bool {
    if ($depth > 8 || $budget < 1) { return false; }
    if (has_shortcode($content, 'fv_ex2_research_desk')) { return true; }
    $blocks = parse_blocks($content);
    return is_array($blocks) && fv_ex2_r272_blocks_have_desk($blocks, $visited, $budget, $depth);
}

/**
 * Pre-head asset enqueue only; cannot repair unknown dynamic render paths.
 * Cryptographic asset pins prevent this optional enhancer silently loading modified originals.
 */
function fv_ex2_r272_reusable_preflight(): void {
    if (!is_singular() || is_admin() || !function_exists('fv_ex2_rd_shortcode')) { return; }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content) || !is_string($post->post_content)) { return; }
    $visited = array(); $budget = 500;
    if (!fv_ex2_r272_content_has_desk($post->post_content, $visited, $budget)) { return; }
    $source = (new ReflectionFunction('fv_ex2_rd_shortcode'))->getFileName();
    $dir = dirname($source);
    $css = $dir . '/assets/source-ledger.css';
    $js = $dir . '/assets/source-ledger.js';
    if (!is_readable($css) || !is_readable($js) ||
        !hash_equals('38676056e2aee5e3db285072bd847b5b5438832d76d9c451e4f56d27134ee291', (string) hash_file('sha256', $css)) ||
        !hash_equals('22a9ab56f3265aece14f76f1cab557ecfb096530e4802fa4dcbc0960fe34533d', (string) hash_file('sha256', $js))) {
        return; // Original evidence remains server-rendered. Do not load unverified optional assets.
    }
    if (!wp_style_is('fv-ex2-research-desk', 'enqueued')) {
        wp_enqueue_style('fv-ex2-research-desk', plugins_url('assets/source-ledger.css', $source), array(), FV_EX2_RD_VERSION);
    }
    if (!wp_script_is('fv-ex2-research-desk', 'enqueued')) {
        wp_enqueue_script('fv-ex2-research-desk', plugins_url('assets/source-ledger.js', $source), array(), FV_EX2_RD_VERSION, true);
    }
}
add_action('wp_enqueue_scripts', 'fv_ex2_r272_reusable_preflight', 21);
