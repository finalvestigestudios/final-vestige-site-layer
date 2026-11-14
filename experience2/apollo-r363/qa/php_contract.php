<?php
/** Real ancestor R345/R355/R360 implementations under API stubs, not installed WordPress. */
define('ABSPATH', __DIR__);
$GLOBALS['registered'] = array(); $GLOBALS['enqueued']=array(); $GLOBALS['post_content']='[fv_apollo_custody_guard_r363]';
function add_shortcode($tag,$fn){$GLOBALS['registered']['shortcode'][$tag]=$fn;}
function add_action($tag,$fn,$priority){$GLOBALS['registered']['action'][]=array($tag,$fn,$priority);}
function is_singular(){return true;}
function get_post(){return (object) array('post_content'=>$GLOBALS['post_content']);}
function has_shortcode($content,$tag){return str_contains($content, '['.$tag.']');}
function plugins_url($asset,$source){return 'https://staging.invalid/'.$asset;}
function wp_enqueue_style($handle,$url,$deps,$version){$GLOBALS['enqueued'][$handle]=$url;}
require dirname(__DIR__).'/custody-guard.php';
$passed=0;
function ok($expr,$label){global $passed; if(!$expr){fwrite(STDERR,"FAIL: $label\n");exit(1);} ++$passed;}
$rows=fv_apollo_r363_reviewed_rows();
ok(count($rows)===4,'four canonically reviewed rows');
ok(count(array_filter($rows,fn($x)=>$x['class']==='board'))===3,'original 1967 board distinct');
ok($rows[3]['class']==='later-test' && str_contains($rows[3]['period'],'2018'),'later 2018 NASA account separate');
ok(str_contains($rows[3]['finding'],'102 deliberate ignitions'),'count from already reviewed R355 record');
foreach($rows as $i=>$r){
 ok(fv_apollo_r363_exact_review($r),"row $i exact review");
 ok(fv_apollo_r363_source_allowed($r),"row $i NASA link allowed");
 foreach(array_keys($r) as $field){
  $mut=$r;$mut[$field]=$field==='source'?'https://www.nasa.gov/attacker-claim':$mut[$field].' [unreviewed]';
  ok(!fv_apollo_r363_exact_review($mut),"row $i edited $field refused");
  ok(!fv_apollo_r363_source_allowed($mut),"row $i edited $field cannot borrow source");
  $render=fv_apollo_r363_render_rows(array($mut));
  ok(str_contains($render,'data-fv-r363-withheld') && !str_contains($render,'data-fv-r363-source'),"row $i changed $field withheld from render");
 }
 $extra=$r;$extra['unreviewed']='new';
 ok(!fv_apollo_r363_exact_review($extra),"row $i extra unreviewed field rejected");
}
$good=fv_apollo_r363_shortcode();$again=fv_apollo_r363_shortcode();
ok(substr_count($good,'data-fv-r363-source')===4,'four source links');
ok(substr_count($good,'data-fv-r363-details')===4,'four semantic details');
ok(substr_count($good,'data-fv-r363-editorial-cta')===1,'exactly one free editorial CTA');
ok(!str_contains($good,'data-fv-r363-withheld'),'valid rows all visible');
ok(!preg_match('/<(img|script|iframe|form|video)\b/i',$good),'no active embeds');
ok(!str_contains($good,'data-fv-commercial-cta'),'no purchase CTA');
ok(str_contains($good,'NOT CLEARED') && str_contains($good,'1967') && str_contains($good,'2018'),'rights and eras printed');
ok(str_contains($good,'fv-apollo-r363-'.(4*count($rows)*(7)+1).'-title')===false,'ID generated, no false hardcoded ID');
// Test ID uniqueness without expecting an exact prior counter value.
preg_match('/id="(fv-apollo-r363-\d+-title)"/',$good,$m1);
preg_match('/id="(fv-apollo-r363-\d+-title)"/',$again,$m2);
ok(isset($m1[1],$m2[1]) && $m1[1]!==$m2[1],'multiple instances unique heading IDs');
$bad=fv_apollo_r363_render_rows(array(array('question'=>'Injected record', 'source'=>'https://www.nasa.gov/')));
ok(str_contains($bad,'data-fv-r363-withheld') && !str_contains($bad,'Injected record'),'modified claims not printed');
$GLOBALS['post_content']='[fv_apollo_custody_guard_r363]';fv_apollo_r363_enqueue();
ok(isset($GLOBALS['enqueued']['fv-apollo-r362-crosswalk']),'reuses existing CSS handle');
$GLOBALS['post_content']='[fv_apollo_unrelated]';$GLOBALS['enqueued']=array();fv_apollo_r363_enqueue();
ok(count($GLOBALS['enqueued'])===0,'no unrequested CSS');
echo json_encode(array('pass'=>$passed,'canonical'=>count($rows),'tamper_fields_per_record'=>7,'source_links'=>4,'purchase_cta'=>0,'wp_installed'=>false),JSON_PRETTY_PRINT)."\n";
