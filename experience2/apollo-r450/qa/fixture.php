<?php
/** Offline fixture of actual inherited PHP; NOT installed WordPress or navigated staging. */
$mode=$argv[1]??'staging';
define('ABSPATH','/fixture/');
if($mode!=='disabled') {define('FV_R450_ENABLE_STAGING',true);define('FV_R449_ENABLE_STAGING',true);}
define('FV_R450_STAGING_PAGE_ID',4500);
define('FV_R449_STAGING_PAGE_ID',4500);
function wp_get_environment_type(){global $mode;return $mode==='production'?'production':'staging';}
function is_singular(){return true;}
function get_queried_object_id(){global $mode;return $mode==='other-page'?123:4500;}
function add_shortcode($tag,$fn){return true;}
function add_action($key,$fn,$priority=10){return true;}
function wp_enqueue_style($handle,$src,$deps=[],$ver=''){return true;}
function wp_enqueue_script($handle,$src,$deps=[],$ver='',$foot=false){return true;}
function plugins_url($path,$file){return '/fixture/'.basename(dirname($file)).'/'.$path;}
require dirname(__DIR__).'/receipt.php';
$body=fv_r450_render();
if($mode==='double')$body.=fv_r450_render();
$root=dirname(dirname(__DIR__));
$styles='';$scripts='';
if($mode!=='production'&&$mode!=='disabled'&&$mode!=='other-page'&&fv_r450_ready()){
 foreach(['apollo-r448/assets/crosswalk.css','apollo-r440/assets/educator-intent.css','apollo-r449/assets/journey.css','apollo-r450/assets/receipt.css'] as $path)
  $styles.='<style>'.file_get_contents($root.'/'.$path).'</style>';
 foreach(['apollo-r448/assets/crosswalk.js','apollo-r440/assets/educator-intent.js','apollo-r450/assets/receipt.js'] as $path)
  $scripts.='<script>'.file_get_contents($root.'/'.$path).'</script>';
}
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R450 local source receipt fixture</title><style>html,body{margin:0;padding:0;background:#111719;color:#f2eee5;font-family:system-ui}body{max-width:100%}</style>'.$styles.'</head><body><main>'.$body.'</main>'.$scripts.'</body></html>';
