<?php
/** Actual PHP/WordPress API-stub integration, NOT an installed WP test. */
$scenario = $argv[1] ?? 'enabled';
$as_html = in_array('--html', $argv, true);
define('ABSPATH', dirname(__DIR__, 4).'/');
if ($scenario === 'enabled' || $scenario === 'modified' || $scenario === 'collision') {
    define('FV_APOLLO_R375_STAGING_ENABLED', true);
    define('FV_APOLLO_R375_APPROVED_HOST', 'staging.fv-test.invalid');
} elseif ($scenario === 'production' || $scenario === 'wronghost') {
    define('FV_APOLLO_R375_STAGING_ENABLED', true);
    define('FV_APOLLO_R375_APPROVED_HOST', 'staging.fv-test.invalid');
}
if ($scenario === 'collision') { function fv_apollo_r365_rows() { return []; } }
$S = array('env'=>($scenario==='production'?'production':'staging'),
           'url'=>($scenario==='wronghost'?'https://lookalike.fv-test.invalid/':'https://staging.fv-test.invalid/'),
           'actions'=>array(), 'shortcodes'=>array(), 'styles'=>array(),
           'posts'=>array(88=>(object)array('post_type'=>'post','post_content'=>'unrelated page')),
           'id'=>88,'is_admin'=>false,'singular'=>true);
