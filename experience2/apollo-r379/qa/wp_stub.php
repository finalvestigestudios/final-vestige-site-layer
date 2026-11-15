<?php
/** Deterministic WP API simulation; NOT an installed WordPress site. */
$scenario = $argv[1] ?? 'part';
$want_html = in_array('--html', $argv, true);
define('ABSPATH', __DIR__ . '/');
if ($scenario !== 'disabled') {
    define('FV_R377_STAGING_ENABLED', true);
    define('FV_R377_APPROVED_HOST', 'apollo-staging.invalid');
}
$GLOBALS['shortcode_tags'] = array(); $GLOBALS['hooks'] = array();
$GLOBALS['styles'] = array(); $GLOBALS['read_part_calls'] = array();
$GLOBALS['env'] = $scenario === 'production' ? 'production' : 'staging';
$GLOBALS['host_url'] = $scenario === 'wronghost' ? 'https://wrong.invalid/' : 'https://apollo-staging.invalid/';
$GLOBALS['_wp_current_template_id'] = $scenario === 'no_id' ? '' : 'assembler//single';
$GLOBALS['theme'] = 'assembler';
$GLOBALS['posts'] = array(101=>(object)array('post_type'=>'wp_block','post_status'=>'publish','post_content'=>''));
function b($name,$html='',$attrs=array(),$inner=array()) {return array('blockName'=>$name,'innerHTML'=>$html,'attrs'=>$attrs,'innerBlocks'=>$inner);}
function encoded($blocks){return json_encode($blocks,JSON_THROW_ON_ERROR);}
$target='[fv_apollo_source_role_desk_r377]';
$GLOBALS['templates']=array(
 'assembler//single'=> (object)array('id'=>'assembler//single','theme'=>'assembler','type'=>'wp_template','status'=>'publish','content'=>encoded(array(b('core/template-part','',array('slug'=>'evidence'))))),
 'assembler//evidence'=> (object)array('id'=>'assembler//evidence','theme'=>'assembler','type'=>'wp_template_part','status'=>'publish','content'=>encoded(array(b('core/shortcode',$target)))),
 'assembler//nested'=> (object)array('id'=>'assembler//nested','theme'=>'assembler','type'=>'wp_template_part','status'=>'publish','content'=>encoded(array(b('core/template-part','',array('slug'=>'evidence'))))),
);
$GLOBALS['posts'][10]=(object)array('post_type'=>'page','post_status'=>'publish','post_content'=>'no shortcode');
if($scenario==='nested')$GLOBALS['templates']['assembler//single']->content=encoded(array(b('core/template-part','',array('slug'=>'nested'))));
if($scenario==='reusable'){
  $GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/block','',array('ref'=>101))));
  $GLOBALS['posts'][101]->post_content=encoded(array(b('core/shortcode',$target)));
}
if($scenario==='duplicate'){
  $GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/shortcode',$target)));
  $GLOBALS['posts'][10]->post_content=$target;
}
if($scenario==='cycle'){
  $GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/template-part','',array('slug'=>'nested'))));
  $GLOBALS['templates']['assembler//nested']->content=encoded(array(b('core/template-part','',array('slug'=>'evidence'))));
}
if($scenario==='cycle_with_sibling'){
  $GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/template-part','',array('slug'=>'nested'))));
  $GLOBALS['templates']['assembler//nested']->content=encoded(array(b('core/template-part','',array('slug'=>'evidence'))));
  $GLOBALS['templates']['assembler//single']->content=encoded(array(b('core/template-part','',array('slug'=>'evidence')),b('core/shortcode',$target)));
}
if($scenario==='missing_with_sibling')$GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/template-part','',array('slug'=>'absent')),b('core/shortcode',$target)));
if($scenario==='draft_with_sibling'){
  $GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/template-part','',array('slug'=>'nested')),b('core/shortcode',$target)));
  $GLOBALS['templates']['assembler//nested']->status='draft';
}
if($scenario==='foreign_with_sibling')$GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/template-part','',array('slug'=>'nested','theme'=>'other')),b('core/shortcode',$target)));
if($scenario==='bad_ref_with_sibling')$GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/block','',array('ref'=>'101')),b('core/shortcode',$target)));
if($scenario==='block_cycle_with_sibling'){
  $GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/block','',array('ref'=>101)),b('core/shortcode',$target)));
  $GLOBALS['posts'][101]->post_content=encoded(array(b('core/block','',array('ref'=>101))));
}
if($scenario==='dag_reuse')$GLOBALS['templates']['assembler//single']->content=encoded(array(b('core/template-part','',array('slug'=>'evidence')),b('core/template-part','',array('slug'=>'evidence'))));
if($scenario==='foreign_theme'){
  $GLOBALS['templates']['assembler//single']->content=encoded(array(b('core/template-part','',array('slug'=>'evidence','theme'=>'other'))));
}
if($scenario==='bad_slug'){
  $GLOBALS['templates']['assembler//single']->content=encoded(array(b('core/template-part','',array('slug'=>'../evidence'))));
}
if($scenario==='wrong_identity')$GLOBALS['templates']['assembler//evidence']->theme='other';
if($scenario==='draft')$GLOBALS['templates']['assembler//evidence']->status='draft';
if($scenario==='hidden_in_attrs')$GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/group','',array('note'=>$target))));
if($scenario==='code_sample')$GLOBALS['templates']['assembler//evidence']->content=encoded(array(b('core/code',$target)));
if($scenario==='missing_part')unset($GLOBALS['templates']['assembler//evidence']);
if($scenario==='wrong_template_type')$GLOBALS['templates']['assembler//single']->type='wp_template_part';
if($scenario==='oversize')$GLOBALS['templates']['assembler//evidence']->content=str_repeat('a',1024*1024+1);
if($scenario==='foreign_owner')$GLOBALS['shortcode_tags']['fv_apollo_source_role_desk_r377']='foreign_shortcode';
function foreign_shortcode(){return 'other';}
function wp_get_environment_type(){return $GLOBALS['env'];}
function home_url($path=''){return $GLOBALS['host_url'];}
function get_stylesheet(){return $GLOBALS['theme'];}
function add_action($name,$cb,$priority=10){$GLOBALS['hooks'][]=array($name,$cb,$priority);}
function do_action_stub($name){$calls=array_values(array_filter($GLOBALS['hooks'],fn($x)=>$x[0]===$name));usort($calls,fn($a,$b)=>$a[2]<=>$b[2]);foreach($calls as $call){call_user_func($call[1]);}}
function shortcode_exists($tag){return isset($GLOBALS['shortcode_tags'][$tag]);}
function add_shortcode($tag,$cb){$GLOBALS['shortcode_tags'][$tag]=$cb;}
function has_shortcode($str,$tag){return preg_match('/\['.preg_quote($tag,'/').'(?=\]|\s|\/)/',(string)$str)===1;}
function is_singular(){return true;}
function get_queried_object_id(){return 10;}
function get_post($id){return $GLOBALS['posts'][$id]??null;}
function parse_blocks($content){$parsed=json_decode($content,true);return is_array($parsed)?$parsed:array();}
function get_block_template($id,$type='wp_template'){
    $GLOBALS['read_part_calls'][]=array($id,$type);
    return $GLOBALS['templates'][$id]??null;
}
function wp_enqueue_style($handle,$url,$deps,$version){$GLOBALS['styles'][$handle]=compact('handle','url','deps','version');}
function wp_style_is($handle,$status='enqueued'){return isset($GLOBALS['styles'][$handle]);}
function plugins_url($path,$file){return 'https://apollo-staging.invalid/plugin/'. $path;}
require dirname(__DIR__,2).'/apollo-r377/source-role-desk.php';
require dirname(__DIR__,2).'/apollo-r378/guarded-reusable-assets.php';
require dirname(__DIR__).'/prehead-template-parts.php';
$checks=array();
function ck($name,$ok){$GLOBALS['checks'][$name]=((bool)$ok);}
$expected = in_array($scenario,array('part','nested','reusable','duplicate','dag_reuse'),true);
do_action_stub('plugins_loaded');
$pre = fv_r379_current_template();
ck('verified_current_template',($pre !== null) === ($scenario !== 'no_id' && $scenario !== 'wrong_template_type'));
$scan=$pre !== null && fv_r379_template_contains_shortcode($pre);
ck('template_scan_expected', $scan === in_array($scenario,array('part','nested','reusable','duplicate','dag_reuse','production','wronghost','disabled','foreign_owner'),true));
ck('scan_does_not_enqueue',count($GLOBALS['styles'])===0);
do_action_stub('wp_enqueue_scripts');
ck('enqueued_if_approved', (count($GLOBALS['styles']) === 1) === $expected);
ck('no_duplicate_styles',count($GLOBALS['styles'])<=1);
ck('no_unapproved_external_requests', !isset($GLOBALS['styles']['remote']));
ck('owner_remains_preserved',$scenario==='foreign_owner' ? ($GLOBALS['shortcode_tags'][FV_R377_TAG]==='foreign_shortcode') : ($GLOBALS['shortcode_tags'][FV_R377_TAG]??null)==='fv_r377_shortcode' || in_array($scenario,array('production','wronghost','disabled'),true));
if($expected){
 ck('r377_style_handle_present',isset($GLOBALS['styles']['fv-apollo-r377-source-role']));
 ck('asset_version_is_sealed',strpos($GLOBALS['styles']['fv-apollo-r377-source-role']['version'],'r377-')===0);
 ck('source_integrity_still_sealed',fv_r377_records()!==null && count(fv_r377_records())===6);
 $html=fv_r377_shortcode();
 ck('historical_cards_preserved',substr_count($html,'data-fv-r377-record')===6);
 ck('single_free_cta',substr_count($html,'data-fv-free-cta')===1);
 ck('no_paid_cta',strpos($html,'payhip')===false);
}
$failed=array_keys(array_filter($checks,fn($x)=>!$x));
if($want_html){
 if($failed)exit(1);
 echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R379 local API stub — NOT WordPress</title></head><body>'.$html.'</body></html>';
}else{
 echo json_encode(array('scenario'=>$scenario,'checks'=>$checks,'passed'=>count($checks)-count($failed),'failed'=>$failed,'stylesheet_count'=>count($GLOBALS['styles']),'template_reads'=>count($GLOBALS['read_part_calls'])),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES).'\n';
}
exit($failed?1:0);
