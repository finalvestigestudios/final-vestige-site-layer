<?php
/** FV Experience 2 / local Assembler parity only. NEVER run on WordPress.com. */
require_once '/wordpress/wp-load.php';
$host = strtolower((string) parse_url(home_url('/'), PHP_URL_HOST));
if (wp_get_environment_type() !== 'local' || !in_array($host, ['127.0.0.1', 'localhost'], true)) {
    throw new RuntimeException('REFUSED: WordPress is not explicitly local loopback');
}
if (wp_get_theme()->get_stylesheet() !== 'assembler' || wp_get_theme()->get('Version') !== '0.0.126') {
    throw new RuntimeException('REFUSED: independently verified Assembler 0.0.126 required');
}
// The Blueprint executes runPHP with no authenticated browser session.
// WordPress applies KSES to Gutenberg/template content when no user has the
// unfiltered_html capability. That silently changes reviewed archival markup.
// Only inside this *fresh localhost-only disposable* instance, adopt WP's
// known default administrator (ID 1) and verify the exact capability before
// attempting a write. NEVER copy or reuse this shortcut on a hosted site.
if (is_multisite() || !function_exists('wp_set_current_user')) {
    throw new RuntimeException('REFUSED: local parity requires single-site WordPress API');
}
wp_set_current_user(1);
if (get_current_user_id() !== 1 || !current_user_can('unfiltered_html')) {
    throw new RuntimeException('REFUSED: local throwaway admin cannot persist unfiltered Gutenberg');
}
$path = '/wordpress/wp-content/uploads/fv-ex2-parity/assembler-public-safe.json';
if (!is_file($path) || filesize($path) < 200 || filesize($path) > 350000) {
    throw new RuntimeException('Missing or oversized sanitized parity manifest');
}
$data = json_decode((string) file_get_contents($path), true, 20, JSON_THROW_ON_ERROR);
if (($data['schema'] ?? '') !== 'fv-local-assembler-parity-v1'
    || ($data['release'] ?? '') !== 'HOLD' || ($data['local_only'] ?? false) !== true
    || ($data['source_theme'] ?? null) !== ['stylesheet'=>'assembler','version'=>'0.0.126']) {
    throw new RuntimeException('REFUSED: staging parity contract mismatch');
}
$allowed = ['page', 'header', 'footer', 'overlay'];
$content = $data['template_content'] ?? [];
if (!is_array($content) || array_keys($content) !== $allowed) {
    throw new RuntimeException('REFUSED: missing required public template parts');
}
foreach ($content as $slug => $markup) {
    if (!is_string($markup) || strlen($markup) > 100000
        || preg_match('~<script\b|<iframe\b|\bon[a-z]{3,}\s*=|javascript\s*:|posthog|googletagmanager|gtag\s*\(~i', $markup)) {
        throw new RuntimeException('REFUSED: unsafe staging template: ' . $slug);
    }
}
$gs = $data['global_styles'] ?? [];
if (($gs['settings']['layout'] ?? null) !== ['contentSize'=>'760px','wideSize'=>'1440px']
    || !is_string($gs['styles']['css'] ?? null)
    || preg_match('~@import\b|url\s*\(\s*[\'\"]?\s*(?:https?:|//)|<script~i', $gs['styles']['css'])) {
    throw new RuntimeException('REFUSED: unexpected or outbound CSS');
}
// Preflight every destination before the first write. A late collision must not
// leave a half-imported local header/page/global-styles configuration.
function fv_local_parity_existing($type, $slug) {
    $old = get_posts(['post_type'=>$type, 'name'=>$slug, 'post_status'=>'any',
        'posts_per_page'=>3, 'suppress_filters'=>true]);
    if (count($old) > 1) {
        throw new RuntimeException('REFUSED: duplicate local override for ' . $type . '/' . $slug);
    }
    foreach ($old as $post) {
        if (get_post_meta($post->ID, '_fv_ex2_local_parity', true) !== '1') {
            throw new RuntimeException('REFUSED: existing non-FV local override for ' . $type . '/' . $slug);
        }
    }
    return $old ? $old[0] : null;
}

