<?php
/** R365 executes the exact component under minimal WordPress API stubs. */
define('ABSPATH', __DIR__);
$GLOBALS['shortcodes']=array(); $GLOBALS['actions']=array();$GLOBALS['styles']=array();
function add_shortcode($tag,$fn){$GLOBALS['shortcodes'][$tag]=$fn;}
function add_action($tag,$fn,$priority){$GLOBALS['actions'][]=array($tag,$fn,$priority);}
function plugins_url($uri,$file){return 'https://staging.invalid/'.$uri;}
function wp_enqueue_style($name,$url,$deps,$ver){$GLOBALS['styles'][$name]=$url;}
require dirname(__DIR__).'/chrono-rail.php';
$count=0;function check($ok,$why){global $count;if(!$ok){fwrite(STDERR,'FAIL '.$why."\n");exit(1);}++$count;}
$rows=fv_apollo_r365_rows();
check(count($rows)===4,'four sourced stages');
check(count(array_filter($rows,fn($r)=>$r['class']==='primary-investigation'))===2,'two 1967 stages');
check(count(array_filter($rows,fn($r)=>$r['class']!=='primary-investigation'))===2,'two later stages');
check(count(array_unique(array_column($rows,'id')))===4,'no duplicate IDs');
check(count(array_unique(array_column($rows,'source')))===3,'three distinct NASA source URLs');
foreach($rows as $i=>$row){
 check(fv_apollo_r365_reviewed($row),'row '.$i.' reviewed');
 check(str_starts_with($row['source'],'https://www.nasa.gov/'),'official NASA host');
 foreach(array_keys($row) as $field){
  $bad=$row;$bad[$field].=' UNREVIEWED';
  check(!fv_apollo_r365_reviewed($bad),'strict source/claim field '.$i.':'.$field);
  $markup=fv_apollo_r365_render_rows(array($bad));
  check(str_contains($markup,'data-fv-withheld'),'tampered row withheld '.$i.':'.$field);
  check(!str_contains($markup,'data-fv-nasa-source'),'tampered source link withheld '.$i.':'.$field);
 }
 $extra=$row;$extra['unreviewed']='unexpected';
 check(!fv_apollo_r365_reviewed($extra),'extra key cannot borrow reviewed status');
}
$html=fv_apollo_r365_shortcode();$second=fv_apollo_r365_shortcode();
check(substr_count($html,'data-fv-source-drawer')===4,'four native details drawers');
check(substr_count($html,'data-fv-nasa-source')===4,'four NASA source links');
check(substr_count($html,'data-fv-free-cta')===1,'one free editorial CTA');
check(substr_count($html,'id="fv-apollo-r365-')===9,'unique IDs for root four stages and their headings');
check(!preg_match('/<(script|img|iframe|video|form|button|canvas)\b/i',$html),'no script embeds, forms or external pictures');
check(!preg_match('/(data-fv-paid|href="[^"]*(checkout|buy_now|utm_|asset_id))/i',$html),'no commerce claims or tracking parameters');
check(str_contains($html,'not conclusively') && str_contains($html,'2018'),'uncertainty and retrospective timeline');
check(str_contains($html,'No NASA photographs') && str_contains($html,'NASA does not endorse'),'media reuse limitation');
check(str_contains($html,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),'verified existing free investigation');
check(!str_contains($second,'id="fv-apollo-r365-1-title"'),'multiple render IDs unique');
check(isset($GLOBALS['shortcodes']['fv_apollo_chronology_r365']),'WP shortcode registered');
check(count($GLOBALS['actions'])===1,'one style action registered');
fv_apollo_r365_enqueue();
check(isset($GLOBALS['styles']['fv-apollo-r365-chronology']),'staging stylesheet enqueued');
$css=file_get_contents(dirname(__DIR__).'/assets/chrono-rail.css');
check(str_contains($css,'@media print') && str_contains($css,'prefers-reduced-motion') && str_contains($css,'forced-colors'),'print and accessibility media');
check(!preg_match('/@import|url\(/i',$css),'no external CSS fetches');
$result=array('passed'=>$count,'rows'=>4,'primary'=>2,'later'=>2,'unique_nasa_sources'=>3,'tampers_rejected'=>count($rows)*count($rows[0]),'wp_installed'=>false,'paid_cta'=>false);
$dir=dirname(__DIR__).'/QA';if(!is_dir($dir)){mkdir($dir,0775,true);}
file_put_contents($dir.'/php-results.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");
file_put_contents($dir.'/fixture.html','<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo evidence custody R365 · STAGING</title><style>'.$css.'</style></head><body style="margin:0">'.$html.'</body></html>');
echo json_encode($result,JSON_PRETTY_PRINT)."\n";
