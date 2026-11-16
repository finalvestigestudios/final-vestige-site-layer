<?php
/* Offline assertions; no WordPress writes or third-party HTTP requests. */
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
require dirname(__DIR__) . '/staging-archive-gallery.php';
$rows = array(
 array('01','Test circumstances','The rocket was unfueled; the cabin still presented hazards.','https://www.nasa.gov/image-detail/apollo-1-crew-honored/','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','Ground-test context does not establish the ignition source.'),
 array('02','Cabin atmosphere','Elevated-pressure pure oxygen contributed to the severe fire risk.','https://www.nasa.gov/image-detail/amf-s67-15717/','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','An oxygen-rich atmosphere is not itself evidence of the first spark.'),
 array('03','Recorded sequence','The Board describes a rapid fire and pressure sequence from surviving signals.','https://www.nasa.gov/image-detail/amf-s66-58038/','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','Recorded markers do not prove an interpolated frame-by-frame reconstruction.'),
 array('04','The hatch','The original pressure hatch opened inward, obstructing emergency egress.','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','Hatch geometry explains an escape constraint, not the cause of ignition.'),
 array('05','Unresolved ignition','The initiating failure was never positively identified by the Board.','https://www.nasa.gov/image-detail/amf-s67-21294/','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','A probable electrical arc must never be described as conclusive proof.'),
 array('06','Changes after the fire','The redesign included a faster outward-opening hatch and flammability testing.','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/','The 102 deliberate Command Module tests occurred later, in December 1967–February 1968; they cannot identify the January 1967 initiator.')
);
function ok($b, $message) {global $count;if (!$b){fwrite(STDERR,"FAIL: $message\n");exit(1);} ++$count;}
$count=0;
ok(fv_r414_validate($rows), 'six permitted records');
$html=fv_r414_markup(1,$rows);
ok(substr_count($html,'class="fv-r414__card"')===6,'six cards');
ok(substr_count($html,'<details>')===6,'six native disclosures');
ok(substr_count($html,'Inspect NASA archive page')===6,'six archive links');
ok(substr_count($html,'Read NASA investigation text')===6,'six report links');
ok(substr_count($html,'Continue to the free Apollo 1 investigation')===1,'single free CTA');
ok(substr_count($html,'<img')===0,'no images');
ok(substr_count($html,'<script')===0,'no script');
ok(substr_count($html,'<form')===0,'no form');
ok(substr_count($html,'href="#fv-r414-gallery-1-')===6,'all navigation');
ok(strpos($html,'not a NASA gallery, endorsement')!==false,'nonendorsement visible');
ok(strpos($html,'image rights not cleared')!==false,'rights disclosure');
ok(strpos(fv_r414_markup(2,$rows),'fv-r414-gallery-2-06')!==false,'multi-instance IDs');
ok(fv_r414_markup(0,$rows)===fv_r414_fallback(),'zero instance fail-open');
ok(fv_r414_markup(1,array())===fv_r414_fallback(),'empty source fail-open');
$mut=$rows; $mut[3][3]='https://nasa.gov/image-detail/test/';ok(!fv_r414_validate($mut),'forbidden root domain');
$mut=$rows; $mut[3][3]='https://www.nasa.gov.evil.com/x/';ok(!fv_r414_validate($mut),'lookalike host');
$mut=$rows; $mut[3][3]='https://www.nasa.gov:9443/x/';ok(!fv_r414_validate($mut),'nonstandard port');
$mut=$rows; $mut[3][3]='http://www.nasa.gov/x/';ok(!fv_r414_validate($mut),'requires HTTPS');
$mut=$rows; $mut[3][3]='https://www.nasa.gov/x/?redirect=evil';ok(!fv_r414_validate($mut),'no query override');
$mut=$rows; $mut[3][3]='https://www.nasa.gov/x/#frag';ok(!fv_r414_validate($mut),'no fragment override');
$mut=$rows; $mut[3][3]='https://www.nasa.gov/x/%2e%2e/';ok(!fv_r414_validate($mut),'no escaped path');
$mut=$rows; $mut[3][0]='04-evil';ok(!fv_r414_validate($mut),'canonical order only');
$mut=$rows; $mut[3][2]='<script>alert(1)</script>';ok(strpos(fv_r414_markup(1,$mut),'&lt;script&gt;')!==false,'HTML escaping');
$mut=$rows; $mut[3][5]='';ok(!fv_r414_validate($mut),'missing limitation');
$mut=$rows;array_pop($mut);ok(!fv_r414_validate($mut),'missing evidence row');
$mut=$rows;$mut[]=end($rows);ok(!fv_r414_validate($mut),'seventh evidence row');
ok(!fv_r414_allowed(),'default disabled');
ok(!fv_r414_verified(dirname(__DIR__)),'missing dependency fails open');
ok(fv_r414_shortcode()===fv_r414_fallback(),'shortcode disabled fallback');
print("PHP PASS $count/$count assertions\n");
