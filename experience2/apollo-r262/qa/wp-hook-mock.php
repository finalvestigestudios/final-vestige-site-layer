<?php
/** R262 PHP hook mock, NOT an installed WordPress test. */
define('ABSPATH','/sim/');
$GLOBALS['styles']=array();$GLOBALS['scripts']=array();$GLOBALS['hooks']=array();
function add_action($hook,$name,$priority=10){$GLOBALS['hooks'][]=array($hook,$name,$priority);}
function plugins_url($path,$file){return '/preview/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$src='',$deps=array(),$ver=''){$GLOBALS['styles'][$handle]=array($src,$deps,$ver);}
function wp_enqueue_script($handle,$src='',$deps=array(),$ver='',$footer=false){$GLOBALS['scripts'][$handle]=array($src,$deps,$ver,$footer);}
function wp_style_is($handle,$mode){return $mode==='enqueued' && array_key_exists($handle,$GLOBALS['styles']);}
function fv_ex2_r224_assets_ok(){return getenv('BASE_VALID')!=='0';}
function is_admin(){return getenv('SIM_ADMIN')==='1';}
function is_singular(){return getenv('SIM_SINGULAR')!=='0';}
$mode=getenv('SIM_MODE') ?: 'pass';
if($mode==='original')wp_enqueue_style('fv-apollo-r224','/preview/base.css');
require dirname(__DIR__).'/fv-apollo-staging-overlay.php';
foreach($GLOBALS['hooks'] as $h){if($h[0]==='wp_enqueue_scripts')call_user_func($h[1]);}
echo json_encode(array('styles'=>$GLOBALS['styles'],'scripts'=>$GLOBALS['scripts'],'hook_priority'=>$GLOBALS['hooks'][0][2],'assets_ok'=>fv_apollo_r262_assets_ok()),JSON_THROW_ON_ERROR);
