<?php
define('ABSPATH', '/tmp');
require dirname(__DIR__) . '/staging-shortcode.php';
$assertions = 0;
function check407($ok, $why) { global $assertions; $assertions++; if (!$ok) throw new Exception($why); }
function fixture407(): string {
    $records = '';
    for ($i = 1; $i <= 6; $i++) {
        $records .= '<article id="fv-ex2-ledger-apollo1-record-0' . $i . '" data-fvx-record data-fvx-search="fixture '. $i . '"><p>EVIDENCE LIMITATION</p><details><summary>Finding</summary><p>Fixture text</p></details>'
            . '<a href="https://www.nasa.gov/image-detail/example-' . $i . '/">NASA record</a>'
            . '<a href="' . FV_R407_BOARD . '">Review Board</a></article>';
    }
    return '<section data-fvx-ledger><label for="fv-ex2-ledger-apollo1-search">Search</label><input id="fv-ex2-ledger-apollo1-search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid"><div id="fv-ex2-ledger-apollo1-grid">'
        . $records . '</div><p>The spark was never conclusively identified. The timeline has not interpolated sensor measurements.</p>'
        . '<a href="' . FV_R407_BOARD . '">Original report</a><a href="' . FV_R407_FREE_ARTICLE . '">Free investigation</a></section>';
}
$html = fixture407();
check407(fv_r407_contract_valid($html), 'valid six-record structure');
check407(!fv_r407_contract_valid(str_replace('data-fvx-record', 'data-unreviewed', $html)), 'must reject missing six records');
check407(!fv_r407_contract_valid(str_replace('EVIDENCE LIMITATION', 'unmarked', $html)), 'must reject removed limitations');
check407(!fv_r407_contract_valid(str_replace('The spark was never conclusively identified.', 'The exact spark was identified.', $html)), 'must reject uncertainty drift');
check407(!fv_r407_contract_valid(str_replace('not interpolated sensor measurements', 'simulated precision', $html)), 'must reject fake telemetry precision');
check407(!fv_r407_contract_valid(str_replace('https://www.nasa.gov/image-detail/example-1/', 'https://private-sponsor.example/pay/', $html)), 'must reject new commerce');
check407(!fv_r407_contract_valid(str_replace(FV_R407_FREE_ARTICLE, 'https://example.org/buy/', $html)), 'must reject CTA switch');
check407(!fv_r407_contract_valid(str_replace('</section>', '<script>1</script></section>', $html)), 'must reject scripts');
check407(!fv_r407_contract_valid(str_replace('</section>', '<img src="https://www.nasa.gov/x"></section>', $html)), 'must reject unlicensed media');
check407(!fv_r407_contract_valid(str_replace('</section>', '<a href="https://www.nasa.gov/another">extra</a></section>', $html)), 'must reject unapproved links');
check407(!fv_r407_contract_valid(str_replace('data-fvx-search="fixture 2"', 'data-fvx-query="fixture 2"', $html)), 'must reject missing indexed field');
check407(!fv_r407_contract_valid(str_replace(FV_R407_FREE_ARTICLE, FV_R407_FREE_ARTICLE . '?utm_campaign=invalid', $html)), 'must reject unapproved CTA query');
check407(strpos(fv_r407_namespace_markup($html, 2), 'fv-ex2-ledger-apollo1-r407-i2-record-01') !== false, 'namespaced record 2');
check407(strpos(fv_r407_namespace_markup($html, 1), 'fv-ex2-ledger-apollo1-r407-i2-') === false, 'no accidental cross instance');
check407(substr_count(fv_r407_chronology(1), 'href="#fv-ex2-ledger-apollo1-r407-i1-record-') === 4, 'four source linked chronology markers');
check407(strpos(fv_r407_chronology(1), 'No geographic') !== false, 'no false map pins');
check407(!fv_r407_assets_valid(dirname(__DIR__)), 'must not admit incomplete installed package');
check407(!fv_r407_authorized(), 'must be disabled by default');
check407(strpos(fv_r407_shortcode(), FV_R407_FREE_ARTICLE) !== false, 'fail-open free investigation link');
foreach (array('assets/research-desk-r407.js','assets/chronology.css') as $rel) {
    check407(fv_r407_git_blob(dirname(__DIR__) . '/' . $rel) === fv_r407_expected_blobs()[$rel], 'exact new source blob ' . $rel);
}
echo 'R407 PHP assertions PASS: ' . $assertions . '/' . $assertions . "\n";
