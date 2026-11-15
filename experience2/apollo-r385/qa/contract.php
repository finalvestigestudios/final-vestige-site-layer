<?php
/** Offline WordPress API doubles; NOT an installed WordPress test. */
error_reporting(E_ALL);
$root=dirname(__DIR__,2);
define('ABSPATH',$root.'/');
$GLOBALS['canonical']=json_decode(file_get_contents($root.'/apollo-r377/custody.json'),true,512,JSON_THROW_ON_ERROR)['records'];
$GLOBALS['records']=$GLOBALS['canonical'];
$GLOBALS['env']=true; $GLOBALS['singular']=true;
$GLOBALS['styles']=array();$GLOBALS['hooks']=array();$GLOBALS['graphs']=array();$GLOBALS['refs']=array();
$GLOBALS['shortcode_tags']=array();
$GLOBALS['main']=(object)array('post_type'=>'post','post_status'=>'publish','post_content'=>'');
function fv_r377_environment(){return $GLOBALS['env'];}
function fv_r377_records(){return $GLOBALS['records'];}
function fv_r381_approved($records){return $records === $GLOBALS['canonical'];}
function add_action($event,$fn,$priority=10){$GLOBALS['hooks'][]=array($event,$priority,$fn);}
function shortcode_exists($tag){return isset($GLOBALS['shortcode_tags'][$tag]);}
function add_shortcode($tag,$fn){$GLOBALS['shortcode_tags'][$tag]=$fn;}
function is_singular(){return $GLOBALS['singular'];}
function get_queried_object_id(){return 123;}
function get_post($id){return $id===123?$GLOBALS['main']:($GLOBALS['refs'][$id]??null);}
function has_shortcode($content,$tag){return strpos($content,'['.$tag.']')!==false;}
function wp_enqueue_style(...$args){$GLOBALS['styles'][]=$args;}
function wp_style_is($handle,$state){foreach($GLOBALS['styles'] as $style){if($style[0]===$handle)return true;}return false;}
function plugins_url($path,$file){return 'http://127.0.0.1:8935/assets/'.$path;}
function parse_blocks($content){return $GLOBALS['graphs'][$content]??array(array('blockName'=>null,'innerHTML'=>$content,'innerBlocks'=>array()));}
function B($name,$html='',$attrs=array(),$kids=array()){return array('blockName'=>$name,'innerHTML'=>$html,'attrs'=>$attrs,'innerBlocks'=>$kids);}
function REF($n){return B('core/block','',array('ref'=>$n));}
function WPBLOCK($content,$status='publish',$type='wp_block'){return (object)array('post_type'=>$type,'post_status'=>$status,'post_content'=>$content);}
require $root.'/apollo-r384/document-gallery.php';
require dirname(__DIR__).'/gallery-asset-guard.php';
$checks=0;
function ok($bool,$name){global $checks;$checks++;if(!$bool)throw new RuntimeException('FAIL '.$name);}
$tag='['.FV_R384_TAG.']';
ok(fv_r384_records()!==false,'canonical NASA record contract');
ok(fv_r384_assets_verified(),'exact CSS SHA-256');
// R384's prehead detector misses shortcode nested behind a WP reusable reference.
$GLOBALS['main']->post_content='parent-7';$GLOBALS['graphs']['parent-7']=array(REF(7));
$GLOBALS['refs'][7]=WPBLOCK('source-leaf');
$GLOBALS['graphs']['source-leaf']=array(B('core/shortcode',$tag));
fv_r384_enqueue();ok(count($GLOBALS['styles'])===0,'reproduce R384 nested-block stylesheet miss');
$GLOBALS['shortcode_tags'][FV_R384_TAG]='fv_r384_shortcode';
ok(fv_r385_gallery_owner(),'R384 shortcode exact owner');
ok(fv_r385_gallery_in_blocks('parent-7'),'published nested shortcode found');
fv_r385_prehead_assets();ok(count($GLOBALS['styles'])===1,'guard loads one CSS for reusable shortcode');
ok($GLOBALS['styles'][0][0]==='fv-apollo-r384-gallery','reuses existing CSS handle');
fv_r385_prehead_assets();ok(count($GLOBALS['styles'])===1,'duplicate preload prevented');
$GLOBALS['styles']=array();
$GLOBALS['main']->post_content='plain article';fv_r385_prehead_assets();
ok(count($GLOBALS['styles'])===0,'unrelated article loads no gallery CSS');
$GLOBALS['main']->post_content='parent-7';
$GLOBALS['refs'][8]=WPBLOCK('source-leaf');
$GLOBALS['graphs']['two-reuses']=array(REF(7),REF(8));
ok(fv_r385_gallery_in_blocks('two-reuses'),'same referenced content allowed twice');
$GLOBALS['graphs']['same-ref']=array(REF(7),REF(7));
ok(fv_r385_gallery_in_blocks('same-ref'),'same block ref reused in siblings');
$GLOBALS['graphs']['nested']=array(REF(7));$GLOBALS['refs'][8]=WPBLOCK('nested');
$GLOBALS['graphs']['source-leaf']=array(B('core/group','',array(),array(B('core/shortcode',$tag))));
ok(fv_r385_gallery_in_blocks('parent-7'),'nested innerBlocks recognized');
ok(fv_r385_gallery_in_blocks('nested'),'nested reference resolved');
$GLOBALS['graphs']['bad-sibling']=array(REF(7),REF(9999));
ok(!fv_r385_gallery_in_blocks('bad-sibling'),'invalid sibling after valid source rejects all');
$GLOBALS['graphs']['bad-ref']=array(REF('7'));
ok(!fv_r385_gallery_in_blocks('bad-ref'),'string reference rejected');
$GLOBALS['graphs']['zero']=array(REF(0));
ok(!fv_r385_gallery_in_blocks('zero'),'zero ref rejected');
$GLOBALS['refs'][12]=WPBLOCK('source-leaf','draft');
$GLOBALS['graphs']['draft']=array(REF(12));
ok(!fv_r385_gallery_in_blocks('draft'),'draft reusable block rejected');
$GLOBALS['refs'][12]=WPBLOCK('source-leaf','publish','page');
ok(!fv_r385_gallery_in_blocks('draft'),'foreign post type rejected');
$GLOBALS['refs'][12]=WPBLOCK('cyclic');$GLOBALS['graphs']['cyclic']=array(REF(12),REF(12));
$GLOBALS['graphs']['root-cycle']=array(REF(12));$GLOBALS['graphs']['cyclic']=array(REF(12),B('core/shortcode',$tag));
ok(!fv_r385_gallery_in_blocks('root-cycle'),'cycle rejected even with valid source');
foreach(array('core/code','core/preformatted','core/html') as $kind){
 $name='example-'.$kind;$GLOBALS['graphs'][$name]=array(B($kind,$tag));
 ok(!fv_r385_gallery_in_blocks($name),$kind.' not an executable shortcode');
}
$GLOBALS['graphs']['malformed']=array(array('blockName'=>'core/paragraph','innerHTML'=>array(),'innerBlocks'=>array()));
ok(!fv_r385_gallery_in_blocks('malformed'),'nonstring block HTML rejected');
$GLOBALS['graphs']['malformed-children']=array(array('blockName'=>'core/group','innerHTML'=>'','innerBlocks'=>'oops'));
ok(!fv_r385_gallery_in_blocks('malformed-children'),'malformed children rejected');
$GLOBALS['graphs']['node-limit']=array_fill(0,201,B('core/paragraph',''));
ok(!fv_r385_gallery_in_blocks('node-limit'),'200-node cap');
$GLOBALS['graphs']['big-fragment']=array(B('core/shortcode',$tag));
ok(!fv_r385_gallery_in_blocks(str_repeat('a',1048577)),'1 MiB cap');
for($i=30;$i<=39;$i++){$GLOBALS['refs'][$i]=WPBLOCK('chain-'.($i+1));$GLOBALS['graphs']['chain-'.$i]=array(REF($i));}
$GLOBALS['graphs']['chain-40']=array(B('core/shortcode',$tag));
ok(!fv_r385_gallery_in_blocks('chain-30'),'bounded depth cap');
$GLOBALS['shortcode_tags'][FV_R384_TAG]='foreign_handler';
ok(!fv_r385_gallery_owner(),'foreign owner rejected');fv_r385_prehead_assets();
ok(count($GLOBALS['styles'])===0,'foreign handler cannot enqueue');
$GLOBALS['shortcode_tags'][FV_R384_TAG]='fv_r384_shortcode';
$GLOBALS['env']=false;fv_r385_prehead_assets();ok(count($GLOBALS['styles'])===0,'production disabled');$GLOBALS['env']=true;
$GLOBALS['singular']=false;fv_r385_prehead_assets();ok(count($GLOBALS['styles'])===0,'archive/non-singular disabled');$GLOBALS['singular']=true;
$GLOBALS['records'][0]['evidence_url']='https://evil.invalid';fv_r385_prehead_assets();
ok(count($GLOBALS['styles'])===0,'tampered NASA records prevent load');$GLOBALS['records']=$GLOBALS['canonical'];
$GLOBALS['main']->post_content='parent-7';
$GLOBALS['graphs']['source-leaf']=array(B('core/shortcode',$tag));
fv_r385_prehead_assets();ok(count($GLOBALS['styles'])===1,'restored canonical record path enqueues');
// Delayed registration deliberately never binds a shortcode or bypasses R384 owner.
$loader=array_filter($GLOBALS['hooks'],fn($h)=>$h[0]==='plugins_loaded' && $h[1]===90);
ok(count($loader)===1,'guard one registration callback');
$fn=array_values($loader)[0][2];$fn();
ok(count(array_filter($GLOBALS['hooks'],fn($h)=>$h[0]==='wp_enqueue_scripts'&&$h[1]===2))===1,'prehead hook installed');
ok($GLOBALS['shortcode_tags'][FV_R384_TAG]==='fv_r384_shortcode','does not replace shortcode');
@mkdir(dirname(__DIR__).'/QA',0775,true);
file_put_contents(dirname(__DIR__).'/QA/php-results.json',json_encode(array('status'=>'PASS_LOCAL_PHP_STUBS_NOT_WORDPRESS','assertions'=>$checks,'source_sha256'=>hash_file('sha256',dirname(__DIR__).'/gallery-asset-guard.php')),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");
echo json_encode(array('status'=>'PASS_LOCAL_PHP_STUBS_NOT_WORDPRESS','assertions'=>$checks),JSON_PRETTY_PRINT)."\n";
