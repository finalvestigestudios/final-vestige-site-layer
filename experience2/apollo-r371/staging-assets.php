<?php
/** R371 STAGING ONLY: conditional before-head asset detection, read-only. */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r371_has_shortcode(string $content): bool {
    return function_exists('has_shortcode')
        ? has_shortcode($content, 'fv_apollo_source_gallery_r371')
        : preg_match('/\[fv_apollo_source_gallery_r371(?:\s|\]|\/)/i', $content) === 1;
}

function fv_apollo_r371_scan(string $content, array &$seen, int $depth, int &$budget): bool {
    if ($depth > 7 || $budget <= 0 || strlen($content) > 250000) { return false; }
    $budget--;
    if (fv_apollo_r371_has_shortcode($content)) { return true; }
    if (!function_exists('parse_blocks')) { return false; }
    $blocks = parse_blocks($content);
    if (!is_array($blocks)) { return false; }
    $walk = static function (array $list, int $level) use (&$walk, &$seen, &$budget): bool {
        if ($level > 7 || $budget <= 0) { return false; }
        foreach ($list as $block) {
            if (--$budget < 0) { return false; }
            if (!is_array($block)) { continue; }
            $inner = $block['innerHTML'] ?? null;
            if (is_string($inner) && fv_apollo_r371_has_shortcode($inner)) { return true; }
            $attrs = is_array($block['attrs'] ?? null) ? $block['attrs'] : array();
            if (($block['blockName'] ?? '') === 'core/block' && function_exists('get_post')) {
                $id = filter_var($attrs['ref'] ?? null, FILTER_VALIDATE_INT);
                if ($id && $id > 0 && !isset($seen['block:'.$id])) {
                    $seen['block:'.$id] = true;
                    $post = get_post($id);
                    if (is_object($post) && ($post->post_type ?? '') === 'wp_block'
                        && is_string($post->post_content ?? null)
                        && fv_apollo_r371_scan($post->post_content,$seen,$level+1,$budget)) { return true; }
                }
            }
            if (($block['blockName'] ?? '') === 'core/template-part'
                && function_exists('get_stylesheet') && function_exists('get_block_template')) {
                $theme = $attrs['theme'] ?? get_stylesheet();
                $slug = $attrs['slug'] ?? null;
                if ($theme === get_stylesheet() && is_string($slug)
                    && preg_match('/^[a-z0-9][a-z0-9_-]{0,95}$/D',$slug)) {
                    $id = $theme.'//'.$slug;
                    if (!isset($seen['part:'.$id])) {
                        $seen['part:'.$id] = true;
                        $tpl = get_block_template($id,'wp_template_part');
                        if (is_object($tpl) && ($tpl->id ?? '') === $id
                            && is_string($tpl->content ?? null)
                            && fv_apollo_r371_scan($tpl->content,$seen,$level+1,$budget)) { return true; }
                    }
                }
            }
            if (is_array($block['innerBlocks'] ?? null) && $walk($block['innerBlocks'],$level+1)) { return true; }
        }
        return false;
    };
    return $walk($blocks,$depth);
}

function fv_apollo_r371_needs_assets(): bool {
    if ((function_exists('is_admin') && is_admin())
        || (function_exists('is_singular') && !is_singular())
        || !function_exists('get_queried_object_id') || !function_exists('get_post')) { return false; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null)) { return false; }
    $seen = array(); $budget = 128;
    if (fv_apollo_r371_scan($post->post_content,$seen,0,$budget)) { return true; }
    $resolved = $GLOBALS['_wp_current_template_id'] ?? null;
    if (!is_string($resolved) || !function_exists('get_stylesheet')
        || !function_exists('get_block_template')) { return false; }
    $prefix = get_stylesheet().'//';
    if (strpos($resolved,$prefix) !== 0 || strlen($resolved) <= strlen($prefix)) { return false; }
    $tpl = get_block_template($resolved,'wp_template');
    return is_object($tpl) && ($tpl->id ?? '') === $resolved
        && is_string($tpl->content ?? null)
        && fv_apollo_r371_scan($tpl->content,$seen,0,$budget);
}

function fv_apollo_r371_prehead(): void {
    if (!fv_apollo_r371_needs_assets() || !function_exists('wp_enqueue_style')
        || !function_exists('plugins_url') || !is_readable(__DIR__.'/assets/source-gallery.css')) { return; }
    if (function_exists('wp_style_is')
        && (wp_style_is('fv-apollo-r371-source-gallery','enqueued')
            || wp_style_is('fv-apollo-r371-source-gallery','done'))) { return; }
    wp_enqueue_style('fv-apollo-r371-source-gallery',plugins_url('assets/source-gallery.css',__FILE__),array(),'r371-stage-1');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r371_prehead',1); }
