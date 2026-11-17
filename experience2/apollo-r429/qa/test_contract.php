<?php
define('ABSPATH', __DIR__);
require dirname(__DIR__) . '/staging-attribution-bridge.php';
$n=0;function check($v,$msg){global $n;$n++;if(!$v){fwrite(STDERR,"FAIL: $msg\n");exit(1);}}
check(!fv_r429_allowed(),'disabled by default');
check(strpos(fv_r429_shortcode(),FV_R429_ARTICLE)!==false,'fail-open article');
$valid=['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'apollo_longform_001'];
check(count(fv_r429_campaign($valid))===4,'all canonical params');
check(strpos(fv_r429_target($valid),'utm_content=apollo_longform_001')!==false,'asset attribution carried');
check(strpos(fv_r429_target($valid),'utm_source=youtube')!==false,'platform attribution carried');
check(strpos(fv_r429_target($valid),'&')!==false,'canonical query link');
foreach (['utm_source'=>'evil','utm_medium'=>'referral','utm_campaign'=>'product_pilot_2026_11','utm_content'=>'bob@example.com'] as $field=>$bad) {
    $x=$valid;$x[$field]=$bad;check(fv_r429_campaign($x)===[],'reject invalid '.$field);
}
foreach (['utm_source','utm_medium','utm_campaign','utm_content'] as $field) {
    $x=$valid;unset($x[$field]);check(fv_r429_campaign($x)===[],'reject missing '.$field);
    $x=$valid;$x[$field]=['arrays'];check(fv_r429_campaign($x)===[],'reject array '.$field);
}
$x=$valid;$x['utm_source']='youtube%26admin%3D1';check(fv_r429_campaign($x)===[],'reject encoded injection');
$x=$valid;$x['utm_content']=str_repeat('x',200);check(fv_r429_campaign($x)===[],'reject length');
$x=$valid;$x['utm_campaign']='history_pilot_2026_13';check(fv_r429_campaign($x)===[],'reject bad date');
$x=$valid;$x['email']='private@example.com';check(!str_contains(fv_r429_target($x),'email'),'do not forward personal data');
check(fv_r429_target([])===FV_R429_ARTICLE,'no campaign default');
check(count(fv_r429_sources())===3,'three documented stages');
$render=fv_r429_render(1,$valid);$render2=fv_r429_render(2,[]);
check(substr_count($render,'fv-r429__cta')===1,'one intent-matched CTA');
check(substr_count($render,'<details>')===3,'three native disclosures');
check(strpos($render,'no single ignition source')!==false,'uncertainty preserved');
check(strpos($render,'2018-02-14')!==false,'later tests dated correctly');
check(strpos($render,'NASA does not endorse')!==false,'endorsement boundary');
check(strpos($render,'<img')===false && strpos($render,'<script')===false,'no external images or scripts');
check(strpos($render,'fv-r429-1-title')!==false && strpos($render2,'fv-r429-2-title')!==false,'instance-safe IDs');
check(strpos(fv_r429_render(101,$valid),'fv-r429-fallback')!==false,'invalid instance fallback');
echo "PASS $n/$n PHP assertions\n";
