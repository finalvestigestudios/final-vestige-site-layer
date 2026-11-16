<?php
/** Deterministic witness: prior R397 admits a dot-segment path at source admission. */
define('ABSPATH','/tmp/fv-r398-admission-witness');
require __DIR__.'/../../apollo-r397/staging-delivery-guard.php';
require __DIR__.'/../staging-canonical-delivery.php';
$home = 'https://staging.fv.example/';
$legacy = 'https://staging.fv.example/wp-content/plugins/site/experience2/apollo-r397/../apollo-r384/assets/gallery.css';
$canonicalDir = 'https://staging.fv.example/wp-content/plugins/site/experience2/apollo-r398';
if (!fv_r397_reviewed_asset_url($legacy,$home,'apollo-r384/assets/gallery.css')) { throw new RuntimeException('R397 witness not reproduced'); }
if (fv_r398_asset_directory($canonicalDir,$home) !== 'https://staging.fv.example/wp-content/plugins/site/experience2') { throw new RuntimeException('R398 canonical sibling path failed'); }
$urls = fv_r398_canonical_css(fv_r398_asset_directory($canonicalDir,$home));
if (count($urls)!==2 || strpos($urls['fv-apollo-r384-gallery'],'/../')!==false || strpos($urls['fv-apollo-r395-mobile-fit'],'/../')!==false) { throw new RuntimeException('R398 left a dot segment'); }
echo "PASS R397 requires '/../' in its accepted CSS URL; R398 two derived CSS paths contain zero traversal; this is an integration portability gap, NOT a demonstrated exploit.\n";
