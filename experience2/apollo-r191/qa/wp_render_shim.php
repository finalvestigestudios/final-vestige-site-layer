<?php
/** WordPress-function shim only: NOT an installed WordPress acceptance test. */
define('ABSPATH','/test/');
class WP_Post { public $post_content='[fv_ex2_apollo_atlas]'; public $post_type='post'; }
$GLOBALS['css']=array();$GLOBALS['js']=array();$GLOBALS['headed']=0;
function plugin_dir_path($file){return dirname($file).'/';}
function plugins_url($file,$plugin){return '/staging/apollo/'.$file;}
function wp_enqueue_style($name,...$args){$GLOBALS['css'][$name]='enqueued';}
function wp_enqueue_script($name,...$args){$GLOBALS['js'][$name]='enqueued';}
function wp_style_is($name,$status){return ($GLOBALS['css'][$name]??'')===$status;}
function did_action($hook){return $hook==='wp_head'?$GLOBALS['headed']:0;}
function add_action(...$args){}
function add_shortcode(...$args){}
function is_admin(){return false;}
function is_singular(){return true;}
function get_queried_object(){return new WP_Post;}
function has_shortcode($content,$tag){return str_contains($content,'['.$tag);}
function parse_blocks($content){return array();}
function get_post($ref){return new WP_Post;}
$plugin=$argv[1]??'';$mode=$argv[2]??'normal';
if (!$plugin || !in_array($mode,['normal','late','printed'],true))exit(3);
require $plugin;
if($mode!=='late') fv_ex2_r191_preflight();
if($mode==='printed'){$GLOBALS['headed']=1;foreach($GLOBALS['css'] as $k=>$v)$GLOBALS['css'][$k]='done';}
if($mode==='late')$GLOBALS['headed']=1;
$rendered=fv_ex2_r191_render();
echo json_encode([
 'html'=>$rendered,
 'js'=>isset($GLOBALS['js']['fv-apollo-r191-context']),
 'css'=>$GLOBALS['css']['fv-apollo-r191']??'absent',
 'fallback'=>str_contains($rendered,'The Apollo evidence Atlas is unavailable'),
 'chronology'=>substr_count($rendered,'<time datetime='),
 'details'=>substr_count($rendered,'<details>'),
],JSON_THROW_ON_ERROR);
