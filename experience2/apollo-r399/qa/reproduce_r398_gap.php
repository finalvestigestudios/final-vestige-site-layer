<?php
/** Reproduces R398's local HTML-tag inspection gap; NOT a production exploit. */
define('ABSPATH', '/tmp/fv-r398-witness');
$GLOBALS['fv_r398_approved_styles']=[
 'fv-apollo-r384-gallery' => 'https://staging.fv.example/wp-content/plugins/final-vestige-site-layer/experience2/apollo-r384/assets/gallery.css'
];
require __DIR__.'/../../apollo-r398/staging-canonical-delivery.php';
$href=$GLOBALS['fv_r398_approved_styles']['fv-apollo-r384-gallery'].'?ver=r384-reviewed-1';
$handle='fv-apollo-r384-gallery';
$altered="<link rel='stylesheet' id='".$handle."-css' onload='unapproved()' href='".$href."' media='all' />\n";
if (fv_r398_guard_style_src($href,$handle)!==$href || strpos($altered,'onload=')===false) { exit(1); }
// R398 exposes no style_loader_tag inspection hook; full HTML alteration
// is outside its guard despite a valid source URL.
echo "PASS: R398 local source URL guard accepts valid href but cannot assess independently mutated link HTML; R399 adds final-tag gate (NOT installed WP).\n";
