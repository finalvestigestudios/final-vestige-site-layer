<?php
/** R355 isolated WordPress API-stub contract; never claim installed WP acceptance. */
define('ABSPATH', true);
$hooks=[]; $shortcodes=[]; $styles=[]; $scripts=[]; $posts=[]; $active=null;
function add_action($name,$callback,$priority=10){$GLOBALS['hooks'][]=[$name,$callback,$priority];}
function add_shortcode($tag,$callback){$GLOBALS['shortcodes'][$tag]=$callback;}
function is_singular(){return true;}
function get_post($id=null){return $id===null ? $GLOBALS['active'] : ($GLOBALS['posts'][$id] ?? null);}
function has_shortcode($content,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $content);}
function parse_blocks($content){preg_match_all('/<!--\s+wp:block\s+\{"ref":(\d+)\}\s*\/-->/', $content, $m);return array_map(fn($id)=>['blockName'=>'core/block','attrs'=>['ref'=>(int)$id],'innerBlocks'=>[]],$m[1]);}
function plugins_url($path,$file){return 'https://stage.invalid/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$url,$deps=[],$version=''){$GLOBALS['styles'][$handle]=$url;}
function wp_enqueue_script($handle,$url,$deps=[],$version='',$footer=false){$GLOBALS['scripts'][$handle]=[$url,$footer];}
function verify($ok,$msg){if(!$ok){throw new RuntimeException($msg);}}
require dirname(__DIR__).'/postfire-ledger.php';
verify(isset($shortcodes['fv_apollo_experience_r355'],$shortcodes['fv_apollo_postfire_r355']),'new shortcodes registered');
$checks=[];
function attempt($name,$content,$refs,$want_assets){
 $GLOBALS['active']=(object)['post_type'=>'post','post_content'=>$content];$GLOBALS['posts']=$refs;$GLOBALS['styles']=[];$GLOBALS['scripts']=[];
 fv_apollo_r355_enqueue();$got=count($GLOBALS['styles']);
 verify(($got>0)===$want_assets,$name.' asset mismatch');
 if($want_assets){verify(isset($GLOBALS['styles']['fv-apollo-r355-postfire']),'missing R355 CSS');verify(isset($GLOBALS['scripts']['fv-apollo-r347-index']),'missing index JS');}
 $GLOBALS['checks'][]=['case'=>$name,'stylesheet_count'=>$got,'pass'=>true];
}
attempt('direct-composite','[fv_apollo_experience_r355]',[],true);
attempt('standalone-postfire','[fv_apollo_postfire_r355]',[],true);
attempt('reusable','<!-- wp:block {"ref":101} /-->',[101=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r355]']],true);
attempt('nested-reusable','<!-- wp:block {"ref":102} /-->',[102=>(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":103} /-->'],103=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_postfire_r355]']],true);
attempt('cyclic-safe','<!-- wp:block {"ref":104} /-->',[104=>(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":104} /-->']],false);
attempt('ordinary-post','<p>Unrelated content</p>',[],false);
$r=fv_apollo_r355_record();verify(fv_apollo_r355_source_is_reviewed($r),'pinned reviewed row');
foreach(['count','date','source','boundary','document_class','scope'] as $field){$changed=$r;$changed[$field].=' unexpected';verify(!fv_apollo_r355_source_is_reviewed($changed),'tamper accepted: '.$field);}
$doc=fv_apollo_r355_experience_shortcode();
verify(substr_count($doc,'data-fv-apollo-entry=')===13,'curated index still 13');
verify(substr_count($doc,'data-fv-custody-approval="approved"')===8,'original 8 NASA pages');
verify(substr_count($doc,'data-fv-r339-cta="editorial"')===1,'exactly one free investigation CTA');
verify(substr_count($doc,'data-fv-r355-reviewed-source')===1,'one later NASA source');
verify(strpos($doc,'102 deliberate ignitions')!==false && strpos($doc,'February 14, 2018')!==false,'temporal separation');
verify(!preg_match('/<img\b|<iframe\b|<script\b/i',$doc),'no embedded media or tracking');
verify(substr_count($doc,'data-fv-apollo-postfire')===1,'one aftercare component');
$standalone=fv_apollo_r355_postfire_shortcode().fv_apollo_r355_postfire_shortcode();
preg_match_all('/id="(fv-apollo-r355-[^"]+)"/', $standalone,$ids);
verify(count($ids[1])===2 && count(array_unique($ids[1]))===2,'instance unique IDs');
echo json_encode(['scope'=>'PHP WordPress API stub, not installed WordPress','cases'=>$checks,'mutations_rejected'=>6,'nasa_new_source'=>'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/','index_references'=>13,'original_distinct_nasa_pages'=>8,'single_editorial_cta'=>true,'pass'=>true],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
