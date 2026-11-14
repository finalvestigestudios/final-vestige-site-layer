<?php
/** R357 WP API model: controlled mocks, NOT installed WordPress/Assembler. */
define('ABSPATH', true);
$hooks=[]; $shortcodes=[]; $styles=[]; $scripts=[]; $posts=[]; $parts=[]; $active=null; $singular=true; $calls=[];
function add_action($tag,$cb,$priority=10){$GLOBALS['hooks'][]=[$tag,$cb,$priority];}
function add_shortcode($tag,$cb){$GLOBALS['shortcodes'][$tag]=$cb;}
function is_singular(){return $GLOBALS['singular'];}
function get_post($id=null){return $id===null ? $GLOBALS['active'] : ($GLOBALS['posts'][$id]??null);}
function get_stylesheet(){return 'fv-child';}
function get_block_template($id,$type='wp_template'){ $GLOBALS['calls'][]=[$id,$type];return $GLOBALS['parts'][$id]??null;}
function has_shortcode($str,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $str);}
function parse_blocks($str){
    // Fixture parses references in content order; WP parse_blocks also returns children.
    preg_match_all('/<!--\s+wp:(block|template-part)\s+(\{[^>]*\})\s*\/-->/', $str, $matches,PREG_SET_ORDER);
    $out=[];foreach($matches as $m){$a=json_decode($m[2],true);if(is_array($a))$out[]=['blockName'=>'core/'.$m[1],'attrs'=>$a,'innerBlocks'=>[]];}
    return $out;
}
function plugins_url($path,$file){return 'https://staging.invalid/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$uri,$deps=[],$v=''){$GLOBALS['styles'][$handle]=$uri;}
function wp_enqueue_script($handle,$uri,$deps=[],$v='',$footer=false){$GLOBALS['scripts'][$handle]=[$uri,$footer];}
function check($ok,$msg){if(!$ok)throw new RuntimeException($msg);}
require dirname(__DIR__).'/template-asset-bridge.php';
check(isset($shortcodes['fv_apollo_experience_r357'])&&isset($shortcodes['fv_apollo_postfire_r357']),'r357 shortcodes registered');
$all=['fv-apollo-r339-chronology','fv-apollo-r340-gallery','fv-apollo-r345-evidence-plate','fv-apollo-r347-index','fv-apollo-r348-custody','fv-apollo-r355-postfire','fv-apollo-r356-print-proof'];
$note=['fv-apollo-r355-postfire','fv-apollo-r356-print-proof'];$checks=[];
function scenario($label,$content,$refs,$templates,$expected,$js,$singular=true){
 $GLOBALS['styles']=[];$GLOBALS['scripts']=[];$GLOBALS['posts']=$refs;$GLOBALS['parts']=$templates;$GLOBALS['calls']=[];
 $GLOBALS['active']=(object)['post_type'=>'page','post_content'=>$content];$GLOBALS['singular']=$singular;
 fv_apollo_r357_enqueue();
 $actual=array_keys($GLOBALS['styles']);sort($actual);sort($expected);
 check($actual===$expected,$label.' CSS '.json_encode($actual));
 check((bool)$GLOBALS['scripts']===$js,$label.' JS');
 foreach($GLOBALS['styles'] as $url)check(strpos($url,'staging.invalid')!==false,$label.' asset url');
 $GLOBALS['checks'][]=['name'=>$label,'css'=>count($actual),'javascript'=>count($GLOBALS['scripts']),'pass'=>true];
}
$b=fn($s)=>(object)['post_type'=>'wp_block','post_content'=>$s];
$t=fn($s)=>(object)['content'=>$s];
$block=fn($id)=>'<!-- wp:block {"ref":'.$id.'} /-->';
$part=fn($slug,$theme=null)=>'<!-- wp:template-part '.json_encode(array_filter(['slug'=>$slug,'theme'=>$theme],fn($x)=>$x!==null)).' /-->';
scenario('direct-note','[fv_apollo_postfire_r357]',[],[],$note,false);
scenario('direct-full','[fv_apollo_experience_r357]',[],[],$all,true);
scenario('both-modes','[fv_apollo_postfire_r357][fv_apollo_experience_r357]',[],[],$all,true);
scenario('reusable-note',$block(12),[12=>$b('[fv_apollo_postfire_r357]')],[],$note,false);
scenario('reusable-full',$block(12),[12=>$b('[fv_apollo_experience_r357]')],[],$all,true);
scenario('template-part-note',$part('apollo-note'),[],['fv-child//apollo-note'=>$t('[fv_apollo_postfire_r357]')],$note,false);
scenario('template-part-full',$part('apollo-experience'),[],['fv-child//apollo-experience'=>$t('[fv_apollo_experience_r357]')],$all,true);
scenario('nested-part-in-reusable',$block(11),[11=>$b($part('apollo-note'))],['fv-child//apollo-note'=>$t('[fv_apollo_postfire_r357]')],$note,false);
scenario('nested-block-in-part',$part('apollo-shell'),[11=>$b('[fv_apollo_experience_r357]')],['fv-child//apollo-shell'=>$t($block(11))],$all,true);
scenario('both-from-separate-parts',$part('apollo-note').$part('apollo-full'),[],['fv-child//apollo-note'=>$t('[fv_apollo_postfire_r357]'),'fv-child//apollo-full'=>$t('[fv_apollo_experience_r357]')],$all,true);
scenario('recursive-template-cycle',$part('loop'),[],['fv-child//loop'=>$t($part('loop'))],[],false);
scenario('recursive-cross-type-cycle',$block(11),[11=>$b($part('loop'))],['fv-child//loop'=>$t($block(11))],[],false);
scenario('same-theme-guard',$part('apollo-note','other-theme'),[],['other-theme//apollo-note'=>$t('[fv_apollo_postfire_r357]')],[],false);
scenario('path-traversal-guard',$part('../apollo-note'),[],['fv-child//../apollo-note'=>$t('[fv_apollo_postfire_r357]')],[],false);
scenario('bad-prefix','[fv_apollo_postfire_r357_fake]',[],[],[],false);
scenario('ordinary-page','No Apollo shortcode here',[],[],[],false);
scenario('absent-template',$part('not-saved'),[],[],[],false);
scenario('non-singular','[fv_apollo_experience_r357]',[],[],[],false,false);
scenario('oversize',str_repeat('z',500001).'[fv_apollo_experience_r357]',[],[],[],false);
$seen=[];$budget=null;$r=fv_apollo_r357_usage(str_repeat('z',500001),$seen,0,$budget);
check($r===[false,false,false],'oversize does not claim complete');
$html=fv_apollo_r357_full();$note_html=fv_apollo_r357_note();
check(substr_count($html,'data-fv-apollo-entry=')===13,'13 source records retained');
check(substr_count($html,'data-fv-r339-cta="editorial"')===1,'exactly one free editorial CTA');
check(substr_count($html,'data-fv-r355-reviewed-source')===1,'later NASA source present');
check(strpos($html,'102 deliberate ignitions')!==false,'postfire evidence');
check(!preg_match('/<img|<iframe|<script/i',$html),'no media/embed/tracking in output');
check(substr_count($note_html,'data-fv-apollo-entry')===0,'standalone note no Atlas');
check(substr_count($note_html,'data-fv-r339-cta="editorial"')===0,'no unrelated sales/CTA in note');
echo json_encode(['scope'=>'mock WordPress APIs only; no installed WP/Assembler acceptance','cases'=>$checks,'total'=>count($checks),'full_index_records'=>13,'free_editorial_ctas'=>1,'product_ctas'=>0,'pass'=>true],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
