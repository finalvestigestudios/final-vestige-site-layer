<?php
/** Structural acceptance tests; no prod write or external network. */
$root=dirname(__DIR__);
$assert=0;
function t($condition,$message) {global $assert; $assert++;if(!$condition){fwrite(STDERR,"FAIL $message\n");exit(1);}}
define('ABSPATH','/tmp/r415-qa');
require $root.'/staging-journey.php';
t(!fv_r415_authorized(),'disabled by default');
t(strpos(fv_r415_shortcode(),'Read the existing Apollo 1 investigation')!==false,'fallback without flags');
t(fv_r415_verified(),'original source identity validates');
$src=fv_r415_catalog();
t(is_array($src)&&count($src)===6,'six exact source records');
t(fv_r414_validate($src),'upstream validates records');
$html=fv_r415_markup(1,$src);
t(substr_count($html,'data-fv-r415-journey')===1,'one journey');
t(substr_count($html,'fv-r414__card')===6,'six archive items');
t(substr_count($html,'Continue to the free Apollo 1 investigation')===1,'exactly one free CTA per experience');
t(strpos($html,'checkout')===false && strpos($html,'payhip')===false,'no checkout commerce');
t(substr_count($html,'NASA original publication')===3,'three primary timeline citations');
t(strpos($html,'not conclusively identify')!==false,'unresolved ignition explicit');
t(strpos($html,'102 separate, later deliberate ignitions')!==false,'later tests separated');
t(strpos($html,'14 March 1968')!==false,'post-accident date explicit');
t(strpos($html,'fv-r414-gallery-1-05')!==false,'timeline record link');
t(strpos($html,'fv-r414-gallery-1-06')!==false,'later-tests record link');
t(strpos($html,'<img')===false && strpos($html,'<iframe')===false,'no unreviewed media');
t(strpos($html,'<script')===false && strpos($html,'<form')===false,'no scripts forms tracking');
t(strpos($html,'data-lat')===false && strpos($html,'geo:')===false,'no invented geospatial pins');
t(substr_count($html,'https://www.nasa.gov/')>=12,'provenance references remain');
$h2=fv_r415_markup(2,$src);
t(strpos($h2,'fv-r414-gallery-2-05')!==false,'namespaced later instance');
t(strpos($h2,'fv-r414-gallery-1-05')===false,'no duplicate first-instance ID');
t(fv_r415_markup(0,$src)===fv_r415_fallback(),'zero instance fail-open');
$bad=$src;$bad[4][3]='https://www.nasa.gov.attacker.invalid/trick/';
t(fv_r415_markup(1,$bad)===fv_r415_fallback(),'lookalike NASA blocked');
$bad=$src;array_pop($bad);
t(fv_r415_markup(1,$bad)===fv_r415_fallback(),'incomplete catalog blocked');
$bad=$src;$bad[1][1]='<script>alert(1)</script>';
t(strpos(fv_r415_markup(1,$bad),'&lt;script&gt;')!==false,'source text escaped');
$sandbox=sys_get_temp_dir().'/fv-r415-'.bin2hex(random_bytes(5));
$testRoot=$sandbox.'/apollo-r415';
foreach (array($sandbox,$testRoot,$testRoot.'/assets',$sandbox.'/apollo-r411',$sandbox.'/apollo-r414',$sandbox.'/apollo-r414/assets') as $dir) mkdir($dir);
$copies=array(
    $root.'/assets/journey.css'=>$testRoot.'/assets/journey.css',
    dirname($root).'/apollo-r411/staging-source-drawer.php'=>$sandbox.'/apollo-r411/staging-source-drawer.php',
    dirname($root).'/apollo-r414/staging-archive-gallery.php'=>$sandbox.'/apollo-r414/staging-archive-gallery.php',
    dirname($root).'/apollo-r414/assets/archive-gallery.css'=>$sandbox.'/apollo-r414/assets/archive-gallery.css',
);
foreach ($copies as $from=>$to) copy($from,$to);
t(fv_r415_verified($testRoot),'complete isolated dependency fixture validates before mutation');
$original=file_get_contents($testRoot.'/assets/journey.css');
file_put_contents($testRoot.'/assets/journey.css',$original.'/*tamper*/');
t(!fv_r415_verified($testRoot),'modified stylesheet alone blocked despite complete valid dependencies');
file_put_contents($testRoot.'/assets/journey.css',$original);
$originalCatalog=file_get_contents($sandbox.'/apollo-r411/staging-source-drawer.php');
file_put_contents($sandbox.'/apollo-r411/staging-source-drawer.php',$originalCatalog.'/*tamper*/');
t(!fv_r415_verified($testRoot),'modified NASA source custody alone blocked');
foreach ($copies as $to) unlink($to);
foreach (array($sandbox.'/apollo-r414/assets',$sandbox.'/apollo-r414',$sandbox.'/apollo-r411',$testRoot.'/assets',$testRoot,$sandbox) as $dir) rmdir($dir);
print "PASS $assert/".$assert." R415 PHP assertions\n";
