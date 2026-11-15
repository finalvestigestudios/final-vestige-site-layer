<?php
/* Strict source relation tests; no installed WordPress, no live requests. */
define('ABSPATH', __DIR__.'/');
require __DIR__.'/../../apollo-r365/chrono-rail.php';
require __DIR__.'/../../apollo-r367/sealed-chronology.php';
require __DIR__.'/../../apollo-r371/source-gallery.php';
require __DIR__.'/../evidence-path.php';
$tests = 0;
function ok($test, $label) { global $tests; ++$tests; if (!$test) { fwrite(STDERR,"FAIL #$tests: $label\n"); exit(1); } }
$events=fv_apollo_r365_rows();$docs=fv_apollo_r371_catalog();
ok(fv_apollo_r372_approved($events,$docs),'canonical source join');
ok(count($events)===4 && count($docs)===4,'record sizes');
$mapping=fv_apollo_r372_join();
ok($mapping===array('fire'=>'review-board','findings'=>'review-board','tests'=>'flammability','decision'=>'atmosphere'),'precise identity join');
$html=fv_apollo_r372_render($events,$docs);
ok(substr_count($html,'data-fv-evidence-stage')===4,'four stages');
ok(substr_count($html,'data-fv-source-drawer')===4,'four native details drawers');
ok(substr_count($html,'data-fv-nasa-source')===4,'four source citations');
ok(substr_count($html,'data-fv-nasa-context')===1,'context distinct from event');
ok(substr_count($html,'data-fv-free-cta')===1,'one free investigation action');
ok(substr_count($html,'data-fv-print-source')===5,'four print sources and one context');
ok(substr_count($html,'https://www.nasa.gov/')>=9,'NASA links');
ok(strpos($html,'2022 retrospective')!==false,'retrospective classification');
ok(strpos($html,'not a fifth event')!==false,'explicit no false chrono event');
ok(strpos($html,'60 percent oxygen')!==false,'baseline atmosphere data');
ok(strpos($html,'No sale or conversion is claimed')!==false,'commerce disclosure');
ok(strpos($html,'data-utm')===false && strpos($html,'<script')===false,'no tracking/script');
ok(strpos($html,'<img')===false && strpos($html,'<iframe')===false,'no media/iframes');
// Independent whole-record and whole-sequence tamper detection.
foreach (array('id','when','era','heading','supported','limit','source','source_title','published','class') as $field) {
  $m=$events;$m[0][$field] .= ' altered';
  ok(!fv_apollo_r372_approved($m,$docs),'reject mutated event field '.$field);
  $blocked=fv_apollo_r372_render($m,$docs);
  ok(strpos($blocked,'data-fv-nasa-source')===false && substr_count($blocked,'data-fv-free-cta')===1,'safe event fallback '.$field);
}
foreach (array('key','when','kind','title','finding','boundary','url','publisher','rights') as $field) {
  $m=$docs;$m[1][$field] .= ' altered';
  ok(!fv_apollo_r372_approved($events,$m),'reject mutated document field '.$field);
  ok(strpos(fv_apollo_r372_render($events,$m),'https://www.nasa.gov/')===false,'hide citations on document tamper '.$field);
}
foreach (array('reverse','duplicate','missing','extra') as $case){
 $m=$events;
 if($case==='reverse')$m=array_reverse($m);
 if($case==='duplicate')$m[2]=$m[1];
 if($case==='missing')array_pop($m);
 if($case==='extra')$m[]=$m[0];
 ok(!fv_apollo_r372_approved($m,$docs),'reject event '.$case);
 $m=$docs;
 if($case==='reverse')$m=array_reverse($m);
 if($case==='duplicate')$m[2]=$m[1];
 if($case==='missing')array_pop($m);
 if($case==='extra')$m[]=$m[0];
 ok(!fv_apollo_r372_approved($events,$m),'reject docs '.$case);
}
$noDeps=phpversion();ok(is_string($noDeps),'PHP runtime known');
$repeat=fv_apollo_r372_render($events,$docs);
preg_match('/id="(fv-apollo-r372-[0-9]+-title)"/',$html,$a);
preg_match('/id="(fv-apollo-r372-[0-9]+-title)"/',$repeat,$b);
ok(isset($a[1],$b[1]) && $a[1]!==$b[1],'repeat unique instances');
$alt=fv_apollo_r372_render(null,$docs);
ok(substr_count($alt,'data-fv-free-cta')===1 && !str_contains($alt,'https://www.nasa.gov/'),'missing dependencies safe');
echo "R372 source custody PASS $tests/$tests assertions\n";
