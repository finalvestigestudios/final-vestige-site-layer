<?php
/** R360 deterministic offline contract: no WP installation or network access. */
define('ABSPATH', __DIR__);
require dirname(__DIR__) . '/rights-audit.php';
require_once dirname(__DIR__,2) . '/apollo-r347/source-index.php';
function check($v, $msg) { if (!$v) { fwrite(STDERR, "FAIL: $msg\n"); exit(2); } }
$rows=fv_apollo_r360_manifest();
check(count($rows)===9,'9 exact sources');
$classes=array_count_values(array_column($rows,'class'));
check(($classes['board']??0)===3 && ($classes['later-history']??0)===1 && ($classes['later-test']??0)===1 && ($classes['photo']??0)===4,'distinct document classes');
check(count(array_unique(array_column($rows,'url')))===9,'nine distinct URLs');
check(count(array_filter($rows, 'fv_apollo_r360_link_allowed'))===9,'approved record pairings');
foreach($rows as $row){
  check($row['commercial_media_rights']==='NOT_CLEARED_LINK_ONLY','rights explicit');
  check($row['link_review']==='official-page-checked-2026-11-14','review status explicit');
  $tampered=$row;$tampered['boundary']='NASA conclusively proved a specific wire';
  check(!fv_apollo_r360_link_allowed($tampered),'tampered claim rejected');
  $tampered=$row;$tampered['url']='https://www.nasa.gov/fabricated';
  check(!fv_apollo_r360_link_allowed($tampered),'fabricated URL rejected');
}
$original = fv_apollo_r349_approved_sources();
check(count($original)===8,'eight historical preapproved pages');
foreach($rows as $row){
  if($row['class']!=='later-test') check(array_key_exists($row['url'],$original),'exact 1967/archival identity');
}
check($rows[8]['url']===fv_apollo_r355_record()['source'] && fv_apollo_r355_source_is_reviewed(fv_apollo_r355_record()),'2018 source independent pin');
$photos=fv_apollo_r340_accessions();
check(count($photos)===4,'four photographs');
foreach($photos as $photo){check(in_array($photo['url'],array_column($rows,'url'),true),'photograph URL reviewed');}
check(count(fv_apollo_r347_records())===13,'13 evidence records');
$html=fv_apollo_r360_rights_audit_shortcode();
check(substr_count($html,'data-fv-rights-reviewed-link')===9,'nine source links');
check(substr_count($html,'data-fv-commercial-clearance="not-cleared"')===9,'each commercial right blocked');
check(strpos($html,'<img')===false && strpos($html,'<script')===false && strpos($html,'checkout')!==false,'no copied media or scripts');
check(strpos($html,'href="https://finalvestige.com')===false,'no unreviewed paid CTA');
$fake=$rows[0];$fake['label']='<script>alert(1)</script>';
check(!fv_apollo_r360_link_allowed($fake),'label injection rejected');
$twice=fv_apollo_r360_rights_audit_shortcode();
check(preg_match('/id="fv-apollo-r360-2-title"/',$twice)===1,'instance ID unique');
echo json_encode(array('pass'=>true,'sources'=>9,'classes'=>$classes,'photo_rights_cleared'=>0,'outbound_links'=>9,'evidence_records'=>13,'tamper_rejections'=>19,'staging_only'=>true), JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES),"\n";
