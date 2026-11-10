<?php
/** CLI-only WordPress filter simulation, exercising actual R270 plugin functions. */
define('ABSPATH', '/test/');
$filters = [];
function add_filter($tag, $callback, $priority, $args) { global $filters; $filters[] = [$tag,$callback,$priority,$args]; }
require __DIR__ . '/../rd-instance-scope.php';
function fixture() {
    $s = '<section data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title">'
       . '<h2 id="fv-ex2-ledger-apollo1-title">NASA evidence</h2>'
       . '<label for="fv-ex2-ledger-apollo1-search">Search</label>'
       . '<input id="fv-ex2-ledger-apollo1-search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid">'
       . '<div id="fv-ex2-ledger-apollo1-grid">';
    for ($i=1; $i<=6; $i++) {
        $id = 'fv-ex2-ledger-apollo1-record-' . sprintf('%02d', $i);
        $s .= '<article id="' . $id . '" data-fvx-record data-fvx-search="Apollo NASA record ' . $i . '">'
        . '<details><summary>Review the underlying finding</summary><p>Finding '. $i .'</p></details>'
        . '<a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">NASA source</a></article>';
    }
    return $s . '</div><p data-fvx-empty hidden>No evidence</p><div data-fvx-tools hidden><p data-fvx-status></p></div></section>';
}
$f = fixture();
$first = fv_ex2_r270_scope_desk($f, 'fv_ex2_research_desk', [], []);
$second = fv_ex2_r270_scope_desk($f, 'fv_ex2_research_desk', [], []);
$third = fv_ex2_r270_scope_desk($f, 'fv_ex2_research_desk', [], []);
$other = fv_ex2_r270_scope_desk($f,'unrelated_shortcode',[],[]);
$broken = fv_ex2_r270_scope_desk(str_replace('data-fvx-record', 'data-unknown-record', $f), 'fv_ex2_research_desk', [], []);
if ($first !== $f || $other !== $f || strpos($second, '--fvx-2') === false ||
    strpos($third, '--fvx-3') === false || $broken !== str_replace('data-fvx-record', 'data-unknown-record', $f)) {
    fwrite(STDERR, "Scope contract failed\n"); exit(1);
}
$joined = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main>' . $first.$second.$third . '</main></body></html>';
preg_match_all('/\bid="([^"]+)"/', $joined, $m);
if (count($m[1]) !== count(array_unique($m[1])) || count($m[1]) !== 27) {
    fwrite(STDERR, "Duplicate IDs or missing records\n"); exit(1);
}
foreach (['for','aria-labelledby','aria-controls'] as $attr) {
    preg_match_all('/\b'. $attr .'="([^"]+)"/', $joined, $refs);
    foreach ($refs[1] as $id) if (!in_array($id,$m[1],true)) { fwrite(STDERR,"Unresolved IDREF: $id\n");exit(1); }
}
if (substr_count($joined,'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/') !== 18) { exit(1); }
if (!empty($filters) && $filters[0][0] === 'do_shortcode_tag') { echo $joined; } else { exit(1); }
