<?php
/** Read-only WordPress-function contract harness, NOT real WordPress. */
error_reporting(E_ALL);
define('ABSPATH', '/mock-wordpress/');
class WP_Post {
    public $ID; public $post_type; public $post_content;
    public function __construct($id, $type, $content) {
        $this->ID = $id; $this->post_type = $type; $this->post_content = $content;
    }
}
$GLOBALS['test_posts'] = array();
$GLOBALS['test_trees'] = array();
$GLOBALS['test_current'] = null;
$GLOBALS['test_enqueued'] = array();
$GLOBALS['test_hooks'] = array();
$GLOBALS['test_shortcodes'] = array();
$GLOBALS['test_head'] = false;
$GLOBALS['test_admin'] = false;
$GLOBALS['test_singular'] = true;
function plugin_dir_path($file) { return dirname($file).'/'; }
function plugins_url($path, $file) { return 'https://staging.invalid/plugin/'.$path; }
function wp_enqueue_style($handle, $url, $deps, $version) {
    $GLOBALS['test_enqueued'][$handle] = array('url'=>$url,'version'=>$version);
}
function wp_style_is($handle, $status) { return $status==='enqueued' && isset($GLOBALS['test_enqueued'][$handle]); }
function is_admin() { return $GLOBALS['test_admin']; }
function is_singular() { return $GLOBALS['test_singular']; }
function get_queried_object() { return $GLOBALS['test_current']; }
function get_post($ref) { return $GLOBALS['test_posts'][$ref] ?? null; }
function has_shortcode($content, $tag) { return strpos($content, '['.$tag.']') !== false; }
function parse_blocks($content) { return $GLOBALS['test_trees'][$content] ?? array(); }
function did_action($name) { return $name==='wp_head' && $GLOBALS['test_head']; }
function add_action($tag,$callback,$priority) { $GLOBALS['test_hooks'][$tag] = $callback; }
function add_shortcode($tag,$callback) { $GLOBALS['test_shortcodes'][$tag] = $callback; }

require dirname(__DIR__).'/dist/fv-ex2-apollo-r187.php';

function block_ref($id) { return array('blockName'=>'core/block','attrs'=>array('ref'=>$id),'innerBlocks'=>array()); }
function block_nested($blocks) { return array('blockName'=>'core/group','attrs'=>array(),'innerBlocks'=>$blocks); }
function reset_case($post) {
    $GLOBALS['test_enqueued'] = array();
    $GLOBALS['test_current'] = $post;
    $GLOBALS['test_head'] = false;
    $GLOBALS['test_admin'] = false;
    $GLOBALS['test_singular'] = true;
}
function prepared_synced() {
    reset_case(new WP_Post(8,'page','<!-- wp:block {"ref":42} /-->'));
    $GLOBALS['test_posts'][42] = new WP_Post(42,'wp_block','[fv_ex2_apollo_atlas]');
    $GLOBALS['test_trees'][$GLOBALS['test_current']->post_content] = array(block_ref(42));
    fv_ex2_r187_preflight();
}
if (in_array('--html', $argv, true)) {
    prepared_synced();
    $GLOBALS['test_head'] = true;
    echo fv_ex2_r187_render();
    exit(0);
}
$checks = array();
function check_case($name, $actual, $expected) {
    $GLOBALS['checks'][] = array('check'=>$name, 'pass'=>$actual === $expected, 'actual'=>$actual,'expected'=>$expected);
}
function was_enqueued() { return count($GLOBALS['test_enqueued']) > 0; }

$direct='[fv_ex2_apollo_atlas]';
reset_case(new WP_Post(1,'page',$direct)); fv_ex2_r187_preflight();
check_case('direct shortcode pre-head CSS',was_enqueued(),true);

prepared_synced();
check_case('single synced block pre-head CSS',was_enqueued(),true);
check_case('conditional CSS version is source digest', $GLOBALS['test_enqueued']['fv-apollo-r187']['version'] ?? null, 'dddb5a73a58d');

