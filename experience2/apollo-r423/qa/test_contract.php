<?php
// CLI source and gate verification, with no WordPress or external HTTP writes.
define('ABSPATH', __DIR__);
require_once dirname(__DIR__) . '/staging-research-desk-bridge.php';
$checks=0;
function check(bool $condition, string $message): void { global $checks; $checks++; if (!$condition) { fwrite(STDERR, "FAIL $message\n"); exit(1); } }
check(fv_r423_git_blob('test') === '30d74d258442c7c65512eafab474568dd706c430', 'known Git blob');
check(!fv_r423_allowed(), 'disabled by default');
check(strpos(fv_r423_shortcode(), FV_R423_ARTICLE) !== false, 'safe fallback');
$root = sys_get_temp_dir() . '/fv-r423-test-' . getmypid();
mkdir($root);mkdir($root.'/templates');mkdir($root.'/assets');
$testFiles=['templates/ledger.html'=>'safe ledger', 'assets/source-ledger.css'=>'body{}', 'assets/source-ledger.js'=>'console.info(0)'];
$expected=[];
foreach($testFiles as $name=>$content){file_put_contents($root.'/'.$name,$content);$expected[$name]=fv_r423_git_blob($content);}
check(fv_r423_valid_files($root,$expected), 'valid pinned fixture files');
file_put_contents($root.'/assets/source-ledger.js','console.info(1)');
check(!fv_r423_valid_files($root,$expected), 'modified JS rejects');
file_put_contents($root.'/assets/source-ledger.js',$testFiles['assets/source-ledger.js']);
file_put_contents($root.'/templates/ledger.html','tampered');
check(!fv_r423_valid_files($root,$expected), 'modified ledger rejects');
file_put_contents($root.'/templates/ledger.html',$testFiles['templates/ledger.html']);
check(!fv_r423_valid_files($root,['../templates/ledger.html'=>$expected['templates/ledger.html']]), 'path traversal rejects');
check(!fv_r423_valid_files($root,['assets/not-here.js'=>'abcdef']), 'non sha rejects');
check(!fv_r423_valid_files($root.'/missing',$expected), 'missing root rejects');
foreach($testFiles as $name=>$v)unlink($root.'/'.$name);
rmdir($root.'/templates');rmdir($root.'/assets');rmdir($root);
$cards='';for($i=1;$i<=6;$i++)$cards.='<article data-fvx-record id="fv-ex2-ledger-apollo1-record-'.sprintf('%02d',$i).'">Archive link</article>';
$fixture='<section data-fvx-ledger><h2 id="fv-ex2-ledger-apollo1-title">Title</h2>' . $cards . '<a href="' . FV_R423_ARTICLE . '">Continue</a></section>';
$out1=fv_r423_render($fixture,1);$out2=fv_r423_render($fixture,2);
check(strpos($out1,'fv-r423-1-record-01')!==false,'per-instance ids');
check(strpos($out2,'fv-r423-2-record-01')!==false,'second ids');
check(strpos($out1,'fv-ex2-ledger-apollo1-record-01')===false,'removed original duplicate ids');
check(substr_count($out1,'What this image cannot prove')===6,'six native details');
check(substr_count($out1,FV_R423_ARTICLE)===1,'one free investigation link');
check(strpos($out1,'2017')!==false,'later museum context');
check(strpos(fv_r423_render($fixture.'<script>bad()</script>',0), 'fv-r423-fallback')!==false,'invalid instance fallback');
check(strpos(fv_r423_render(str_replace('data-fvx-record','data-bad',$fixture),1),'fv-r423-fallback')!==false,'missing records fallback');
check(strpos(fv_r423_render(str_replace('data-fvx-ledger','data-bad',$fixture),1),'fv-r423-fallback')!==false,'missing ledger fallback');
check(strpos(fv_r423_render(str_replace(FV_R423_ARTICLE,'https://invalid.example/',$fixture),1),'fv-r423-fallback')!==false,'missing CTA fallback');
check(strpos($out1,'<img')===false && strpos($out1,'<script')===false, 'no external media/scripts in fixture');
echo "PASS $checks/$checks PHP assertions\n";
