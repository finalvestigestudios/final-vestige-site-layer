<?php
/** R372 conditional style loading BEFORE wp_head; read-only, bounded, staging only. */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r372_has_shortcode(string $content): bool {
    return function_exists('has_shortcode')
        ? (bool)has_shortcode($content,'fv_apollo_source_path_r372')
        : preg_match('/\[fv_apollo_source_path_r372(?:\s|\]|\/)/i', $content) === 1;
}
function fv_apollo_r372_scan(string $content, array &$seen, int $depth, int &$budget): bool {
    if ($depth > 7 || $budget <= 0 || strlen($content) > 250000) { return false; }
    --$budget;
    if (fv_apollo_r372_has_shortcode($content)) { return true; }
    if (!function_exists('parse_blocks')) { return false; }
    $blocks = parse_blocks($content);
    if (!is_array($blocks)) { return false; }
    foreach ($blocks as $block) {
        if (--$budget < 0) { return false; }
        if (!is_array($block)) { continue; }
        $inner = $block['innerHTML'] ?? null;
        if (is_string($inner) && fv_apollo_r372_has_shortcode($inner)) { return true; }
        $attrs = is_array($block['attrs'] ?? null) ? $block['attrs'] : array();
        if (($block['blockName'] ?? '') === 'core/block' && function_exists('get_post')) {
            $ref = filter_var($attrs['ref'] ?? null,FILTER_VALIDATE_INT);
            if ($ref && $ref > 0 && !isset($seen['ref:'.$ref])) {
                $seen['ref:'.$ref] = true;
                $post = get_post($ref);
                if (is_object($post) && ($post->post_type ?? '') === 'wp_block'
                    && is_string($post->post_content ?? null)
                    && fv_apollo_r372_scan($post->post_content,$seen,$depth+1,$budget)) { return true; }
            }
        }
        if (($block['blockName'] ?? '') === 'core/template-part' && function_exists('get_stylesheet')
            && function_exists('get_block_template')) {
            $theme = $attrs['theme'] ?? get_stylesheet();
            $slug = $attrs['slug'] ?? null;
            if ($theme === get_stylesheet() && is_string($slug) &&
                preg_match('/^[a-z0-9][a-z0-9_-]{0,95}$/D',$slug)) {
                $ref = $theme.'//'.$slug;
                if (!isset($seen['part:'.$ref])) {
                    $seen['part:'.$ref] = true;
                    $tpl = get_block_template($ref,'wp_template_part');
                    if (is_object($tpl) && ($tpl->id ?? '') === $ref && is_string($tpl->content ?? null)
                        && fv_apollo_r372_scan($tpl->content,$seen,$depth+1,$budget)) { return true; }
                }
            }
        }
        // Inner blocks need separate recursion; avoid serializing arbitrary parser output.
        if (is_array($block['innerBlocks'] ?? null) &&
            fv_apollo_r372_walk_blocks($block['innerBlocks'],$seen,$depth+1,$budget)) { return true; }
    }
    return false;
}
function fv_apollo_r372_walk_blocks(array $blocks, array &$seen, int $depth, int &$budget): bool {
    if ($depth > 7 || $budget <= 0) { return false; }
    foreach ($blocks as $block) {
        if (--$budget < 0) { return false; }
        if (!is_array($block)) { continue; }
        $inner = $block['innerHTML'] ?? null;
        if (is_string($inner) && fv_apollo_r372_has_shortcode($inner)) { return true; }
        // Reuse exactly the same guarded handling of refs and template parts.
        $attrs = is_array($block['attrs'] ?? null) ? $block['attrs'] : array();
        if (($block['blockName'] ?? '') === 'core/block' && function_exists('get_post')) {
            $ref = filter_var($attrs['ref'] ?? null,FILTER_VALIDATE_INT);
            if ($ref && $ref > 0 && !isset($seen['ref:'.$ref])) {
                $seen['ref:'.$ref] = true;
                $post = get_post($ref);
                if (is_object($post) && ($post->post_type ?? '') === 'wp_block'
                    && is_string($post->post_content ?? null)
                    && fv_apollo_r372_scan($post->post_content,$seen,$depth+1,$budget)) { return true; }
            }
        }
        if (($block['blockName'] ?? '') === 'core/template-part' && function_exists('get_stylesheet')
            && function_exists('get_block_template')) {
            $theme = $attrs['theme'] ?? get_stylesheet(); $slug = $attrs['slug'] ?? null;
            if ($theme === get_stylesheet() && is_string($slug) && preg_match('/^[a-z0-9][a-z0-9_-]{0,95}$/D',$slug)) {
                $ref = $theme.'//'.$slug;
                if (!isset($seen['part:'.$ref])) {
                    $seen['part:'.$ref] = true;
                    $tpl = get_block_template($ref,'wp_template_part');
                    if (is_object($tpl) && ($tpl->id ?? '') === $ref && is_string($tpl->content ?? null)
                        && fv_apollo_r372_scan($tpl->content,$seen,$depth+1,$budget)) { return true; }
                }
            }
        }
        if (is_array($block['innerBlocks'] ?? null) &&
            fv_apollo_r372_walk_blocks($block['innerBlocks'],$seen,$depth+1,$budget)) { return true; }
    }
    return false;
}
function fv_apollo_r372_needs_assets(): bool {
    if ((function_exists('is_admin') && is_admin())
        || (function_exists('is_singular') && !is_singular())
        || !function_exists('get_post') || !function_exists('get_queried_object_id')) { return false; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null)) { return false; }
    $seen = array(); $budget = 128;
    if (fv_apollo_r372_scan($post->post_content,$seen,0,$budget)) { return true; }
    $resolved = $GLOBALS['_wp_current_template_id'] ?? null;
    if (!is_string($resolved) || !function_exists('get_stylesheet') || !function_exists('get_block_template')) { return false; }
    $prefix = get_stylesheet().'//';
    if (strpos($resolved,$prefix) !== 0 || strlen($resolved) <= strlen($prefix)) { return false; }
    $tpl = get_block_template($resolved,'wp_template');
    return is_object($tpl) && ($tpl->id ?? '') === $resolved
        && is_string($tpl->content ?? null)
        && fv_apollo_r372_scan($tpl->content,$seen,0,$budget);
}
function fv_apollo_r372_prehead(): void {
    if (!fv_apollo_r372_needs_assets() || !function_exists('wp_enqueue_style') ||
        !function_exists('plugins_url') || !is_readable(__DIR__.'/assets/evidence-path.css')) { return; }
    if (function_exists('wp_style_is') &&
        (wp_style_is('fv-apollo-r372-evidence-path','enqueued') || wp_style_is('fv-apollo-r372-evidence-path','done'))) { return; }
    wp_enqueue_style('fv-apollo-r372-evidence-path',plugins_url('assets/evidence-path.css',__FILE__),array(),'r372-draft-1');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r372_prehead',1); }
