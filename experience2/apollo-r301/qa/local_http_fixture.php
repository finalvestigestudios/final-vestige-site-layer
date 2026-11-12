<?php
/* R301 local-only PHP HTTP route: NOT a WordPress installation or deployed endpoint. */
if (str_starts_with(parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/', '/assets/apollo-source-experience.css')) {
    header('Content-Type: text/css; charset=utf-8');
    header('Cache-Control: no-store');
    readfile(dirname(__DIR__, 2) . '/apollo-r281/assets/apollo-source-experience.css');
    return;
}
header("Content-Security-Policy: default-src 'none'; style-src 'self'; connect-src 'none'; img-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'");
header('Cache-Control: no-store');
header('Content-Type: text/html; charset=utf-8');
define('ABSPATH', __DIR__);
function plugins_url($path, $file) { return '/assets/' . basename($path); }
function is_singular() {return true;}
function get_post($id=null) {return (object)['post_content'=>'[fv_apollo_source_experience]'];}
function has_shortcode($content, $tag) {return strpos($content, '['.$tag) !== false;}
function add_action($name,$callback) {}
function add_shortcode($name,$callback) {}
function wp_enqueue_style($handle,$src,$deps,$version) { $GLOBALS['queued_version']=$version; }
function wp_style_is($name,$state) {return $state==='enqueued' && ($_GET['queue'] ?? '')==='1';}
require dirname(__DIR__,2) . '/apollo-r281/apollo-source-experience.php';
$queue=($_GET['queue']??'')==='1';
$instances=($_GET['instances']??'')==='2'?2:1;
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo Evidence staging HTTP fixture</title><?php if($queue): ?><link rel="stylesheet" href="/assets/apollo-source-experience.css?ver=<?php echo FV_R294_STYLE_VERSION; ?>"><?php endif; ?></head><body><main><?php for($i=0;$i<$instances;$i++)echo fv_r281_render(); ?></main></body></html>
