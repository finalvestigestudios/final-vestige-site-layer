<?php
/** Staging-only actual R273/PHP renderer and R280 pending-custody mutation gate. */
error_reporting(E_ALL);
define('ABSPATH', '/offline-qa-only/');
function add_action($name, $callback, $priority=10) {}
function add_shortcode($name, $callback) {}
function plugins_url($path, $file) { return '/offline/review-custody.css'; }
function wp_style_is($handle, $flag) { return true; }
require __DIR__ . '/../../apollo-r277/apollo-review-shortcode.php';
require __DIR__ . '/../../apollo-r273/review-custody.php';
$valid = fv_ex2_r273_review_panel([]);
$nasa = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
$free = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
$cases = [
  'original-pending-only' => [$valid,true],
  'false-approved-headline' => [str_replace('Editorial review remains open','Editorial review approved',$valid),false],
  'false-approved-status' => [str_replace('Editorial review pending','Editorial review approved',$valid),false],
  'hidden-shared-source-warning' => [str_replace('two editorial record categories, not two independent','two unrelated independent',$valid),false],
  'removed-NASA-nonendorsement' => [str_replace('NASA has not endorsed Final Vestige','NASA officially endorses Final Vestige',$valid),false],
  'source-label-mutated' => [str_replace('Read NASA primary source:','Visit information:',$valid),false],
  'new-tab-rel-removed' => [str_replace('rel="noopener noreferrer"','rel="noreferrer"',$valid),false],
  'added-commercial-form' => [$valid.'<form action="https://seller.invalid/checkout"><button>Buy</button></form>',false],
  'added-remote-image' => [$valid.'<img src="https://seller.invalid/pixel" alt="">',false],
  'added-iframe' => [$valid.'<iframe src="https://seller.invalid/"></iframe>',false],
  'added-inline-event-handler' => [str_replace('<aside class="fv-r273"','<aside onclick="location.href=\'https://seller.invalid\'" class="fv-r273"',$valid),false],
  'added-javascript-url' => [$valid.'<p title="javascript:alert(1)">x</p>',false],
  'removed-primary-source-anchor' => [str_replace('href="'.$nasa.'"','href="https://example.invalid/"',$valid),false],
  'removed-free-investigation' => [str_replace('href="'.$free.'"','href="https://example.invalid/"',$valid),false],
  'added-unrelated-link' => [$valid.'<a href="https://example.invalid">More</a>',false],
  'empty' => ['',false],
  'not-a-string' => [null,false],
];
$results=[];
foreach ($cases as $label => $case) {
    $actual = fv_r277_has_source_custody($case[0]);
    if ($actual !== $case[1]) {fwrite(STDERR,"FAIL $label\n");exit(1);}
    $results[] = ['case'=>$label,'result'=>'PASS','accepted'=>$actual];
}
$rendered=fv_r277_render_shortcode(['review_state'=>'approved','merchant_url'=>'https://seller.invalid']);
if (strpos($rendered,'seller.invalid')!==false || !fv_r277_has_source_custody($rendered)) {
  fwrite(STDERR,"FAIL shortcode render cannot approve or sell\n");exit(1);
}
$dir=$argv[1]??null;
if ($dir) {if (!is_dir($dir)) mkdir($dir,0775,true);file_put_contents($dir.'/rendered.html',$rendered);file_put_contents($dir.'/php_receipt.json',json_encode($results,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");}
echo 'R280 actual PHP pending-only + negative controls '.count($cases).'/'.count($cases)." PASS\n";
