<?php
/** Real PHP executing WordPress API STUBS, NOT installed WordPress. */
define('ABSPATH', true);
$GLOBALS['hooks']=[];$GLOBALS['shortcodes']=[];$GLOBALS['styles']=[];$GLOBALS['scripts']=[];
$GLOBALS['posts']=[];$GLOBALS['parts']=[];$GLOBALS['templates']=[];$GLOBALS['active']=null;
$GLOBALS['singular']=true;$GLOBALS['assigned']='';$GLOBALS['calls']=[];$GLOBALS['checks']=[];
function add_action($tag,$cb,$priority=10){$GLOBALS['hooks'][]=[$tag,$cb,$priority];}
function add_shortcode($tag,$cb){$GLOBALS['shortcodes'][$tag]=$cb;}
function is_singular(){return $GLOBALS['singular'];}
function get_post($id=null){return $id===null ? $GLOBALS['active'] : ($GLOBALS['posts'][$id]??null);}
function get_stylesheet(){return $GLOBALS['theme']??'fv-child';}
function get_page_template_slug($post=null){return $GLOBALS['assigned'];}
function get_block_template($id,$type='wp_template'){$GLOBALS['calls'][]=[$id,$type];return ($type==='wp_template'?$GLOBALS['templates']:$GLOBALS['parts'])[$id]??null;}
function has_shortcode($str,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $str);}
function parse_blocks($str){
 preg_match_all('/<!--\s+wp:(block|template-part)\s+(\{[^>]*\})\s*\/-->/', $str, $ms,PREG_SET_ORDER);
 $out=[];foreach($ms as $m){$attrs=json_decode($m[2],true);if(is_array($attrs))$out[]=['blockName'=>'core/'.$m[1],'attrs'=>$attrs,'innerBlocks'=>[]];}return $out;
}
function plugins_url($path,$file){return 'https://staging.invalid/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$uri,$deps=[],$v=''){$GLOBALS['styles'][$handle]=$uri;}
function wp_enqueue_script($handle,$uri,$deps=[],$v='',$footer=false){$GLOBALS['scripts'][$handle]=[$uri,$footer];}
function check($ok,$msg){if(!$ok)throw new RuntimeException($msg);}
require dirname(__DIR__).'/explicit-template-prehead.php';
$full=['fv-apollo-r339-chronology','fv-apollo-r340-gallery','fv-apollo-r345-evidence-plate','fv-apollo-r347-index','fv-apollo-r348-custody','fv-apollo-r355-postfire','fv-apollo-r356-print-proof'];
$note=['fv-apollo-r355-postfire','fv-apollo-r356-print-proof'];
$block=fn($id)=>'<!-- wp:block {"ref":'.$id.'} /-->';
$part=fn($slug)=>'<!-- wp:template-part {"slug":"'.$slug.'"} /-->';
$b=fn($s)=>(object)['post_type'=>'wp_block','post_content'=>$s];
$t=fn($slug,$content,$overrides=[]) => (object)array_merge(['id'=>'fv-child//'.$slug,'slug'=>$slug,'theme'=>'fv-child','content'=>$content],$overrides);
function scenario($name,$assigned,$tpl,$expected,$js,$opts=[]){
 $GLOBALS['styles']=[];$GLOBALS['scripts']=[];$GLOBALS['calls']=[];
 $GLOBALS['theme']=$opts['theme']??'fv-child';$GLOBALS['assigned']=$assigned;
 $GLOBALS['singular']=$opts['singular']??true;$GLOBALS['parts']=$opts['parts']??[];
 $GLOBALS['posts']=$opts['posts']??[];$GLOBALS['templates']=[];
 if($tpl!==null){$id='fv-child//'.($opts['lookup_slug']??$assigned);$GLOBALS['templates'][$id]=$tpl;}
 $GLOBALS['active']=$opts['active']??(object)['ID'=>101,'post_content'=>'Post body only','post_type'=>'page'];
 fv_apollo_r358_enqueue();$actual=array_keys($GLOBALS['styles']);sort($actual);sort($expected);
 check($actual===$expected,$name.' styles mismatch '.json_encode($actual));
 check((bool)$GLOBALS['scripts']===$js,$name.' script mismatch');
 foreach($GLOBALS['calls'] as $call)check($call[1]==='wp_template'||$call[1]==='wp_template_part',$name.' template type');
 $GLOBALS['checks'][]=['name'=>$name,'styles'=>count($actual),'scripts'=>count($GLOBALS['scripts']),'passed'=>true];
}
scenario('exact-full','apollo-lesson',$t('apollo-lesson','[fv_apollo_experience_r357]'),$full,true);
scenario('exact-note','apollo-note',$t('apollo-note','[fv_apollo_postfire_r357]'),$note,false);
scenario('exact-both','apollo-both',$t('apollo-both','[fv_apollo_experience_r357][fv_apollo_postfire_r357]'),$full,true);
scenario('template-html-path','templates/apollo-note.html',$t('apollo-note','[fv_apollo_postfire_r357]'),$note,false,['lookup_slug'=>'apollo-note']);
scenario('part-only-in-assigned-template','apollo-shell',$t('apollo-shell',$part('apollo-note')),$note,false,['parts'=>['fv-child//apollo-note'=>(object)['content'=>'[fv_apollo_postfire_r357]']]]);
scenario('reusable-only-in-assigned-template','apollo-shell',$t('apollo-shell',$block(12)),$full,true,['posts'=>[12=>$b('[fv_apollo_experience_r357]')]]);
scenario('default-template','','',[],false);
scenario('literal-default','default',$t('default','[fv_apollo_experience_r357]'),[],false);
scenario('no-explicit-template','apollo-missing',null,[],false);
scenario('custom-php-file','templates/apollo.php',$t('apollo','[fv_apollo_experience_r357]'),[],false);
scenario('path-traversal','../apollo',$t('apollo','[fv_apollo_experience_r357]'),[],false);
scenario('foreign-theme','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]'),[],false,['theme'=>'unrelated']);
scenario('returned-id-drift','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]',['id'=>'fv-child//other']),[],false);
scenario('returned-slug-drift','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]',['slug'=>'other']),[],false);
scenario('returned-theme-drift','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]',['theme'=>'other']),[],false);
scenario('empty-no-shortcode','apollo-shell',$t('apollo-shell','Hello'),[],false);
scenario('non-singular','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]'),[],false,['singular'=>false]);
scenario('invalid-post-id','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]'),[],false,['active'=>(object)['ID'=>0,'post_content'=>'hi']]);
scenario('invalid-post-content','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]'),[],false,['active'=>(object)['ID'=>101]]);
scenario('recursive-part','apollo-shell',$t('apollo-shell',$part('loop')),[],false,['parts'=>['fv-child//loop'=>(object)['content'=>$part('loop')]]]);
scenario('missing-part','apollo-shell',$t('apollo-shell',$part('missing')),[],false);
scenario('foreign-part','apollo-shell',$t('apollo-shell','<!-- wp:template-part {"slug":"note","theme":"alien"} /-->'),[],false,['parts'=>['alien//note'=>(object)['content'=>'[fv_apollo_postfire_r357]']]]);
scenario('oversize-template','apollo-shell',$t('apollo-shell',str_repeat('a',500001).'[fv_apollo_experience_r357]'),[],false);
scenario('invalid-theme-slug','apollo-shell',$t('apollo-shell','[fv_apollo_experience_r357]'),[],false,['theme'=>'../wrong']);
check(isset($GLOBALS['shortcodes']['fv_apollo_experience_r357']),'R357 shortcode intact');
check(count($GLOBALS['hooks'])>=2,'both existing and new enqueue hooks registered');
$h=$GLOBALS['shortcodes']['fv_apollo_experience_r357']();
check(substr_count($h,'data-fv-apollo-entry=')===13,'13 original source records');
check(substr_count($h,'data-fv-r339-cta="editorial"')===1,'one free investigation CTA');
check(!preg_match('/<img|<iframe|<script/i',$h),'no added media or script');
$report=['scope'=>'PHP WordPress API stub, not installed WordPress or verified Assembler','cases'=>$GLOBALS['checks'],'total'=>count($GLOBALS['checks']),'source_records'=>13,'editorial_cta'=>1,'paid_cta'=>0,'pass'=>true];
echo json_encode($report,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