reset_case(new WP_Post(2,'page','<!-- wp:group -->'));
$GLOBALS['test_trees']['<!-- wp:group -->'] = array(block_nested(array(block_ref(42))));
fv_ex2_r187_preflight(); check_case('nested group synced CSS',was_enqueued(),true);

reset_case(new WP_Post(3,'page','<!-- wp:block {"ref":44} /-->'));
$GLOBALS['test_trees'][$GLOBALS['test_current']->post_content] = array(block_ref(44));
$GLOBALS['test_posts'][44] = new WP_Post(44,'wp_block','<!-- wp:block {"ref":42} /-->');
$GLOBALS['test_trees'][$GLOBALS['test_posts'][44]->post_content] = array(block_ref(42));
fv_ex2_r187_preflight(); check_case('chained synced refs CSS',was_enqueued(),true);

reset_case(new WP_Post(4,'page','<!-- wp:block {"ref":65} /-->'));
$GLOBALS['test_trees'][$GLOBALS['test_current']->post_content] = array(block_ref(65));
$GLOBALS['test_posts'][65] = new WP_Post(65,'wp_block','<!-- wp:block {"ref":65} /-->');
$GLOBALS['test_trees'][$GLOBALS['test_posts'][65]->post_content] = array(block_ref(65));
fv_ex2_r187_preflight(); check_case('self-referential cycle terminates without enqueue',was_enqueued(),false);

reset_case(new WP_Post(5,'page','<!-- wp:block {"ref":99} /-->'));
$GLOBALS['test_trees'][$GLOBALS['test_current']->post_content] = array(block_ref(99));
fv_ex2_r187_preflight(); check_case('missing reference does not enqueue',was_enqueued(),false);

reset_case(new WP_Post(6,'page','<!-- wp:block {"ref":66} /-->'));
$GLOBALS['test_trees'][$GLOBALS['test_current']->post_content] = array(block_ref(66));
$GLOBALS['test_posts'][66] = new WP_Post(66,'post',$direct);
fv_ex2_r187_preflight(); check_case('non wp_block ref not considered',was_enqueued(),false);

reset_case(new WP_Post(7,'page','<!-- wp:group -->'));
$GLOBALS['test_trees'][$GLOBALS['test_current']->post_content] = array_fill(0, 98, block_nested(array()));
$seen = array(); $budget=96;
check_case('node scan budget fails closed',fv_ex2_r187_has_target($GLOBALS['test_current']->post_content,$seen,$budget),false);
check_case('node budget bounded',$budget>=-1,true);
fv_ex2_r187_preflight(); check_case('over-budget does not enqueue',was_enqueued(),false);

reset_case(new WP_Post(7,'page','no shortcode'));
fv_ex2_r187_preflight();check_case('ordinary post no CSS',was_enqueued(),false);

reset_case(new WP_Post(11,'page',$direct));$GLOBALS['test_admin']=true;
fv_ex2_r187_preflight();check_case('admin never enqueues',was_enqueued(),false);

reset_case(new WP_Post(12,'page',$direct));$GLOBALS['test_singular']=false;
fv_ex2_r187_preflight();check_case('archive never enqueues',was_enqueued(),false);

prepared_synced();$GLOBALS['test_head']=true;$render=fv_ex2_r187_render();
check_case('shortcode from synced block renders full atlas after header',strpos($render,'fv-apollo-atlas')!==false,true);
check_case('post-render references original investigation',strpos($render,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')!==false,true);
check_case('second shortcode fails open to original investigation',strpos(fv_ex2_r187_render(),'evidence Atlas is unavailable')!==false,true);

$failed = array_filter($checks,function($x){return !$x['pass'];});
echo json_encode(array('environment'=>'MOCK_WP_FUNCTIONS_NOT_INSTALLED_WORDPRESS',
 'checks'=>$checks,'passed'=>count($checks)-count($failed),'failed'=>count($failed),
 'html_sha256'=>hash('sha256',$render),'php_sha256'=>hash_file('sha256',dirname(__DIR__).'/dist/fv-ex2-apollo-r187.php')),
 JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
exit($failed ? 1 : 0);
