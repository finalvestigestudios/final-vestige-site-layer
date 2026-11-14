<?php
/** Apollo R354: executable WordPress API contract STUB, not installed WordPress acceptance. */
define('ABSPATH', true);
$hooks=[]; $shortcodes=[]; $styles=[]; $scripts=[]; $posts=[]; $active=null;
function add_action($tag,$callback,$priority=10){$GLOBALS['hooks'][]=[$tag,$callback,$priority];}
function add_shortcode($tag,$callback){$GLOBALS['shortcodes'][$tag]=$callback;}
function is_singular(){return true;}
function get_post($id=null){return $id===null ? $GLOBALS['active'] : ($GLOBALS['posts'][$id] ?? null);}
function has_shortcode($c,$tag){return (bool)preg_match('/\['.preg_quote($tag,'/').'(?=[\s\]\/])/', $c);}
function parse_blocks($content){
    // Structured reusable-block fixtures only: no claim this substitutes for Gutenberg parsing.
    preg_match_all('/<!--\s+wp:block\s+\{"ref":(\d+)\}\s*\/-->/', $content, $m);
    return array_map(fn($id)=>['blockName'=>'core/block','attrs'=>['ref'=>(int)$id],'innerBlocks'=>[]],$m[1]);
}
function plugins_url($path,$file){return 'https://staging.example.invalid/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$url,$deps=[],$version=''){$GLOBALS['styles'][$handle]=[$url,$version];}
function wp_enqueue_script($handle,$url,$deps=[],$version='',$footer=false){$GLOBALS['scripts'][$handle]=[$url,$version,$footer];}
function check($condition,$message){if(!$condition)throw new RuntimeException($message);}
require dirname(__DIR__,2).'/apollo-r348/source-custody.php';
check(isset($shortcodes['fv_apollo_experience_r348']) && isset($shortcodes['fv_apollo_source_drawer_r348']), 'shortcode registration');
check(count($hooks)>=1,'enqueue hook registered');
$scenarios=[];
function run_case($label,$content,$refs,$expected_styles,$expected_script){
    $GLOBALS['posts']=$refs; $GLOBALS['active']=(object)['post_type'=>'post','post_content'=>$content];
    $GLOBALS['styles']=[];$GLOBALS['scripts']=[];
    // Only the registered root R348 hook exists before first render; dependency hooks may load afterward.
    fv_apollo_r348_enqueue();
    $got=array_keys($GLOBALS['styles']);sort($got);sort($expected_styles);
    check($got===$expected_styles,$label.' styles '.json_encode($got));
    check((bool)count($GLOBALS['scripts'])===$expected_script,$label.' scripts');
    $GLOBALS['scenarios'][]=['case'=>$label,'styles'=>$got,'scripts'=>array_keys($GLOBALS['scripts']),'pass'=>true];
}
$all=['fv-apollo-r339-chronology','fv-apollo-r340-gallery','fv-apollo-r345-evidence-plate','fv-apollo-r347-index','fv-apollo-r348-custody'];
run_case('direct-composite','[fv_apollo_experience_r348]',[],$all,true);
run_case('direct-drawer','[fv_apollo_source_drawer_r348]',[],['fv-apollo-r348-custody'],false);
run_case('reusable-composite','<!-- wp:block {"ref":52} /-->',[52=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r348]']],$all,true);
run_case('nested-reusable','<!-- wp:block {"ref":53} /-->',[53=>(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":54} /-->'],54=>(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r348]']],$all,true);
run_case('cyclic-no-shortcode','<!-- wp:block {"ref":62} /-->',[62=>(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":62} /-->']],[],false);
run_case('ordinary-post','<p>Nothing historical here.</p>',[],[],false);
// Exact source/claim validation and outlet escrow. No network or WP writes.
$html=fv_apollo_r348_experience_shortcode();
check(substr_count($html,'data-fv-apollo-entry=')===13,'13 evidence entries');
check(substr_count($html,'data-fv-r339-cta="editorial"')===1,'sole editorial CTA');
check(substr_count($html,'data-fv-apollo-source-index')===1,'one index');
check(substr_count($html,'data-fv-apollo-custody')===1,'one crosswalk');
check(substr_count($html,'data-fv-custody-approval="approved"')===8,'eight approved pages');
check(!preg_match('/<script|<img|<iframe/i',$html),'no inline scripts, images or iframes');
check(strpos($html,'No single ignition')!==false || strpos($html,'single ignition source')!==false,'certainty boundary preserved');
$urls=fv_apollo_r349_approved_sources();
check(count($urls)===8,'exact reviewed URL allowlist count');
foreach (fv_apollo_r347_records() as $entry)check(array_key_exists($entry['url'],$urls),'record approved link');
$negative=fv_apollo_r349_source_link('https://www.nasa.gov.attacker.test/fake','Fake claim');
check(strpos($negative,'<a ')===false && strpos($negative,'review')!==false,'domain spoof quarantined');
$serialized=['scope'=>'Real PHP/WordPress API contract STUB ONLY; no installed WordPress or live server', 'scenarios'=>$GLOBALS['scenarios'], 'evidence_entries'=>13,'distinct_approved_nasa_pages'=>8,'single_free_editorial_cta'=>true,'no_content_writes'=>true,'pass'=>true];
echo json_encode($serialized,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
