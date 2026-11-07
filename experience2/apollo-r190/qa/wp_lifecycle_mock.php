<?php
/** Controlled WordPress function shim ONLY; not an installed WP test. */
define('ABSPATH', '/mock/');
class WP_Post { public $post_content='[fv_ex2_apollo_atlas]'; public $post_type='post'; }
$GLOBALS['styles'] = array();
$GLOBALS['scripts'] = array();
$GLOBALS['head_done'] = false;
function plugin_dir_path($file) { return dirname($file).'/'; }
function plugins_url($file,$plugin) { return '/staged/apollo/'.$file; }
function wp_enqueue_style(...$args) { $GLOBALS['styles'][$args[0]]='enqueued'; }
function wp_enqueue_script(...$args) { $GLOBALS['scripts'][$args[0]]='enqueued'; }
function wp_style_is($handle,$state='enqueued') {return ($GLOBALS['styles'][$handle] ?? '') === $state;}
function did_action($hook) {return ($hook === 'wp_head' && $GLOBALS['head_done']) ? 1 : 0;}
function add_action(...$args) { }
function add_shortcode(...$args) { }
function is_admin() { return false; }
function is_singular() { return true; }
function get_queried_object() { return new WP_Post(); }
function has_shortcode($content,$tag) { return str_contains($content,'['.$tag); }
function parse_blocks($content) {return array();}
function get_post($id=null) {return new WP_Post();}
$plugin=$argv[1] ?? ''; $state=$argv[2] ?? 'normal';
if (!$plugin || !in_array($state,array('normal','printed','late'),true)) { exit(3); }
require $plugin;
$rev=str_contains(basename($plugin),'r190') ? 'r190' : 'r189';
$preflight='fv_ex2_'.$rev.'_preflight';
$render='fv_ex2_'.$rev.'_render';
if ($state !== 'late') {
    $preflight();
    if ($state === 'printed') {
       foreach ($GLOBALS['styles'] as $key=>$value) $GLOBALS['styles'][$key]='done';
       $GLOBALS['head_done']=true;
    }
} else $GLOBALS['head_done']=true;
$html=$render();
echo json_encode(array(
 'is_evidence'=>str_contains($html,'Four dates. Distinct kinds of evidence.'),
 'is_fallback'=>str_contains($html,'The Apollo evidence Atlas is unavailable'),
 'cta_count'=>substr_count($html,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),
 'js_enqueued'=>array_key_exists('fv-apollo-'.$rev.'-context',$GLOBALS['scripts']),
 'css_state'=>$GLOBALS['styles']['fv-apollo-'.$rev] ?? 'absent',
 'chronology_count'=>substr_count($html,'<time datetime='),
 'source_details'=>substr_count($html,'<details>'),
 'campaign_not_embedded'=>strpos($html,'utm_source=')===false,
),JSON_THROW_ON_ERROR);
