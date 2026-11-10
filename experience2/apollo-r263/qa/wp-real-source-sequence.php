<?php
/**
 * R263 offline WordPress API simulation with ACTUAL source-sealed R224 and R262
 * plugin PHP. Does NOT represent an installed WordPress/Assembler acceptance.
 * Invocation: php wp-real-source-sequence.php <R224 PHP> <R262 PHP> <scenario>
 * No production connection, filesystem changes or external HTTP calls.
 */
declare(strict_types=1);
define('ABSPATH', '/fv-r263-offline-harness/');
class WP_Post {
    public string $post_content;
    public string $post_type;
    public function __construct(string $content='', string $type='post') {
        $this->post_content=$content; $this->post_type=$type;
    }
}
$base=$argv[1] ?? ''; $overlay=$argv[2] ?? ''; $mode=$argv[3] ?? 'direct';
$validModes=['direct','synced','absent','admin','non_singular','late','duplicate',
    'corrupt_base_css','corrupt_base_fragment','corrupt_overlay_css','corrupt_overlay_js'];
if (!in_array($mode, $validModes, true) || !is_file($base) || !is_file($overlay)) exit(3);
$GLOBALS['scenario']=$mode;
$GLOBALS['fv_actions']=[]; $GLOBALS['fv_styles']=[]; $GLOBALS['fv_scripts']=[];
$GLOBALS['fv_shortcodes']=[]; $GLOBALS['fv_head_fired']=false;
function add_action($tag,$callback,$priority=10) {
    $GLOBALS['fv_actions'][]=['tag'=>$tag,'callback'=>$callback,'priority'=>$priority];
}
function add_shortcode($tag,$callback) {$GLOBALS['fv_shortcodes'][$tag]=$callback;}
function plugin_dir_path($file) {return dirname($file).'/';}
function plugins_url($path,$file) {return '/plugins/'.basename(dirname($file)).'/'.$path;}
function wp_enqueue_style($handle,$url='',$dependencies=[],$version='') {
    $GLOBALS['fv_styles'][$handle]=['status'=>'enqueued','url'=>$url,'deps'=>$dependencies,'version'=>$version];
}
function wp_enqueue_script($handle,$url='',$dependencies=[],$version='',$in_footer=false) {
    $GLOBALS['fv_scripts'][$handle]=['url'=>$url,'deps'=>$dependencies,'version'=>$version,'in_footer'=>$in_footer];
}
function wp_style_is($handle,$status) {return ($GLOBALS['fv_styles'][$handle]['status']??'absent')===$status;}
function did_action($tag) {return ($tag==='wp_head' && $GLOBALS['fv_head_fired']) ? 1 : 0;}
function is_admin() {return $GLOBALS['scenario']==='admin';}
function is_singular() {return $GLOBALS['scenario']!=='non_singular';}
function get_queried_object() {
    $mode=$GLOBALS['scenario'];
    if($mode==='absent' || $mode==='late') return new WP_Post('No Apollo shortcode here.');
    if($mode==='synced') return new WP_Post('<!-- wp:block {"ref":77} /-->');
    if($mode==='duplicate') return new WP_Post('[fv_ex2_apollo_atlas][fv_ex2_apollo_atlas]');
    return new WP_Post('[fv_ex2_apollo_atlas]');
}
function has_shortcode($content,$tag) {return is_string($content) && strpos($content,'['.$tag)!==false;}
function parse_blocks($content) {
    if(str_contains($content,'<!-- wp:block')) return [['blockName'=>'core/block','attrs'=>['ref'=>77],'innerBlocks'=>[]]];
    return [];
}
function get_post($ref) {return $ref===77 ? new WP_Post('[fv_ex2_apollo_atlas]','wp_block') : null;}
require $base;
require $overlay;
// Emulate WordPress action scheduling, not a separately fabricated base function.
usort($GLOBALS['fv_actions'], fn($a,$b)=> $a['priority'] <=> $b['priority']);
foreach ($GLOBALS['fv_actions'] as $action) {
    if ($action['tag']==='wp_enqueue_scripts') call_user_func($action['callback']);
}
if($mode==='late') $GLOBALS['fv_head_fired']=true;
$invoke=!in_array($mode, ['absent','admin','non_singular'], true);
$html=$invoke ? fv_ex2_r224_render() : '';
$second=$mode==='duplicate' ? fv_ex2_r224_render() : null;
$atlasPresent=str_contains($html,'id="fv-apollo-source-drawer"');
$result=[
  'mode'=>$mode,
  'render_invoked'=>$invoke,
  'hooks'=>array_map(fn($x)=>[$x['callback'],$x['priority']],$GLOBALS['fv_actions']),
  'styles'=>$GLOBALS['fv_styles'],
  'scripts'=>$GLOBALS['fv_scripts'],
  'base_assets_ok'=>fv_ex2_r224_assets_ok(),
  'overlay_assets_ok'=>fv_apollo_r262_assets_ok(),
  'atlas_present'=>$atlasPresent,
  'fallback'=>str_contains($html,'The Apollo evidence Atlas is unavailable'),
  'html_sha256'=>hash('sha256',$html),
  'source_drawer_records'=>substr_count($html,'fv-apollo-drawer-record'),
  'html'=>$mode==='direct' || $mode==='synced' ? $html : null,
  'second_fallback'=>$second===null?null:str_contains($second,'The Apollo evidence Atlas is unavailable'),
  'second_atlas'=>$second===null?null:str_contains($second,'id="fv-apollo-source-drawer"'),
];
echo json_encode($result,JSON_THROW_ON_ERROR|JSON_UNESCAPED_SLASHES);
