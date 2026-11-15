<?php
/** R378 WordPress API-stub regression; NOT a real WordPress install. */
$scenario=$argv[1]??'reusable';
define('ABSPATH',__DIR__.'/');
if ($scenario !== 'disabled') { define('FV_R377_STAGING_ENABLED',true); define('FV_R377_APPROVED_HOST','approved.staging.invalid'); }
$GLOBALS['styles']=array();$GLOBALS['hooks']=array();$GLOBALS['shortcode_tags']=array();
$GLOBALS['env']=$scenario==='production'?'production':'staging';
$GLOBALS['url']=$scenario==='wronghost'?'https://notapproved.invalid/':'https://approved.staging.invalid/';
$GLOBALS['posts']=array(10=>(object)array('ID'=>10,'post_type'=>'page','post_status'=>'publish','post_content'=>''));
$GLOBALS['posts'][101]=(object)array('ID'=>101,'post_type'=>'wp_block','post_status'=>'publish','post_content'=>'[fv_apollo_source_role_desk_r377]');
$GLOBALS['posts'][102]=(object)array('ID'=>102,'post_type'=>'wp_block','post_status'=>'draft','post_content'=>'[fv_apollo_source_role_desk_r377]');
$GLOBALS['posts'][103]=(object)array('ID'=>103,'post_type'=>'post','post_status'=>'publish','post_content'=>'[fv_apollo_source_role_desk_r377]');
$GLOBALS['posts'][201]=(object)array('ID'=>201,'post_type'=>'wp_block','post_status'=>'publish','post_content'=>'<!-- wp:block {"ref":202} /-->');
$GLOBALS['posts'][202]=(object)array('ID'=>202,'post_type'=>'wp_block','post_status'=>'publish','post_content'=>'<!-- wp:block {"ref":201} /-->');
function wp_get_environment_type(){return $GLOBALS['env'];}
function home_url($x=''){return $GLOBALS['url'];}
function add_action($name,$cb,$priority=10){$GLOBALS['hooks'][]=array($name,$cb,$priority);}
function do_hook($name){$r=array_filter($GLOBALS['hooks'],fn($h)=>$h[0]===$name);usort($r,fn($a,$b)=>$a[2]<=>$b[2]);foreach($r as $h){call_user_func($h[1]);}}
function shortcode_exists($name){return isset($GLOBALS['shortcode_tags'][$name]);}
function add_shortcode($name,$cb){$GLOBALS['shortcode_tags'][$name]=$cb;}
function has_shortcode($text,$tag){return preg_match('/\['.preg_quote($tag,'/').'(?=\s|\]|\/)/',(string)$text)===1;}
function parse_blocks($content){
 $r=array();preg_match_all('/<!--\s+wp:block\s+\{"ref":(\d+)\}\s+\/-->/',(string)$content,$m,PREG_SET_ORDER);
 foreach($m as $match)$r[]=array('blockName'=>'core/block','attrs'=>array('ref'=>(int)$match[1]),'innerBlocks'=>array());
 return $r;
}
function get_post($id){return $GLOBALS['posts'][$id]??null;}
function get_queried_object_id(){return 10;}
function is_singular(){return true;}
function plugins_url($uri,$file){return 'https://approved.staging.invalid/plugin/'.$uri;}
function wp_enqueue_style($handle,$url,$deps=array(),$version=''){$GLOBALS['styles'][$handle]=compact('handle','url','deps','version');}
function wp_style_is($handle,$kind='enqueued'){return isset($GLOBALS['styles'][$handle]);}
function foreign_owner(){return '<p>Foreign</p>';}
if($scenario==='preowned') add_shortcode('fv_apollo_source_role_desk_r377','foreign_owner');
require dirname(__DIR__,2).'/apollo-r377/source-role-desk.php';
require dirname(__DIR__).'/guarded-reusable-assets.php';
$checks=[];
function check($n,$truth){$GLOBALS['checks'][$n]=(bool)$truth;}
check('correct_host',fv_r377_environment()===!in_array($scenario,array('production','wronghost','disabled'),true));
check('sealed_css',fv_r378_css_asset()!==null);
do_hook('plugins_loaded');
$expectedOwner=!in_array($scenario,array('production','wronghost','disabled','preowned'),true);
check('shortcode_ownership',fv_r378_r377_owner()===$expectedOwner);
// Establish rendered post before wp_enqueue_scripts.
$models=array(
 'direct'=>'[fv_apollo_source_role_desk_r377]',
 'reusable'=>'<!-- wp:block {"ref":101} /-->',
 'nested'=>'<!-- wp:block {"ref":301} /-->',
 'duplicate'=>'<!-- wp:block {"ref":101} /--><!-- wp:block {"ref":101} /-->',
 'cycle'=>'<!-- wp:block {"ref":201} /-->',
 'wrong_type'=>'<!-- wp:block {"ref":103} /-->',
 'draft'=>'<!-- wp:block {"ref":102} /-->',
 'unrelated'=>'No Apollo shortcode or block',
 'production'=>'<!-- wp:block {"ref":101} /-->',
 'wronghost'=>'<!-- wp:block {"ref":101} /-->',
 'disabled'=>'<!-- wp:block {"ref":101} /-->',
 'preowned'=>'<!-- wp:block {"ref":101} /-->',
 'oversize'=>str_repeat('X',1024*1024+1).'<!-- wp:block {"ref":101} /-->',
 'tamper'=>'<!-- wp:block {"ref":101} /-->',
 'symlink'=>'<!-- wp:block {"ref":101} /-->',
);
$GLOBALS['posts'][301]=(object)array('ID'=>301,'post_type'=>'wp_block','post_status'=>'publish','post_content'=>'<!-- wp:block {"ref":101} /-->');
$GLOBALS['posts'][10]->post_content=$models[$scenario]??$models['reusable'];
$shouldStyle=in_array($scenario,array('direct','reusable','nested','duplicate'),true);
check('finder_expected',fv_r378_has_shortcode_in_blocks($GLOBALS['posts'][10]->post_content)===in_array($scenario,array('direct','reusable','nested','duplicate','production','wronghost','disabled','preowned','tamper','symlink'),true));
$css=dirname(__DIR__,2).'/apollo-r377/assets/source-role.css';
$backup=file_get_contents($css);
if($scenario==='tamper') file_put_contents($css,$backup."\n/* injected */");
if($scenario==='symlink'){rename($css,$css.'.backup');symlink($css.'.backup',$css);}
try{
 check('css_integrity_check', (fv_r378_css_asset()!==null)===!in_array($scenario,array('tamper','symlink'),true));
 do_hook('wp_enqueue_scripts');
 check('conditional_enqueue',count($GLOBALS['styles'])===($shouldStyle?1:0));
 check('correct_handle',!$shouldStyle||isset($GLOBALS['styles']['fv-apollo-r377-source-role']));
 if($shouldStyle){
  $s=$GLOBALS['styles']['fv-apollo-r377-source-role'];
  check('expected_style_url',str_ends_with($s['url'],'assets/source-role.css'));
  if($scenario!=='direct')check('sha_pinned_version',str_contains($s['version'],'7a900dc0bf5e'));
  do_hook('wp_enqueue_scripts');
  check('repeated_hook_dedup',count($GLOBALS['styles'])===1);
 }
 if($scenario==='preowned')check('foreign_owner_preserved',$GLOBALS['shortcode_tags'][FV_R378_TARGET]==='foreign_owner');
}finally{
 if($scenario==='tamper')file_put_contents($css,$backup);
 if($scenario==='symlink'){unlink($css);rename($css.'.backup',$css);}
}
$failed=array_keys(array_filter($checks,fn($v)=>!$v));
if(in_array('--html',$argv,true)) {
 if($failed || !in_array($scenario,array('direct','reusable','nested','duplicate'),true)){fwrite(STDERR,json_encode($failed));exit(1);}
 $content = fv_r377_shortcode();
 $css=file_get_contents(dirname(__DIR__,2).'/apollo-r377/assets/source-role.css');
 echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
 .'<title>R378 approved staging API-stub fixture, NOT WordPress</title><style>'.$css.'</style></head><body>'.$content.'</body></html>';
 exit(0);
}
echo json_encode(array('scenario'=>$scenario,'passed'=>count($checks)-count($failed),'failed'=>$failed,'checks'=>$checks),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
exit(count($failed)?1:0);
