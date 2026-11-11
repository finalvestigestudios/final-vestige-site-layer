<?php
require __DIR__ . '/../review-custody.php';
function check273($ok, $label) { if (!$ok) { fwrite(STDERR, "FAIL $label\n"); exit(1); } }
$normal=fv_ex2_r273_review_panel([]);
check273(substr_count($normal,'Editorial review pending')===2,'missing records fail closed');
check273(strpos($normal,'Editorial review remains open')!==false,'open headline');
check273(substr_count($normal,'https://www.nasa.gov/')===2,'primary NASA anchors');
check273(substr_count($normal,'Read the free Apollo 1 investigation')===1,'single original CTA');
check273(substr_count($normal,'data-fv-review-ready="false"')===1,'no release unlock');
check273(strpos($normal,'href="https://finalvestige.com/collection')===false,'no merchant');
check273(substr_count($normal,'<details')===1 && substr_count($normal,'<summary')===1,'native no JS');
$invalid=fv_ex2_r273_review_panel(['board'=>['state'=>'review-recorded','receipt_sha256'=>'invalid','reviewer'=>'A','review_date'=>'2026-11-10']]);
check273(substr_count($invalid,'Editorial review pending')===2,'bad receipt fail closed');
$valid=fv_ex2_r273_review_panel(['board'=>['state'=>'review-recorded','receipt_sha256'=>str_repeat('a',64),'reviewer'=>'A','review_date'=>'2026-11-10']]);
check273(substr_count($valid,'Review receipt supplied')===1 && substr_count($valid,'Editorial review pending')===1,'mixed record states');
check273(strpos($valid,'data-fv-review-ready="false"')!==false,'receipt cannot unlock');
$attacker=fv_ex2_r273_review_panel(['board'=>['state'=>'review-recorded','receipt_sha256'=>str_repeat('a',64),'reviewer'=>'<script>alert(1)</script>','review_date'=>'2026-11-10'],'irrelevant'=>['url'=>'https://evil.invalid']]);
check273(strpos($attacker,'<script>')===false && substr_count($attacker,'https://www.nasa.gov/')===2,'untrusted input isolation');
check273(strpos($attacker,'evil.invalid')===false,'no arbitrary links');
check273(strpos($normal,'NASA has not endorsed')!==false,'rights boundary');
echo "R273 PHP 13/13 PASS\n";
