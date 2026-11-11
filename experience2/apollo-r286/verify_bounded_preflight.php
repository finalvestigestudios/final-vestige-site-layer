<?php
/** R286 reproducible WordPress-API simulation; NOT installed WordPress. */
define('ABSPATH', '/offline/');
$posts=[];$current=null;$reads=[];$enqueued=[];$synthetic=null;$shortcode_checks=0;$count=0;
function add_action($hook,$callback,$priority=10) {}
function add_shortcode($name,$callback) {}
function is_singular() { return true; }
function get_post($id=null) {
    global $posts,$current,$reads;
    if ($id===null) { return $current; }
    $reads[]=$id;
    return $posts[$id] ?? null;
}
function has_shortcode($content,$tag) {
    global $shortcode_checks;
    ++$shortcode_checks;
    return str_contains($content, '['.$tag.']');
}
function parse_blocks($content) {
    global $synthetic;
    if ($content==='<!-- wp:synthetic -->') { return $synthetic; }
    preg_match_all('/<!-- wp:block \{"ref":(\d+)\} \/-->/', $content,$m);
    return array_map(fn($id)=>['blockName'=>'core/block','attrs'=>['ref'=>$id],'innerBlocks'=>[]],$m[1]);
}
function plugins_url($path,$file) { return '/fixtures/'.$path; }
function wp_enqueue_style($handle,$url,$deps,$version) { global $enqueued; $enqueued[]=[$handle,$url,$version]; }
function wp_style_is($handle,$state) { return true; }
require getenv('APOLLO_SOURCE') ?: __DIR__.'/../apollo-r281/apollo-source-experience.php';
function blockpost($content,$type='wp_block',$status='publish') {
    return (object)['post_content'=>$content,'post_type'=>$type,'post_status'=>$status];
}
function check_case($label,$content,$records,$expected,$max_reads=null,$max_checks=null) {
    global $current,$posts,$reads,$enqueued,$shortcode_checks,$count;
    $current=blockpost($content,'page');$posts=$records;$reads=[];$enqueued=[];$shortcode_checks=0;
    fv_r281_preflight();
    $got=count($enqueued)>0;
    if ($got!==$expected) { throw new RuntimeException("$label: expected ".($expected?'enqueue':'no enqueue').", got ".($got?'enqueue':'no enqueue').", database reads=".count($reads)); }
    if ($max_reads!==null && count($reads)>$max_reads) { throw new RuntimeException("$label: unbounded get_post reads ".count($reads)); }
    if ($max_checks!==null && $shortcode_checks>$max_checks) { throw new RuntimeException("$label: unbounded block scans $shortcode_checks"); }
    ++$count;
    echo "$label PASS reads=".count($reads)." shortcode_checks=$shortcode_checks\n";
}
$short='[fv_apollo_source_experience]';
$ref=fn($id)=>'<!-- wp:block {"ref":'.$id.'} /-->';
// Ordinary nested source placement remains discoverable; no false negative.
check_case('approved_two_hop',$ref(1),[1=>blockpost($ref(2)),2=>blockpost($short)],true,2);
// A published pattern containing many siblings must not read the entire DB graph.
$synthetic=[];$records=[];$id=1;
for ($g=0;$g<10;$g++) {
    $inner=[];
    for($j=0;$j<10;$j++,$id++) {
        $inner[]=['blockName'=>'core/block','attrs'=>['ref'=>$id],'innerBlocks'=>[]];
        $records[$id]=blockpost($id===80?$short:'unrelated');
    }
    $synthetic[]=['blockName'=>'core/group','innerBlocks'=>$inner];
}
check_case('global_ref_fanout_budget','<!-- wp:synthetic -->',$records,false,32);
// Far below the read cap, the same pattern still preflights successfully.
$records[20]=blockpost($short);
check_case('bounded_nested_positive','<!-- wp:synthetic -->',$records,true,20);
// Each individual synced block is <250 KB, but the combined scan is >500 KB.
check_case('aggregate_content_budget',$ref(1),[
    1=>blockpost(str_repeat('x',240000).$ref(2)),
    2=>blockpost(str_repeat('x',240000).$ref(3)),
    3=>blockpost(str_repeat('x',100000).$short),
],false,3);
// Distinct nested groups may each have <128 nodes, but aggregate fan-out
// must still stop after 256 inspected parse nodes.
$synthetic=[];
for($g=0;$g<12;$g++) {
    $inner=[];
    for($j=0;$j<24;$j++){$inner[]=['blockName'=>'core/paragraph','innerBlocks'=>[], 'innerHTML'=>'irrelevant'];}
    $synthetic[]=['blockName'=>'core/group','innerBlocks'=>$inner];
}
check_case('global_node_budget','<!-- wp:synthetic -->',[],false,0,260);
// No visitor source is lost when head preflight declines large dynamic graphs.
$render=fv_r281_render();
if (!str_contains($render,'data-fv-evidence-status="editorial-review-pending"') ||
    !str_contains($render,'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/') ||
    !str_contains($render,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')) {
    throw new RuntimeException('Readable, free, source-linked fallback not preserved');
}
++$count;
echo "source_and_free_cta_unmodified PASS\n";
echo "R286 $count/$count PASS (WordPress API simulation only)\n";
