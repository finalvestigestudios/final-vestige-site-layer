<?php
/* Executable PHP source custody regression: no WordPress install. */
define('ABSPATH', __DIR__.'/');
require __DIR__.'/../../apollo-r365/chrono-rail.php';
require __DIR__.'/../../apollo-r367/sealed-chronology.php';
require __DIR__.'/../source-gallery.php';
$n=0;
function must($truth, $label) { global $n; ++$n; if (!$truth) { fwrite(STDERR, "FAIL $n $label\n"); exit(1); } }
$good=fv_apollo_r371_catalog();
$base=fv_apollo_r365_rows();
must(count($good)===4,'four reviewed source records');
must(fv_apollo_r371_is_sealed($good),'baseline catalog sealed');
must(fv_apollo_r367_is_sealed($base),'upstream chronology sealed');
$out=fv_apollo_r371_render($good,$base);
must(strpos($out,'data-fv-source-gallery')!==false,'gallery rendered');
must(substr_count($out,'data-fv-source-drawer')===4,'four native source drawers');
must(substr_count($out,'data-fv-nasa-source')===4,'four unique source anchors');
must(substr_count($out,'data-fv-free-cta')===1,'exactly one free link');
must(strpos($out,'<img')===false,'no embedded images');
must(strpos($out,'<iframe')===false,'no iframe');
must(strpos($out,'<script')===false,'no scripts');
must(strpos($out,'utm_')===false,'no analytics or utm');
must(strpos($out,'wp_remote_')===false,'no network requests');
must(strpos($out,'paypal')===false && strpos($out,'payhip')===false,'no merchant CTA');
must(strpos($out,'NASA does not endorse')!==false,'NASA nonendorsement');
foreach($good as $i=>$item){
  must(strpos($out,htmlspecialchars($item['title'],ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'))!==false,"title $i");
  must(strpos($out,htmlspecialchars($item['boundary'],ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'))!==false,"boundary $i");
  must(strpos($out,htmlspecialchars($item['url'],ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'))!==false,"source $i");
  foreach(['key','when','kind','title','finding','boundary','url','publisher','rights'] as $field){
    $mut=$good; $mut[$i][$field].='—changed';
    must(!fv_apollo_r371_is_sealed($mut),"seal rejects $i $field");
    $blocked=fv_apollo_r371_render($mut,$base);
    must(strpos($blocked,'data-fv-source-gallery')===false,"gallery withheld $i $field");
    must(substr_count($blocked,'data-fv-free-cta')===1,"fallback has one free CTA $i $field");
    must(strpos($blocked,'data-fv-nasa-source')===false,"fallback withholds sources $i $field");
  }
}
$mut=$good; unset($mut[1]);must(!fv_apollo_r371_is_sealed($mut),'missing record rejected');
$mut=$good; $mut[0]=$mut[1];must(!fv_apollo_r371_is_sealed($mut),'duplicate rejected');
$mut=$good; [$mut[0],$mut[1]]=[$mut[1],$mut[0]];must(!fv_apollo_r371_is_sealed($mut),'reorder rejected');
$mut=$good; $mut[]=array('title'=>'extra');must(!fv_apollo_r371_is_sealed($mut),'extra rejected');
$badChron=$base; $badChron[1]['heading'].=' tampered';
$blocked=fv_apollo_r371_render($good,$badChron);
must(strpos($blocked,'data-fv-source-gallery')===false,'upstream chronology tamper withheld');
must(strpos($blocked,'data-fv-nasa-source')===false,'upstream NASA sources withheld');
$second=fv_apollo_r371_render($good,$base);
preg_match_all('/\bid="([^"]+)"/',$out.$second,$matches);
must(count($matches[1])===count(array_unique($matches[1])),'two instances unique ids');
must(strpos($out,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')!==false,'free investigation only');
echo json_encode(['status'=>'PASS','assertions'=>$n,'records'=>count($good),'mutation_fields'=>count($good)*9, 'notes'=>'WordPress-independent PHP unit tests, NOT installed WordPress'],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
