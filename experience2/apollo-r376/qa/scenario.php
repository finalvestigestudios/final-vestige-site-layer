<?php
/** R376 WordPress lifecycle API-stub, NOT an installed WordPress integration. */
$scenario = $argv[1] ?? 'enabled';
$as_html = in_array('--html', $argv, true);
define('ABSPATH', dirname(__DIR__, 4).'/');
if ($scenario !== 'disabled') {
    define('FV_APOLLO_R376_STAGING_ENABLED', true);
    define('FV_APOLLO_R376_APPROVED_HOST', 'staging.fv-review.invalid');
}
$S = array('environment' => $scenario === 'production' ? 'production':'staging',
 'url' => $scenario === 'wronghost' ? 'https://impostor.fv-review.invalid/' : 'https://staging.fv-review.invalid/',
 'actions'=>array(), 'shortcodes'=>array(), 'styles'=>array(),
 'posts'=>array(3=>(object)array('post_type'=>'post','post_content'=>'a separate unrelated post')),
 'id'=>3,'is_admin'=>false,'singular'=>true);
function wp_get_environment_type() {global $S;return $S['environment'];}
function home_url($p='') {global $S;return $S['url'];}
function is_admin(){global $S;return $S['is_admin'];}
function is_singular(){global $S;return $S['singular'];}
function get_queried_object_id(){global $S;return $S['id'];}
function get_post($id){global $S;return $S['posts'][$id]??null;}
function get_stylesheet(){return 'assembler';}
function get_block_template($id,$type){return null;}
function parse_blocks($html){return array();}
function has_shortcode($html,$tag){return str_contains($html,'['.$tag.']');}
function add_shortcode($tag,$callback){global $S;$S['shortcodes'][$tag]=$callback;}
function remove_shortcode($tag){global $S;unset($S['shortcodes'][$tag]);}
function shortcode_exists($tag){global $S;return array_key_exists($tag,$S['shortcodes']);}
function add_action($hook,$callback,$priority=10){global $S;$S['actions'][]=array($hook,$callback,$priority);}
function remove_action($hook,$callback,$priority=10){global $S;$before=count($S['actions']);$S['actions']=array_values(array_filter($S['actions'],fn($a)=>$a!==array($hook,$callback,$priority)));return count($S['actions'])<$before;}
function has_action($hook,$callback){global $S;foreach($S['actions'] as $a)if($a[0]===$hook && $a[1]===$callback)return $a[2];return false;}
function wp_enqueue_style($handle,$url,$deps=array(),$version=null){global $S;$S['styles'][$handle]=compact('handle','url','deps','version');}
function wp_style_is($handle,$where){global $S;return array_key_exists($handle,$S['styles']);}
function plugins_url($url,$file){return 'https://staging.fv-review.invalid/static/'.$url;}
function run_hook($hook){global $S;$a=array_filter($S['actions'],fn($v)=>$v[0]===$hook);usort($a,fn($x,$y)=>$x[2]<=>$y[2]);foreach($a as $item)call_user_func($item[1]);}
if ($scenario === 'preowned') {add_shortcode('fv_apollo_source_path_r372','preowned_handler');}
function preowned_handler($args=array()){return '<p>Other owner remains intact</p>';}
if ($scenario === 'functioncollision') {function fv_apollo_r365_rows(){return array();}}
require dirname(__DIR__).'/secure-gate.php';
$checks=array();function ck($ok,$name){global $checks;$checks[$name]=(bool)$ok;}
$root=dirname(__DIR__,2);
ck(count(fv_apollo_r376_manifest())===6,'manifest_has_six_dependencies');
ck(fv_apollo_r376_files_valid($root),'reviewed_dep_bytes_verified');
$approved = ($scenario==='enabled'||$scenario==='preowned'||$scenario==='functioncollision'||$scenario==='mutation');
ck(fv_apollo_r376_environment()===$approved,'staging_host_environment_gate');
run_hook('plugins_loaded');
$active=($scenario==='enabled'||$scenario==='mutation');
ck(function_exists('fv_apollo_r372_shortcode')===$active,'expected_wordpress_load_state');
$tag='fv_apollo_source_path_r372';
if ($scenario === 'preowned') {
    ck($S['shortcodes'][$tag]==='preowned_handler','preexisting_callback_never_overwritten');
    ck(call_user_func($S['shortcodes'][$tag])==='<p>Other owner remains intact</p>','preexisting_output_intact');
} elseif ($scenario==='functioncollision') {
    ck(!shortcode_exists($tag),'collided_family_does_not_claim_shortcode');
} elseif ($approved) {
    ck(shortcode_exists($tag),'staging_shortcode_registered');
    ck(($S['shortcodes'][$tag]??null)==='fv_apollo_r372_shortcode','approved_source_renderer_owns_shortcode');
} else {
    ck(!shortcode_exists($tag),'nonapproved_environment_has_no_shortcode');
}
ck(!shortcode_exists('fv_apollo_chronology_r365'),'unreviewed_chronology_shortcode_not_exposed');
ck(!shortcode_exists('fv_apollo_source_gallery_r371'),'unreviewed_gallery_shortcode_not_exposed');
ck(has_action('wp_enqueue_scripts','fv_apollo_r365_enqueue')===false,'global_style_hook_absent');
$rendered='';
if ($active) {
    $S['posts'][3]->post_content='unrelated content';run_hook('wp_enqueue_scripts');
    ck(count($S['styles'])===0,'unrelated_page_zero_assets');
    $S['posts'][3]->post_content='[fv_apollo_source_path_r372]';run_hook('wp_enqueue_scripts');run_hook('wp_enqueue_scripts');
    ck(count($S['styles'])===1,'only_one_r372_css');
    $rendered=call_user_func($S['shortcodes'][$tag],array());
    ck(substr_count($rendered,'data-fv-evidence-stage')===4,'four_approved_chronology_stages');
    ck(substr_count($rendered,'data-fv-source-drawer')===4,'four_native_source_drawers');
    ck(substr_count($rendered,'data-fv-nasa-source')===4,'source_evidence_links');
    ck(substr_count($rendered,'data-fv-free-cta')===1,'exactly_one_free_next_action');
    ck(!str_contains($rendered,'payhip.com'),'no_unapproved_checkout');
}
if ($scenario==='mutation') {
    $temporary=sys_get_temp_dir().'/apollo_r376_'.getmypid();
    foreach(fv_apollo_r376_manifest() as $path=>$digest){$target=$temporary.'/'.$path;@mkdir(dirname($target),0770,true);copy($root.'/'.$path,$target);}
    ck(fv_apollo_r376_files_valid($temporary),'copied_reviewed_tree_passes');
    file_put_contents($temporary.'/apollo-r372/assets/evidence-path.css','/* tampered */', FILE_APPEND);
    ck(!fv_apollo_r376_files_valid($temporary),'tampered_css_rejected');
    copy($root.'/apollo-r372/assets/evidence-path.css',$temporary.'/apollo-r372/assets/evidence-path.css');
    rename($temporary.'/apollo-r372/assets',$temporary.'/apollo-r372/real-assets');
    symlink('real-assets',$temporary.'/apollo-r372/assets');
    ck(!fv_apollo_r376_files_valid($temporary),'symlinked_ancestor_rejected');
    unlink($temporary.'/apollo-r372/assets');rename($temporary.'/apollo-r372/real-assets',$temporary.'/apollo-r372/assets');
    foreach(fv_apollo_r376_manifest() as $path=>$digest)unlink($temporary.'/'.$path);
    foreach(array('apollo-r365','apollo-r367','apollo-r371','apollo-r372/assets','apollo-r372') as $dir)@rmdir($temporary.'/'.$dir);
    @rmdir($temporary);
}
$passes=count(array_filter($checks));$fails=count($checks)-$passes;
if ($as_html) {
    if($fails){fwrite(STDERR,json_encode($checks));exit(1);}
    $css=file_get_contents($root.'/apollo-r372/assets/evidence-path.css');
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R376 WordPress stub — NOT installed staging</title><style>'.str_replace('</style','<\\/style',$css).'</style></head><body>'.$rendered.'</body></html>';
} else {
    echo json_encode(array('scenario'=>$scenario,'status'=>$fails?'FAIL':'API_STUB_ONLY_PASS','checks'=>$checks,'passed'=>$passes,'failed'=>$fails,'styles'=>array_values($S['styles'])),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
}
exit($fails?1:0);
