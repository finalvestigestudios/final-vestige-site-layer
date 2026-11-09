<?php
/** R232 independent missing/tampered source fallback smoke, does not boot WordPress. */
declare(strict_types=1);
error_reporting(E_ALL);
define('ABSPATH','/offline/');
$GLOBALS['assets'] = [];
function add_action($a,$b,$c=10) {}
function add_shortcode($a,$b) {}
function plugins_url($p,$f) { return 'https://staging.invalid/research-desk/'.$p; }
function plugin_dir_path($f) { return dirname($f).'/'; }
function esc_url($s) { return htmlspecialchars($s,ENT_QUOTES,'UTF-8'); }
function did_action($a) { return 1; }
function wp_style_is($a,$b) { return false; }
function wp_script_is($a,$b) { return false; }
function wp_enqueue_style($a,$b,$c,$d) { $GLOBALS['assets'][]=$a; }
function wp_enqueue_script($a,$b,$c,$d,$e) { $GLOBALS['assets'][]=$a; }
function is_singular(){ return true; }
function get_post(){ return (object)['post_content'=>'[fv_ex2_research_desk]']; }
function has_shortcode($s,$t){return strpos($s,'['.$t.']')!==false;}
$base=dirname(__DIR__);
$runtime=$base.'/fv-ex2-r232-runtime.php';
if (!is_readable($runtime)) throw new RuntimeException('runtime missing');
require $runtime;
$html=fv_ex2_r232_shortcode();
if (substr_count($html,'Research source viewer unavailable')!==1 || substr_count($html,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')!==1) {
    throw new RuntimeException('missing-template fallback broken');
}
if (count($GLOBALS['assets'])!==0) throw new RuntimeException('assets loaded on fallback');
print "PASS: missing-template fallback, one original CTA, no assets\n";
