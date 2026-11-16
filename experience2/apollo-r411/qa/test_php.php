<?php
error_reporting(E_ALL);
ini_set('display_errors','1');
ob_start();require __DIR__.'/render_fixture.php';$html=ob_get_clean();
$passed=0;
function check($truth,$message) {global $passed; if(!$truth){fwrite(STDERR,"FAIL $message\n");exit(1);} $passed++;}
check(fv_r411_authorized(),'authorized staging');
check(fv_r411_css_ok(),'exact pinned CSS');
check(count(fv_r411_catalog())===6,'catalog six');
check(substr_count($html,'<details class="fv-r411__disclosure">')===6,'six native disclosures');
check(substr_count($html,'<summary>')===6,'six native summary controls');
check(substr_count($html,FV_R411_BOARD)>=5,'board source links');
check(substr_count($html,FV_R411_AFTER)===1,'later-test citation only in record six');
check(substr_count($html,FV_R411_ARTICLE)===1,'single next-action link');
check(substr_count($html,FV_R411_RIGHTS)===1,'rights disclosure citation');
check(strpos($html,'<script')===false,'no JS tags');
check(strpos($html,'<img')===false,'no NASA media embedding');
check(strpos($html,'utm_')===false,'no injected tracking');
check(strpos($html,'affiliate')===false,'no affiliate content');
check(substr_count($html,'data-fv-r411-sources')===1,'source region');
check(substr_count($html,'aria-labelledby')===1,'accessible section heading');
check(substr_count($html,'<li class="fv-r411__item">')===6,'semantic ordered list');
check(strpos($html,'Unresolved ignition')!==false,'uncertainty visible');
check(strpos($html,'cannot identify the January 1967 initiator')!==false,'later tests distinct');
check(strpos($html,'not endorsed')!==false,'NASA nonendorsement present');
check(strpos(fv_r411_shortcode(),'fv-r411-sources-2-heading')!==false,'multi instance unique title');
check(strpos(fv_r411_markup(3),'fv-r411-sources-3-heading')!==false,'instance stable heading');
$urls=[];foreach(fv_r411_catalog() as $row){
    check(preg_match('/^0[1-6]$/',$row[0])===1,'record number');
    foreach(array(3,4) as $i){check(strpos($row[$i], 'https://www.nasa.gov/')===0,'official NASA source URL');}
    $urls[]=$row[3];
}
check(count(array_unique($urls))===6,'six unique archive references');
$GLOBALS['fv_r411_env']='production';check(!fv_r411_authorized(),'production rejected');
check(strpos(fv_r411_shortcode(),'Source view unavailable')!==false,'production fails open to free article');
$GLOBALS['fv_r411_env']='staging';$GLOBALS['fv_r411_page']=412;check(!fv_r411_authorized(),'other page rejected');
$GLOBALS['fv_r411_page']=411;check(fv_r411_authorized(),'restored staging');
$bad=sys_get_temp_dir().'/fv_r411_missing_'.getmypid();check(!fv_r411_css_ok($bad),'missing css rejected');
$copy=sys_get_temp_dir().'/fv_r411_tamper_'.getmypid();@mkdir($copy.'/assets',0700,true);
file_put_contents($copy.'/assets/source-drawer.css',".fv-r411{color:red}");
check(!fv_r411_css_ok($copy),'tampered css rejected');
unlink($copy.'/assets/source-drawer.css');rmdir($copy.'/assets');rmdir($copy);
print "R411 PHP assertions PASS {$passed}\n";
