<?php
/** Deterministic WordPress API stub: never represents installed WordPress. */
$scenario=$argv[1]??'enabled';$html=in_array('--html',$argv,true);
define('ABSPATH', __DIR__ . '/');
if ($scenario!=='disabled') {define('FV_R377_STAGING_ENABLED',true); define('FV_R377_APPROVED_HOST','staging.r377.invalid');}
$GLOBALS['mock']=array('environment'=>$scenario==='production'?'production':'staging','url'=> $scenario==='wronghost'?'https://other.invalid/':'https://staging.r377.invalid/',
'actions'=>array(),'tags'=>array(),'styles'=>array(),'post'=>(object)array('post_content'=>'Unrelated text'));
function wp_get_environment_type(){return $GLOBALS['mock']['environment'];}
function home_url($p=''){return $GLOBALS['mock']['url'];}
function add_action($n,$fn,$priority=10){$GLOBALS['mock']['actions'][]=array($n,$fn,$priority);}
function run_hook($n){$hooks=array_filter($GLOBALS['mock']['actions'],fn($a)=>$a[0]===$n);usort($hooks,fn($a,$b)=>$a[2]<=>$b[2]);foreach($hooks as $h)call_user_func($h[1]);}
function shortcode_exists($n){return isset($GLOBALS['mock']['tags'][$n]);}
function add_shortcode($n,$fn){$GLOBALS['mock']['tags'][$n]=$fn;}
function is_singular(){return true;}
function get_post($id){return $GLOBALS['mock']['post'];}
function get_queried_object_id(){return 15;}
function has_shortcode($s,$tag){return str_contains($s,'['.$tag.']');}
function wp_enqueue_style($handle,$url,$d,$v){$GLOBALS['mock']['styles'][$handle]=compact('handle','url','v');}
function plugins_url($uri,$file){return 'https://staging.r377.invalid/approved/'.$uri;}
function foreign_owner(){return '<p>Foreign shortcode owner</p>';}
if ($scenario==='preowned') add_shortcode('fv_apollo_source_role_desk_r377','foreign_owner');
require dirname(__DIR__).'/source-role-desk.php';
$checks=array();
function ck($key,$value){$GLOBALS['checks'][$key]=(bool)$value;}
$enabled=in_array($scenario,array('enabled','preowned','tamper'),true);
ck('environment',fv_r377_environment()===$enabled);
ck('six_records',count(fv_r377_records()??array())===6);
run_hook('plugins_loaded');
if($scenario==='preowned') {
 ck('preserved_preowned',$GLOBALS['mock']['tags'][FV_R377_TAG] === 'foreign_owner');
 ck('foreign_output',call_user_func($GLOBALS['mock']['tags'][FV_R377_TAG])==='<p>Foreign shortcode owner</p>');
}else ck('owned_iff_approved',shortcode_exists(FV_R377_TAG)===($scenario==='enabled'||$scenario==='tamper'));
if ($scenario==='enabled'||$scenario==='tamper') {
 $GLOBALS['mock']['post']->post_content='Unrelated';run_hook('wp_enqueue_scripts');
 ck('no_sitewide_style',count($GLOBALS['mock']['styles'])===0);
 $GLOBALS['mock']['post']->post_content='['.FV_R377_TAG.']';run_hook('wp_enqueue_scripts');
 ck('only_conditional_stylesheet',count($GLOBALS['mock']['styles'])===1);
 $render=call_user_func($GLOBALS['mock']['tags'][FV_R377_TAG]);
 ck('six_rendered',substr_count($render,'data-fv-r377-record')===6);
 ck('six_native_drawers',substr_count($render,'data-fv-r377-source')===6);
 ck('one_free_cta',substr_count($render,'data-fv-free-cta')===1);
 ck('no_unapproved_merchant',!str_contains($render,'payhip.com') && !str_contains($render,'<img'));
 ck('distinct_source_roles',str_contains($render,'image catalog') && str_contains($render,'S66-58038'));
 $render2=fv_r377_render(fv_r377_records());
 ck('repeated_instance_unique_ids',preg_match('/aria-labelledby="([^"]+)"/', $render,$m) && preg_match('/aria-labelledby="([^"]+)"/', $render2,$n) && $m[1]!==$n[1]);
 $bad=fv_r377_records();$bad[2]['claim']='False: Crew photograph is a telemetry chart';
 ck('mutated_array_fallback',!str_contains(fv_r377_render($bad),'data-fv-r377-record'));
}
if ($scenario==='tamper') {
 $temp=tempnam(sys_get_temp_dir(),'fv377-');copy(dirname(__DIR__).'/custody.json',$temp);
 ck('copied_data_is_valid',fv_r377_records($temp)!==null);
 file_put_contents($temp,'\n{"injected":true}',FILE_APPEND);
 ck('altered_bytes_rejected',fv_r377_records($temp)===null);
 unlink($temp);$link=sys_get_temp_dir().'/fv377-link-'.getmypid();
 @symlink(dirname(__DIR__).'/custody.json',$link);ck('symlinked_record_rejected',fv_r377_records($link)===null);@unlink($link);
 ck('missing_file_rejected',fv_r377_records('/tmp/definitely-not-a-source-377.json')===null);
}
$failed=count(array_filter($checks,fn($v)=>$v===false));
if($html){if($failed){fwrite(STDERR,json_encode($checks));exit(1);}echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R377 local fixture—not WordPress staging</title><link rel="stylesheet" href="../assets/source-role.css"></head><body>'.($render??'').'</body></html>';}
else echo json_encode(array('scenario'=>$scenario,'status'=>$failed?'FAIL':'API_STUB_PASS','checks'=>$checks,'passed'=>count($checks)-$failed,'failed'=>$failed),JSON_PRETTY_PRINT)."\n";
exit($failed?1:0);
