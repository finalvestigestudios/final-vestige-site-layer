<?php
/* WP API stubs only; must not be cited as installed WordPress acceptance. */
define('ABSPATH', __DIR__.'/');
$GLOBALS['posts']=array(); $GLOBALS['templates']=array(); $GLOBALS['parsed']=array();
$GLOBALS['queried']=10; $GLOBALS['admin']=false; $GLOBALS['singular']=true; $GLOBALS['theme']='assembler';
$GLOBALS['queued']=array(); $GLOBALS['actions']=array();
function has_shortcode($text,$name){return strpos($text,'['.$name.']')!==false;}
function parse_blocks($content){return $GLOBALS['parsed'][$content]??array();}
function get_post($id){return $GLOBALS['posts'][$id]??null;}
function get_stylesheet(){return $GLOBALS['theme'];}
function get_block_template($id,$type){return $GLOBALS['templates'][$type.':'.$id]??null;}
function get_queried_object_id(){return $GLOBALS['queried'];}
function is_singular(){return $GLOBALS['singular'];}
function is_admin(){return $GLOBALS['admin'];}
function wp_style_is($handle,$state){return isset($GLOBALS['queued'][$handle]);}
function wp_enqueue_style($handle,$url,$deps,$version){$GLOBALS['queued'][$handle]=array($url,$deps,$version);}
function plugins_url($path,$source){return 'https://staging.example.test/staged/'.$path;}
function add_action($hook,$fn,$priority){$GLOBALS['actions'][]=array($hook,$fn,$priority);}
require __DIR__.'/../staging-assets.php';
$n=0;
function check($ok,$reason){global $n;$n++;if(!$ok){fwrite(STDERR,"FAIL $n $reason\n");exit(1);}}
$gallery='[fv_apollo_source_gallery_r371]';
$GLOBALS['posts'][10]=(object)array('post_content'=>$gallery,'post_type'=>'page');
check(fv_apollo_r371_needs_assets(),'direct shortcode');
fv_apollo_r371_prehead();
check(count($GLOBALS['queued'])===1,'direct enqueue one CSS');
check(isset($GLOBALS['queued']['fv-apollo-r371-source-gallery']),'correct handle');
check($GLOBALS['queued']['fv-apollo-r371-source-gallery'][2]==='r371-stage-1','version');
fv_apollo_r371_prehead();check(count($GLOBALS['queued'])===1,'no duplicate enqueue');
check($GLOBALS['actions'][0]===array('wp_enqueue_scripts','fv_apollo_r371_prehead',1),'before-head priority');
$GLOBALS['queued']=array();$GLOBALS['posts'][10]->post_content='ordinary post';
check(!fv_apollo_r371_needs_assets(),'unrelated page negative');
fv_apollo_r371_prehead();check(count($GLOBALS['queued'])===0,'unrelated page no CSS');
$GLOBALS['admin']=true;$GLOBALS['posts'][10]->post_content=$gallery;
check(!fv_apollo_r371_needs_assets(),'admin excluded');$GLOBALS['admin']=false;
$GLOBALS['singular']=false;check(!fv_apollo_r371_needs_assets(),'non singular excluded');$GLOBALS['singular']=true;
$GLOBALS['posts'][10]->post_content='blockref';
$GLOBALS['parsed']['blockref']=array(array('blockName'=>'core/block','attrs'=>array('ref'=>22),'innerBlocks'=>array()));
$GLOBALS['posts'][22]=(object)array('post_type'=>'wp_block','post_content'=>$gallery);
check(fv_apollo_r371_needs_assets(),'nested reusable block');
$GLOBALS['posts'][22]=(object)array('post_type'=>'post','post_content'=>$gallery);
check(!fv_apollo_r371_needs_assets(),'reject non wp_block');
$GLOBALS['posts'][22]=(object)array('post_type'=>'wp_block','post_content'=>'cyclic');
$GLOBALS['parsed']['cyclic']=array(array('blockName'=>'core/block','attrs'=>array('ref'=>22),'innerBlocks'=>array()));
check(!fv_apollo_r371_needs_assets(),'cycle rejected');
$GLOBALS['posts'][10]->post_content='templatepart';
$GLOBALS['parsed']['templatepart']=array(array('blockName'=>'core/template-part','attrs'=>array('theme'=>'assembler','slug'=>'apollo'),'innerBlocks'=>array()));
$GLOBALS['templates']['wp_template_part:assembler//apollo']=(object)array('id'=>'assembler//apollo','content'=>$gallery);
check(fv_apollo_r371_needs_assets(),'same-theme template');
$GLOBALS['parsed']['templatepart'][0]['attrs']['theme']='foreign';
check(!fv_apollo_r371_needs_assets(),'foreign theme refused');
$GLOBALS['parsed']['templatepart'][0]['attrs']['theme']='assembler';
$GLOBALS['templates']['wp_template_part:assembler//apollo']->id='forged//apollo';
check(!fv_apollo_r371_needs_assets(),'wrong template identity refused');
$GLOBALS['templates']['wp_template_part:assembler//apollo']->id='assembler//apollo';
$GLOBALS['posts'][10]->post_content='blank';
$GLOBALS['_wp_current_template_id']='assembler//single';
$GLOBALS['templates']['wp_template:assembler//single']=(object)array('id'=>'assembler//single','content'=>$gallery);
check(fv_apollo_r371_needs_assets(),'resolved template accepted');
$GLOBALS['_wp_current_template_id']='foreign//single';
check(!fv_apollo_r371_needs_assets(),'foreign resolved template refused');
$GLOBALS['_wp_current_template_id']='assembler//single';
$GLOBALS['templates']['wp_template:assembler//single']->id='spoof//single';
check(!fv_apollo_r371_needs_assets(),'stale resolved template rejected');
$GLOBALS['templates']['wp_template:assembler//single']->id='assembler//single';
$GLOBALS['_wp_current_template_id']=null;
$GLOBALS['posts'][10]->post_content=str_repeat('x',250001);
check(!fv_apollo_r371_needs_assets(),'oversized content rejected');
$GLOBALS['posts'][10]->post_content='blank';
$GLOBALS['_wp_current_template_id']=null;
$GLOBALS['parsed']['inner']=array(array('blockName'=>'core/group','attrs'=>array(),'innerHTML'=>'','innerBlocks'=>array(array('blockName'=>'core/shortcode','innerHTML'=>$gallery))));
$GLOBALS['posts'][10]->post_content='inner';
check(fv_apollo_r371_needs_assets(),'nested inner block accepted');
echo json_encode(['status'=>'PASS','assertions'=>$n,'scope'=>'WordPress API STUBS, not installed WordPress'],JSON_PRETTY_PRINT)."\n";
