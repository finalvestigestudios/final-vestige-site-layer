<?php
/** R343: simulated WordPress preflight, no installed WP or live changes. */
declare(strict_types=1);
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
$fixture = ['top'=>'', 'blocks'=>[]];
$styles = [];
$singular = true;
function add_shortcode($name, $callback): void {}
function add_action($name, $callback, $priority=10): void {}
function is_singular(): bool { return $GLOBALS['singular']; }
function has_shortcode($content, $tag): bool { return preg_match('/\\['.preg_quote($tag,'/').'(?=[\\]\\s])/', $content)===1; }
function get_post($id=null) {
    $f=$GLOBALS['fixture'];
    if($id===null){return (object)['post_type'=>'post','post_content'=>$f['top']];}
    return isset($f['blocks'][(string)$id]) ? (object)$f['blocks'][(string)$id] : null;
}
function parse_blocks($content): array {
    preg_match_all('/<!-- wp:block \\{"ref":(\\d+)\\} \\/-->/', $content, $matches);
    $out=[];
    foreach($matches[1] as $id){$out[]=['blockName'=>'core/block','attrs'=>['ref'=>(int)$id],'innerBlocks'=>[]];}
    return $out;
}
function plugins_url($relative,$file): string { return '/wp/apollo-r339/'.$relative; }
function wp_enqueue_style($handle,$url,$dependencies,$version): void { $GLOBALS['styles'][$handle]=$url; }
require __DIR__ . '/../../apollo-r339/chronology-rail.php';
$ref=fn($id)=>'<!-- wp:block {"ref":'.$id.'} /-->';
$record=fn($text,$type='wp_block')=>['post_type'=>$type,'post_content'=>$text];
$cases=[
['direct shortcode','[fv_apollo_chronology_r339]',[],true,true],
['direct with attributes','[fv_apollo_chronology_r339 id="x"]',[],true,true],
['gallery only','[fv_apollo_gallery_r340]',[],true,false],
['composite only','[fv_apollo_experience_r340]',[],true,false],
['text without shortcode','ordinary prose',[],true,false],
['escaped plain text','[fv_apollo_chronology_r339ish]',[],true,false],
['reusable direct',$ref(11),[11=>$record('[fv_apollo_chronology_r339]')],true,true],
['two-level reference',$ref(12),[12=>$record($ref(11)),11=>$record('[fv_apollo_chronology_r339]')],true,true],
['missing block',$ref(99),[],true,false],
['wrong type',$ref(11),[11=>$record('[fv_apollo_chronology_r339]','post')],true,false],
['cycle',$ref(11),[11=>$record($ref(11))],true,false],
['non-singular','[fv_apollo_chronology_r339]',[],false,false],
['unrelated block',$ref(11),[11=>$record('[fv_apollo_experience_r340]')],true,false],
['repeated path',$ref(11).$ref(11),[11=>$record('[fv_apollo_chronology_r339]')],true,true],
];
$deep=[]; for($i=1;$i<=7;$i++){$deep[$i]=$record($ref($i+1));} $deep[8]=$record('[fv_apollo_chronology_r339]');
$cases[]=['bounded depth',$ref(1),$deep,true,false];
$large=str_repeat('x',500001).'[fv_apollo_chronology_r339]';
$cases[]=['bounded size',$large,[],true,false];
$passes=[];
foreach($cases as [$name,$top,$blocks,$is_singular,$expected]){
    $fixture=['top'=>$top,'blocks'=>$blocks];$singular=$is_singular;$styles=[];
    fv_apollo_r339_enqueue();
    $found=isset($styles['fv-apollo-r339-chronology']);
    if($found!==$expected){fwrite(STDERR,'FAIL '.$name.' '.json_encode($styles)."\n");exit(1);}
    if(count($styles)>1){fwrite(STDERR,'FAIL unexpected styles '.$name."\n");exit(1);}
    if($found && $styles['fv-apollo-r339-chronology']!=='/wp/apollo-r339/assets/chronology-rail.css'){
        fwrite(STDERR,'FAIL unexpected stylesheet path '.$name."\n");exit(1);
    }
    $passes[]=$name;
}
// The direct chronology still contains no merchant CTA, geospatial fields, or image embeds.
$html=fv_apollo_r339_shortcode();
if(substr_count($html, 'data-fv-r339-cta="editorial"')!==1 || substr_count($html,'data-fv-r339-source=')!==6 ||
   str_contains($html,'data-geo-pin') || str_contains($html,'data-affiliate') || str_contains($html,'<img')){
    fwrite(STDERR,'FAIL evidence/funnel contract');exit(1);
}
echo json_encode(['result'=>'PASS','scenarios'=>count($passes),'cases'=>$passes,'single_editorial_cta'=>true,'chronology_source_links'=>6],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
