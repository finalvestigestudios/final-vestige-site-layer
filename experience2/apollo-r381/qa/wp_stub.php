<?php
/** R381 local WordPress API stub: proves component behavior, NOT installed WordPress. */
error_reporting(E_ALL);
ini_set('display_errors','stderr');
define('ABSPATH',__DIR__.'/');
define('FV_R377_STAGING_ENABLED',true);
define('FV_R377_APPROVED_HOST','staging.fv.invalid');
$GLOBALS['events']=[]; $GLOBALS['codes']=[]; $GLOBALS['styles']=[];
$GLOBALS['page_content']='[fv_apollo_evidence_to_investigation_r381]';
$GLOBALS['environment']='staging';$GLOBALS['hostname']='staging.fv.invalid';
function add_action($name,$callback,$priority=10){$GLOBALS['events'][$name][]=$callback;}
function add_shortcode($name,$fn){$GLOBALS['codes'][$name]=$fn;}
function shortcode_exists($name){return isset($GLOBALS['codes'][$name]);}
function do_action($name){foreach($GLOBALS['events'][$name]??[] as $fn){$fn();}}
function wp_get_environment_type(){return $GLOBALS['environment'];}
function home_url($path='/'){return 'https://'.$GLOBALS['hostname'].$path;}
function is_singular(){return true;}
function get_queried_object_id(){return 101;}
function get_post($id=null){return (object)['ID'=>101,'post_content'=>$GLOBALS['page_content']];}
function has_shortcode($content,$tag){return strpos($content,'['.$tag)!==false;}
function wp_enqueue_style($handle,$url,$deps=[],$version=null){$GLOBALS['styles'][$handle]=[$url,$version];}
function plugins_url($asset,$file){return 'https://staging.fv.invalid/wp-content/plugins/fv-r381/'.$asset;}
require_once __DIR__.'/../../apollo-r377/source-role-desk.php';
require_once __DIR__.'/../evidence-to-investigation.php';
function check($truth,$label,&$checks){$checks[$label]=(bool)$truth;}

$checks=[];$records=fv_r377_records();
check($records!==null,'sealed_R377_records_available',$checks);
$html=fv_r381_render($records);
check(strpos($html,'data-fv-r381')!==false,'valid_evidence_component',$checks);
check(substr_count($html,'data-fv-r381-item')===3,'exact_three_source_records',$checks);
check(substr_count($html,'data-fv-r381-drawer')===3,'three_native_source_drawers',$checks);
check(substr_count($html,'data-fv-r381-next')===1,'exact_one_editorial_next_step',$checks);
check(substr_count($html,'data-fv-r381-nasa')===3,'three_cited_NASA_sources',$checks);
check(strpos($html,'later deliberate engineering tests')!==false,'post_fire_tests_marked',$checks);
check(strpos($html,'did not conclusively identify')!==false,'no_certainty_inflation',$checks);
check(strpos($html,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')!==false,'free_destination_exact',$checks);
check(!preg_match('~<script|<img|<iframe|<form|payhip|checkout|utm_(?:source|medium|campaign|content)~i',$html),'no_tracking_or_unverified_commerce',$checks);
check(strpos($html,'not a license to reproduce images')!==false,'NASA_media_rights_caveat',$checks);
check(strpos($html,'Primary investigation')!==false && strpos($html,'2018 retrospective')!==false,'source_custody_present',$checks);
$mutated=$records;$mutated[4]['claim']='A speculative exact ignition source was conclusively proven.';
check(!fv_r381_verified($mutated),'rejected_altered_sealed_record',$checks);
check(strpos(fv_r381_render($mutated),'Research records unavailable')!==false,'altered_record_fail_open',$checks);
check(strpos(fv_r381_render(null),'Read the free Apollo 1 investigation')!==false,'missing_record_safe_fallback',$checks);
check(!fv_r381_verified(array_slice($records,0,3)),'rejected_truncated_records',$checks);
// Register only on approved staging and do not overwrite an existing owner.
do_action('plugins_loaded');
check(isset($GLOBALS['codes'][FV_R381_TAG]),'stage_shortcode_registered',$checks);
check(fv_r381_shortcode()===$html || strpos(fv_r381_shortcode(),'data-fv-r381')!==false,'stage_shortcode_render',$checks);
do_action('wp_enqueue_scripts');
check(count($GLOBALS['styles'])===1 && isset($GLOBALS['styles']['fv-apollo-r381']),'single_relevant_stylesheet',$checks);
$GLOBALS['styles']=[];$GLOBALS['page_content']='[unrelated_shortcode]';
do_action('wp_enqueue_scripts');
check(count($GLOBALS['styles'])===0,'no_sitewide_stylesheet',$checks);
$GLOBALS['page_content']='[fv_apollo_evidence_to_investigation_r381]';
$GLOBALS['environment']='production';$GLOBALS['styles']=[];
do_action('wp_enqueue_scripts');
check(count($GLOBALS['styles'])===0 && strpos(fv_r381_shortcode(),'Research records unavailable')!==false,'production_fail_closed',$checks);
$GLOBALS['environment']='staging';$GLOBALS['hostname']='wrong.fv.invalid';
check(!fv_r377_environment(),'wrong_host_rejected',$checks);
$GLOBALS['hostname']='staging.fv.invalid';
// Foreign shortcode collision: this component never overwrites it.
$GLOBALS['codes'][FV_R381_TAG]='foreign_owner';
do_action('plugins_loaded');
check($GLOBALS['codes'][FV_R381_TAG]==='foreign_owner','foreign_shortcode_owner_preserved',$checks);
if (in_array('--html',$argv,true)) { echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R381 LOCAL PHP STUB — NOT WORDPRESS STAGING</title></head><body>'.$html.'</body></html>'; exit; }
$result=['fixture'=>'PHP_WP_API_STUB_NOT_INSTALLED_WORDPRESS','total'=>count($checks),'passed'=>array_sum($checks),'checks'=>$checks];
echo json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
if ($result['passed']!==$result['total']) { exit(1); }
