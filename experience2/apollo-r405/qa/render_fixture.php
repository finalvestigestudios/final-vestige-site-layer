<?php
// Browser-only structural fixture. NOT NASA text, not the reviewed #158 HTML.
define('ABSPATH', '/tmp');
require dirname(__DIR__) . '/staging-shortcode.php';
$cards='';
for ($n=1; $n<=6; $n++) {
  $i=sprintf('%02d',$n);
  $cards.='<article data-fvx-record data-fvx-search="source '.$n.' '.($n===4?'hatch':'oxygen').'" id="fv-ex2-ledger-apollo1-record-'.$i.'"><h2>Structural fixture record '.$n.'</h2><p>This is synthetic test text, not an Apollo claim.</p><details><summary>Source limitation</summary><p>No historical inferences from fixtures.</p></details><a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">NASA primary record</a></article>';
}
$html='<section class="fv-ex2-ledger" data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title"><h1 id="fv-ex2-ledger-apollo1-title">Research Desk — structural fixture</h1><div data-fvx-tools hidden><label for="fv-ex2-ledger-apollo1-search">Search source records</label><input id="fv-ex2-ledger-apollo1-search" type="search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid"><span data-fvx-status role="status" aria-live="polite"></span></div><div id="fv-ex2-ledger-apollo1-grid" class="fv-ex2-ledger__grid">'.$cards.'</div><p data-fvx-empty hidden>No matching evidence records.</p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read free investigation</a></section>';
print('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>');
print(fv_ex2_r405_namespace_markup($html,1));
print(fv_ex2_r405_namespace_markup($html,2));
print('</body></html>');
