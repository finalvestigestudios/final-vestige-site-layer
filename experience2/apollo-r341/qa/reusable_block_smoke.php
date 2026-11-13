<?php
/** R341: isolated WP-function stub acceptance, not an installed WordPress proof. */
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
$fixture = array('top' => '', 'blocks' => array());
$styles = array();
function add_shortcode($name, $callback): void {}
function add_action($name, $callback, $priority = 10): void {}
function is_singular(): bool { return true; }
function has_shortcode($content, $tag): bool { return strpos($content, '[' . $tag . ']') !== false; }
function get_post($id = null) {
    global $fixture;
    if ($id === null) { return (object) array('post_type' => 'post', 'post_content' => $fixture['top']); }
    if (!isset($fixture['blocks'][(string) $id])) { return null; }
    return (object) $fixture['blocks'][(string) $id];
}
function parse_blocks($content): array {
    preg_match_all('/<!-- wp:block \{"ref":(\d+)\} \/-->/', $content, $matches);
    $blocks = array();
    foreach ($matches[1] as $id) {
        $blocks[] = array('blockName' => 'core/block', 'attrs' => array('ref' => (int) $id), 'innerBlocks' => array());
    }
    return $blocks;
}
function plugins_url($relative, $file): string { return '/wp/plugins/apollo-r340/' . $relative; }
function wp_enqueue_style($handle, $url, $dependencies, $version): void {
    global $styles;
    $styles[] = $handle;
}
require __DIR__ . '/../../apollo-r340/apollo-accession-gallery.php';
$both = array('fv-apollo-r339-chronology', 'fv-apollo-r340-gallery');
$gallery = array('fv-apollo-r340-gallery');
$ref = function ($id): string { return '<!-- wp:block {"ref":' . $id . '} /-->'; };
$record = function ($content, $type = 'wp_block'): array { return array('post_type' => $type, 'post_content' => $content); };
$cases = array(
    array('direct composed', '[fv_apollo_experience_r340]', array(), $both),
    array('direct gallery', '[fv_apollo_gallery_r340]', array(), $gallery),
    array('unrelated content', '[unrelated]', array(), array()),
    array('reusable gallery', $ref(42), array(42 => $record('[fv_apollo_gallery_r340]')), $gallery),
    array('reusable composed', $ref(43), array(43 => $record('[fv_apollo_experience_r340]')), $both),
    array('nested reference', $ref(44), array(44 => $record($ref(43)), 43 => $record('[fv_apollo_experience_r340]')), $both),
    array('mixed references', $ref(42) . $ref(43), array(42 => $record('[fv_apollo_gallery_r340]'), 43 => $record('[fv_apollo_experience_r340]')), $both),
    array('missing reference', $ref(404), array(), array()),
    array('wrong post type', $ref(42), array(42 => $record('[fv_apollo_experience_r340]', 'post')), array()),
    array('cycle', $ref(42), array(42 => $record($ref(42))), array()),
    array('non-block content', '<!-- wp:paragraph -->ordinary words<!-- /wp:paragraph -->', array(), array()),
);
$deep = array();
for ($i = 1; $i <= 7; $i++) { $deep[$i] = $record($ref($i + 1)); }
$deep[8] = $record('[fv_apollo_experience_r340]');
$cases[] = array('depth bounded', $ref(1), $deep, array());
foreach ($cases as $case) {
    $fixture = array('top' => $case[1], 'blocks' => $case[2]);
    $styles = array();
    fv_apollo_r340_enqueue();
    if ($styles !== $case[3]) {
        fwrite(STDERR, 'FAIL ' . $case[0] . ': ' . json_encode($styles) . "\n");
        exit(1);
    }
}
echo 'PASS ' . count($cases) . " isolated reusable-block preflight cases\n";
