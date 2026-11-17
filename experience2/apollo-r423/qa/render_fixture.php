<?php
// Offline contract fixture. It is NOT the installed WordPress Research Desk or its full upstream template.
define('ABSPATH', __DIR__);
require_once dirname(__DIR__) . '/staging-research-desk-bridge.php';
$cards = '';
for ($i=1; $i<=6; $i++) {
    $n = sprintf('%02d', $i);
    $cards .= '<article id="fv-ex2-ledger-apollo1-record-' . $n . '" data-fvx-record data-fvx-search="oxygen investigation source ' . $n . '"><h3>Source ' . $n . '</h3><p>Original NASA source and limitation preserved.</p><details><summary>Read original finding</summary><p>Review source separately from inference.</p></details></article>';
}
$template = '<section data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title">'
 . '<h2 id="fv-ex2-ledger-apollo1-title">The proof and the gaps</h2>'
 . '<label for="fv-ex2-ledger-apollo1-search">Search</label>'
 . '<input id="fv-ex2-ledger-apollo1-search" data-fvx-search />'
 . '<div id="fv-ex2-ledger-apollo1-grid">' . $cards . '</div>'
 . '<a href="' . FV_R423_ARTICLE . '">Read the original Apollo 1 investigation</a></section>';
$count = isset($argv[1]) ? max(1, min(2,(int)$argv[1])) : 2;
$css = file_get_contents(dirname(__DIR__) . '/assets/bridge.css');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R423 offline fixture</title><style>' . $css . '</style></head><body>';
for ($i=1;$i<=$count;$i++) echo fv_r423_render($template,$i);
echo '</body></html>';
