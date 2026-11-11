<?php
/** R274 PHP gate for reentrancy, descriptive links, false receipts. */
require __DIR__ . '/../../apollo-r273/review-custody.php';
function ok274($ok,$name) { if (!$ok) {fwrite(STDERR,"FAIL: $name\n"); exit(1);} }
$record=['state'=>'review-recorded','receipt_sha256'=>str_repeat('f',64),'reviewer'=>'Editor','review_date'=>'2026-11-10'];
$one = fv_ex2_r273_review_panel([]);
$two = fv_ex2_r273_review_panel(['board'=>$record]);
$three = fv_ex2_r273_review_panel(['board'=>$record,'chronology'=>$record]);
$all = $one.$two.$three;
ok274(substr_count($all, 'id="fv-r273-title"')===1,'first ID stable');
ok274(substr_count($all, 'id="fv-r273-title-2"')===1,'second ID unique');
ok274(substr_count($all, 'id="fv-r273-title-3"')===1,'third ID unique');
foreach (['fv-r273-title','fv-r273-title-2','fv-r273-title-3'] as $id) ok274(substr_count($all, 'aria-labelledby="'.$id.'"')===1,'valid unique reference '.$id);
ok274(substr_count($all,'Read NASA primary source: Apollo 204 Review Board report')===3,'review board source-specific link');
ok274(substr_count($all,'Read NASA primary source: Four recorded chronology markers')===3,'chronology source-specific link');
ok274(substr_count($all,'data-fv-review-ready="false"')===3,'no receipt can publish');
ok274(substr_count($all,'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/')===6,'primary URLs unchanged');
ok274(substr_count($all,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')===3,'free investigation unchanged');
ok274(strpos($all,'payhip')===false && strpos($all,'minimuseum')===false,'no commerce injection');
$impossible = fv_ex2_r273_review_panel(['board'=>array_merge($record,['review_date'=>'2026-02-30'])]);
ok274(substr_count($impossible,'Editorial review pending')===2,'impossible date rejected');
$malicious = fv_ex2_r273_review_panel(['board'=>array_merge($record,['reviewer'=>'<script>alert(1)</script>']), 'intruder'=>['url'=>'https://evil.invalid']]);
ok274(strpos($malicious,'<script>')===false && strpos($malicious,'evil.invalid')===false,'no untrusted markup/links');
ok274(substr_count($malicious,'data-fv-review-ready="false"')===1,'suspicious receipt cannot unlock');
echo "R274 PHP reentrancy and receipt custody: 15/15 PASS\n";
