<?php
/* R278 loopback-only PHP built-in server fixture. NOT a WordPress installation. */
header("Content-Security-Policy: default-src 'none'; style-src 'self'; script-src 'none'; connect-src 'none'; img-src 'none'; font-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'");
header('Cache-Control: no-store');
$path=parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH);
if($path==='/assets/review-custody.css'){
 header('Content-Type: text/css; charset=UTF-8');
 readfile(__DIR__.'/../../apollo-r273/assets/review-custody.css');return true;
}
if($path==='/assets/missing.css'){http_response_code(404);echo 'missing';return true;}
if($path!=='/atlas'){http_response_code(404);echo 'not found';return true;}
define('ABSPATH','/apollo-http-qa/');
function add_action($a,$b,$c=10){}
function add_shortcode($a,$b){}
function wp_style_is($a,$b){return false;}
function plugins_url($name,$file){return isset($_GET['missing_css'])?'/assets/missing.css':'/assets/review-custody.css';}
require __DIR__.'/../../apollo-r277/apollo-review-shortcode.php';
header('Content-Type: text/html; charset=UTF-8');
echo '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><body><main>';
echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://merchant.invalid/buy']);
echo fv_r277_render_shortcode(['receipt_sha256'=>str_repeat('0',64)]);
echo '</main></body></html>';