function wp_get_environment_type(){global $S;return $S['env'];}
function home_url($path=''){global $S;return $S['url'];}
function is_admin(){global $S;return $S['is_admin'];}
function is_singular(){global $S;return $S['singular'];}
function get_queried_object_id(){global $S;return $S['id'];}
function get_post($id){global $S;return $S['posts'][$id]??null;}
function get_stylesheet(){return 'assembler';}
function get_block_template($id,$kind){return null;}
function parse_blocks($txt){return array();}
function has_shortcode($txt,$name){return str_contains($txt,'['.$name.']');}
function add_shortcode($tag,$callback){global $S;$S['shortcodes'][$tag]=$callback;}
function add_action($hook,$fn,$priority=10){global $S;$S['actions'][]=array($hook,$fn,$priority);}
function remove_action($hook,$fn,$priority=10){global $S;
    $S['actions']=array_values(array_filter($S['actions'],fn($a)=>$a!==array($hook,$fn,$priority)));
}
function wp_enqueue_style($handle,$url,$deps=array(),$version=null){global $S;$S['styles'][]=compact('handle','url','deps','version');}
function wp_style_is($handle,$status){global $S;return in_array($handle,array_column($S['styles'],'handle'),true);}
function plugins_url($path,$from){return 'https://staging.fv-test.invalid/assets/'.$path;}
function run_hook($hook){global $S;$a=array_filter($S['actions'],fn($x)=>$x[0]===$hook);
    usort($a,fn($x,$y)=>$x[2]<=>$y[2]);foreach($a as $x){call_user_func($x[1]);}
}
require __DIR__.'/../staging-gate.php';
$checks=array();
function ck($ok,$name){global $checks;$checks[$name]=(bool)$ok;}
$root=dirname(__DIR__,2);
ck(fv_apollo_r375_files_valid($root),'reviewed_dependencies_match');
ck(fv_apollo_r375_manifest()!==array(),'six_pinned_sources');
ck(count(fv_apollo_r375_manifest())===6,'six_files');
$can=($scenario==='enabled'||$scenario==='modified');
ck(fv_apollo_r375_environment()===($scenario==='enabled'||$scenario==='modified'||$scenario==='collision'),'environment_guard');
run_hook('plugins_loaded');
$loaded=function_exists('fv_apollo_r372_shortcode');
ck($loaded===$can,'staging_only_load');
ck(!in_array(array('wp_enqueue_scripts','fv_apollo_r365_enqueue',20),$S['actions'],true),'no_unconditional_global_r365_style');
$callback=$S['shortcodes']['fv_apollo_source_path_r372']??null;
ck(is_callable($callback),'shortcode_registered');
$unrelated=call_user_func($callback,array());
$S['posts'][88]->post_content='unrelated page';
run_hook('wp_enqueue_scripts');
ck(count($S['styles'])===0,'unrelated_article_has_zero_css');
$S['posts'][88]->post_content='[fv_apollo_source_path_r372]';
run_hook('wp_enqueue_scripts');run_hook('wp_enqueue_scripts');
$html=call_user_func($callback,array());
if ($can) {
    ck(count($S['styles'])===1,'repeated_hooks_enqueue_one_css');
    ck($S['styles'][0]['handle']==='fv-apollo-r372-evidence-path','r372_scoped_css_only');
    ck(substr_count($html,'data-fv-evidence-stage')===4,'exactly_four_stages');
    ck(substr_count($html,'data-fv-source-drawer')===4,'four_native_drawers');
    ck(substr_count($html,'data-fv-free-cta')===1,'single_free_ordinance');
    ck(substr_count($html,'data-fv-nasa-source')===4,'four_nasa_source_relations');
    ck(substr_count($html,'data-fv-nasa-context')===1,'separate_retrospective');
    ck(str_contains($html,'Not established:'),'uncertainty_visible');
    ck(str_contains($html,'No coordinates, speculative map edges'),'no_map_claim');
    ck(!str_contains($html,'href="https://payhip.com/'),'no_checkout');
} else {
    ck(count($S['styles'])===0,'disabled_css_zero');
    ck(!str_contains($html,'nasa.gov'),'disabled_does_not_expose_unverified_nasa');
    ck(str_contains($html,'Read the existing free Apollo 1 investigation'),'disabled_useful_fallback');
}
// Test stale/corrupt dependencies in a disposable copy; no upstream edits.
if ($scenario==='modified') {
    $dir=sys_get_temp_dir().'/fv_r375_'.getmypid();
    foreach(fv_apollo_r375_manifest() as $rel=>$hash){
        $dst=$dir.'/'.$rel; @mkdir(dirname($dst),0770,true);
        copy($root.'/'.$rel,$dst);
    }
    ck(fv_apollo_r375_files_valid($dir),'disposable_clean_copy_accepted');
    file_put_contents($dir.'/apollo-r372/assets/evidence-path.css','/* corrupted */',FILE_APPEND);
    ck(!fv_apollo_r375_files_valid($dir),'mutated_css_rejected');
    file_put_contents($dir.'/apollo-r372/assets/evidence-path.css',file_get_contents($root.'/apollo-r372/assets/evidence-path.css'));
    file_put_contents($dir.'/apollo-r371/source-gallery.php','<?php // swapped',FILE_APPEND);
    ck(!fv_apollo_r375_files_valid($dir),'mutated_documentary_code_rejected');
    foreach(fv_apollo_r375_manifest() as $rel=>$hash)unlink($dir.'/'.$rel);
    foreach(array('apollo-r365','apollo-r367','apollo-r371','apollo-r372/assets','apollo-r372') as $name) @rmdir($dir.'/'.$name);
    @rmdir($dir);
}
$pass=count(array_filter($checks));$fail=count($checks)-$pass;
if ($as_html) {
    if ($fail){fwrite(STDERR,json_encode($checks)."\n");exit(1);}
    $css=file_get_contents($root.'/apollo-r372/assets/evidence-path.css');
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo R375 local WordPress stub — NOT staging</title>';
    echo '<style>'.str_replace('</style','<\/style',$css).'</style></head><body>'.$html.'</body></html>';
} else {
    echo json_encode(array('scenario'=>$scenario,'status'=>$fail?'FAIL':'API_STUB_PASS_NOT_WORDPRESS',
        'passed'=>$pass,'failed'=>$fail,'checks'=>$checks,'styles'=>$S['styles']),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
}
exit($fail?1:0);
