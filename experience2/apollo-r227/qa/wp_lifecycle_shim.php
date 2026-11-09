<?php
/**
 * R227 read-only WordPress lifecycle simulator for the pinned Apollo R225 adapter.
 * This is NOT a WordPress installation or production integration test.
 * Usage: php wp_lifecycle_shim.php <dist/fv-ex2-apollo-r224.php> <scenario>
 */
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
if (PHP_SAPI !== 'cli') exit(2);
define('ABSPATH', '/r227-staging-only/');
class WP_Post {
    public $post_content;
    public $post_type;
    public function __construct($content='', $type='post') {
        $this->post_content = $content;
        $this->post_type = $type;
    }
}
$GLOBALS['rd_css'] = [];
$GLOBALS['rd_post'] = new WP_Post();
$GLOBALS['rd_reusable'] = [];
$GLOBALS['rd_head'] = 0;
$GLOBALS['rd_wp_actions'] = [];
$GLOBALS['rd_wp_shortcodes'] = [];
$GLOBALS['rd_parses'] = 0;
function plugin_dir_path($path) {return dirname($path).'/';}
function plugins_url($path,$plugin) {return '/staging/apollo/'.ltrim($path, '/');}
function add_action($name,$callback,$priority=10) {$GLOBALS['rd_wp_actions'][$name] = $callback;}
function add_shortcode($name,$callback) {$GLOBALS['rd_wp_shortcodes'][$name] = $callback;}
function is_admin() {return false;}
function is_singular() {return true;}
function get_queried_object() {return $GLOBALS['rd_post'];}
function get_post($id) {return $GLOBALS['rd_reusable'][$id] ?? null;}
function has_shortcode($content,$name) {return strpos($content,'['.$name) !== false;}
function did_action($name) {return $name === 'wp_head' ? $GLOBALS['rd_head'] : 0;}
function wp_enqueue_style($handle,...$args) {$GLOBALS['rd_css'][$handle] = 'enqueued';}
function wp_style_is($handle,$status) {return ($GLOBALS['rd_css'][$handle] ?? '') === $status;}
function parse_blocks($content) {
    $GLOBALS['rd_parses']++;
    // Parses test fixtures only, intentionally not a WordPress block parser.
    // A nested core/group fixture contains the inner core/block reference.
    preg_match_all('/<!-- wp:block \{"ref":(\d+)\} \/-->/', $content, $matches);
    $blocks = [];
    foreach ($matches[1] as $ref) {
        $blocks[]=['blockName'=>'core/block','attrs'=>['ref'=>(int)$ref],'innerBlocks'=>[]];
    }
    if (strpos($content, '<!-- wp:group -->') !== false) {
        return [['blockName'=>'core/group','innerBlocks'=>$blocks]];
    }
    return $blocks;
}

$plugin = $argv[1] ?? '';
$mode = $argv[2] ?? '';
$valid = ['direct','reusable','nested','cycle','missing-ref','ordinary','late','printed','double','tamper','missing-file'];
if (!is_file($plugin) || !in_array($mode,$valid,true)) {fwrite(STDERR, "bad arguments\n");exit(2);}
switch ($mode) {
 case 'direct': case 'double': case 'late': case 'printed':
 case 'tamper': case 'missing-file':
   $GLOBALS['rd_post'] = new WP_Post('[fv_ex2_apollo_atlas]');break;
 case 'reusable':
   $GLOBALS['rd_post'] = new WP_Post('<!-- wp:block {"ref":101} /-->');
   $GLOBALS['rd_reusable'][101] = new WP_Post('[fv_ex2_apollo_atlas]','wp_block');break;
 case 'nested':
   $GLOBALS['rd_post'] = new WP_Post('<!-- wp:group --><!-- wp:block {"ref":101} /--><!-- /wp:group -->');
   $GLOBALS['rd_reusable'][101] = new WP_Post('<!-- wp:block {"ref":102} /-->','wp_block');
   $GLOBALS['rd_reusable'][102] = new WP_Post('[fv_ex2_apollo_atlas]','wp_block');break;
 case 'cycle':
   $GLOBALS['rd_post'] = new WP_Post('<!-- wp:block {"ref":101} /-->');
   $GLOBALS['rd_reusable'][101] = new WP_Post('<!-- wp:block {"ref":102} /-->','wp_block');
   $GLOBALS['rd_reusable'][102] = new WP_Post('<!-- wp:block {"ref":101} /-->','wp_block');break;
 case 'missing-ref':
   $GLOBALS['rd_post'] = new WP_Post('<!-- wp:block {"ref":777} /-->');break;
 case 'ordinary':
   $GLOBALS['rd_post'] = new WP_Post('No Apollo shortcode on this page.');break;
}
require $plugin;
$preflight = $GLOBALS['rd_wp_actions']['wp_enqueue_scripts'] ?? null;
if (!$preflight || !isset($GLOBALS['rd_wp_shortcodes']['fv_ex2_apollo_atlas'])) exit(3);
if ($mode !== 'late') call_user_func($preflight);
if ($mode === 'printed') {
    $GLOBALS['rd_head'] = 1;
    foreach ($GLOBALS['rd_css'] as &$state) $state='done';
    unset($state);
}
if ($mode === 'late') $GLOBALS['rd_head'] = 1;
// No shortcode is rendered on pages where the parser did not find one.
$first = in_array($mode, ['cycle','missing-ref','ordinary'], true) ? '' : call_user_func($GLOBALS['rd_wp_shortcodes']['fv_ex2_apollo_atlas']);
$second = ($mode === 'double') ? call_user_func($GLOBALS['rd_wp_shortcodes']['fv_ex2_apollo_atlas']) : null;
$result = [
 'mode'=>$mode, 'css'=>$GLOBALS['rd_css']['fv-apollo-r224'] ?? 'absent',
 'html'=>$first, 'second_html'=>$second,
 'fallback'=>strpos($first,'The Apollo evidence Atlas is unavailable') !== false,
 'second_fallback'=>is_string($second) && strpos($second,'The Apollo evidence Atlas is unavailable') !== false,
 'parse_calls'=>$GLOBALS['rd_parses'],
 'content_sha256'=>hash('sha256',$first)
];
echo json_encode($result, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR);
