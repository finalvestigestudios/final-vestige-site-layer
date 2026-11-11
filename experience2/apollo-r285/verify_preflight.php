<?php
/** R285 WordPress-API simulation, deliberately NOT installed-WordPress acceptance. */
define('ABSPATH','/offline/');
$posts=[]; $current=null; $enqueued=[]; $reads=[];
function add_action($hook,$callback,$priority=10) {}
function add_shortcode($name,$callback) {}
function is_singular() { return true; }
function get_post($id=null) {
    global $posts,$current,$reads;
    if ($id===null) { return $current; }
    $reads[]=$id;
    return $posts[$id]??null;
}
function has_shortcode($content,$tag) { return strpos($content,'['.$tag.']')!==false; }
function parse_blocks($content) {
    preg_match_all('/<!-- wp:block \\{"ref":(\\d+)\\} \\/-->/', $content,$matches);
    return array_map(fn($id)=>['blockName'=>'core/block','attrs'=>['ref'=>$id], 'innerBlocks'=>[]],$matches[1]);
}
function plugins_url($path,$file) { return '/fixtures/'.$path; }
function wp_enqueue_style($handle,$url,$deps,$version) {
    global $enqueued; $enqueued[]=[$handle,$url,$version];
}
function wp_style_is($handle,$state) { return true; }
require __DIR__.'/../apollo-r281/apollo-source-experience.php';
function blockpost($text,$status='publish',$type='wp_block') {
    return (object)['post_content'=>$text,'post_status'=>$status,'post_type'=>$type];
}
function check_preflight($name,$content,$refs,$expected,$expected_reads=null) {
    global $posts,$current,$enqueued,$reads;
    $posts=$refs;$current=blockpost($content,'publish','page');$enqueued=[];$reads=[];
    fv_r281_preflight();
    if (count($enqueued)!==($expected?1:0)) { throw new Exception($name.' wrong enqueue count'); }
    if ($expected && $enqueued[0]!==['fv-apollo-evidence-r281', '/fixtures/assets/apollo-source-experience.css','r285']) {
        throw new Exception($name.' wrong stylesheet or version');
    }
    if ($expected_reads!==null && $reads!==$expected_reads) { throw new Exception($name.' incorrect reads'); }
    echo $name." PASS\n";
}
$short='[fv_apollo_source_experience]';
$ref=fn($id)=>'<!-- wp:block {"ref":'.$id.'} /-->';
check_preflight('direct',$short,[],true,[]);
check_preflight('unrelated','Plain text',[],false,[]);
check_preflight('one_hop',$ref(14),[14=>blockpost($short)],true,[14]);
check_preflight('two_hops',$ref(14),[14=>blockpost($ref(15)),15=>blockpost($short)],true,[14,15]);
check_preflight('cycle',$ref(14),[14=>blockpost($ref(15)),15=>blockpost($ref(14))],false,[14,15]);
check_preflight('duplicate',$ref(14).$ref(14),[14=>blockpost('nothing')],false,[14]);
check_preflight('missing',$ref(14),[],false,[14]);
check_preflight('draft',$ref(14),[14=>blockpost($short,'draft')],false,[14]);
check_preflight('wrong_type',$ref(14),[14=>blockpost($short,'publish','page')],false,[14]);
check_preflight('unrelated_block',$ref(14),[14=>blockpost('nothing')],false,[14]);
$deep=[];for($i=1;$i<=11;$i++){$deep[$i]=blockpost($i===11?$short:$ref($i+1));}
check_preflight('depth_limit',$ref(1),$deep,false);
check_preflight('content_limit',str_repeat('x',250001).$short,[],false,[]);
check_preflight('referenced_content_limit',$ref(14),[14=>blockpost(str_repeat('x',250001).$short)],false,[14]);
check_preflight('no_ref_leak',$ref(14),[14=>blockpost($short)],true,[14]);
