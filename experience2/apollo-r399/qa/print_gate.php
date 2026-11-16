<?php
/** Source-controlled minimal WP-hook boundary regression. PHP stubs, not installed WP. */
define('ABSPATH','/tmp/fv-r399-qa');
$ledger=json_decode(file_get_contents(__DIR__.'/../../apollo-r377/custody.json'),true);
$GLOBALS['q']=['env'=>'staging','page'=>true,'rows'=>$ledger['records'],'registered'=>[],'styles'=>[],'filters'=>[],'host'=>'https://qa.example/',
  'plugin'=>'https://qa.example/wp-content/plugins/fv-site-layer/experience2/apollo-r399'];
function wp_get_environment_type(){return $GLOBALS['q']['env'];}
function is_page($slug){return $GLOBALS['q']['page'] && $slug==='apollo-1-evidence-atlas';}
function fv_r384_records(){return $GLOBALS['q']['rows'];}
function wp_style_is($h,$status){return in_array($h,$GLOBALS['q']['registered'],true);}
function wp_enqueue_style($h,$url,$deps,$version,$media){$GLOBALS['q']['styles'][]=[$h,$url,$deps,$version,$media];$GLOBALS['q']['registered'][]=$h;}
function plugins_url($path,$file){return $GLOBALS['q']['plugin'];}
function home_url($path){return $GLOBALS['q']['host'];}
function add_action($hook,$fn,$priority){}
function add_filter($hook,$fn,$priority,$arity){$GLOBALS['q']['filters'][]=[$hook,$fn,$priority,$arity];}
require __DIR__.'/../staging-final-tag-guard.php';
$n=0;
function check($ok,$label){global $n;$n++;if(!$ok)throw new RuntimeException("R399 test #$n failed: $label");}
check(fv_r399_reviewed_records($ledger['records']),'full NASA records');
$mut=$ledger['records'];$mut[5]['context_role']='unreviewed claim';
check(!fv_r399_reviewed_records($mut),'tampered context rejected');
$mut=$ledger['records'];$mut[0]['purchase_url']='https://merchant.invalid';
check(!fv_r399_reviewed_records($mut),'invented commerce field rejected');
if (!defined('FV_R399_APOLLO_QA_ENABLE')) check(fv_r399_reviewed_delivery()===false,'default disabled');
if (defined('FV_R399_APOLLO_QA_ENABLE') && FV_R399_APOLLO_QA_ENABLE===true){
 $urls=fv_r399_reviewed_delivery();check(is_array($urls)&&count($urls)===2,'opt-in accepts canonical URLs');
 $GLOBALS['q']['plugin'].='/../';check(fv_r399_reviewed_delivery()===false,'reject traversal');
 $GLOBALS['q']['plugin']=substr($GLOBALS['q']['plugin'],0,-4);
 fv_r399_enqueue_prepaint();check(count($GLOBALS['q']['styles'])===2,'two accepted prepaint styles');
 check(count($GLOBALS['q']['filters'])===2 && $GLOBALS['q']['filters'][0][2]===PHP_INT_MAX && $GLOBALS['q']['filters'][1][0]==='style_loader_tag' && $GLOBALS['q']['filters'][1][2]===PHP_INT_MAX && $GLOBALS['q']['filters'][1][3]===4,'last-mile filter added');
 foreach($urls as $handle=>$url){
   $v=$handle==='fv-apollo-r384-gallery'?'r384-reviewed-1':'r395-reviewed-1';
   $good=$url.'?ver='.$v;
   check(fv_r399_guard_style_src($good,$handle)===$good,'accept exact print URL');
   foreach([$good.'&extra=1',str_replace('qa.example','evil.invalid',$good),$url] as $bad){
     check(fv_r399_guard_style_src($bad,$handle)==='','block post-enqueue mutation');
   }
 }
 foreach($urls as $handle=>$url){
   $version=$handle==='fv-apollo-r384-gallery'?'r384-reviewed-1':'r395-reviewed-1';
   $media=$handle==='fv-apollo-r384-gallery'?'all':'screen';
   $href=$url.'?ver='.$version;
   $tag="<link rel='stylesheet' id='".$handle."-css' href='".$href."' media='".$media."' />\n";
   check(fv_r399_guard_style_tag($tag,$handle,$href,$media)===$tag,'accept only canonical WordPress HTML tag');
   check(fv_r399_guard_style_tag($tag,$handle,$href,'print')==='','reject altered media argument');
   check(fv_r399_guard_style_tag($tag,$handle,$href.'#x',$media)==='','reject altered href argument');
   check(fv_r399_guard_style_tag(false,$handle,$href,$media)==='','reject invalid tag type');
   $tampered=[
     str_replace(" id="," onload='unapproved()' id=",$tag),
     str_replace(" href="," data-track='1' href=",$tag),
     str_replace(" media='".$media."'"," media='print'",$tag),
     str_replace("stylesheet","preload",$tag),
     str_replace($href,"https://evil.invalid/evil.css",$tag),
     str_replace(" />", " disabled />", $tag),
     $tag."<script>unapproved()</script>",
     str_replace("-css'","-foreign-css'",$tag),
   ];
   foreach($tampered as $i=>$bad) {
     check($bad!==$tag,'mutation was meaningful '.$i);
     check(fv_r399_guard_style_tag($bad,$handle,$href,$media)==='','reject altered link HTML '.$i);
     check(fv_r399_guard_style_src($href,$handle)===$href,'URL-only guard cannot detect HTML mutation '.$i);
   }
 }
 check(fv_r399_guard_style_tag('<link>','unrelated','https://cdn.example/other.css','screen')==='<link>','do not rewrite unrelated styles');
 check(fv_r399_reviewed_delivery()===false,'pre-registered handles block repeat');
}
echo "R399 print gate PASS: $n PHP stub assertions; no WordPress installation\n";
