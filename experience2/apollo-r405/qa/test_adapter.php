<?php
/** Native PHP staging-gate contract. This test does not enable/install WordPress. */
define('ABSPATH', '/tmp');
$hooks = array(); $shortcodes = array(); $styles = array(); $scripts = array();
function add_action($n, $fn, $prio) { $GLOBALS['hooks'][$n] = array($fn, $prio); }
function add_shortcode($n, $fn) { $GLOBALS['shortcodes'][$n] = $fn; }
function wp_get_environment_type() { return $GLOBALS['environment'] ?? 'production'; }
function is_singular() { return $GLOBALS['singular'] ?? false; }
function get_queried_object_id() { return $GLOBALS['page_id'] ?? 0; }
function wp_script_is($name, $state) { return $GLOBALS['original_script'] ?? false; }
function wp_style_is($name, $state) { return $GLOBALS['original_style'] ?? false; }
function plugins_url($path, $file) { return 'https://staging.example.test/wp-content/plugins/r405/' . $path; }
function wp_enqueue_style($name, $url, $deps, $ver) { $GLOBALS['styles'][] = array($name,$url,$deps,$ver); }
function wp_enqueue_script($name, $url, $deps, $ver, $footer) { $GLOBALS['scripts'][] = array($name,$url,$deps,$ver,$footer); }
require dirname(__DIR__) . '/staging-shortcode.php';
$pass = 0;
function ok($v, $message) { global $pass; if (!$v) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } $pass++; }
ok(isset($hooks['wp_enqueue_scripts']) && $hooks['wp_enqueue_scripts'][1] === 99, 'pre-render registered');
ok(isset($shortcodes['fv_ex2_research_desk_r405']), 'isolated shortcode registered');
ok(!fv_ex2_r405_authorized(), 'default off');
fv_ex2_r405_enqueue();
ok(count($styles)===0 && count($scripts)===0, 'default no enqueue');
ok(strpos(fv_ex2_r405_shortcode(), 'Read the free Apollo 1 investigation')!==false, 'default fallback useful');
$GLOBALS['environment']='staging'; $GLOBALS['singular']=true; $GLOBALS['page_id']=123;
ok(!fv_ex2_r405_authorized(), 'approval still absent');
ok(!fv_ex2_r405_assets_valid(dirname(__DIR__)), 'missing reviewed template fails custody');
$input='<label for="fv-ex2-ledger-apollo1-search">Search</label><input id="fv-ex2-ledger-apollo1-search" aria-controls="fv-ex2-ledger-apollo1-grid"><div id="fv-ex2-ledger-apollo1-grid"><a href="#fv-ex2-ledger-apollo1-record-01">view</a><article id="fv-ex2-ledger-apollo1-record-01"></article></div>';
$a=fv_ex2_r405_namespace_markup($input,1); $b=fv_ex2_r405_namespace_markup($input,2); $c=fv_ex2_r405_namespace_markup($input,3);
ok($a===$input, 'first instance preserves IDs');
ok(strpos($b,'fv-ex2-ledger-apollo1-instance-2-search')!==false, 'second IDs namespaced');
ok(strpos($b,'for="fv-ex2-ledger-apollo1-instance-2-search"')!==false, 'label namespaced');
ok(strpos($b,'aria-controls="fv-ex2-ledger-apollo1-instance-2-grid"')!==false, 'aria namespaced');
ok(strpos($b,'href="#fv-ex2-ledger-apollo1-instance-2-record-01"')!==false, 'fragment namespaced');
ok(strpos($c,'fv-ex2-ledger-apollo1-instance-3-search')!==false, 'third namespaced');
ok($a!==$b && $b!==$c, 'instances distinct without JS');
ok(fv_ex2_r405_git_blob(__FILE__) !== null, 'Git-style blob read works');
ok(fv_ex2_r405_git_blob('/not/a/file') === null, 'missing file rejected');
ok(count(fv_ex2_r405_expected_blobs())===4, 'four byte gates');
// Verify PHP Git-blob SHA against native git hash-object for the current source.
$expected=trim(shell_exec('git hash-object '.escapeshellarg(__FILE__)) ?? '');
ok($expected===fv_ex2_r405_git_blob(__FILE__), 'Git SHA matches git hash-object');
print("PASS $pass native PHP adapter assertions; original NASA staging template absent, so positive installation gate NOT TESTED\n");
