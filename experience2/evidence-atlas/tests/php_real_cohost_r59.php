<?php
/**
 * R59 CLI WordPress API contract probe using CURRENT SHA-pinned R84 Desk and
 * SOURCE-BUILT Atlas plus the unchanged R58 suite adapter. This is NOT WP core.
 * One PHP process per scenario to avoid static shortcode singleton side effects.
 */
declare(strict_types=1);
define('ABSPATH', '/tmp/fv-r59-cli-contract/');
define('FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS', array(42));
class WP_Post {
    public $ID;
    public $post_content;
    public function __construct(int $id, string $body='') {$this->ID=$id; $this->post_content=$body;}
}
$GLOBALS['hooks']=array(); $GLOBALS['shortcodes']=array();
$GLOBALS['styles']=array(); $GLOBALS['scripts']=array();
$GLOBALS['enqueued_styles']=array(); $GLOBALS['enqueued_scripts']=array();
$GLOBALS['page']=new WP_Post(42);
$GLOBALS['singular']=true;
function add_action($name,$callback,$priority=10){$GLOBALS['hooks'][]=array($name,$callback,$priority);}
function add_shortcode($name,$callback){$GLOBALS['shortcodes'][$name]=$callback;}
function shortcode_exists($name){return isset($GLOBALS['shortcodes'][$name]);}
function esc_url($value){return htmlspecialchars($value,ENT_QUOTES,'UTF-8');}
function plugin_dir_path($source){return dirname($source).'/';}
function plugins_url($path,$source){return 'fixture://'.basename(dirname($source)).'/'.$path;}
function is_singular(){return $GLOBALS['singular'];}
function get_queried_object(){return $GLOBALS['page'];}
function has_shortcode($content,$name){return strpos($content,'['.$name.']')!==false;}
function wp_register_style($name,$url,$dependencies=array(),$version=null){$GLOBALS['styles'][$name]=array('url'=>$url,'version'=>$version);}
function wp_register_script($name,$url,$dependencies=array(),$version=null,$footer=false){$GLOBALS['scripts'][$name]=array('url'=>$url,'version'=>$version,'footer'=>$footer);}
function wp_enqueue_style($name,$url=null,$dependencies=array(),$version=null){
    if($url!==null){wp_register_style($name,$url,$dependencies,$version);}
    if(isset($GLOBALS['styles'][$name])){$GLOBALS['enqueued_styles'][$name]=true;}
}
function wp_enqueue_script($name,$url=null,$dependencies=array(),$version=null,$footer=false){
    if($url!==null){wp_register_script($name,$url,$dependencies,$version,$footer);}
    if(isset($GLOBALS['scripts'][$name])){$GLOBALS['enqueued_scripts'][$name]=true;}
}
function do_action($name){
    $actions=array_values(array_filter($GLOBALS['hooks'],function($a)use($name){return $a[0]===$name;}));
    usort($actions,function($a,$b){return $a[2]<=>$b[2];});
    foreach($actions as $entry){call_user_func($entry[1]);}
}
$mode=$argv[1]??'nested';
$desk=getenv('FV_R59_DESK_ROOT'); $atlas=getenv('FV_R59_ATLAS_ROOT');
if(!$desk||!$atlas){fwrite(STDERR,"Missing ORIGINAL Desk or built Atlas root\n");exit(2);}
if(!in_array($mode,array('nested','top-level','not-allowed','non-singular'),true)){exit(2);}
$GLOBALS['page']=new WP_Post($mode==='not-allowed'?99:42,$mode==='top-level'?'[fv_ex2_apollo_suite]':'<!-- wp:block {"ref":123} /-->');
$GLOBALS['singular']=$mode!=='non-singular';
require rtrim($desk,'/').'/final-vestige-ex2-research-desk.php';
require rtrim($atlas,'/').'/final-vestige-ex2-evidence-atlas.php';
require dirname(__DIR__).'/integration/fv-ex2-apollo-suite.php';
do_action('wp_enqueue_scripts');
$earlyStyles=array_keys($GLOBALS['enqueued_styles']);
$earlyScripts=array_keys($GLOBALS['enqueued_scripts']);
$verifiedDesk=fv_ex2_apollo_verified_desk();
$verifiedAtlas=fv_ex2_apollo_verified_atlas();
$markup=fv_ex2_apollo_suite_shortcode();
$allStyles=array_keys($GLOBALS['enqueued_styles']);
$allScripts=array_keys($GLOBALS['enqueued_scripts']);
$result=array(
  'mode'=>$mode,'original_r38_pinned'=>$verifiedDesk!==null && realpath($verifiedDesk)===realpath($desk.'/final-vestige-ex2-research-desk.php'),
  'active_r84_pinned'=>$verifiedDesk!==null && realpath($verifiedDesk)===realpath($desk.'/final-vestige-ex2-research-desk.php'),
  'built_atlas_pinned'=>$verifiedAtlas!==null && realpath($verifiedAtlas)===realpath($atlas.'/final-vestige-ex2-evidence-atlas.php'),
  'prehead_styles'=>$earlyStyles,'prehead_scripts'=>$earlyScripts,
  'after_shortcode_styles'=>$allStyles,'after_shortcode_scripts'=>$allScripts,
  'suite_rendered'=>strpos($markup,'class="fv-ex2-apollo-suite"')!==false,
  'desk_records'=>substr_count($markup,'data-fvx-record '),
  'atlas_records'=>substr_count($markup,'data-fva-record '),
  'provisional_disclosed'=>strpos($markup,'unconfirmed S67-19766')!==false,
  'source_desk_unchanged'=>strpos($markup,'NASA S67-15717 · NASA')!==false,
  'no_embedded_media'=>strpos($markup,'<img')===false,
  'markup_sha256'=>hash('sha256',$markup),
  'duplicate_fallback'=>strpos(fv_ex2_apollo_suite_shortcode(),'already appears on this page')!==false,
);
if (($argv[2]??'')==='--html') { if (!$result['suite_rendered']) { exit(3); } echo $markup; exit(0); }
echo json_encode($result,JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT),"\n";
