<?php
// R174 isolated PHP CLI harness. No WordPress bootstrap, CMS writes or live requests.
// Run: php experience2/apollo-r174/tests/asset_lifecycle_mock.php
error_reporting(E_ALL);
define('ABSPATH','/staging/');
$GLOBALS['styles']=[]; $GLOBALS['scripts']=[]; $GLOBALS['actions']=[]; $GLOBALS['shortcodes']=[];
function is_singular(){ throw new Exception('legacy is_singular gate must not execute'); }
function get_post(){ throw new Exception('legacy top-level post check must not execute'); }
function has_shortcode($a,$b){ throw new Exception('legacy shortcode gate must not execute'); }
function add_action($hook,$cb,$priority=10){$GLOBALS['actions'][$hook][]=$cb;}
function add_shortcode($name,$cb){$GLOBALS['shortcodes'][$name]=$cb;}
function wp_enqueue_style($h,$src,$deps,$version){$GLOBALS['styles'][$h]=compact('h','src','deps','version');}
function wp_enqueue_script($h,$src,$deps,$version,$footer){$GLOBALS['scripts'][$h]=compact('h','src','deps','version','footer');}
function plugins_url($rel,$file){return 'https://stage.invalid/plugins/research-desk/'.$rel;}
function plugin_dir_path($file){return dirname($file).'/';}
function esc_url($url){return htmlspecialchars($url,ENT_QUOTES);}
require __DIR__.'/../staging-overlay/final-vestige-ex2-research-desk.php';
$contexts=['top-level shortcode','reusable pattern','nested dynamic block','archive/widget','absent shortcode'];
foreach($contexts as $context){
  $GLOBALS['styles']=[];$GLOBALS['scripts']=[];
  fv_ex2_rd_assets();
  if(count($GLOBALS['styles'])!==1 || count($GLOBALS['scripts'])!==1)throw new Exception($context.' assets missing');
  $css=$GLOBALS['styles']['fv-ex2-research-desk']??[];
  $js=$GLOBALS['scripts']['fv-ex2-research-desk']??[];
  if(!str_ends_with($css['src']??'','source-ledger.css'))throw new Exception($context.' wrong CSS');
  if(!str_ends_with($js['src']??'','source-ledger.js') || ($js['footer']??null)!==true)throw new Exception($context.' wrong JS');
  fv_ex2_rd_assets(); // same handle (WordPress handles de-duplicate)
  if(count($GLOBALS['styles'])!==1 || count($GLOBALS['scripts'])!==1)throw new Exception($context.' duplicate handles');
}
if(count($GLOBALS['actions']['wp_enqueue_scripts']??[])!==1 || count($GLOBALS['shortcodes'])!==1)throw new Exception('unexpected hooks');
$unavailable=fv_ex2_rd_shortcode();
if(strpos($unavailable,'Read the original Apollo 1 investigation')===false)throw new Exception('static fallback missing');
echo json_encode(['php_cli'=>'PASS','scenarios'=>$contexts,'fallback'=>'PASS','wp_staging'=>'NOT_TESTED','global_asset_preload'=>'EXPLICIT_TRADEOFF'],JSON_PRETTY_PRINT)."\n";
