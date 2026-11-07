<?php
/**
 * FV EX2 isolated PHP callback smoke; never install on WordPress.
 * Usage: php verify_ex2_php_hooks.php /path/to/fv-ex2-playground-review.php valid|wrong_page|flag_off
 * Evaluates actual plugin PHP with a minimal callback stub, NOT WordPress core.
 */
if (PHP_SAPI !== 'cli' || $argc !== 3) {fwrite(STDERR, "CLI only: <plugin.php> <valid|wrong_page|flag_off>\n");exit(2);}
$source = $argv[1]; $scenario = $argv[2];
$expected = '91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04';
if (!in_array($scenario, ['valid','wrong_page','flag_off'], true) || !is_file($source) || hash_file('sha256', $source) !== $expected) {
    fwrite(STDERR, "FAIL CLOSED: scenario or source SHA-256 mismatch\n"); exit(3);
}
define('ABSPATH', '/ISOLATED_FV_STUB_NOT_WORDPRESS/');
$GLOBALS['fv_scenario']=$scenario; $GLOBALS['fv_actions']=[]; $GLOBALS['fv_shortcodes']=[];
$GLOBALS['fv_assets']=['css'=>'','js'=>'','registered'=>[],'enqueued'=>[]];
function get_option($key,$default='') {return $GLOBALS['fv_scenario']==='flag_off' ? '' : 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1';}
function is_page($slug) {return $GLOBALS['fv_scenario']!=='wrong_page' && $slug==='fv-ex2-review';}
function add_action($name,$fn) {$GLOBALS['fv_actions'][$name][]=$fn;}
function add_shortcode($name,$fn) {$GLOBALS['fv_shortcodes'][$name]=$fn;}
function wp_register_style($name,$src,$deps,$version) {$GLOBALS['fv_assets']['registered'][]=$name;}
function wp_register_script($name,$src,$deps,$version,$footer) {$GLOBALS['fv_assets']['registered'][]=$name;}
function wp_enqueue_style($name) {$GLOBALS['fv_assets']['enqueued'][]=$name;}
function wp_enqueue_script($name) {$GLOBALS['fv_assets']['enqueued'][]=$name;}
function wp_add_inline_style($name,$content) {$GLOBALS['fv_assets']['css'].=$content;}
function wp_add_inline_script($name,$content) {$GLOBALS['fv_assets']['js'].=$content;}
require $source;
$actions=$GLOBALS['fv_actions']['wp_enqueue_scripts']??[];
$shortcodes=$GLOBALS['fv_shortcodes'];
$ok=true;
if ($scenario==='flag_off') { $ok=(count($actions)===0 && count($shortcodes)===0); }
else {
    $ok=(count($actions)===1 && count($shortcodes)===1 && isset($shortcodes['fv_ex2_playground']));
    if ($ok) { $actions[0](); $html=$shortcodes['fv_ex2_playground'](); }
    $assets=$GLOBALS['fv_assets'];
    if ($scenario==='wrong_page') { $ok=$ok && $html==='' && $assets['css']==='' && $assets['js']==='' && count($assets['enqueued'])===0; }
    if ($scenario==='valid') {
        preg_match_all('/class="fv-margin-strip__item"/', $html, $margins);
        preg_match('/<nav class="fv-hf__chapter-nav".*?<\/nav>/s', $html, $chapterNav);
        preg_match_all('/href="#fv-hf-(?:title|chronicle|evidence|inquiry|method-title|observer|mind-title)"/', $chapterNav[0]??'', $chapters);
        $ok=$ok && $html!=='' && strlen($assets['css'])>1000 && strlen($assets['js'])>1000
            && count($assets['enqueued'])===2 && count($margins[0])===72 && count($chapters[0])===7
            && substr_count($html,'https://finalvestige.com/focus/')===5 && substr_count($html,'data-fv-archive-img')===2;
    }
}
if (!$ok) {fwrite(STDERR, "FAIL: PHP callbacks/guard/content contract in $scenario\n");exit(4);}
$result=['scenario'=>$scenario,'status'=>'PASS','source_sha256'=>$expected];
if ($scenario==='valid') { $result += ['html_sha256'=>hash('sha256',$html),'css_sha256'=>hash('sha256',$assets['css']),'js_sha256'=>hash('sha256',$assets['js']), 'html_bytes'=>strlen($html),'css_bytes'=>strlen($assets['css']),'js_bytes'=>strlen($assets['js']),'chapters'=>7,'margins'=>72,'focus_links'=>5,'archive_images'=>2]; }
echo json_encode($result,JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT)."\n";
