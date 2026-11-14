<?php
/** R349 local PHP preflight: no WordPress installation or network required. */
define('ABSPATH', true);
require_once dirname(__DIR__) . '/source-policy.php';
require_once dirname(__DIR__, 2) . '/apollo-r348/source-custody.php';
function fv_r349_check(bool $ok, string $message): void {
    if (!$ok) { fwrite(STDERR, "FAIL: $message\n"); exit(1); }
    echo "PASS: $message\n";
}
$approved = fv_apollo_r349_approved_sources();
fv_r349_check(count($approved) === 8, 'eight reviewed exact source-page identities');
fv_r349_check($approved === fv_apollo_r348_approved_pages(), 'R348 and all renderers share one immutable registry');
foreach ($approved as $url=>$label) {
    fv_r349_check(strpos(fv_apollo_r349_source_link($url, $label), 'href="'.$url.'"') !== false, 'approved NASA page rendered: '.$label);
}
foreach (array(
    'javascript:alert(1)',
    'https://www.nasa.gov.evil.invalid/path',
    'https://www.nasa.gov/image-detail/unreviewed/',
    'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html?redirect=1',
    'http://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html',
    'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html#fragment',
) as $bad) {
    $html = fv_apollo_r349_source_link($bad, 'Needs review', array('onclick'=>'alert(1)'));
    fv_r349_check(strpos($html, 'href=') === false && strpos($html, 'onclick') === false && strpos($html, 'withheld') !== false, 'unreviewed identity quarantined');
}
$full = fv_apollo_r348_experience_shortcode();
fv_r349_check(substr_count($full, 'data-fv-custody-source') === 8, 'eight custody source links');
fv_r349_check(substr_count($full, 'data-fv-apollo-source-link=') === 13, '13 approved evidence-index links');
fv_r349_check(substr_count($full, 'data-fv-r339-source=') === 6, 'six chronology source links');
fv_r349_check(substr_count($full, 'data-fv-r340-source=') === 4, 'four gallery source links');
fv_r349_check(substr_count($full, 'data-fv-apollo-primary-source=') === 3, 'three source plates');
fv_r349_check(substr_count($full, 'data-fv-r339-cta="editorial"') === 1, 'one unchanged free editorial continuation');
fv_r349_check(strpos($full, 'data-fv-source-review-required') === false, 'no false quarantine for reviewed sources');
echo "R349 PHP POLICY PREFLIGHT: PASS\n";
