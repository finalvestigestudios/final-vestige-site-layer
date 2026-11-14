<?php
/** WordPress API stub integration regression, NOT installed WordPress. */
define('ABSPATH','/srv/wp/'); define('WPINC','wp-includes');
$GLOBALS['hooks']=[]; $GLOBALS['filters']=[]; $GLOBALS['shortcodes']=[];
$GLOBALS['styles']=[]; $GLOBALS['scripts']=[]; $GLOBALS['posts']=[];
$GLOBALS['parts']=[]; $GLOBALS['templates']=[]; $GLOBALS['calls']=[]; $GLOBALS['checks']=[];
$GLOBALS['singular']=true; $GLOBALS['block_theme']=true; $GLOBALS['theme']='fv-child';
function add_action($tag,$cb,$priority=10){$GLOBALS['hooks'][]=[$tag,$cb,$priority];}
function add_filter($tag,$cb,$priority=10,$args=1){$GLOBALS['filters'][]=[$tag,$cb,$priority];}
function add_shortcode($tag,$cb){$GLOBALS['shortcodes'][$tag]=$cb;}
function is_singular(){return $GLOBALS['singular'];}
function wp_is_block_theme(){return $GLOBALS['block_theme'];}
function get_post($id=null){return $id===null?($GLOBALS['active']??null):($GLOBALS['posts'][$id]??null);}
function get_stylesheet(){return $GLOBALS['theme'];}
function get_page_template_slug($post=null){return $GLOBALS['assigned']??'';}
function get_block_template($id,$type='wp_template'){$GLOBALS['calls'][]=[$id,$type];return ($type==='wp_template'?$GLOBALS['templates']:$GLOBALS['parts'])[$id]??null;}
function has_shortcode($str,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $str);}
function parse_blocks($str){preg_match_all('/<!--\s+wp:(block|template-part)\s+(\{[^>]*\})\s*\/-->/', $str,$ms,PREG_SET_ORDER);$out=[];foreach($ms as $m){$a=json_decode($m[2],true);if(is_array($a))$out[]=['blockName'=>'core/'.$m[1],'attrs'=>$a,'innerBlocks'=>[]];}return $out;}
function plugins_url($path,$file){return 'https://staging.invalid/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($h,$u,$d=[],$v=''){$GLOBALS['styles'][$h]=$u;}
function wp_enqueue_script($h,$u,$d=[],$v='',$footer=false){$GLOBALS['scripts'][$h]=[$u,$footer];}
function assert_ok($ok,$desc){if(!$ok)throw new RuntimeException($desc);}
require dirname(__DIR__).'/resolved-block-template-prehead.php';
$full=['fv-apollo-r339-chronology','fv-apollo-r340-gallery','fv-apollo-r345-evidence-plate','fv-apollo-r347-index','fv-apollo-r348-custody','fv-apollo-r355-postfire','fv-apollo-r356-print-proof'];
$note=['fv-apollo-r355-postfire','fv-apollo-r356-print-proof'];
$block=fn($n)=>'<!-- wp:block {"ref":'.$n.'} /-->';
$part=fn($s,$th=null)=>'<!-- wp:template-part {"slug":"'.$s.'"'.($th!==null?',"theme":"'.$th.'"':'').'} /-->';
function trial($name,$slug,$content,$expected=[],$script=false,$opts[]){
 $GLOBALS['styles']=[];$GLOBALS['scripts']=[];$GLOBALS['calls']=[];
 $GLOBALS['theme']=$opts['theme']??'fv-child';$GLOBALS['singular']=$opts['singular']??true;
 $GLOBALS['block_theme']=$opts['block_theme']??true;
 $GLOBALS['assigned']='';$GLOBALS['active']=(object)['ID'=>101,'post_content'=>'No shortcode here','post_type'=>'page'];
 $GLOBALS['parts']=$opts['parts']??[];$GLOBALS['posts']=$opts['posts']??[];
 $id=$opts['id']??($GLOBALS['theme'].'//'.$slug);$actual=$opts['actual']??$content;
 $GLOBALS['_wp_current_template_id']=$id;
 $GLOBALS['_wp_current_template_content']=$actual;
 $GLOBALS['templates']=[];
 if(!($opts['missing']??false)){
  $record=(object)['id'=>$id,'theme'=>$GLOBALS['theme'],'slug'=>$slug,'content'=>$content];
  foreach(($opts['record_changes']??[]) as $k=>$v){$record->$k=$v;}
  $GLOBALS['templates'][$id]=$record;
 }
 $path=$opts['path']??'/srv/wp/wp-includes/template-canvas.php';
 $returned=fv_apollo_r359_capture_template($path);
 assert_ok($returned===$path,$name.' template_include modified');
 if(isset($opts['postcapture_content']))$GLOBALS['_wp_current_template_content']=$opts['postcapture_content'];
 if(isset($opts['postcapture_id']))$GLOBALS['_wp_current_template_id']=$opts['postcapture_id'];
 if(isset($opts['postcapture_theme']))$GLOBALS['theme']=$opts['postcapture_theme'];
 fv_apollo_r359_enqueue();
 $styles=array_keys($GLOBALS['styles']);sort($styles);sort($expected);
 assert_ok($styles===$expected,$name.' styles '.json_encode($styles).' expected '.json_encode($expected));
 assert_ok((bool)$GLOBALS['scripts']===$script,$name.' scripts mismatch');
 assert_ok(count($GLOBALS['scripts'])<=1,$name.' script duplication');
 $GLOBALS['checks'][]=['case'=>$name,'styles'=>count($styles),'js'=>count($GLOBALS['scripts']),'result'=>'PASS'];
}
trial('default-page-full','page','[fv_apollo_experience_r357]',$full,true);
trial('default-page-note','page','[fv_apollo_postfire_r357]',$note,false);
trial('single-post-full','single','[fv_apollo_experience_r357]',$full,true);
trial('front-page-note','front-page','[fv_apollo_postfire_r357]',$note);
trial('index-fallback-full','index','[fv_apollo_experience_r357]',$full,true);
trial('page-id-specific','page-101','[fv_apollo_experience_r357]',$full,true);
trial('both-shortcodes','page','[fv_apollo_experience_r357][fv_apollo_postfire_r357]',$full,true);
trial('no-shortcode','page','Other template only');
trial('template-part-note','page',$part('source'),$note,false,['parts'=>['fv-child//source'=>(object)['content'=>'[fv_apollo_postfire_r357]']]]);
trial('reusable-full','single',$block(44),$full,true,['posts'=>[44=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r357]']]]);
trial('foreign-template-part','page',$part('source','other'),[],false,['parts'=>['other//source'=>(object)['content'=>'[fv_apollo_experience_r357]']]]);
trial('nested-recursive-part','page',$part('loop'),[],false,['parts'=>['fv-child//loop'=>(object)['content'=>$part('loop')]]]);
trial('missing-template-record','page','[fv_apollo_experience_r357]',[],false,['missing'=>true]);
trial('classic-theme','page','[fv_apollo_experience_r357]',[],false,['block_theme'=>false]);
trial('non-singular','page','[fv_apollo_experience_r357]',[],false,['singular'=>false]);
trial('non-canvas-php','page','[fv_apollo_experience_r357]',[],false,['path'=>'/srv/wp/wp-content/themes/fv-child/page.php']);
trial('spoofed-canvas-basename','page','[fv_apollo_experience_r357]',[],false,['path'=>'/evil/wp-includes/template-canvas.php']);
trial('bad-theme-name','page','[fv_apollo_experience_r357]',[],false,['theme'=>'../foreign']);
trial('foreign-id','page','[fv_apollo_experience_r357]',[],false,['id'=>'other//page']);
trial('invalid-id-traversal','page','[fv_apollo_experience_r357]',[],false,['id'=>'fv-child//../page']);
trial('record-id-drift','page','[fv_apollo_experience_r357]',[],false,['record_changes'=>['id'=>'fv-child//else']]);
trial('record-slug-drift','page','[fv_apollo_experience_r357]',[],false,['record_changes'=>['slug'=>'else']]);
trial('record-theme-drift','page','[fv_apollo_experience_r357]',[],false,['record_changes'=>['theme'=>'alien']]);
trial('stale-global-vs-record','page','[fv_apollo_experience_r357]',[],false,['actual'=>'[fv_apollo_postfire_r357]']);
trial('mutated-global-after-capture','page','[fv_apollo_experience_r357]',[],false,['postcapture_content'=>'[fv_apollo_postfire_r357]']);
trial('swapped-id-after-capture','page','[fv_apollo_experience_r357]',[],false,['postcapture_id'=>'fv-child//different']);
trial('swapped-theme-after-capture','page','[fv_apollo_experience_r357]',[],false,['postcapture_theme'=>'other']);
trial('oversized-template','page',str_repeat('x',500001).'[fv_apollo_experience_r357]');
trial('empty-template','page','');
trial('source-within-part','single',$part('outer'),$full,true,['parts'=>['fv-child//outer'=>(object)['content'=>$part('inner'),'id'=>'fv-child//outer'],'fv-child//inner'=>(object)['content'=>'[fv_apollo_experience_r357]']]]);
trial('same-handles-repeat','page','[fv_apollo_experience_r357]',$full,true);
$before=count($GLOBALS['styles']);fv_apollo_r359_enqueue();
assert_ok(count($GLOBALS['styles'])===$before,'duplicate enqueue handles');
assert_ok(count($GLOBALS['filters'])===1,'one template_include registration');
assert_ok(count($GLOBALS['hooks'])>=3,'R357 R358 R359 hooks preserved');
$h=$GLOBALS['shortcodes']['fv_apollo_experience_r357']();
assert_ok(substr_count($h,'data-fv-apollo-entry=')===13,'13 approved source entries unchanged');
assert_ok(substr_count($h,'data-fv-r339-cta="editorial"')===1,'one free editorial CTA unchanged');
assert_ok(!preg_match('/<img|<iframe|<script/i',$h),'no new media or tracking');
echo json_encode(['type'=>'WordPress API stub only; not installed WordPress','total'=>count($GLOBALS['checks']),'cases'=>$GLOBALS['checks'],'source_records'=>13,'editorial_cta'=>1,'paid_cta'=>0,'passed'=>true],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES),"\n";
