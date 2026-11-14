<?php
/** Read-only PHP WordPress-hook stubs and strict source-gate regression. */
declare(strict_types=1);
define('ABSPATH', __DIR__);
$shortcodes=[]; $actions=[]; $assets=[];
function add_shortcode($name,$fn) { global $shortcodes; $shortcodes[$name]=$fn; }
function add_action($hook,$fn,$priority=10) { global $actions; $actions[] = [$hook,$fn,$priority]; }
function plugins_url($path,$file) { return 'https://staging.invalid/' . basename(dirname($file)) . '/' . $path; }
function wp_enqueue_style($handle,$url,$deps,$version) { global $assets; $assets[] = [$handle,$url,$deps,$version]; }
require_once dirname(__DIR__,2).'/apollo-r365/chrono-rail.php';
require_once dirname(__DIR__,2).'/apollo-r367/sealed-chronology.php';
require_once dirname(__DIR__).'/reflow-adapter.php';
function ok($v,$why) { global $n; $n++; if(!$v) throw new RuntimeException($why); }
$n=0;
ok(isset($shortcodes['fv_apollo_chronology_r368']), 'Missing opt-in shortcode');
ok(count(array_filter($actions,fn($a)=>$a[1]==='fv_apollo_r368_enqueue'))===1,'Duplicate/missing hook');
fv_apollo_r368_enqueue();
ok(count($assets)===2,'Expected R367 and R368 styles');
ok($assets[0][0]==='fv-apollo-r367-sequence' && $assets[1][0]==='fv-apollo-r368-reflow','Wrong style handles');
ok($assets[0][2]===['fv-apollo-r365-chronology'] && $assets[1][2]===['fv-apollo-r367-sequence'],'Ordering failed');
ok(str_contains($assets[1][1],'apollo-r368/assets/reflow.css'), 'Wrong CSS URL');
$canonical = $shortcodes['fv_apollo_chronology_r368']([]);
ok(substr_count($canonical,'data-fv-nasa-source')===4,'Canonical NASA citations lost');
ok(substr_count($canonical,'data-fv-source-drawer')===4,'Source drawers lost');
ok(substr_count($canonical,'data-fv-free-cta')===1,'Free CTA not unique');
ok(!str_contains($canonical,'payhip.com'), 'Premature purchase CTA');
$rows=fv_apollo_r365_rows();
foreach($rows as $i=>$record) {
  foreach($record as $field=>$value) {
    $bad=$rows; $bad[$i][$field]= $value.' altered';
    $html=fv_apollo_r367_render($bad);
    ok(!str_contains($html,'data-fv-nasa-source'), "Leaked source $i.$field");
    ok(substr_count($html,'data-fv-free-cta')===1,"Lost free CTA $i.$field");
  }
}
// A sealed chronology MUST NOT silently become the sequence-unsealed R365 output
// if the R367 dependency is missing. Separate PHP process tests this below.
$probe=<<<'P'
<?php
define('ABSPATH', __DIR__);
require $argv[1];
echo fv_apollo_r368_shortcode();
P;
$temp=tempnam(sys_get_temp_dir(),'fv-r368-');file_put_contents($temp,$probe);
$cmd='php '.escapeshellarg($temp).' '.escapeshellarg(dirname(__DIR__).'/reflow-adapter.php');
$missing=shell_exec($cmd);unlink($temp);
ok(is_string($missing) && str_contains($missing,'Evidence chronology temporarily unavailable'),'Fail-open free investigation fallback absent');
ok(!str_contains($missing,'data-fv-nasa-source') && substr_count($missing,'data-fv-free-cta')===1,'Missing dependency leaked citations/CTA');
echo json_encode(['passed'=>true,'assertions'=>$n,'styles'=>array_column($assets,0),'source_integrity'=>'reviewed original R367 gate retained','missing_dependency'=>'free investigation preserved without NASA citations'],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