// The five records are intentionally fixed. No arbitrary post types, slugs,
// private records or external URLs are imported from a manifest.
$style_json = wp_json_encode(['version'=>2, 'settings'=>$gs['settings'], 'styles'=>$gs['styles']]);
if (!is_string($style_json) || !$style_json) {
    throw new RuntimeException('REFUSED: invalid global style serialization');
}
$records = [
    'page' => ['type'=>'wp_template', 'slug'=>'page', 'content'=>$content['page'], 'area'=>null],
    'header' => ['type'=>'wp_template_part', 'slug'=>'header', 'content'=>$content['header'], 'area'=>'header'],
    'footer' => ['type'=>'wp_template_part', 'slug'=>'footer', 'content'=>$content['footer'], 'area'=>'footer'],
    'overlay' => ['type'=>'wp_template_part', 'slug'=>'fv-archive-index-overlay',
                  'content'=>$content['overlay'], 'area'=>'navigation-overlay'],
    'global_styles' => ['type'=>'wp_global_styles', 'slug'=>'wp-global-styles-assembler',
                        'content'=>$style_json, 'area'=>null],
];
$existing = [];
foreach ($records as $key => $record) {
    $existing[$key] = fv_local_parity_existing($record['type'], $record['slug']);
}

function fv_local_parity_insert_verified($record, $old) {
    $type = $record['type']; $slug = $record['slug'];
    // wp_insert_post() unslashes post content. Preserve the exact reviewed Gutenberg
    // bytes through that boundary; the post-save readback below remains mandatory.
    $args = ['post_type'=>$type, 'post_status'=>'publish', 'post_title'=>'FV local-only '.$slug,
             'post_name'=>$slug, 'post_content'=>wp_slash($record['content']), 'comment_status'=>'closed'];
    if ($old) { $args['ID'] = $old->ID; }
    $id = wp_insert_post($args, true);
    if (is_wp_error($id) || !$id) {
        throw new RuntimeException('Local parity insert failed: '.$slug);
    }
    if (is_wp_error(wp_set_object_terms($id, 'assembler', 'wp_theme'))) {
        throw new RuntimeException('Local theme taxonomy assignment failed: '.$slug);
    }
    if ($record['area'] !== null && taxonomy_exists('wp_template_part_area')) {
        if (is_wp_error(wp_set_object_terms($id, $record['area'], 'wp_template_part_area'))) {
            throw new RuntimeException('Local template area assignment failed: '.$slug);
        }
    }
    update_post_meta($id, '_fv_ex2_local_parity', '1');
    // WP may filter/sanitize post content or adjust duplicate slugs silently.
    // Read back the exact WordPress-stored record, not the wp_insert_post return.
    $saved = get_post($id);
    // Report only which local-only invariants failed; never emit HTML, source
    // bytes, logged-in user records or filesystem paths in CI artifacts.
    $drift = [];
    if (!$saved) {
        $drift[] = 'missing';
    } else {
        if ($saved->post_type !== $type) $drift[] = 'type';
        if ($saved->post_name !== $slug) $drift[] = 'slug';
        if ($saved->post_status !== 'publish') $drift[] = 'status';
        if ($saved->post_content !== $record['content']) $drift[] = 'content';
    }
    if (get_post_meta($id, '_fv_ex2_local_parity', true) !== '1') $drift[] = 'marker';
    if ($drift) {
        throw new RuntimeException('REFUSED: local template readback differs: '.$slug
            .'; mismatches='.implode(',', $drift));
    }
    $themes = wp_get_object_terms($id, 'wp_theme', ['fields'=>'names']);
    if (is_wp_error($themes) || !is_array($themes) || !in_array('assembler', $themes, true)) {
        throw new RuntimeException('REFUSED: Assembler theme association absent: '.$slug);
    }
    if ($record['area'] !== null && taxonomy_exists('wp_template_part_area')) {
        $areas = wp_get_object_terms($id, 'wp_template_part_area', ['fields'=>'names']);
        if (is_wp_error($areas) || !is_array($areas) || !in_array($record['area'], $areas, true)) {
            throw new RuntimeException('REFUSED: template-part area association absent: '.$slug);
        }
    }
    return $id;
}
$ids = [];
foreach ($records as $key => $record) {
    $ids[$key] = fv_local_parity_insert_verified($record, $existing[$key]);
}
echo 'FV isolated local Assembler presentation parity imported and read back; RELEASE HOLD; IDs: '
    . wp_json_encode($ids);
