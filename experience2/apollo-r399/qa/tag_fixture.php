<?php
/** Read-only fixture emission: canonical WordPress HTML + adversarial alterations. */
define('ABSPATH','/tmp/fv-r399-fixture');
require __DIR__.'/../staging-final-tag-guard.php';
$base='https://staging.fv.example/wp-content/plugins/final-vestige-site-layer/experience2';
$GLOBALS['fv_r399_approved_styles']=fv_r399_canonical_css($base);
$cases=[];
foreach ($GLOBALS['fv_r399_approved_styles'] as $handle=>$url) {
 $version=$handle==='fv-apollo-r384-gallery'?'r384-reviewed-1':'r395-reviewed-1';
 $media=$handle==='fv-apollo-r384-gallery'?'all':'screen';
 $href=$url.'?ver='.$version;
 $canonical="<link rel='stylesheet' id='".$handle."-css' href='".$href."' media='".$media."' />\n";
 $samples=[
  'canonical'=>$canonical,
  'extra-onload'=>str_replace(' id='," onload='unapproved()' id=",$canonical),
  'different-id'=>str_replace("-css'", "-evil-css'",$canonical),
  'unapproved-css'=>str_replace($href,'https://attacker.invalid/unapproved.css',$canonical),
  'extra-dom'=>$canonical."<script>unapproved()</script>",
  'changed-media'=>str_replace("media='".$media."'","media='print'",$canonical),
  'tracking-attribute'=>str_replace(' href='," data-track='1' href=",$canonical),
  'preload-not-style'=>str_replace('stylesheet','preload',$canonical),
 ];
 foreach ($samples as $label=>$tag) {
  $accepted=fv_r399_guard_style_tag($tag,$handle,$href,$media);
  $should_accept=$label==='canonical';
  if (($accepted!=='')!==$should_accept || ($should_accept && $accepted!==$canonical)) {fwrite(STDERR,"FAIL $handle $label\n");exit(1);}
  $cases[]=['handle'=>$handle,'case'=>$label,'allowed'=>$should_accept,'output'=>$accepted];
 }
}
echo json_encode(['scope'=>'PHP-STUB-TO-CHROMIUM-NO-WORDPRESS','cases'=>$cases],JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT)."\n";
