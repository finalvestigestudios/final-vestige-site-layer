<?php
/** R295: actual staging PHP source assertions (no installed WordPress needed). */
define('ABSPATH', __DIR__);
function plugins_url($path, $file) { return '/staging/' . $path; }
require dirname(__DIR__, 2) . '/apollo-r281/apollo-source-experience.php';
function check_r295($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }
$records = fv_r288_source_reconciliation();
check_r295(count($records) === 3, 'three distinct but related NASA records');
check_r295(fv_r288_reconciliation_valid($records), 'reviewed source digest valid');
check_r295($records[2]['url'] === FV_R295_NASA_MEMORANDUM, 'NASA memorandum URL pinned');
check_r295(str_contains($records[2]['boundary'], 'does not display a separate signed date'), 'uncertain date acknowledged');
check_r295(str_contains($records[2]['boundary'], 'not independent confirmation'), 'source dependence acknowledged');
$changed = $records;
$changed[2]['statement'] .= ' additional unsupported text';
check_r295(!fv_r288_reconciliation_valid($changed), 'tampering rejected');
$html = fv_r281_render();
check_r295(substr_count($html, 'href="'.FV_R295_NASA_MEMORANDUM.'"') === 1, 'single memorandum link');
check_r295(substr_count($html, 'href="'.FV_R281_FREE.'"') === 1, 'one relevant next action');
check_r295(!str_contains($html, '<script') && !str_contains($html, '<img'), 'no remote JS or unreviewed image');
check_r295(!str_contains(strtolower($html), 'mini-museum'), 'no inserted commerce');
check_r295(str_contains($html, 'editorial-review-pending'), 'historical editorial hold retained');
echo "PASS 11/11 R295 source custody assertions\n";
