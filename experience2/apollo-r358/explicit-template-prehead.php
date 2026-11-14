<?php
/**
 * Apollo R358 — explicit assigned block-template pre-head assets, STAGING ONLY.
 * Companion to R357; does not change source claims, checkout, analytics or site settings.
 * Supports exact assigned template IDs, never guesses default theme layout hierarchy.
 */
if (!defined('ABSPATH')) { exit; }
$apollo_r358_upstream = dirname(__DIR__) . '/apollo-r357/template-asset-bridge.php';
if (is_readable($apollo_r358_upstream)) { require_once $apollo_r358_upstream; }

/** Convert a WordPress explicitly assigned custom *block* template path to a safe slug. */
function fv_apollo_r358_template_slug($assigned): ?string {
    if (!is_string($assigned) || $assigned === '' || $assigned === 'default') { return null; }
    // Custom block template slug; WordPress can also save templates/slug.html.
    if (preg_match('/\Atemplates\/([a-zA-Z0-9_-]{1,80})\.html\z/D', $assigned, $m)) {
        return $m[1];
    }
    return preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $assigned) ? $assigned : null;
}
/** [full, note, scan_complete, explicit_template_reviewed] — discovery, not deployment approval. */
function fv_apollo_r358_assigned_usage($post): array {
    if (!is_object($post) || !isset($post->ID, $post->post_content)
        || !is_numeric($post->ID) || (int)$post->ID <= 0
        || !function_exists('get_page_template_slug') || !function_exists('get_block_template')
        || !function_exists('get_stylesheet') || !function_exists('fv_apollo_r357_usage')) {
        return array(false, false, false, false);
    }
    $slug = fv_apollo_r358_template_slug(get_page_template_slug($post));
    $theme = (string)get_stylesheet();
    if ($slug === null || !preg_match('/\A[a-zA-Z0-9_-]{1,80}\z/D', $theme)) {
        return array(false, false, false, false);
    }
    $id = $theme . '//' . $slug;
    $tpl = get_block_template($id, 'wp_template');
    if (!is_object($tpl) || !isset($tpl->content) || !is_string($tpl->content)) {
        return array(false, false, false, false);
    }
    // An injected or stale template with a different identity cannot authorize assets.
    if ((isset($tpl->id) && (string)$tpl->id !== $id)
        || (isset($tpl->slug) && (string)$tpl->slug !== $slug)
        || (isset($tpl->theme) && (string)$tpl->theme !== $theme)) {
        return array(false, false, false, false);
    }
    $seen = array(); $budget = null;
    $found = fv_apollo_r357_usage($tpl->content, $seen, 0, $budget);
    return array((bool)$found[0], (bool)$found[1], (bool)$found[2], true);
}
/** Only enqueues a known local component set; allows R357's native WP handles to dedupe. */
function fv_apollo_r358_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')
        || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    $usage = fv_apollo_r358_assigned_usage(get_post());
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
if (function_exists('add_action')) {
    add_action('wp_enqueue_scripts', 'fv_apollo_r358_enqueue', 17);
}
