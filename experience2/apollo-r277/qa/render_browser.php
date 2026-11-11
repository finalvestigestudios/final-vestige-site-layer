<?php
/** R277 actual R276 HTML and CSS rendered through staging adapter; NOT WordPress. */
define('ABSPATH','/staging-test/');
function add_action($name,$callback,$priority=10) {}
function plugins_url($name,$file) { return 'https://example.test/plugins/fv/apollo-r277/'.$name; }
function wp_style_is($handle,$state) {return true;} // CSS is present via <style> in this fixture.
function add_shortcode($name,$callback) {}
require __DIR__.'/../apollo-review-shortcode.php';
$css=file_get_contents(__DIR__.'/../../apollo-r273/assets/review-custody.css');
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R277 genuine Apollo component source QA fixture — no CMS</title><style><?php echo $css; ?></style><style>html{scrollbar-width:none}body{margin:0;background:#101317;color:#f1e8d6;font:16px/1.5 system-ui,sans-serif}main>h1{margin:1rem auto;padding:1rem;max-width:74rem;overflow-wrap:anywhere}</style></head><body><main><h1>Apollo source custody — R277 local staging acceptance</h1><?php
 echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://malicious.invalid/buy']);
 echo fv_r277_render_shortcode(['receipt_sha256'=>str_repeat('a',64)]);
?></main></body></html>
