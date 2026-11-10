<?php
/** R272 authentic source/plugin shim; no WP installation. Exits nonzero on failure. */
define('ABSPATH', '/test-only/');
$actions=[];$shortcodes=[];$filters=[];$posts=[];$current=null;$singular=true;$admin=false;$enqueued=[];$styles=[];$scripts=[];$count_reads=0;$calls=[];
function add_action($name,$callback,$priority=10){$GLOBALS['actions'][]=[$name,$callback,$priority];}
function add_shortcode($name,$cb){$GLOBALS['shortcodes'][$name]=$cb;}
function add_filter($name,$callback,$priority=10,$accepted=1){$GLOBALS['filters'][]=[$name,$callback];}
function plugin_dir_path($path){return dirname($path).'/';}
function plugins_url($path,$source){return 'staging-plugin://'.basename(dirname($source)).'/'.$path;}
function esc_url($s){return $s;}
function get_post($id=null){$GLOBALS['count_reads']++;if($id===null)return $GLOBALS['current'];return $GLOBALS['posts'][$id]??null;}
function is_singular(){return $GLOBALS['singular'];}
function is_admin(){return $GLOBALS['admin'];}
function has_shortcode($s,$name){return strpos($s,'['.$name.']')!==false;}
function parse_blocks($content){
  preg_match_all('/<!--\s*wp:(?:block|group)(?:\s+(\{.*?\}))?\s*-->/', $content, $hits,PREG_SET_ORDER);
  $blocks=[];foreach($hits as $hit){$json=json_decode($hit[1]??'{}',true)??[];$blocks[]=['blockName'=>isset($json['ref'])?'core/block':'core/group','attrs'=>$json,'innerBlocks'=>[]];}
  return $blocks;
}
function wp_enqueue_style($handle,$src,$deps,$version){$GLOBALS['styles'][$handle]=[$src,$version];$GLOBALS['calls'][]='css';}
function wp_enqueue_script($handle,$src,$deps,$version,$footer){$GLOBALS['scripts'][$handle]=[$src,$version,$footer];$GLOBALS['calls'][]='js';}
function wp_style_is($handle,$type){return isset($GLOBALS['styles'][$handle]);}
function wp_script_is($handle,$type){return isset($GLOBALS['scripts'][$handle]);}
function insist($ok,$reason){if(!$ok){fwrite(STDERR,"R272 FAIL: $reason\n");exit(2);}}
function fixture($content,$type='wp_block',$status='publish'){return (object)['post_content'=>$content,'post_type'=>$type,'post_status'=>$status];}
function context($text,$refs=[],$is_singular=true,$is_admin=false){$GLOBALS['current']=fixture($text,'post');$GLOBALS['posts']=$refs;$GLOBALS['singular']=$is_singular;$GLOBALS['admin']=$is_admin;$GLOBALS['styles']=[];$GLOBALS['scripts']=[];$GLOBALS['count_reads']=0;$GLOBALS['calls']=[];}
function scenario($label,$post,$refs,$expected,$singular=true,$admin=false){
  context($post,$refs,$singular,$admin);
  fv_ex2_rd_assets(); // real original priority 20
  fv_ex2_r272_reusable_preflight(); // additive priority 21
  $found=isset($GLOBALS['styles']['fv-ex2-research-desk']) && isset($GLOBALS['scripts']['fv-ex2-research-desk']);
  insist($found===$expected,"$label eligibility expected ".(int)$expected);
  insist(count($GLOBALS['styles'])+count($GLOBALS['scripts'])===($expected?2:0),"$label asset count");
  insist(count($GLOBALS['calls'])===($expected?2:0),"$label double enqueue");
  if($expected){
    insist(strpos($GLOBALS['styles']['fv-ex2-research-desk'][0],'source-ledger.css')!==false,"$label css path");
    insist($GLOBALS['scripts']['fv-ex2-research-desk'][1]===FV_EX2_RD_VERSION,"$label version");
    insist($GLOBALS['scripts']['fv-ex2-research-desk'][2]===true,"$label footer");
  }
  return 1;
}
require __DIR__.'/../../apollo-r271/fixtures/research-desk/final-vestige-ex2-research-desk.php';
require __DIR__.'/../rd-reusable-preflight.php';
require __DIR__.'/../../apollo-r271/fixtures/rd-instance-scope.php';
insist(count($GLOBALS['actions'])===2 && $GLOBALS['actions'][0][2]===20 && $GLOBALS['actions'][1][2]===21, 'hook ordering');
$tag='[fv_ex2_research_desk]'; $ref=function($id){return '<!-- wp:block {"ref":'.$id.'} -->';};
$n=0;
$n+=scenario('direct-shortcode',$tag,[],true);
$n+=scenario('single-reusable',$ref(10),[10=>fixture($tag)],true);
$n+=scenario('two-layer-reusable',$ref(10),[10=>fixture($ref(20)),20=>fixture($tag)],true);
$n+=scenario('unrelated-neighbor',$ref(10).$ref(11),[10=>fixture('unrelated'),11=>fixture($tag)],true);
$n+=scenario('repeated-ref',$ref(10).$ref(10),[10=>fixture($tag)],true);
$n+=scenario('cycle',$ref(10),[10=>fixture($ref(20)),20=>fixture($ref(10))],false);
$n+=scenario('missing-ref',$ref(404),[],false);
$n+=scenario('draft-ref',$ref(10),[10=>fixture($tag,'wp_block','draft')],false);
$n+=scenario('wrong-type',$ref(10),[10=>fixture($tag,'post')],false);
$n+=scenario('empty-main','',[],false);
$n+=scenario('nonsingular',$ref(10),[10=>fixture($tag)],false,false,false);
$n+=scenario('admin',$ref(10),[10=>fixture($tag)],false,true,true);
$n+=scenario('invalid-ref','<!-- wp:block {"ref":"ab"} -->',[10=>fixture($tag)],false);
$n+=scenario('deep-chain',$ref(1),[1=>fixture($ref(2)),2=>fixture($ref(3)),3=>fixture($ref(4)),4=>fixture($tag)],true);
$refs=[];for($i=1;$i<=38;$i++)$refs[$i]=fixture($ref($i+1));$refs[39]=fixture($tag);
$n+=scenario('depth-bound',$ref(1),$refs,false);
$n+=scenario('non-reusable-shortcode-comment','<!-- wp:paragraph -->Evidence text<!-- /wp:paragraph -->',[],false);
// Demonstrate the inherited bug: original PR158 misses a shortcode held in a core/block reference.
context($ref(10),[10=>fixture($tag)]);fv_ex2_rd_assets();
insist(count($GLOBALS['styles'])===0 && count($GLOBALS['scripts'])===0,'inherited gap not reproduced');
fv_ex2_r272_reusable_preflight();
insist(count($GLOBALS['styles'])===1 && count($GLOBALS['scripts'])===1,'reusable preflight did not fix gap');$n++;
// Repeated preflight must never enqueue duplicate handles.
context($ref(10),[10=>fixture($tag)]);fv_ex2_r272_reusable_preflight();$first=[$GLOBALS['styles'],$GLOBALS['scripts']];fv_ex2_r272_reusable_preflight();
insist($first===[$GLOBALS['styles'],$GLOBALS['scripts']],'duplicate enqueue');$n++;
// Authentic PR158 shortcode content remains identical to its frozen template.
$actual=fv_ex2_rd_shortcode();
insist($actual===file_get_contents(__DIR__.'/../../apollo-r271/fixtures/research-desk/templates/ledger.html'),'source altered');$n++;
insist(substr_count($actual,'https://www.nasa.gov/')===13,'NASA links altered');$n++;
echo "R272 $n/$n PHP staging API-simulation checks PASS\n";
