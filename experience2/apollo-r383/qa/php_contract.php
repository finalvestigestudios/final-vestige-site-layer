<?php
/** Deterministic WP API-stub test. This is NOT an installed WordPress/Assembler staging test. */
error_reporting(E_ALL);
define('ABSPATH',__DIR__.'/');
define('FV_R381_TAG','fv_apollo_curated_atlas_r381');
$GLOBALS['shortcode_tags'] = array(FV_R381_TAG => 'fv_r381_shortcode');
$GLOBALS['posts'] = array();
$GLOBALS['enqueued'] = array();
$GLOBALS['hooks'] = array();
$GLOBALS['ok_env']=true; $GLOBALS['ok_assets']=true; $GLOBALS['ok_records']=true;
$GLOBALS['query_id']=900;
function fv_r377_environment(){return $GLOBALS['ok_env'];}
function fv_r381_assets_verified(){return $GLOBALS['ok_assets'];}
function fv_r377_records(){return array('approved');}
function fv_r381_approved($v){return $GLOBALS['ok_records'] && $v === array('approved');}
function shortcode_exists($tag){return isset($GLOBALS['shortcode_tags'][$tag]);}
function is_singular(){return true;}
function get_queried_object_id(){return $GLOBALS['query_id'];}
function get_post($id){return $GLOBALS['posts'][$id] ?? null;}
function wp_enqueue_style($h,$u,$d,$v){$GLOBALS['enqueued']['css'][$h] = array($u,$v);}
function wp_enqueue_script($h,$u,$d,$v,$footer){$GLOBALS['enqueued']['js'][$h] = array($u,$v,$footer);}
function wp_style_is($h,$s){return isset($GLOBALS['enqueued']['css'][$h]);}
function wp_script_is($h,$s){return isset($GLOBALS['enqueued']['js'][$h]);}
function plugins_url($relative,$file){return 'https://approved-stage.example/wp/plugins/apollo-r381/'.$relative;}
function has_shortcode($s,$tag){return strpos($s,'['.$tag.']') !== false;}
function add_action($tag,$cb,$priority=10){$GLOBALS['hooks'][$tag][] = array($cb,$priority);}
function parse_blocks($text){
 if (strncmp($text,'json:',5) === 0){$a=json_decode(substr($text,5),true);return $a;}
 return array(array('blockName'=>null,'innerHTML'=>$text,'innerBlocks'=>array()));
}
require __DIR__.'/../reusable-atlas-assets.php';
$checks=0; $scenario=0;
function expect($cond,$message){global $checks; $checks++; if (!$cond){fwrite(STDERR,'FAIL '.$message."\n");exit(1);}}
function block($kind,$html='',$ref=null,$children=array()){
 $b=array('blockName'=>$kind,'innerHTML'=>$html,'innerBlocks'=>$children);
 if ($ref !== null){$b['attrs']=array('ref'=>$ref);}return $b;
}
function graph(...$blocks){return 'json:'.json_encode($blocks,JSON_UNESCAPED_SLASHES);}
function post($type,$status,$content){return (object)array('post_type'=>$type,'post_status'=>$status,'post_content'=>$content);}
function case_check($label,$content,$valid,$override=array()) {
 global $scenario; $scenario++; $GLOBALS['enqueued']=array(); $GLOBALS['posts'][900]=post('page','publish',$content);
 foreach (array('ok_env'=>true,'ok_assets'=>true,'ok_records'=>true) as $n=>$v) {$GLOBALS[$n]=$override[$n] ?? $v;}
 $GLOBALS['shortcode_tags'][FV_R381_TAG]=$override['owner']??'fv_r381_shortcode';
 fv_r383_prehead_assets();
 $css=count($GLOBALS['enqueued']['css']??array());$js=count($GLOBALS['enqueued']['js']??array());
 expect(($css===1 && $js===1)===$valid,$label.' load CSS+JS iff approved');
 expect($css===$js,$label.' no half-loaded assets');
 if($valid){expect(isset($GLOBALS['enqueued']['css']['fv-apollo-r381-atlas']),$label.' CSS handle');
 expect(isset($GLOBALS['enqueued']['js']['fv-apollo-r381-atlas']),$label.' JS handle');
 fv_r383_prehead_assets();expect(count($GLOBALS['enqueued']['css'])===1 && count($GLOBALS['enqueued']['js'])===1,$label.' idempotence');}
}
$tag='['.FV_R381_TAG.']';
$GLOBALS['posts'][10]=post('wp_block','publish',$tag);
$GLOBALS['posts'][11]=post('wp_block','publish',graph(block('core/block','',10)));
$GLOBALS['posts'][12]=post('wp_block','draft',$tag);
$GLOBALS['posts'][13]=post('page','publish',$tag);
$GLOBALS['posts'][14]=post('wp_block','publish',graph(block('core/block','',14)));
$GLOBALS['posts'][15]=post('wp_block','publish',graph(block('core/block','',16)));
$GLOBALS['posts'][16]=post('wp_block','publish',graph(block('core/block','',15)));
case_check('direct classic',$tag,true);
case_check('core shortcode',graph(block('core/shortcode',$tag)),true);
case_check('reusable',graph(block('core/block','',10)),true);
case_check('nested reusable',graph(block('core/block','',11)),true);
case_check('same ref siblings',graph(block('core/block','',10),block('core/block','',10)),true);
case_check('direct and same reusable',graph(block('core/shortcode',$tag),block('core/block','',10)),true);
case_check('unrelated',graph(block('core/paragraph','Plain')),false);
case_check('escaped code',graph(block('core/code',$tag)),false);
case_check('escaped preformatted',graph(block('core/preformatted',$tag)),false);
case_check('draft ref',graph(block('core/block','',12)),false);
case_check('foreign post type',graph(block('core/block','',13)),false);
case_check('missing ref',graph(block('core/block','',999)),false);
case_check('non-int ref',graph(block('core/block','',"10")),false);
case_check('self cycle',graph(block('core/block','',14)),false);
case_check('two node cycle',graph(block('core/block','',15)),false);
case_check('good then missing ref',graph(block('core/shortcode',$tag),block('core/block','',999)),false);
case_check('good then cycle',graph(block('core/shortcode',$tag),block('core/block','',14)),false);
case_check('good then malformed',graph(block('core/shortcode',$tag),'bad'),false);
case_check('invalid json', 'json:{',false);
case_check('oversize content',$tag.str_repeat('x',1048576),false);
case_check('bad environment',$tag,false,array('ok_env'=>false));
case_check('bad assets',$tag,false,array('ok_assets'=>false));
case_check('bad records',$tag,false,array('ok_records'=>false));
case_check('other owner',$tag,false,array('owner'=>'unrelated_plugin_callback'));
// registration gate is only delegated to the correct owner, after R381 has registered.
$GLOBALS['shortcode_tags'][FV_R381_TAG]='fv_r381_shortcode';$GLOBALS['ok_env']=true;
foreach ($GLOBALS['hooks']['plugins_loaded']??array() as $h){$h[0]();}
expect(count($GLOBALS['hooks']['wp_enqueue_scripts']??array())===1,'only one guarded enqueue hook');
expect($GLOBALS['hooks']['wp_enqueue_scripts'][0][1]===2,'prehead priority 2');
fwrite(STDOUT,json_encode(array('status'=>'PASS_LOCAL_PHP_STUB_NOT_WORDPRESS','scenarios'=>$scenario,'assertions'=>$checks),JSON_PRETTY_PRINT)."\n");
