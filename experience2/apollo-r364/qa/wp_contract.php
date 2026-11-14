<?php
/** WordPress API stub; NOT real WP installation or production acceptance. */
define('ABSPATH','/srv/wp/'); define('WPINC','wp-includes');
$GLOBALS['actions']=[]; $GLOBALS['filters']=[]; $GLOBALS['shortcodes']=[]; $GLOBALS['styles']=[];
$GLOBALS['scripts']=[]; $GLOBALS['posts']=[]; $GLOBALS['parts']=[]; $GLOBALS['templates']=[];
$GLOBALS['theme']='fv-child'; $GLOBALS['singular']=true; $GLOBALS['block_theme']=true;
$GLOBALS['checks']=[]; $GLOBALS['assigned']='';
function add_action($t,$c,$p=10){$GLOBALS['actions'][]=[$t,$c,$p];}
function add_filter($t,$c,$p=10,$a=1){$GLOBALS['filters'][]=[$t,$c,$p];}
function add_shortcode($t,$c){$GLOBALS['shortcodes'][$t]=$c;}
function is_singular(){return $GLOBALS['singular'];}
function wp_is_block_theme(){return $GLOBALS['block_theme'];}
function get_post($id=null){return $id===null?($GLOBALS['post']??null):($GLOBALS['posts'][$id]??null);}
function get_stylesheet(){return $GLOBALS['theme'];}
function get_page_template_slug($p=null){return $GLOBALS['assigned'];}
function get_block_template($id,$type='wp_template'){
    return ($type==='wp_template'?$GLOBALS['templates']:$GLOBALS['parts'])[$id]??null;
}
function has_shortcode($s,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $s);}
function parse_blocks($s){
    preg_match_all('/<!--\s+wp:(block|template-part)\s+(\{[^>]*\})\s*\/-->/', $s, $m, PREG_SET_ORDER);
    $out=[];foreach($m as $a){$v=json_decode($a[2],true);if(is_array($v))$out[]=['blockName'=>'core/'.$a[1],'attrs'=>$v,'innerBlocks'=>[]];}
    return $out;
}
function plugins_url($path,$file){return 'https://fixture.invalid/wp-content/plugins/apollo/'.$path;}
function wp_enqueue_style($handle,$url,$deps=[],$version=''){$GLOBALS['styles'][$handle]=$url;}
function wp_enqueue_script($handle,$url,$deps=[],$version='',$footer=false){$GLOBALS['scripts'][$handle]=$url;}
function ok($val,$reason){if(!$val){fwrite(STDERR,"FAILED: ".$reason."\n");exit(2);}}
require dirname(__DIR__).'/custody-asset-bridge.php';
require dirname(__DIR__, 2).'/apollo-r359/resolved-block-template-prehead.php';
$direct='[fv_apollo_custody_guard_r363]'; $alias=$direct;
$part=fn($slug,$theme=null)=>'<!-- wp:template-part {"slug":"'.$slug.'"'.($theme?',"theme":"'.$theme.'"':'').'} /-->';
$block=fn($id)=>'<!-- wp:block {"ref":'.$id.'} /-->';
function trial($name,$content,$expected,$opts=[]){
    $GLOBALS['styles']=[];$GLOBALS['scripts']=[];
    $GLOBALS['singular']=$opts['singular']??true;$GLOBALS['block_theme']=$opts['block_theme']??true;
    $GLOBALS['theme']=$opts['theme']??'fv-child';$GLOBALS['assigned']=$opts['assigned']??'';
    $GLOBALS['post']=(object)['ID'=>101,'post_content'=>$content,'post_type'=>'page'];
    $GLOBALS['parts']=$opts['parts']??[]; $GLOBALS['posts']=$opts['posts']??[];
    $GLOBALS['templates']=$opts['templates']??[];
    $GLOBALS['fv_apollo_r359_snapshot']=null;
    unset($GLOBALS['_wp_current_template_id'],$GLOBALS['_wp_current_template_content']);
    if(isset($opts['resolved'])){
        $tpl=$opts['resolved'];$id=$tpl->id;
        $GLOBALS['templates'][$id]=$tpl;
        $GLOBALS['_wp_current_template_id']=$id;
        $GLOBALS['_wp_current_template_content']=$tpl->content;
        fv_apollo_r359_capture_template('/srv/wp/wp-includes/template-canvas.php');
        if(isset($opts['after_snapshot']))$GLOBALS['_wp_current_template_content']=$opts['after_snapshot'];
    }
    [$found,$status]=fv_apollo_r364_usage();
    fv_apollo_r364_enqueue();
    $styles=array_keys($GLOBALS['styles']);
    ok($found===$expected,$name.' detection: '.$status);
    ok(count($styles)===($expected?1:0),$name.' style count '.json_encode($styles));
    ok(!$styles || $styles[0]==='fv-apollo-r362-crosswalk',$name.' incorrect style');
    ok(!$GLOBALS['scripts'],$name.' unwanted script');
    if($expected){$count=count($GLOBALS['styles']);fv_apollo_r364_enqueue();ok(count($GLOBALS['styles'])===$count,$name.' duplicate handles');}
    $GLOBALS['checks'][]=['case'=>$name,'found'=>$found,'status'=>$status,'styles'=>count($styles),'pass'=>true];
}
$record=fn($id,$slug,$content)=>(object)['id'=>$id,'slug'=>$slug,'theme'=>'fv-child','content'=>$content];
trial('ordinary-direct-post',$direct,true);
trial('alias-direct-post',$alias,true);
trial('alias-with-attributes','[fv_apollo_custody_guard_r363 title="proof"]',true);
trial('bare-unrelated-post','Plain free investigation.',false);
trial('lookalike-tag','[fv_apollo_custody_guard_r363_extra]',false);
trial('non-singular',$direct,false,['singular'=>false]);
trial('reusable-block', $block(8),true,['posts'=>[8=>(object)['post_type'=>'wp_block','post_content'=>$direct]]]);
trial('reusable-not-approved',$block(8),false,['posts'=>[8=>(object)['post_type'=>'post','post_content'=>$direct]]]);
trial('reusable-missing',$block(8),false);
trial('nested-reusable-block',$block(8),true,['posts'=>[8=>(object)['post_type'=>'wp_block','post_content'=>$block(9)],9=>(object)['post_type'=>'wp_block','post_content'=>$alias]]]);
trial('reusable-recursive-cycle',$block(8),false,['posts'=>[8=>(object)['post_type'=>'wp_block','post_content'=>$block(8)]]]);
trial('part-same-theme',$part('evidence'),true,['parts'=>['fv-child//evidence'=>$record('fv-child//evidence','evidence',$alias)]]);
trial('part-cross-theme',$part('evidence','alien'),false,['parts'=>['alien//evidence'=>(object)['content'=>$direct]]]);
trial('part-traversal',$part('../evidence'),false);
trial('part-stale-identity',$part('evidence'),false,['parts'=>['fv-child//evidence'=>(object)['id'=>'wrong//evidence','slug'=>'evidence','theme'=>'fv-child','content'=>$direct]]]);
trial('part-nested-reusable',$part('evidence'),true,['parts'=>['fv-child//evidence'=>$record('fv-child//evidence','evidence',$block(8))], 'posts'=>[8=>(object)['post_type'=>'wp_block','post_content'=>$direct]]]);
trial('part-recursive-cycle',$part('evidence'),false,['parts'=>['fv-child//evidence'=>$record('fv-child//evidence','evidence',$part('evidence'))]]);
trial('assigned-template',$alias===null?'': 'No shortcodes',true,['assigned'=>'templates/special.html','templates'=>['fv-child//special'=>$record('fv-child//special','special',$alias)]]);
trial('assigned-foreign-template','Plain',false,['assigned'=>'templates/special.html','templates'=>['fv-child//special'=>(object)['id'=>'alien//special','theme'=>'fv-child','slug'=>'special','content'=>$direct]]]);
trial('assigned-unrecognized-slug','Plain',false,['assigned'=>'../special','templates'=>['fv-child//special'=>$record('fv-child//special','special',$direct)]]);
trial('default-resolved-template','Plain',true,['resolved'=>$record('fv-child//page','page',$direct)]);
trial('default-resolved-template-part','Plain',true,['resolved'=>$record('fv-child//single','single',$part('evidence')),'parts'=>['fv-child//evidence'=>$record('fv-child//evidence','evidence',$direct)]]);
trial('default-stale-after-capture','Plain',false,['resolved'=>$record('fv-child//page','page',$direct),'after_snapshot'=>'Plain'] );
trial('default-classic-theme','Plain',false,['resolved'=>$record('fv-child//page','page',$direct),'block_theme'=>false]);
trial('oversized-post-refuses',$direct.str_repeat('x',500001),false);
trial('oversized-nested-refuses',$block(8),false,['posts'=>[8=>(object)['post_type'=>'wp_block','post_content'=>$direct.str_repeat('X',500001)]]]);
trial('combined-valid-and-oversized-refuses',$direct.$block(8),false,['posts'=>[8=>(object)['post_type'=>'wp_block','post_content'=>str_repeat('X',500001)]]]);
trial('empty-post','',false);
$result=['kind'=>'WP_API_STUB_NOT_INSTALLED_WP','passed'=>true,'cases'=>count($GLOBALS['checks']),'detail'=>$GLOBALS['checks'],'media_rights_granted'=>0,'paid_ctas'=>0];
echo json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES),"\n";
