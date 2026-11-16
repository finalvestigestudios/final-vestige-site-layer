<?php
// Synthetic structure-matched fixture. NOT the actual PR #158 NASA HTML.
define('ABSPATH', '/tmp');
require dirname(__DIR__) . '/staging-shortcode.php';
$cards = '';
for ($n = 1; $n <= 6; $n++) {
    $id = sprintf('%02d', $n);
    $topic = $n === 4 ? 'hatch' : 'oxygen';
    $cards .= '<article id="fv-ex2-ledger-apollo1-record-'.$id.'" data-fvx-record data-fvx-search="record '.$n.' '.$topic.'"><h2>Fixture evidence '.$n.'</h2><p>Demonstration record. No historical assertions.</p><details><summary>Open finding '.$n.'</summary><p id="fv-ex2-ledger-apollo1-finding-'.$id.'">This is a test disclosure.</p></details><a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/" rel="noopener noreferrer">NASA primary record</a></article>';
}
$base = '<section class="fv-ex2-ledger" data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title"><h1 id="fv-ex2-ledger-apollo1-title">Apollo Research Desk — synthetic fixture</h1><div data-fvx-tools hidden><label for="fv-ex2-ledger-apollo1-search">Search evidence</label><input type="search" id="fv-ex2-ledger-apollo1-search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid"><span role="status" aria-live="polite" data-fvx-status></span></div><div class="fv-ex2-ledger__grid" id="fv-ex2-ledger-apollo1-grid">'.$cards.'</div><p data-fvx-empty hidden>Nothing matched.</p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a></section>';
print('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R406 local synthetic fixture</title><link rel="stylesheet" href="/fixture.css"><link rel="stylesheet" href="/access.css"><script defer src="/r406.js"></script></head><body>');
for ($i=1; $i<=2; $i++) { print(fv_ex2_r406_namespace_markup($base, $i)); }
print('</body></html>');
