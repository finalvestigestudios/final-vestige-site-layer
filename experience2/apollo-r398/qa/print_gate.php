<?php
/** Source-controlled minimal WP-hook boundary regression. PHP stubs, not installed WP. */
define('ABSPATH','/tmp/fv-r398-qa');
$ledger=json_decode(file_get_contents(__DIR__.'/../../apollo-r377/custody.json'),true);
$GLOBALS['q']=['env'=>'staging','page'=>true,'rows'=>$ledger['records'],'registered'=>[],'styles'=>[],'filters'=>[],'host'=>'https://qa.example/',
  'plugin'=>'https://qa.example/wp-content/plugins/fv-site-layer/experience2/apollo-r398'];
function wp_get_environment_type(){return $GLOBALS['q']['env'];}
function is_page($slug){return $GLOBALS['q']['page'] && $slug==='apollo-1-evidence-atlas';}
function fv_r384_records(){return $GLOBALS['q']['rows'];}
function wp_style_is($h,$status){return in_array($h,$GLOBALS['q']['registered'],true);}
function wp_enqueue_style($h,$url,$deps,$version,$media){$GLOBALS['q']['styles'][]=[$h,$url,$deps,$version,$media];$GLOBALS['q']['registered'][]=$h;}
function plugins_url($path,$file){return $GLOBALS['q']['plugin'];}
function home_url($path){return $GLOBALS['q']['host'];}
function add_action($hook,$fn,$priority){}
function add_filter($hook,$fn,$priority,$arity){$GLOBALS['q']['filters'][]=[$hook,$fn,$priority,$arity];}
require __DIR__.'/../staging-canonical-delivery.php';
$n=0;
function check($ok,$label){global $n;$n++;if(!$ok)throw new RuntimeException("R398 test #$n failed: $label");}
check(fv_r398_reviewed_records($ledger['records']),'full NASA records');
$mut=$ledger['records'];$mut[5]['context_role']='unreviewed claim';
check(!fv_r398_reviewed_records($mut),'tampered context rejected');
$mut=$ledger['records'];$mut[0]['purchase_url']='https://merchant.invalid';
check(!fv_r398_reviewed_records($mut),'invented commerce field rejected');
if (!defined('FV_R398_APOLLO_QA_ENABLE')) check(fv_r398_reviewed_delivery()===false,'default disabled');
if (defined('FV_R398_APOLLO_QA_ENABLE') && FV_R398_APOLLO_QA_ENABLE===true){
 $urls=fv_r398_reviewed_delivery();check(is_array($urls)&&count($urls)===2,'opt-in accepts canonical URLs');
 $GLOBALS['q']['plugin'].='/../';check(fv_r398_reviewed_delivery()===false,'reject traversal');
 $GLOBALS['q']['plugin']=substr($GLOBALS['q']['plugin'],0,-4);
 fv_r398_enqueue_prepaint();check(count($GLOBALS['q']['styles'])===2,'two accepted prepaint styles');
 check(count($GLOBALS['q']['filters'])===1 && $GLOBALS['q']['filters'][0][2]===PHP_INT_MAX,'last-mile filter added');
 foreach($urls as $handle=>$url){
   $v=$handle==='fv-apollo-r384-gallery'?'r384-reviewed-1':'r395-reviewed-1';
   $good=$url.'?ver='.$v;
   check(fv_r398_guard_style_src($good,$handle)===$good,'accept exact print URL');
   foreach([$good.'&extra=1',str_replace('qa.example','evil.invalid',$good),$url] as $bad){
     check(fv_r398_guard_style_src($bad,$handle)==='','block post-enqueue mutation');
   }
 }
 check(fv_r398_reviewed_delivery()===false,'pre-registered handles block repeat');
}
echo "R398 print gate PASS: $n PHP stub assertions; no WordPress installation\n";
