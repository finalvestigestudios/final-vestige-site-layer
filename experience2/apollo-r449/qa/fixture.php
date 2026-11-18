<?php
/** Render installed SOURCE PHP into local HTML; it is NOT navigated WordPress staging. */
$mode=$argv[1]??'staging';
define('ABSPATH','/fixture/');
if($mode!=='not-enabled')define('FV_R449_ENABLE_STAGING',true);
define('FV_R449_STAGING_PAGE_ID',4001);
function wp_get_environment_type(){global $mode;return $mode==='production'?'production':'staging';}
function is_singular(){return true;}
function get_queried_object_id(){global $mode;return $mode==='wrong-page'?9999:4001;}
function add_shortcode($a,$b){return true;}
function add_action($a,$b,$c=10){return true;}
function wp_enqueue_style($a,$b,$c=[],$d=''){return true;}
function wp_enqueue_script($a,$b,$c=[],$d='',$e=false){return true;}
function plugins_url($file,$base){return '/stage/'.basename(dirname($base)).'/'.$file;}
require dirname(__DIR__).'/journey.php';
$render=fv_r449_render();
if($mode==='double')$render.=fv_r449_render();
$root=dirname(dirname(__DIR__));
$valid=fv_r449_verified();
$styles='';$scripts='';
if($valid && $mode!=='production' && $mode!=='not-enabled' && $mode!=='wrong-page') {
  foreach(['apollo-r448/assets/crosswalk.css','apollo-r440/assets/educator-intent.css','apollo-r449/assets/journey.css'] as $p)
    $styles.='\n<style>'.file_get_contents($root.'/'.$p).'</style>';
  foreach(['apollo-r448/assets/crosswalk.js','apollo-r440/assets/educator-intent.js'] as $p)
    $scripts.='\n<script>'.file_get_contents($root.'/'.$p).'</script>';
}
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">';
echo '<title>Apollo Evidence Journey R449 — Local Fixture</title><style>html,body{margin:0;padding:0;background:#111719;color:#f2eee5;font-family:system-ui}body{max-width:100%;overflow-x:clip}</style>'.$styles.'</head><body><main>'.$render.'</main>'.$scripts.'</body></html>';
