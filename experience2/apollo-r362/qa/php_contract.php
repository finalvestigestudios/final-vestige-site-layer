<?php
/** Staging-only PHP contract: actual R362 source with installed WP API stubs, not a real WP install. */
define('ABSPATH', __DIR__);
$GLOBALS['calls'] = array();
function add_shortcode($tag,$fn){$GLOBALS['calls']['shortcode'][$tag]=$fn;}
function add_action($tag,$fn,$priority){$GLOBALS['calls']['action'][$tag][]=$fn;}
function is_singular(){return true;}
function get_post(){return (object) array('post_content'=>'[fv_apollo_research_crosswalk_r362]');}
function has_shortcode($text,$tag){return strpos($text,'['.$tag) !== false;}
function wp_enqueue_style($name,$path,$deps,$version){$GLOBALS['calls']['enqueued'][]=$name;}
function plugins_url($path,$file){return '/staging/'.basename($file).'/'.$path;}
require dirname(__DIR__) . '/research-crosswalk.php';
$pass=0;
function check($condition,$label){global $pass; if(!$condition){fwrite(STDERR,"FAIL: $label\n");exit(1);} $pass++;}
$rows=fv_apollo_r362_rows();
check(count($rows)===4,'four reviewed rows');
check(count(array_filter($rows,fn($r)=>$r['source_key']==='board'))===3,'three original Board rows');
check($rows[3]['source_key']==='postfire' && strpos($rows[3]['period'],'2018')!==false,'2018 separated from original Board');
check(strpos($rows[3]['finding'],'102 deliberate ignitions')!==false,'post-fire count from pinned upstream record');
foreach($rows as $i=>$r){check(fv_apollo_r362_link_allowed($r),"$i verified link");}
foreach($rows as $i=>$r){
 $bad=$r;$bad['url']='https://nasa.gov.evil.example/path';check(!fv_apollo_r362_link_allowed($bad),"$i external host rejected");
 $bad=$r;$bad['source_key']=$r['source_key']==='postfire'?'board':'postfire';check(!fv_apollo_r362_link_allowed($bad),"$i class mismatch rejected");
 $bad=$r;$bad['url']='http://www.nasa.gov/';check(!fv_apollo_r362_link_allowed($bad),"$i downgrade rejected");
}
check(isset($GLOBALS['calls']['shortcode']['fv_apollo_research_crosswalk_r362']),'shortcode registered');
$first=fv_apollo_r362_shortcode();$second=fv_apollo_r362_shortcode();
check(substr_count($first,'data-fv-r362-reviewed-source')===4,'four screen NASA links');
check(substr_count($first,'data-fv-r362-editorial-cta')===1,'exactly one editorial continuation');
check(strpos($first,'data-fv-source-review-required')===false,'source identity passes');
check(strpos($first,'<img')===false && strpos($first,'<script')===false && strpos($first,'<form')===false,'no media script or form');
check(strpos($first,'<iframe')===false && strpos($first,'checkout')===false,'no embedded/external checkout');
check(preg_match('/id="fv-apollo-r362-1-title"/',$first)===1,'first unique root id');
check(preg_match('/id="fv-apollo-r362-2-title"/',$second)===1,'second unique root id');
check(strpos($first,'2018 retrospective of tests after the fire')!==false,'2018 source date present');
check(strpos($first,'No single ignition source was conclusively identified')!==false,'Board uncertainty retained');
check(strpos($first,'NOT cleared')!==false,'rights status present');
check(substr_count($first,'data-fv-r362-period="board"')===3 && substr_count($first,'data-fv-r362-period="postfire"')===1,'document classes visible');
check(substr_count($first,'fv-apollo-r362__print-source')===4,'print-only custody present');
fv_apollo_r362_enqueue();check(($GLOBALS['calls']['enqueued']??[])===['fv-apollo-r362-crosswalk'],'one deterministic CSS asset');
$css=file_get_contents(dirname(__DIR__).'/assets/research-crosswalk.css');
check(strpos($css,'@media print')!==false && strpos($css,'@media(forced-colors:active)')!==false,'print and forced-colors CSS present');
check(strpos($css,'@media(prefers-reduced-motion:reduce)')!==false,'motion CSS present');
check(strpos($css,'__print-source[hidden]{display:block!important}')!==false,'print provenance restored');
echo json_encode(['php_stub_pass'=>$pass,'document_rows'=>count($rows),'screen_nasa_links'=>4,'editorial_cta'=>1,'media_rights'=>'NOT_CLEARED_LINK_ONLY','real_wp'=>false],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
