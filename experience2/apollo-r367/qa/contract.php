<?php
/** R367 exact-claim + whole-sequence mutation tests (no WP installation). */
declare(strict_types=1);
define('ABSPATH', __DIR__);
require_once dirname(__DIR__, 2) . '/apollo-r365/chrono-rail.php';
require_once dirname(__DIR__) . '/sealed-chronology.php';
function ck(bool $pass, string $why): void { global $assertions; $assertions++; if (!$pass) { throw new RuntimeException($why); } }
$assertions = 0;
$rows = fv_apollo_r365_rows();
ck(fv_apollo_r367_is_sealed($rows), 'Canonical sequence rejected');
$ok = fv_apollo_r367_render($rows);
ck(substr_count($ok, 'data-fv-nasa-source') === 4, 'Valid sources missing');
ck(substr_count($ok, 'data-fv-source-drawer') === 4, 'Source drawers missing');
ck(substr_count($ok, 'data-fv-free-cta') === 1, 'Unexpected free CTA count');
ck(!str_contains($ok, 'href="https://payhip.com/'), 'Unverified commerce link');
ck(!str_contains($ok, 'https://www.google-analytics.com/'), 'Duplicate analytics');
foreach ($rows as $index => $row) {
    foreach ($row as $field => $value) {
        $bad = $rows;
        $bad[$index][$field] = $value . ' (altered)';
        ck(!fv_apollo_r367_is_sealed($bad), "Mutation accepted at $index.$field");
        $html = fv_apollo_r367_render($bad);
        ck(substr_count($html, 'data-fv-nasa-source') === 0, "Altered citation leaked at $index.$field");
        ck(substr_count($html, 'data-fv-free-cta') === 1, "Free access missing at $index.$field");
    }
}
for ($a=0; $a<count($rows); $a++) {
    for ($b=$a+1; $b<count($rows); $b++) {
        $bad=$rows; [$bad[$a],$bad[$b]] = [$bad[$b],$bad[$a]];
        ck(!fv_apollo_r367_is_sealed($bad), "Swap $a/$b accepted");
        ck(!str_contains(fv_apollo_r367_render($bad),'data-fv-nasa-source'), "Swap $a/$b citation leaked");
    }
    $bad=$rows; $bad[$a]=$rows[($a+1)%count($rows)];
    ck(!fv_apollo_r367_is_sealed($bad), "Duplicate $a accepted");
    $bad=$rows; array_splice($bad,$a,1);
    ck(!fv_apollo_r367_is_sealed($bad), "Deletion $a accepted");
}
foreach ([null,'',false,123,[],[$rows[0]],array_reverse($rows),array_merge($rows,[$rows[0]])] as $bad) {
    ck(!fv_apollo_r367_is_sealed($bad),'Bad set accepted');
    ck(!str_contains(fv_apollo_r367_render($bad),'data-fv-nasa-source'),'Bad set leaked citations');
}
ck(substr_count(fv_apollo_r367_shortcode(), 'data-fv-nasa-source') === 4, 'Shortcode lost canonical records');
echo json_encode(['passed'=>true,'assertions'=>$assertions,'source_count'=>4,'checks'=>'all reviewed fields, source links, source integrity, swaps, duplicates, deletions, missing/extra records, no paid CTA'],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES) . "\n";
