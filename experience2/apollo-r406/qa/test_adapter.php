<?php
// Standalone native PHP contract; no staging install, no WordPress writes.
define('ABSPATH', '/tmp');
$hooks = array();
function add_action($n, $fn, $p = 10) { $GLOBALS['hooks'][$n] = $fn; }
function add_shortcode($n, $fn) { $GLOBALS['hooks'][$n] = $fn; }
require dirname(__DIR__) . '/staging-shortcode.php';
$passed = 0;
function assertion($condition, $description) {
    global $passed;
    if (!$condition) { throw new RuntimeException('FAIL: ' . $description); }
    $passed++;
}
assertion(isset($hooks['fv_ex2_research_desk_r406']), 'separate shortcode registered');
assertion(isset($hooks['wp_enqueue_scripts']), 'page pre-enqueue hook registered');
assertion(!fv_ex2_r406_authorized(), 'default OFF');
assertion(strpos(fv_ex2_r406_shortcode(), 'Read the free Apollo 1 investigation') !== false, 'fail open to free article');
assertion(fv_ex2_r406_git_blob('/not/a/real/file') === null, 'missing file rejected');
assertion(fv_ex2_r406_assets_valid(__DIR__) === false, 'incomplete package rejected');
$markup = '<section aria-labelledby="fv-ex2-ledger-apollo1-title"><h1 id="fv-ex2-ledger-apollo1-title"></h1><label for="fv-ex2-ledger-apollo1-search"></label><input id="fv-ex2-ledger-apollo1-search" aria-controls="fv-ex2-ledger-apollo1-grid"><div id="fv-ex2-ledger-apollo1-grid"><article id="fv-ex2-ledger-apollo1-record-01"></article></div></section>';
$a = fv_ex2_r406_namespace_markup($markup,1);
$b = fv_ex2_r406_namespace_markup($markup,2);
assertion($a !== $b, 'server IDs unique across multiple instances');
assertion(strpos($a, 'fv-ex2-ledger-apollo1-r406-i1-title') !== false, 'first desk also namespaced');
assertion(strpos($b, 'fv-ex2-ledger-apollo1-r406-i2-record-01') !== false, 'second record deep-link stable');
assertion(strpos($a, 'for="fv-ex2-ledger-apollo1-r406-i1-search"') !== false, 'label remapped');
assertion(strpos($b, 'aria-controls="fv-ex2-ledger-apollo1-r406-i2-grid"') !== false, 'aria-controls remapped');
assertion(strpos($b, 'aria-labelledby="fv-ex2-ledger-apollo1-r406-i2-title"') !== false, 'aria-labelledby remapped');
assertion(strpos($a.$b, 'id="fv-ex2-ledger-apollo1-search"') === false, 'original ID absent');
$one = fv_ex2_r406_expected_blobs();
assertion(count($one) === 4, 'exactly four required assets');
assertion($one['templates/ledger.html'] === '403d128c57b9bc82dac7c619651689070edef86c', 'NASA ledger pinned');
assertion($one['assets/research-desk-r406.js'] === 'a925ef792a4f894208f88d8edb3a7b4620b3028f', 'JS pin exact');
assertion(strpos(fv_ex2_r406_fallback(), 'https://finalvestige.com/') !== false, 'fallback destination deterministic');
try { fv_ex2_r406_namespace_markup($markup,0); assertion(false, 'zero instance rejected'); }
catch (InvalidArgumentException $e) { $passed++; }
echo "PHP R406 PASS ".$passed."/".$passed." assertions\n";
