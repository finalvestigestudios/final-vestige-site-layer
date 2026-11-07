<?php
/* R178 real PHP CLI unit contract against stubbed WordPress APIs.
 * NOT an installed WordPress theme/block/CSP test. Usage:
 * for s in preflight nested early absent double missing; do php qa/php_contract.php "$s"; done
 */
error_reporting(E_ALL);
define('ABSPATH','/local-test/');
$mode=$argv[1]??'';
$cases=array('preflight','nested','early','absent','double','missing');
if (!in_array($mode,$cases,true)) { fwrite(STDERR,"Unknown test case\n"); exit(2); }
$GLOBALS['registered']=array();$GLOBALS['styles']=array();$GLOBALS['scripts']=array();
$GLOBALS['head']=false;$GLOBALS['style_done']=false;$GLOBALS['missing']=$mode==='missing';
$GLOBALS['content']=in_array($mode,array('preflight','double','missing'),true)?'[fv_ex2_research_desk]':'<!-- wp:block {"ref":5} /-->';
function add_action($hook,$fn,$priority=10){}
function add_shortcode($tag,$fn){}
function wp_register_style($h,$src,$deps,$ver){$GLOBALS['registered']['css']=true;}
function wp_register_script($h,$src,$deps,$ver,$footer){$GLOBALS['registered']['js']=true;}
function wp_enqueue_style($h){$GLOBALS['styles'][$h]=true;}
function wp_enqueue_script($h){$GLOBALS['scripts'][$h]=true;}
function plugins_url($path,$file){return 'https://example.invalid/'.basename($path);}
function plugin_dir_path($file){return $GLOBALS['missing']?'/does-not-exist/':__DIR__.'/fixtures/';}
function esc_url($s){return htmlspecialchars($s,ENT_QUOTES);}
function is_singular(){return true;}
function get_post(){return (object)array('post_content'=>$GLOBALS['content']);}
function has_shortcode($s,$tag){return strpos($s,'['.$tag)!==false;}
function did_action($name){return $name==='wp_head'&&$GLOBALS['head']?1:0;}
function wp_style_is($h,$state){return $state==='done'&&$GLOBALS['style_done'];}
require dirname(__DIR__).'/research-desk-adapter.php';
fv_ex2_rd_register_assets();
if ($mode!=='early'&&$mode!=='missing')fv_ex2_rd_preflight_assets();
if ($mode!=='early')$GLOBALS['head']=true;
if ($mode==='preflight')$GLOBALS['style_done']=true;
$output=$mode==='absent'?'':fv_ex2_rd_shortcode();
if ($mode==='double')$output.=fv_ex2_rd_shortcode();
$assert=function($ok,$msg)use($mode){if(!$ok){fwrite(STDERR,"FAIL [$mode] $msg\n");exit(1);}};
$assert(count($GLOBALS['registered'])===2,'asset handles not registered');
if ($mode==='absent'){
  $assert(!$output&&count($GLOBALS['styles'])===0&&count($GLOBALS['scripts'])===0,'unneeded assets enqueued');
}elseif($mode==='missing'){
  $assert(strpos($output,'Read the original Apollo 1 investigation')!==false&&count($GLOBALS['scripts'])===0,'failed-open fallback missing');
}else{
  $assert(count($GLOBALS['styles'])===1&&count($GLOBALS['scripts'])===1,'on-demand asset enqueues');
  $assert(substr_count($output,'data-fvx-record')===6,'six synthetic records must remain');
  $late=substr_count($output,'data-fvx-r178-late-style');
  $assert($late===($mode==='nested'||$mode==='double'?1:0),'wrong late stylesheet fallback');
  if($mode==='double')$assert(substr_count($output,'data-fvx-ledger')===1&&strpos($output,'Return to the evidence records')!==false,'duplicate ID guard');
}
echo "PASS $mode: PHP CLI contract (not WordPress)\n";
