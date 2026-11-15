<?php
/** R395 integration unit tests: self-contained WordPress function stubs, no site writes. */
if (!defined('ABSPATH')) define('ABSPATH', '/tmp/r395-read-only');
$state = [ 'env'=>'staging', 'page'=>true, 'records'=>true, 'enqueued'=>[], 'actions'=>[] ];
function wp_get_environment_type() { return $GLOBALS['state']['env']; }
function is_page($slug) { return $slug === 'apollo-1-evidence-atlas' && $GLOBALS['state']['page']; }
function fv_r384_records() { return $GLOBALS['state']['records'] ? [ ['id'=>'01-ground-test'] ] : false; }
function plugins_url($path,$file) { return 'https://approved-staging.example/wp-content/plugins/fv-ex2/apollo-r395/'.$path; }
function wp_enqueue_style($name,$url,$dep,$version,$media) { $GLOBALS['state']['enqueued'][]=compact('name','url','dep','version','media'); }
function add_action($action,$callback,$priority) { $GLOBALS['state']['actions'][]=compact('action','callback','priority'); }
require __DIR__.'/../staging-prepaint.php';

$checks = 0;
function ok($v,$message){global $checks;$checks++;if(!$v){fwrite(STDERR,"FAILED $message\n");exit(1);}}
ok(count($state['actions'])===1,'single action');
ok($state['actions'][0]['priority']===99,'priority');
if (!defined('FV_R395_APOLLO_QA_ENABLE')) {
 ok(!fv_r395_prepaint_eligible(),'no explicit opt-in');
 fv_r395_enqueue_prepaint();ok(count($state['enqueued'])===0,'no automatic styles');
}
// To simulate a controlled approved staging define, explicitly supply
// -d auto_prepend_file in the subprocess run; no config file is modified.
if (defined('FV_R395_APOLLO_QA_ENABLE')) {
  ok(fv_r395_prepaint_eligible(),'approved staging eligible');
  fv_r395_enqueue_prepaint();ok(count($state['enqueued'])===2,'two sheets ordered');
  ok($state['enqueued'][0]['name']==='fv-apollo-r384-gallery','original handle');
  ok($state['enqueued'][1]['dep']===['fv-apollo-r384-gallery'],'fit depends on base');
  ok($state['enqueued'][1]['media']==='screen','print stays unchanged');
  ok(str_contains($state['enqueued'][1]['url'],'mobile-fit.css'),'reviewed path');
  $state['env']='production';ok(!fv_r395_prepaint_eligible(),'production refused');
  $state['env']='development';ok(!fv_r395_prepaint_eligible(),'development refused');
  $state['env']='staging';$state['page']=false;ok(!fv_r395_prepaint_eligible(),'wrong page refused');
  $state['page']=true;$state['records']=false;ok(!fv_r395_prepaint_eligible(),'custody refused');
  $state['records']=true;
  ok(fv_r395_reviewed_file(dirname(__DIR__,2).'/apollo-r384/assets/gallery.css',FV_R395_BASE_SHA256),'original CSS pinned');
  ok(fv_r395_reviewed_file(__DIR__.'/../assets/mobile-fit.css',FV_R395_FIT_SHA256),'fit CSS pinned');
  ok(!fv_r395_reviewed_file(__FILE__,FV_R395_FIT_SHA256),'mismatched file refused');
  ok(!fv_r395_reviewed_file(__DIR__.'/not-there.css',FV_R395_FIT_SHA256),'missing file refused');
}
echo "PASS $checks assertions; staged opt-in=".(defined('FV_R395_APOLLO_QA_ENABLE')?'on':'off')."\n";
