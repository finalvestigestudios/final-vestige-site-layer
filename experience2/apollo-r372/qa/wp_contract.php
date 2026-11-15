<?php
/* WordPress lifecycle API STUBS ONLY. Not WordPress installed acceptance. */
define('ABSPATH',__DIR__.'/');
$A=array('admin'=>false,'singular'=>true,'id'=>2,'style'=>'assembler','posts'=>array(), 'templates'=>array(),'blocks'=>array(),'styles'=>array(),'actions'=>array());
function is_admin(){global $A;return $A['admin'];}
function is_singular(){global $A;return $A['singular'];}
function get_queried_object_id(){global $A;return $A['id'];}
function get_post($id){global $A;return $A['posts'][$id]??null;}
function get_stylesheet(){global $A;return $A['style'];}
function get_block_template($id,$type){global $A;return $A['templates'][$type.'|'.$id]??null;}
function parse_blocks($text){global $A;return $A['blocks'][$text]??array();}
function has_shortcode($content,$name){return strpos($content,'['.$name.']')!==false;}
function wp_enqueue_style($handle,$url,$deps,$version){global $A;$A['styles'][]=compact('handle','url','deps','version');}
function plugins_url($path,$file){return 'https://staging.invalid/wp-content/plugins/apollo-r372/'.$path;}
function wp_style_is($handle,$kind){global $A;return in_array($handle,array_column($A['styles'],'handle'),true);}
function add_action($hook,$fn,$priority){global $A;$A['actions'][]=array($hook,$fn,$priority);}
require __DIR__.'/../staging-assets.php';
$checks=0;
function ck($good,$label){global $checks;++$checks;if(!$good){fwrite(STDERR,"FAIL #$checks $label\n");exit(1);}}
$short='[fv_apollo_source_path_r372]';
$A['posts'][2]=(object)array('post_content'=>'unrelated');
ck(!fv_apollo_r372_needs_assets(),'unrelated article no assets');
$A['posts'][2]=(object)array('post_content'=>$short);
ck(fv_apollo_r372_needs_assets(),'direct singular shortcode');
fv_apollo_r372_prehead();fv_apollo_r372_prehead();
ck(count($A['styles'])===1,'one style despite repeated execution');
ck($A['styles'][0]['handle']==='fv-apollo-r372-evidence-path','scoped handle');
ck($A['styles'][0]['deps']===array(),'no new dependencies');
ck($A['actions'][0]===array('wp_enqueue_scripts','fv_apollo_r372_prehead',1),'before-head hook priority');
$A['posts'][2]=(object)array('post_content'=>'shared');
$A['blocks']['shared']=array(array('blockName'=>'core/block','attrs'=>array('ref'=>14),'innerHTML'=>''));
$A['posts'][14]=(object)array('post_type'=>'wp_block','post_content'=>$short);
ck(fv_apollo_r372_needs_assets(),'nested reusable block');
$A['posts'][14]=(object)array('post_type'=>'post','post_content'=>$short);
ck(!fv_apollo_r372_needs_assets(),'reject non wp_block ref');
$A['posts'][14]=(object)array('post_type'=>'wp_block','post_content'=>'shared');
ck(!fv_apollo_r372_needs_assets(),'cycle fail safe');
$A['posts'][2]=(object)array('post_content'=>'part');
$A['blocks']['part']=array(array('blockName'=>'core/template-part','attrs'=>array('slug'=>'footer','theme'=>'assembler'),'innerHTML'=>''));
$A['templates']['wp_template_part|assembler//footer']=(object)array('id'=>'assembler//footer','content'=>$short);
ck(fv_apollo_r372_needs_assets(),'matching theme part');
$A['blocks']['part'][0]['attrs']['theme']='other';
ck(!fv_apollo_r372_needs_assets(),'reject foreign theme part');
$A['blocks']['part'][0]['attrs']['theme']='assembler';
$A['templates']['wp_template_part|assembler//footer']->id='wrong';
ck(!fv_apollo_r372_needs_assets(),'reject spoofed part identity');
$A['posts'][2]=(object)array('post_content'=>'not content');
$GLOBALS['_wp_current_template_id']='assembler//single';
$A['templates']['wp_template|assembler//single']=(object)array('id'=>'assembler//single','content'=>$short);
ck(fv_apollo_r372_needs_assets(),'actual resolved block template');
$GLOBALS['_wp_current_template_id']='foreign//single';
ck(!fv_apollo_r372_needs_assets(),'reject foreign resolved template');
$GLOBALS['_wp_current_template_id']='assembler//single';
$A['templates']['wp_template|assembler//single']->id='assembler//stale';
ck(!fv_apollo_r372_needs_assets(),'reject stale template identity');
unset($GLOBALS['_wp_current_template_id']);
$A['posts'][2]=(object)array('post_content'=>str_repeat('x',250001).$short);
ck(!fv_apollo_r372_needs_assets(),'oversize content fail closed');
$A['posts'][2]=(object)array('post_content'=>$short);
$A['admin']=true;ck(!fv_apollo_r372_needs_assets(),'admin excluded');$A['admin']=false;
$A['singular']=false;ck(!fv_apollo_r372_needs_assets(),'archives excluded');$A['singular']=true;
$A['blocks']['inner']=array(array('blockName'=>'core/group','innerHTML'=>'', 'innerBlocks'=>array(array('blockName'=>'core/shortcode','innerHTML'=>$short))));
$A['posts'][2]=(object)array('post_content'=>'inner');
ck(fv_apollo_r372_needs_assets(),'nested innerBlocks shortcode');
$A['blocks']['inner']=array(array('blockName'=>'core/group','innerHTML'=>'', 'innerBlocks'=>array(array('blockName'=>'core/block','attrs'=>array('ref'=>17),'innerHTML'=>''))));
$A['posts'][17]=(object)array('post_type'=>'wp_block','post_content'=>$short);
ck(fv_apollo_r372_needs_assets(),'nested innerBlocks reusable');
$A['blocks']['inner']=array(array('blockName'=>'core/group','innerHTML'=>'', 'innerBlocks'=>array(array('blockName'=>'core/template-part','attrs'=>array('slug'=>'sidebar'),'innerHTML'=>''))));
$A['templates']['wp_template_part|assembler//sidebar']=(object)array('id'=>'assembler//sidebar','content'=>$short);
ck(fv_apollo_r372_needs_assets(),'nested innerBlocks template part');
echo "R372 WordPress API-STUB PASS $checks/$checks assertions (NOT installed WP)\n";
