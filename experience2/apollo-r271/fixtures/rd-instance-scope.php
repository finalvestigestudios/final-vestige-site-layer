<?php
/**
 * Plugin Name: FV Experience 2.0 Research Desk — Multi-instance Scope (STAGING ONLY)
 * Description: Optional, server-side IDREF namespacing for repeat Apollo Research Desk shortcodes. Not production approved.
 * Version: 0.0.1-r270
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Preserve the first Research Desk's published fragment identifiers. Scope later
 * copies to their own label/control/heading targets, even without JavaScript.
 *
 * This does NOT modify NASA claims, source URLs, Research Desk PR #158 or homepage.
 * Invalid/unrecognized markup is returned untouched: never erase the evidence.
 * Reusable and nested blocks pass through the same do_shortcode_tag filter.
 */
function fv_ex2_r270_scope_desk($output, $tag, $attr, $match): string {
    static $instances = 0;
    if ($tag !== 'fv_ex2_research_desk' || !is_string($output)) { return $output; }
    if (substr_count($output, 'data-fvx-ledger') !== 1 ||
        substr_count($output, 'data-fvx-record') !== 6) { return $output; }
    $names = array('title', 'search', 'grid', 'record-01', 'record-02', 'record-03',
        'record-04', 'record-05', 'record-06');
    foreach ($names as $name) {
        if (substr_count($output, 'id="fv-ex2-ledger-apollo1-' . $name . '"') !== 1) {
            return $output;
        }
    }
    $instances++;
    if ($instances === 1) { return $output; }
    $suffix = '--fvx-' . $instances;
    $updated = preg_replace_callback(
        '/\b(id|for|aria-labelledby|aria-controls)="(fv-ex2-ledger-apollo1-(?:title|search|grid|record-0[1-6]))"/',
        static function (array $hit) use ($suffix): string {
            return $hit[1] . '="' . $hit[2] . $suffix . '"';
        },
        $output
    );
    return is_string($updated) ? $updated : $output;
}
add_filter('do_shortcode_tag', 'fv_ex2_r270_scope_desk', 20, 4);
