<?php
/** R356 WordPress API contract fixture: not an installed WordPress or Assembler acceptance test. */
define('ABSPATH', true);
$hooks=[]; $shortcodes=[]; $styles=[]; $scripts=[]; $posts=[]; $active=null; $singular=true;
function add_action($tag,$cb,$priority=10){$GLOBALS['hooks'][]=[$tag,$cb,$priority];}
function add_shortcode($tag,$cb){$GLOBALS['shortcodes'][$tag]=$cb;}
function is_singular(){return $GLOBALS['singular'];}
function get_post($id=null){return $id===null ? $GLOBALS['active'] : ($GLOBALS['posts'][$id]??null);}
function has_shortcode($str,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $str);}
function parse_blocks($str){
    preg_match_all('/<!--\s+wp:block\s+\{"ref":(\d+)\}\s*\/-->/', $str, $matches);
    return array_map(fn($id)=>['blockName'=>'core/block','attrs'=>['ref'=>(int)$id],'innerBlocks'=>[]],$matches[1]);
}
function plugins_url($path,$file){return 'https://staging.invalid/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$uri,$deps=[],$v=''){$GLOBALS['styles'][$handle]=$uri;}
function wp_enqueue_script($handle,$uri,$deps=[],$v='',$footer=false){$GLOBALS['scripts'][$handle]=[$uri,$footer];}
function check($ok,$msg){if(!$ok)throw new RuntimeException($msg);}
require dirname(__DIR__).'/asset-bridge.php';
check(isset($shortcodes['fv_apollo_experience_r356']) && isset($shortcodes['fv_apollo_postfire_r356']),'shortcodes registered');
$all=['fv-apollo-r339-chronology','fv-apollo-r340-gallery','fv-apollo-r345-evidence-plate','fv-apollo-r347-index','fv-apollo-r348-custody','fv-apollo-r355-postfire'];
$checks=[];
function scenario($name,$text,$refs,$expected,$js,$singular=true){
    $GLOBALS['styles']=[]; $GLOBALS['scripts']=[]; $GLOBALS['posts']=$refs; $GLOBALS['singular']=$singular;
    $GLOBALS['active']=(object)['post_type'=>'post','post_content'=>$text];
    fv_apollo_r356_enqueue();
    $actual=array_keys($GLOBALS['styles']);sort($actual);sort($expected);
    check($actual===$expected,$name.' CSS mismatch '.json_encode($actual));
    check((bool)count($GLOBALS['scripts'])===$js,$name.' JS mismatch');
    foreach($GLOBALS['styles'] as $path){check(strpos($path,'staging.invalid')!==false,$name.' path');}
    $GLOBALS['checks'][]=['case'=>$name,'styles'=>count($actual),'scripts'=>count($GLOBALS['scripts']),'pass'=>true];
}
scenario('standalone-note','[fv_apollo_postfire_r356]',[],['fv-apollo-r355-postfire'],false);
scenario('standalone-spaced','[fv_apollo_postfire_r356 /]',[],['fv-apollo-r355-postfire'],false);
scenario('full-composite','[fv_apollo_experience_r356]',[],$all,true);
scenario('both-composite-wins','[fv_apollo_postfire_r356][fv_apollo_experience_r356]',[],$all,true);
scenario('reusable-note','<!-- wp:block {"ref":17} /-->',[17=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_postfire_r356]']],['fv-apollo-r355-postfire'],false);
scenario('nested-composite','<!-- wp:block {"ref":17} /-->',[17=>(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":18} /-->'],18=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r356]']],$all,true);
scenario('cyclic-reusable','<!-- wp:block {"ref":17} /-->',[17=>(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":17} /-->']],[],false);
scenario('unrelated-post','<p>No shortcode</p>',[],[],false);
scenario('prefix-spoof','[fv_apollo_postfire_r356_fake]',[],[],false);
scenario('non-singular','[fv_apollo_experience_r356]',[],[],false,false);
scenario('oversized-content',str_repeat('x',500001).'[fv_apollo_experience_r356]',[],[],false);
$html=fv_apollo_r356_experience();
check(substr_count($html,'data-fv-apollo-entry=')===13,'unchanged 13 evidence entries');
check(substr_count($html,'data-fv-r339-cta="editorial"')===1,'unchanged sole editorial continuation');
check(substr_count($html,'data-fv-r355-reviewed-source')===1,'reviewed later source');
check(strpos($html,'102 deliberate ignitions')!==false,'post-Board evidence present');
check(!preg_match('/<img|<iframe|<script/i',$html),'no external media or script embedded');
$note=fv_apollo_r356_postfire();
check(strpos($note,'102 deliberate ignitions')!==false && strpos($note,'data-fv-apollo-entry')===false,'standalone note without Atlas');
check(substr_count($note,'data-fv-r339-cta="editorial"')===0,'no unrelated CTA on note');
$result=['scope'=>'WordPress API stub only; no installed WordPress, Assembler or live pages', 'cases'=>$checks,
    'standalone_css_assets'=>1,'standalone_js_assets'=>0,'full_css_assets'=>6,'full_js_assets'=>1,
    'composite_entries'=>13,'composite_editorial_ctas'=>1,'embedded_media'=>0,'pass'=>true];
echo json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
