<?php
/** WordPress API stub, not a real WP installation. */
define('ABSPATH', true);
$main = (object)array('post_type'=>'post','post_content'=>'');
$blocks = array(); $styles=array(); $scripts=array(); $shortcodes=array();
function is_singular(){return true;}
function get_post($id=null){global $main,$blocks;return $id===null?$main:($blocks[$id]??null);}
function has_shortcode($c,$tag){return strpos($c,'['.$tag)!==false;}
function parse_blocks($c){ preg_match_all('/<!-- wp:block \{"ref":([0-9]+)\} \/-->/', $c,$m);return array_map(function($x){return array('blockName'=>'core/block','attrs'=>array('ref'=>(int)$x));},$m[1]); }
function add_shortcode($name,$callback){global $shortcodes;$shortcodes[$name]=$callback;}
function add_action($name,$callback){}
function plugins_url($relative,$file){return '/wp-content/plugins/apollo-r347/'.ltrim($relative,'/');}
function wp_enqueue_style($name,$url,$deps,$version){global $styles;$styles[$name]=$url;}
function wp_enqueue_script($name,$url,$deps,$version,$footer){global $scripts;$scripts[$name]=$url;}
require dirname(__DIR__).'/source-index.php';
function check($ok,$name){if(!$ok)throw new RuntimeException('FAILED '.$name);echo "PASS $name\n";}
check(isset($shortcodes['fv_apollo_experience_r347'],$shortcodes['fv_apollo_source_index_r347']),'two distinct shortcodes registered');
$main->post_content='Ordinary content';fv_apollo_r347_enqueue();check(count($GLOBALS['styles'])===0,'unrelated content never enqueues');
$main->post_content='[fv_apollo_source_index_r347]';fv_apollo_r347_enqueue();check(array_keys($GLOBALS['styles'])===array('fv-apollo-r347-index'),'index-only loads one stylesheet');check(count($GLOBALS['scripts'])===1,'index-only optional JavaScript queued');
$styles=$scripts=array();$main->post_content='[fv_apollo_experience_r347]';fv_apollo_r347_enqueue();check(count($styles)===4,'composite loads four scoped CSS handles');check(count($scripts)===1,'composite filter JS queued');
$styles=$scripts=array();$main->post_content='<!-- wp:block {"ref":17} /-->';
$blocks[17]=(object)array('post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":18} /-->');
$blocks[18]=(object)array('post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r347] <!-- wp:block {"ref":17} /-->');
fv_apollo_r347_enqueue();check(count($styles)===4,'nested cyclic reusable block resolves once');
$styles=$scripts=array();$main->post_content='<!-- wp:block {"ref":9999} /-->';fv_apollo_r347_enqueue();check(count($styles)===0,'missing block fails safely');
$styles=$scripts=array();$main->post_content=str_repeat('A',500001).'[fv_apollo_experience_r347]';fv_apollo_r347_enqueue();check(count($styles)===0,'oversized content short-circuits bounded scan');
$markup=fv_apollo_r347_experience_shortcode();check(substr_count($markup,'data-fv-apollo-entry=')===13,'composite has 13 canonical-source entries');check(substr_count($markup,'data-fv-r339-cta="editorial"')===1,'composite has exactly one editorial continuation');
check(strpos($markup,'payhip.com')===false&&strpos($markup,'data-geo-pin')===false&&strpos($markup,'<img')===false,'no merchandise, map pins or embedded photos');
echo "PASS preflight: 12/12\n";
