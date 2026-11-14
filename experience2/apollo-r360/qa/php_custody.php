<?php
/** R360 review-only provenance and commerce isolation regression; no WP installation. */
define('ABSPATH',true);
require dirname(__DIR__,2).'/apollo-r359/resolved-block-template-prehead.php';
$checks=array();
function ok($predicate,$name){global $checks;if(!$predicate){throw new RuntimeException('FAIL: '.$name);} $checks[]=$name;}
$full=fv_apollo_r357_full();
$note=fv_apollo_r357_note();
$records=fv_apollo_r347_records();
$pages=fv_apollo_r348_custody();
$source='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
ok(count($records)===13,'curated evidence index has 13 records');
ok(count($pages)===8,'NASA URL custody has eight distinct sources');
ok(array_sum(array_map(fn($p)=>count($p['items']),$pages))===13,'custody covers each evidence record');
ok(count(array_filter($pages,fn($p)=>$p['approved']))===8,'source policy approves exact eight NASA addresses');
ok(function_exists('fv_apollo_r350_integrity_ok')&&fv_apollo_r350_integrity_ok(),'reviewed editorial snapshot digests are valid');
ok(substr_count($full,'data-fv-r339-cta="editorial"')===1,'single free continuation CTA');
ok(substr_count($full,'data-fv-apollo-entry=')===13,'render retains 13 indexed entries');
ok(substr_count($full,'data-fv-custody-source')===8,'eight custody links rendered');
ok(substr_count($full,'data-fv-r355-reviewed-source')===1,'later NASA source has dedicated verified link');
ok(strpos($note,$source)!==false,'post-fire NASA official page is linked');
ok(strpos($note,'102 deliberate ignitions')!==false,'102 postfire test ignitions separately contextualized');
ok(strpos($note,'2018')!==false,'postfire historical classification is dated');
ok(strpos($full,'Evidence boundary:')!==false,'full evidence boundaries visible');
ok(strpos($full,'rights')!==false||strpos($full,'Rights')!==false,'source rights limitations visible');
ok(preg_match('/<img\b|<iframe\b|<video\b/i',$full)===0,'no embedded NASA images/video/iframes');
ok(preg_match('/checkout|buy now|add to cart|utm_|pixel|analytics|subscribe/i',$note)===0,'no commercial, tracking, or subscription mutation in standalone note');
ok(strpos($full,'data-fv-apollo-source-index')!==false,'semantic Evidence Atlas section present');
ok(strpos($full,'data-fv-apollo-custody')!==false,'semantic Source Drawer section present');
ok(strpos($full,'data-fv-apollo-postfire')!==false,'post-fire source distinction visible');
$css=file_get_contents(dirname(__DIR__,2).'/apollo-r355/postfire-ledger.css');
ok(strpos($css,'a[data-fv-r355-reviewed-source]')!==false,'specific 44px link target correction present');
ok(strpos($css,'min-height:44px')!==false,'CSS minimum 44px target defined');
$uri='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
ok(substr_count($full,$uri)>=1,'single original editorial destination retained');
echo json_encode(array('status'=>'LOCAL_PHP_PASS','type'=>'PHP CLI with reviewed modules, not installed WordPress','count'=>count($checks),'checks'=>$checks),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES),"\n";
