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
$path = '/wordpress/wp-content/uploads/fv-ex2-parity/site-parity.safe.json';
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
// This optional importer changes ONLY an isolated *local* WP database.
// Never overwrite pre-existing non-FV theme overrides: fail closed.
function fv_local_parity_insert($type, $slug, $markup, $area = null) {
    $old = get_posts(['post_type'=>$type,'name'=>$slug,'post_status'=>'any','posts_per_page'=>2]);
    if ($old) {
        foreach ($old as $post) {
            if (get_post_meta($post->ID, '_fv_ex2_local_parity', true) !== '1') {
                throw new RuntimeException('REFUSED: existing non-FV local override for ' . $slug);
            }
        }
    }
    $args = ['post_type'=>$type, 'post_status'=>'publish', 'post_title'=>'FV local-only '.$slug,
             'post_name'=>$slug, 'post_content'=>$markup, 'comment_status'=>'closed'];
    if ($old) $args['ID']=$old[0]->ID;
    $id = wp_insert_post($args, true);
    if (is_wp_error($id) || !$id) throw new RuntimeException('Local parity insert failed: '.$slug);
    if (is_wp_error(wp_set_object_terms($id, 'assembler', 'wp_theme'))) {
        throw new RuntimeException('Local theme taxonomy assignment failed');
    }
    if ($area !== null && taxonomy_exists('wp_template_part_area')) {
        if (is_wp_error(wp_set_object_terms($id, $area, 'wp_template_part_area'))) {
            throw new RuntimeException('Local template area assignment failed');
        }
    }
    update_post_meta($id, '_fv_ex2_local_parity', '1');
    return $id;
}
$ids = [];
$ids['page'] = fv_local_parity_insert('wp_template', 'page', $content['page']);
$ids['header'] = fv_local_parity_insert('wp_template_part', 'header', $content['header'], 'header');
$ids['footer'] = fv_local_parity_insert('wp_template_part', 'footer', $content['footer'], 'footer');
$ids['overlay'] = fv_local_parity_insert('wp_template_part', 'fv-archive-index-overlay', $content['overlay'], 'navigation-overlay');
$style_json = wp_json_encode(['version'=>2, 'settings'=>$gs['settings'], 'styles'=>$gs['styles']]);
$ids['global_styles'] = fv_local_parity_insert('wp_global_styles', 'wp-global-styles-assembler', $style_json);
echo 'FV isolated local Assembler presentation parity imported; RELEASE HOLD; IDs: '.wp_json_encode($ids);
