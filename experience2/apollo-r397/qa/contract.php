<?php
/** Native PHP against WP stubs only. Must not be mistaken for installed WP. */
if (!defined('ABSPATH')) define('ABSPATH', '/tmp/apollo-r397-read-only');
$ledger = json_decode((string)file_get_contents(__DIR__.'/../../apollo-r377/custody.json'), true);
$GLOBALS['fixture'] = [
    'env'=>'staging', 'page'=>true, 'records'=>$ledger['records'], 'styles'=>[],
    'actions'=>[], 'registered'=>[], 'src_override'=>[], 'site'=>'https://staging.fv.example/',
];
function wp_get_environment_type() {return $GLOBALS['fixture']['env'];}
function is_page($slug) {return $slug==='apollo-1-evidence-atlas' && $GLOBALS['fixture']['page'];}
function fv_r384_records() {return $GLOBALS['fixture']['records'];}
function home_url($path='/') {return $GLOBALS['fixture']['site'];}
function plugins_url($path, $file) {
    $u='https://staging.fv.example/wp-content/plugins/final-vestige-site-layer/experience2/apollo-r397/'.$path;
    return $GLOBALS['fixture']['src_override'][$path] ?? $u;
}
function wp_style_is($handle,$status) {return in_array($handle,$GLOBALS['fixture']['registered'],true);}
function wp_enqueue_style($handle,$src,$deps,$ver,$media) {
    $GLOBALS['fixture']['styles'][]=compact('handle','src','deps','ver','media');
    $GLOBALS['fixture']['registered'][]=$handle;
}
function add_action($name,$callback,$priority) {$GLOBALS['fixture']['actions'][]=compact('name','callback','priority');}
require __DIR__.'/../staging-delivery-guard.php';
$n=0;
function ok($value,$why) {global $n;$n++; if(!$value){fwrite(STDERR,"FAIL $n $why\n");exit(1);}}
$base=$GLOBALS['fixture'];
ok(count($base['actions'])===1,'one hook');
ok($base['actions'][0]['priority']===99,'prepaint enqueue priority');
ok(fv_r397_exact_records($ledger['records']),'whole ledger accepted');
foreach ($ledger['records'] as $i=>$record) {
  foreach (array_keys($record) as $field) {
    $wrong=$ledger['records'];$wrong[$i][$field].=' modified';
    ok(!fv_r397_exact_records($wrong),"tamper $i/$field");
  }
  $wrong=$ledger['records'];$wrong[$i]['offsite_cta']='https://merchant.invalid/';
  ok(!fv_r397_exact_records($wrong),"extra injected field $i");
  $wrong=$ledger['records'];unset($wrong[$i]['context_role']);
  ok(!fv_r397_exact_records($wrong),"missing retrospective class $i");
}
$wrong=$ledger['records'];$wrong[0]['context_role']=null;
ok(!fv_r397_exact_records($wrong),'null context role rejected');
ok(!fv_r397_exact_records(array_reverse($ledger['records'])),'reordered source denied');
ok(!fv_r397_exact_records([$ledger['records'][0]]),'partial source denied');
ok(!fv_r397_exact_records(false),'false source denied');
foreach (array('https://staging.fv.example/', 'https://staging.fv.example:443/') as $url) {
  ok(fv_r397_reviewed_asset_url('https://staging.fv.example/wp-content/plugins/site/experience2/apollo-r397/../apollo-r384/assets/gallery.css',$url,'apollo-r384/assets/gallery.css')===($url==='https://staging.fv.example/'),'origin/port policy');
}
$good='https://staging.fv.example/wp-content/plugins/site/experience2/apollo-r397/../apollo-r384/assets/gallery.css';
$bad=[
  str_replace('https:', 'http:', $good),
  str_replace('staging.fv.example','cdn.attacker.invalid',$good),
  str_replace('staging.fv.example','staging.fv.example.evil.invalid',$good),
  str_replace('https://','https://user:password@',$good),
  str_replace('.example/', '.example:8443/', $good),
  $good.'?key=123', $good.'#escape',
  str_replace('/apollo-r397/../','/apollo-r397/%2e%2e/',$good),
  str_replace('/apollo-r397/../','/apollo-r397/../../',$good),
  str_replace('/apollo-r397/../','/apollo-r397//../',$good),
  str_replace('apollo-r384/assets/gallery.css','apollo-r395/assets/mobile-fit.css',$good),
  str_replace('/apollo-r397/../','/apollo-r396/../',$good),
];
foreach($bad as $i=>$url) ok(!fv_r397_reviewed_asset_url($url,$base['site'],'apollo-r384/assets/gallery.css'),'reject unsafe URL '.$i);
$enabled=defined('FV_R397_APOLLO_QA_ENABLE') && FV_R397_APOLLO_QA_ENABLE===true;
if (!$enabled) {
    ok(fv_r397_reviewed_delivery()===false,'default-off');
    fv_r397_enqueue_prepaint();ok($GLOBALS['fixture']['styles']===[],'zero output disabled');
} else {
    ok(is_array(fv_r397_reviewed_delivery()),'staging eligible');
    foreach (array('fv-apollo-r384-gallery','fv-apollo-r395-mobile-fit') as $handle) {
        $GLOBALS['fixture']['registered']=[$handle];
        ok(fv_r397_reviewed_delivery()===false,'block collision '.$handle);
    }
    $GLOBALS['fixture']['registered']=[];
    foreach(array('production','development') as $env) {
        $GLOBALS['fixture']['env']=$env;
        ok(fv_r397_reviewed_delivery()===false,'block other env '.$env);
    }
    $GLOBALS['fixture']['env']='staging';
    $GLOBALS['fixture']['page']=false;
    ok(fv_r397_reviewed_delivery()===false,'block other page');
    $GLOBALS['fixture']['page']=true;
    $GLOBALS['fixture']['records']=[$ledger['records'][0]];
    ok(fv_r397_reviewed_delivery()===false,'block partial ledger');
    $GLOBALS['fixture']['records']=$ledger['records'];
    foreach (array('base','fit') as $which) {
      $name=$which==='base'?'../apollo-r384/assets/gallery.css':'../apollo-r395/assets/mobile-fit.css';
      foreach (array('http://staging.fv.example/offsite.css','https://foreign.invalid/style.css') as $url) {
        $GLOBALS['fixture']['src_override'][$name]=$url;
        ok(fv_r397_reviewed_delivery()===false,'block mutated '.$which.' CDN');
      }
      $GLOBALS['fixture']['src_override']=[];
    }
    $GLOBALS['fixture']['site']='http://staging.fv.example/';
    ok(fv_r397_reviewed_delivery()===false,'no insecure WordPress site');
    $GLOBALS['fixture']['site']=$base['site'];
    fv_r397_enqueue_prepaint();
    ok(count($GLOBALS['fixture']['styles'])===2,'exact two styles enqueued');
    ok($GLOBALS['fixture']['styles'][0]['media']==='all','base print support');
    ok($GLOBALS['fixture']['styles'][1]['deps']===['fv-apollo-r384-gallery'],'dependent fit');
    ok($GLOBALS['fixture']['styles'][1]['media']==='screen','fit screen only');
    ok(fv_r397_reviewed_delivery()===false,'no double enqueue once handles registered');
}
echo "R397 PASS $n PHP assertions, opt-in ".($enabled?'on':'off')."; stubs only; no WP writes\n";
