<?php
/** R396 real PHP execution with WordPress *stubs only*. No WP installation. */
if (!defined('ABSPATH')) define('ABSPATH', '/tmp/apollo-r396-readonly');
$ledger = json_decode(file_get_contents(__DIR__.'/../../apollo-r377/custody.json'), true);
$GLOBALS['fixture'] = [
    'env'=>'staging', 'page'=>true, 'records'=>$ledger['records'],
    'actions'=>[], 'styles'=>[],
];
function wp_get_environment_type() { return $GLOBALS['fixture']['env']; }
function is_page($slug) { return $slug === 'apollo-1-evidence-atlas' && $GLOBALS['fixture']['page']; }
function fv_r384_records() { return $GLOBALS['fixture']['records']; }
function plugins_url($path,$source) { return 'https://staging.example.invalid/wp-content/plugins/apollo-r396/'.$path; }
function wp_enqueue_style($handle,$src,$deps,$ver,$media) {
    $GLOBALS['fixture']['styles'][]=compact('handle','src','deps','ver','media');
}
function add_action($name,$callback,$priority) { $GLOBALS['fixture']['actions'][]=compact('name','callback','priority'); }
require __DIR__.'/../staging-custody.php';
$assertions = 0;
function check($condition,$reason) {
    global $assertions; $assertions++;
    if (!$condition) { fwrite(STDERR,"FAIL #$assertions: $reason\n");exit(1); }
}
check(count($GLOBALS['fixture']['actions'])===1,'single hook');
check($GLOBALS['fixture']['actions'][0]['priority']===99,'head enqueue priority');
check(fv_r396_records_are_reviewed($ledger['records']),'six canonical NASA records accepted');
check(!fv_r396_records_are_reviewed(false),'boolean false rejected');
check(!fv_r396_records_are_reviewed([$ledger['records'][0]]),'one-card spoof rejected');
check(!fv_r396_records_are_reviewed(array_reverse($ledger['records'])),'reordered cards rejected');
check(!fv_r396_records_are_reviewed(array_slice($ledger['records'],0,5)),'five-card spoof rejected');
check(!fv_r396_records_are_reviewed(array_merge($ledger['records'],[$ledger['records'][0]])),'seven-card spoof rejected');
check(!fv_r396_records_are_reviewed(['first'=>$ledger['records'][0]]),'associative array rejected');
check(!fv_r396_records_are_reviewed('not-an-array'),'text rejected');
foreach (array('id','heading','kind','claim','boundary','evidence_url','evidence_role','catalog_note','context_url') as $key) {
    $t=$ledger['records'];$t[0][$key] .= ' ALTERED';
    check(!fv_r396_records_are_reviewed($t),'mutated visible field '.$key);
}
foreach (array(0,1,2,3,4,5) as $idx) {
    $t=$ledger['records'];unset($t[$idx]['boundary']);
    check(!fv_r396_records_are_reviewed($t),'missing boundary '.$idx);
}
$t=$ledger['records'];$t[5]['evidence_url']=$t[0]['evidence_url'];
check(!fv_r396_records_are_reviewed($t),'later tests cannot become Board report');
$t=$ledger['records'];$t[4]['claim']="Board proved ignition source.";
check(!fv_r396_records_are_reviewed($t),'false certainty rejected');
check(fv_r396_file_is_reviewed(__DIR__.'/../../apollo-r384/assets/gallery.css',FV_R396_BASE_SHA256),'base verified');
check(fv_r396_file_is_reviewed(__DIR__.'/../../apollo-r395/assets/mobile-fit.css',FV_R396_FIT_SHA256),'fit verified');
check(!fv_r396_file_is_reviewed(__FILE__,FV_R396_BASE_SHA256),'bad hash rejected');
check(!fv_r396_file_is_reviewed(__DIR__.'/no-such-file',FV_R396_BASE_SHA256),'missing file rejected');
$enabled=defined('FV_R396_APOLLO_QA_ENABLE') && FV_R396_APOLLO_QA_ENABLE === true;
if (!$enabled) {
    check(!fv_r396_prepaint_eligible(),'default off');
    fv_r396_enqueue_prepaint();check(count($GLOBALS['fixture']['styles'])===0,'default no output');
} else {
    check(fv_r396_prepaint_eligible(),'staging eligible with exact ledger');
    fv_r396_enqueue_prepaint();check(count($GLOBALS['fixture']['styles'])===2,'exact two sheets');
    $s=$GLOBALS['fixture']['styles'];
    check($s[0]['handle']==='fv-apollo-r384-gallery','base handle');
    check($s[0]['media']==='all','base print and screen');
    check($s[1]['handle']==='fv-apollo-r395-mobile-fit','fit handle');
    check($s[1]['deps']===['fv-apollo-r384-gallery'],'fit after base');
    check($s[1]['media']==='screen','no new print styles');
    check(str_contains($s[1]['src'],'/apollo-r395/assets/mobile-fit.css'),'reviewed fit URL');
    $GLOBALS['fixture']['records']=[$ledger['records'][0]];
    check(!fv_r396_prepaint_eligible(),'bad record set prevents styles');
    $GLOBALS['fixture']['records']=$ledger['records'];
    $GLOBALS['fixture']['env']='production';check(!fv_r396_prepaint_eligible(),'production denied');
    $GLOBALS['fixture']['env']='development';check(!fv_r396_prepaint_eligible(),'development denied');
    $GLOBALS['fixture']['env']='staging';$GLOBALS['fixture']['page']=false;
    check(!fv_r396_prepaint_eligible(),'other page denied');
    $GLOBALS['fixture']['page']=true;check(fv_r396_prepaint_eligible(),'staging restored');
}
echo "R396 PASS $assertions assertions; opt-in ".($enabled?'on':'off')."; no WP writes\n";
