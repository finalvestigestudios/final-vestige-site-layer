<?php
/** Synthetic text fixture — NOT PR #158 NASA source content or a production page. */
define('ABSPATH', '/tmp');
require dirname(__DIR__) . '/staging-shortcode.php';
$records = '';
for ($i = 1; $i <= 6; $i++) {
    $id = sprintf('%02d',$i);
    $topic = ($i === 4 ? 'hatch' : 'oxygen');
    $records .= '<article id="fv-ex2-ledger-apollo1-record-' . $id . '" data-fvx-record data-fvx-search="fixture record ' . $i . ' ' . $topic . '"><h3>Test-only record ' . $i . '</h3><p>Fixture text is not a historical claim.</p><p class="fv-ex2-ledger__boundary">EVIDENCE LIMITATION: synthetic.</p><details><summary>Review this test disclosure</summary><p id="fv-ex2-ledger-apollo1-finding-' . $id . '">No real NASA copy in test.</p></details><a href="' . FV_R407_BOARD . '">NASA original Review Board</a></article>';
}
$template = '<section class="fv-ex2-ledger" data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title"><div class="fv-ex2-ledger__wrap"><h2 id="fv-ex2-ledger-apollo1-title">Synthetic evidence fixture</h2><div data-fvx-tools hidden><label for="fv-ex2-ledger-apollo1-search">Search source records</label><input id="fv-ex2-ledger-apollo1-search" type="search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid"><span data-fvx-status role="status" aria-live="polite"></span></div><div class="fv-ex2-ledger__grid" id="fv-ex2-ledger-apollo1-grid">' . $records . '</div><p data-fvx-empty hidden>No fixture matches.</p><footer><a href="' . FV_R407_FREE_ARTICLE . '">Read the original Apollo investigation</a></footer></div></section>';
print '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R407 synthetic-only QA fixture</title></head><body>';
for ($i = 1; $i <= 3; $i++) {
    $markup = fv_r407_namespace_markup($template, $i);
    if ($i === 1) {
        // First instance deliberately malformed: R406 previously allowed one bad selector to stop all later initialization.
        $markup = str_replace('aria-controls="fv-ex2-ledger-apollo1-r407-i1-grid"', 'aria-controls="bad[selector"', $markup);
    }
    print '<div class="fv-r407" data-fv-r407>' . fv_r407_chronology($i) . $markup . '</div>';
}
print '</body></html>';
