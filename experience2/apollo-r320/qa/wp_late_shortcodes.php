<?php
/**
 * R320 independent WordPress lifecycle stub for local-only QA.
 * NOT a WordPress installation or production acceptance.
 * Usage: php wp_late_shortcodes.php preflight-hit 2
 * No network, CMS database, merchant, analytics or user writes.
 */
$case = $argv[1] ?? 'late-dynamic';
$instances = (int) ($argv[2] ?? 2);
if ($instances < 1 || $instances > 3) { exit(21); }
if (!in_array($case, ['preflight-hit','late-dynamic','already-queued','footer-closed','admin','feed'], true)) { exit(22); }
define('ABSPATH', __DIR__);
$GLOBALS['r320_scripts'] = [];
$GLOBALS['r320_styles'] = [];
$GLOBALS['r320_queue_calls'] = 0;
$GLOBALS['r320_initial'] = $case === 'already-queued';
function plugins_url($path, $file) { return '/assets/'.basename($path); }
function is_singular() { return true; }
function is_admin() { return ($GLOBALS['case'] ?? '') === 'admin'; }
function is_feed() { return ($GLOBALS['case'] ?? '') === 'feed'; }
function did_action($hook) { return $hook === 'wp_footer' && ($GLOBALS['case'] ?? '') === 'footer-closed' ? 1 : 0; }
function get_post($id = null) { return (object) ['post_content' => ($GLOBALS['case'] ?? '') === 'preflight-hit' ? '[fv_apollo_source_experience]' : 'No static shortcode; dynamic block expands at render']; }
function has_shortcode($content, $tag) { return strpos($content, '['.$tag.']') !== false; }
function add_action($hook,$callback) {}
function add_shortcode($tag,$callback) {}
function wp_enqueue_style($handle,$url,$deps,$ver) { $GLOBALS['r320_styles'][$handle] = ['url'=>$url,'version'=>$ver]; }
function wp_style_is($handle,$state) { return isset($GLOBALS['r320_styles'][$handle]) && $state === 'enqueued'; }
function wp_script_is($handle,$state) { return ($GLOBALS['r320_initial'] || isset($GLOBALS['r320_scripts'][$handle])) && $state === 'enqueued'; }
function wp_enqueue_script($handle,$url,$deps,$ver,$footer) {
    $GLOBALS['r320_queue_calls']++;
    $GLOBALS['r320_scripts'][$handle]=['url'=>$url,'version'=>$ver,'footer'=>$footer];
}
$GLOBALS['case']=$case;
if ($case === 'already-queued') { $GLOBALS['r320_scripts']['fv-apollo-click-continuation-r313'] = ['url'=>'/assets/apollo-cache-continuation.js','version'=>'existing','footer'=>true]; }
$source = getenv('APOLLO_R320_PHP') ?: dirname(__DIR__, 2).'/apollo-r281/apollo-source-experience.php';
require $source;
fv_r281_preflight();
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R320 local lifecycle fixture</title></head><body><main><?php for ($i=0;$i<$instances;$i++) {echo fv_r281_render();} ?></main></body></html>
<?php
$queue=['case'=>$case,'calls'=>$GLOBALS['r320_queue_calls'],'scripts'=>$GLOBALS['r320_scripts'],'styles'=>$GLOBALS['r320_styles']];
echo '\n<!--R320_QUEUE:'.json_encode($queue,JSON_UNESCAPED_SLASHES).'-->';
