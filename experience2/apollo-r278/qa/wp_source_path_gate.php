<?php
/** WP API simulation: explicitly NOT installed WordPress. */
error_reporting(E_ALL);
define('ABSPATH', '/offline-wordpress-fixture/');
$GLOBALS['posts'] = [];
$GLOBALS['shortcodes'] = [];
$GLOBALS['hooks'] = [];
$GLOBALS['enqueues'] = [];
$GLOBALS['query_id'] = 1;
$GLOBALS['is_singular'] = true;
$GLOBALS['style_done'] = false;
function add_action($name, $callback, $priority = 10) { $GLOBALS['hooks'][$name][] = $callback; }
function add_shortcode($name, $callback) { $GLOBALS['shortcodes'][$name] = $callback; }
function plugins_url($name, $file) { return 'https://example.test/plugins/fv/apollo-r277/' . $name; }
function get_post($id) { return $GLOBALS['posts'][$id] ?? null; }
function is_singular() { return $GLOBALS['is_singular']; }
function get_queried_object_id() { return $GLOBALS['query_id']; }
function wp_enqueue_style($handle, $url, $deps, $version) { $GLOBALS['enqueues'][] = [$handle, $url, $deps, $version]; }
function wp_style_is($handle, $state) { return $GLOBALS['style_done']; }
function has_shortcode($content, $shortcode) { return strpos($content, '[' . $shortcode) !== false; }
function parse_blocks($content) {
    if (isset($GLOBALS['parsed'][$content])) { return $GLOBALS['parsed'][$content]; }
    return [];
}
function expect($condition, $label) { if (!$condition) {fwrite(STDERR,"FAIL $label\n");exit(1);} echo "PASS $label\n"; }
require __DIR__ . '/../../apollo-r277/apollo-review-shortcode.php';
foreach ($GLOBALS['hooks']['init'] as $fn) { $fn(); }
expect(isset($GLOBALS['shortcodes'][FV_R277_SHORTCODE]), 'shortcode registered');
expect(isset($GLOBALS['hooks']['wp_enqueue_scripts']), 'preflight hook registered');
$block = static fn($id) => ['blockName'=>'core/block','attrs'=>['ref'=>$id],'innerBlocks'=>[]];
$post = static fn($type,$status,$text) => (object)['post_type'=>$type,'post_status'=>$status,'post_content'=>$text];
$GLOBALS['posts'] = [1=>$post('post','publish','intro'),2=>$post('wp_block','publish','[fv_apollo_review_custody]'),3=>$post('wp_block','draft','[fv_apollo_review_custody]')];
$GLOBALS['parsed']['intro'] = [$block(2)];
$seen=[];expect(fv_r277_contains_shortcode('text [fv_apollo_review_custody]',0,$seen), 'direct content detected');
$seen=[];expect(fv_r277_contains_shortcode('intro',0,$seen), 'published reusable detected');
$GLOBALS['parsed']['intro']=[$block(3)];$seen=[];
expect(!fv_r277_contains_shortcode('intro',0,$seen), 'draft reusable excluded');
$GLOBALS['parsed']['intro']=[$block(2)];
$GLOBALS['posts'][2] = $post('wp_block','publish','recursion');
$GLOBALS['parsed']['recursion']=[$block(2)];$seen=[];
expect(!fv_r277_contains_shortcode('intro',0,$seen), 'cycle terminated');
$GLOBALS['posts'][2] = $post('wp_block','publish','[fv_apollo_review_custody]');
$GLOBALS['parsed']['intro'] = [['blockName'=>'core/group','innerBlocks'=>[$block(2)]]];$seen=[];
expect(fv_r277_contains_shortcode('intro',0,$seen), 'nested referenced reusable detected');
$GLOBALS['posts'][1]=$post('post','publish','intro');
fv_r277_enqueue_preflight();
expect(count($GLOBALS['enqueues'])===1 && $GLOBALS['enqueues'][0][0]===FV_R277_STYLE,'one same-origin stylesheet preflight');
expect(str_contains($GLOBALS['enqueues'][0][1], 'review-custody.css'),'original R276 CSS path retained');
$GLOBALS['is_singular']=false;fv_r277_enqueue_preflight();
expect(count($GLOBALS['enqueues'])===1, 'no load on non-singular content');
$GLOBALS['is_singular']=true;
$html1=fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://example.net/buy','receipt_sha256'=>str_repeat('a',64)]);
$html2=fv_r277_render_shortcode(['state'=>'verified']);
expect(substr_count($html1.$html2,'<link rel="stylesheet"')===1, 'dynamic late fallback linked only once');
expect(substr_count($html1.$html2,'data-fv-review-ready="false"')===2,'both panels remain unverified');
expect(!str_contains($html1.$html2,'example.net')&&!str_contains($html1.$html2,'approved'),'untrusted shortcode attributes ignored');
expect(substr_count($html1.$html2,'Read the free Apollo 1 investigation')===2, 'one free article action per panel');
expect(substr_count($html1.$html2,'Read NASA primary source:')===4,'both panels preserve two original-source record links');
expect(str_contains($html1.$html2,'two editorial record categories, not two independent'), 'source dependency explicitly disclosed');
expect(substr_count($html1.$html2,'id="fv-r273-title')===2, 'repeated panels have distinct heading identifiers');
expect(!str_contains($html1.$html2,'<script'), 'no JavaScript or tracking inserted');
expect(!str_contains($html1.$html2,'Mini Museum'), 'no unapproved merchant CTA');
$seen=[];expect(!fv_r277_contains_shortcode('no shortcode',9,$seen), 'depth limit safe');
$source=__DIR__.'/../../apollo-r273/review-custody.php';
expect(fv_r277_source_pinned($source),'frozen authentic historical renderer passes SHA-256 custody');
$temp=tempnam(sys_get_temp_dir(),'r278');
file_put_contents($temp,file_get_contents($source)."\\n/* altered */");
expect(!fv_r277_source_pinned($temp),'edited historical source is rejected');
unlink($temp);
expect(!fv_r277_source_pinned('/nonexistent/apollo/source.php'),'missing source rejected');
$nested=$block(2);
for($i=0;$i<8;$i++)$nested=['blockName'=>'core/group','innerBlocks'=>[$nested]];
$GLOBALS['parsed']['R278-two-paths']=[$nested,$block(2)];
$seen=[];
expect(fv_r277_contains_shortcode('R278-two-paths',0,$seen),'shallow reusable route survives earlier depth-truncated branch');
expect(count($seen)===0,'active recursion stack unwound');
expect(str_contains(fv_r277_fallback_sources(),'NASA Apollo 204 Review Board report')&&str_contains(fv_r277_fallback_sources(),'Free Apollo 1 investigation'),'readable fail-open retains primary and free routes');
echo "R278 inherited WordPress API simulation plus source pin/depth/fallback assertions PASS (NOT INSTALLED WORDPRESS).\\n";
