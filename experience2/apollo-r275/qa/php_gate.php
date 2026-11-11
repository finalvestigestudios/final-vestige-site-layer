<?php
/** R275 fail-closed PHP display custody; no CMS writes. */
require __DIR__ . '/../../apollo-r273/review-custody.php';
function admit275(bool $ok, string $label): void {
    if (!$ok) { fwrite(STDERR, "FAIL $label\n"); exit(1); }
    echo "PASS $label\n";
}
$synthetic = ['state'=>'review-recorded','receipt_sha256'=>str_repeat('a',64),
    'reviewer'=>'Fixture only','review_date'=>'2026-11-10'];
$html = fv_ex2_r273_review_panel(['board'=>$synthetic,'chronology'=>$synthetic]);
admit275(str_contains($html,'Unverified review metadata present'),'unverified metadata heading');
admit275(substr_count($html,'self-reported, unverified')===2,'self-reported metadata not accepted as verified');
admit275(str_contains($html,'not two independent source confirmations'),'shared single NASA primary-source boundary');
admit275(str_contains($html,'data-fv-review-ready="false"'),'no automatic publication');
admit275(substr_count($html,'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/')===2,'exact trusted NASA source twice');
admit275(substr_count($html,'Read the free Apollo 1 investigation')===1,'one separate free investigation action');
$future = fv_ex2_r273_review_panel(['board'=>array_merge($synthetic,['review_date'=>'2099-11-10'])]);
admit275(substr_count($future,'Editorial review pending')===2,'future self-reported review rejected');
admit275(!str_contains($future,'data-fv-review-ready="true"'),'future receipt cannot activate publication');
echo "R275 PHP: 8/8 PASS\n";
