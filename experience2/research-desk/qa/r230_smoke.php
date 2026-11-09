<?php
/** Executable R230 WordPress-function shim. Run from repo: php experience2/research-desk/qa/r230_smoke.php */
error_reporting(E_ALL);
define('ABSPATH', '/offline-staging/');
$hooks = []; $assets = []; $flags = ['head'=>0,'footer'=>0,'style_done'=>false,'script_done'=>false];
function add_action($name,$callback,$priority=10){global $hooks;$hooks[$name][]=$callback;}
function add_shortcode($name,$callback){}
function is_singular(){return true;}
function get_post(){return (object)['post_content'=>'<!-- wp:block {"ref":42} /-->'];}
function has_shortcode($text,$name){return strpos($text,'['.$name.']')!==false;}
function plugins_url($path,$file){return 'https://staging.invalid/ex2/'.$path;}
function plugin_dir_path($file){return dirname($file).'/';}
function esc_url($url){return htmlspecialchars($url,ENT_QUOTES,'UTF-8');}
function did_action($name){global $flags;return $flags[$name==='wp_head'?'head':'footer']??0;}
function wp_style_is($handle,$state){global $flags;return $state==='done'&&$flags['style_done'];}
function wp_script_is($handle,$state){global $flags;return $state==='done'&&$flags['script_done'];}
function wp_enqueue_style($handle,$url,$deps,$version){global $assets;$assets['style'][$handle]=$url;}
function wp_enqueue_script($handle,$url,$deps,$version,$footer){global $assets;$assets['script'][$handle]=$url;}
require dirname(__DIR__).'/fv-ex2-r230-runtime.php';
foreach(($hooks['wp_enqueue_scripts']??[]) as $fn)$fn();
$flags['head']=1;
$one=fv_ex2_r230_shortcode();
$two=fv_ex2_r230_shortcode();
function check($ok,$why){if(!$ok){fwrite(STDERR,"FAIL: $why\n");exit(2);}}
check(strpos($one,'fv-ex2-ledger-apollo1-')!==false,'missing original namespace');
check(strpos($two,'fv-ex2-ledger-apollo1-copy-2-')!==false,'missing second namespace');
check(substr_count($one.$two,'<link rel="stylesheet"')===1,'late stylesheet not singleton');
check(strpos($one.$two,'https://www.nasa.gov/')!==false,'expected source links missing');
check(count($assets['script']??[])===1,'optional script not enqueued');
check(count($assets['style']??[])===1,'style not enqueued');
echo "PASS R230 nested + 2 instances, 1 CSS link, 1 queued JS, R158 source link present\n";
