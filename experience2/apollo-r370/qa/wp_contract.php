<?php
/** WordPress API-stub logic tests. NOT installed-WP or production acceptance. */
error_reporting(E_ALL);
define('ABSPATH','/isolated-stub/');
$GLOBALS['stub']=['post'=>null,'queried'=>7,'singular'=>true,'admin'=>false,'blocks'=>[], 'templates'=>[], 'enqueued'=>[], 'actions'=>[]];
function is_admin(){return $GLOBALS['stub']['admin'];}
function is_singular(){return $GLOBALS['stub']['singular'];}
function get_queried_object_id(){return $GLOBALS['stub']['queried'];}
function get_post($id){return $id===$GLOBALS['stub']['queried']?$GLOBALS['stub']['post']:($GLOBALS['stub']['blocks'][$id]??null);}
function get_stylesheet(){return 'assembler';}
function get_block_template($id,$type){return $GLOBALS['stub']['templates'][$type.':'.$id]??null;}
function parse_blocks($text){return json_decode($text,true)??[];}
function has_shortcode($text,$tag){return str_contains($text,'['.$tag.']') || str_contains($text,'['.$tag.' ');}
function add_action($h,$cb,$priority){$GLOBALS['stub']['actions'][]=[$h,$cb,$priority];}
function wp_style_is($handle,$state){return array_key_exists($handle,$GLOBALS['stub']['enqueued']);}
function plugins_url($path,$file){return 'https://staging.invalid/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$url,$deps,$version){$GLOBALS['stub']['enqueued'][$handle]=compact('url','deps','version');}
require dirname(__DIR__).'/prehead-assets.php';
$assertions=0;
function check($value,$message){global $assertions;$assertions++;if(!$value){throw new RuntimeException('FAIL: '.$message);}}
function reset_stage($content){$GLOBALS['stub']['post']=(object)['post_content'=>$content,'post_type'=>'page'];$GLOBALS['stub']['blocks']=[];$GLOBALS['stub']['templates']=[];$GLOBALS['stub']['enqueued']=[];unset($GLOBALS['_wp_current_template_id']);$GLOBALS['stub']['singular']=true;$GLOBALS['stub']['admin']=false;}
function block($name,$attrs=[],$inner=[]){return ['blockName'=>$name,'attrs'=>$attrs,'innerHTML'=>'','innerBlocks'=>$inner];}
$short='[fv_apollo_educator_bridge_r369]';
reset_stage('simple content '.$short);
check(fv_apollo_r370_needs_assets(),'direct shortcode detected');
check(count($GLOBALS['stub']['actions'])===1,'one hook registered');
check($GLOBALS['stub']['actions'][0]===['wp_enqueue_scripts','fv_apollo_r370_prehead',1],'pre-head priority');
fv_apollo_r370_prehead();
check(count($GLOBALS['stub']['enqueued'])===4,'all four styles enqueued');
$expect=['fv-apollo-r365-chronology','fv-apollo-r367-sequence','fv-apollo-r368-reflow','fv-apollo-r369-educator-bridge'];
check(array_keys($GLOBALS['stub']['enqueued'])===$expect,'CSS order');
check($GLOBALS['stub']['enqueued'][$expect[3]]['deps']===[$expect[2]],'correct dependency R369');
check($GLOBALS['stub']['enqueued'][$expect[2]]['deps']===[$expect[1]],'correct dependency R368');
check($GLOBALS['stub']['enqueued'][$expect[1]]['deps']===[$expect[0]],'correct dependency R367');
check(str_contains($GLOBALS['stub']['enqueued'][$expect[3]]['url'],'evidence-bridge.css'),'resolved R369 URL');
fv_apollo_r370_prehead();check(count($GLOBALS['stub']['enqueued'])===4,'idempotent');
reset_stage('no shortcode');check(!fv_apollo_r370_needs_assets(),'unrelated no styles');fv_apollo_r370_prehead();check(count($GLOBALS['stub']['enqueued'])===0,'no global load');
$GLOBALS['stub']['admin']=true;check(!fv_apollo_r370_needs_assets(),'admin suppressed');
$GLOBALS['stub']['admin']=false;$GLOBALS['stub']['singular']=false;check(!fv_apollo_r370_needs_assets(),'non singular suppressed');
$GLOBALS['stub']['singular']=true;
reset_stage(json_encode([block('core/block',['ref'=>42])]));
$GLOBALS['stub']['blocks'][42]=(object)['post_type'=>'wp_block','post_content'=>$short];
check(fv_apollo_r370_needs_assets(),'reusable block detected');
$GLOBALS['stub']['blocks'][42]->post_type='post';check(!fv_apollo_r370_needs_assets(),'wrong type denied');
$GLOBALS['stub']['blocks'][42]=(object)['post_type'=>'wp_block','post_content'=>json_encode([block('core/block',['ref'=>42])])];
check(!fv_apollo_r370_needs_assets(),'cyclic reusable block denied');
reset_stage(json_encode([block('core/template-part',['slug'=>'resources'])]));
$GLOBALS['stub']['templates']['wp_template_part:assembler//resources']=(object)['id'=>'assembler//resources','content'=>$short];
check(fv_apollo_r370_needs_assets(),'own-theme template part');
$GLOBALS['stub']['templates']['wp_template_part:assembler//resources']->id='other//resources';
check(!fv_apollo_r370_needs_assets(),'stale template identity denied');
reset_stage(json_encode([block('core/template-part',['slug'=>'resources','theme'=>'foreign'])]));
$GLOBALS['stub']['templates']['wp_template_part:foreign//resources']=(object)['id'=>'foreign//resources','content'=>$short];
check(!fv_apollo_r370_needs_assets(),'foreign theme denied');
reset_stage(json_encode([block('core/template-part',['slug'=>'../../secret'])]));
check(!fv_apollo_r370_needs_assets(),'malformed template slug denied');
reset_stage(json_encode([block('core/paragraph',[],[block('core/shortcode')])]));
check(!fv_apollo_r370_needs_assets(),'empty nested block denied');
reset_stage('page without Apollo shortcode');
$GLOBALS['_wp_current_template_id']='assembler//single';
$GLOBALS['stub']['templates']['wp_template:assembler//single']=(object)['id'=>'assembler//single','content'=>$short];
check(fv_apollo_r370_needs_assets(),'actual resolved template recognized');
$GLOBALS['stub']['templates']['wp_template:assembler//single']->id='assembler//page';
check(!fv_apollo_r370_needs_assets(),'stale resolved template denied');
$GLOBALS['_wp_current_template_id']='foreign//single';check(!fv_apollo_r370_needs_assets(),'foreign resolved template denied');
$GLOBALS['_wp_current_template_id']='assembler//single';unset($GLOBALS['stub']['templates']['wp_template:assembler//single']);
check(!fv_apollo_r370_needs_assets(),'missing resolved template denied');
reset_stage(str_repeat('x',250001).$short);check(!fv_apollo_r370_needs_assets(),'oversized content refused');
reset_stage(json_encode([block('core/group',[],[block('core/paragraph')])]));
check(!fv_apollo_r370_needs_assets(),'no match complex blocks');
$seen=[]; $budget=128;check(!fv_apollo_r370_scan('[]', $seen, 8, $budget),'depth cap');
print json_encode(['passed'=>true,'assertions'=>$assertions,'scope'=>'WP API stub; not installed WordPress','styles'=>$expect],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES).'\n';
