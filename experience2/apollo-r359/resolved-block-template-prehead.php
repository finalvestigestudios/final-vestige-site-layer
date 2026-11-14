<?php
/**
 * Apollo R359: exact WordPress-resolved block-template assets (staging only).
 * This companion never guesses the template hierarchy and never changes content.
 * WP core's locate_block_template() resolves the template before template_include.
 * WordPress 6.3+ internally exposes the resolved ID and content in globals.
 * If these implementation details drift, this adapter fails closed for asset discovery.
 */
if (!defined('ABSPATH')) { exit; }
$fv_r359_upstream = dirname(__DIR__) . '/apollo-r358/explicit-template-prehead.php';
if (is_readable($fv_r359_upstream)) { require_once $fv_r359_upstream; }

/**
 * Record only the exact already-resolved WP block canvas; preserve template selection.
 * Do not use get_query_template() here: that would rerun hierarchy filters and could
 * select a different template than WordPress will render.
 */
function fv_apollo_r359_capture_template($template) {
    $GLOBALS['fv_apollo_r359_snapshot'] = null;
    if (!is_string($template) || !defined('WPINC') || !function_exists('is_singular')
        || !is_singular() || !function_exists('wp_is_block_theme') || !wp_is_block_theme()
        || !function_exists('get_stylesheet') || !function_exists('get_block_template')) {
        return $template;
    }
    $canvas = rtrim((string)ABSPATH, '/\\') . '/' . trim((string)WPINC, '/\\') . '/template-canvas.php';
    if (str_replace('\\', '/', $template) !== str_replace('\\', '/', $canvas)) { return $template; }
    $id = $GLOBALS['_wp_current_template_id'] ?? null;
    $content = $GLOBALS['_wp_current_template_content'] ?? null;
    $theme = get_stylesheet();
    if (!is_string($theme) || !preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $theme)
        || !is_string($id) || !preg_match('/\A' . preg_quote($theme, '/') . '\/\/([a-zA-Z0-9_-]{1,80})\z/D', $id, $m)
        || !is_string($content) || $content === '' || strlen($content) > 500000) {
        return $template;
    }
    $record = get_block_template($id, 'wp_template');
    if (!is_object($record) || !isset($record->content) || !is_string($record->content)
        || $record->content !== $content || ($record->id ?? null) !== $id
        || ($record->slug ?? null) !== $m[1] || ($record->theme ?? null) !== $theme) {
        return $template;
    }
    $GLOBALS['fv_apollo_r359_snapshot'] = array(
        'id' => $id, 'theme' => $theme, 'content' => $content,
        'digest' => hash('sha256', $content)
    );
    return $template;
}

/** Resolve only a captured template whose ID and content remain identical. */
function fv_apollo_r359_resolved_usage(): array {
    $snapshot = $GLOBALS['fv_apollo_r359_snapshot'] ?? null;
    if (!is_array($snapshot) || !function_exists('is_singular') || !is_singular()
        || !function_exists('get_stylesheet') || !function_exists('fv_apollo_r357_usage')
        || ($snapshot['theme'] ?? null) !== get_stylesheet()
        || ($GLOBALS['_wp_current_template_id'] ?? null) !== ($snapshot['id'] ?? null)
        || ($GLOBALS['_wp_current_template_content'] ?? null) !== ($snapshot['content'] ?? null)
        || hash('sha256', (string)($snapshot['content'] ?? '')) !== ($snapshot['digest'] ?? null)) {
        return array(false, false, false);
    }
    $seen = array(); $budget = null;
    $usage = fv_apollo_r357_usage($snapshot['content'], $seen, 0, $budget);
    // A partial traversal must never be treated as evidence that source assets are complete.
    if (empty($usage[2])) { return array(false, false, false); }
    return array((bool)$usage[0], (bool)$usage[1], true);
}

/** R358/R357 keep the exact same handles; WordPress deduplicates handles. */
function fv_apollo_r359_enqueue(): void {
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    $usage = fv_apollo_r359_resolved_usage();
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
        if (is_readable($root . '/' . $asset[1])) {
            wp_enqueue_style($asset[0], plugins_url('../' . $asset[1], __FILE__), array(), '0.0.1-research');
        }
    }
    if ($usage[0] && function_exists('wp_enqueue_script')
        && is_readable($root . '/apollo-r347/assets/source-index.js')) {
        wp_enqueue_script('fv-apollo-r347-index', plugins_url('../apollo-r347/assets/source-index.js', __FILE__), array(), '0.0.1-research', true);
    }
}
if (function_exists('add_filter')) { add_filter('template_include', 'fv_apollo_r359_capture_template', 999, 1); }
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_apollo_r359_enqueue', 16); }
