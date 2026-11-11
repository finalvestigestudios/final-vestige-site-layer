<?php
/** R296: actual-PHP, non-network, source-custody and one-action regression. */
define('ABSPATH', __DIR__);
function plugins_url($path, $file) { return '/assets/'.basename($path); }
require dirname(__DIR__, 2) . '/apollo-r281/apollo-source-experience.php';
function claim($value, $label) { if (!$value) { fwrite(STDERR, "FAIL: $label\n"); exit(1); } }
$html=fv_r281_render();
claim(str_contains($html, '<details class="fv-r296__date-disclosure">'), 'native source comparison');
claim(str_contains($html, 'Unresolved source distinction:'), 'conflict remains visible');
claim(str_contains($html, 'Editorial reconciliation remains pending.'), 'review boundary remains visible');
claim(substr_count($html, 'class="fv-r281__reconciliation-list"')===1, 'one reconciled source list');
claim(substr_count($html, 'href="'.FV_R295_NASA_MEMORANDUM.'"')===1, 'memorandum linked once');
claim(substr_count($html, 'href="'.FV_R281_FREE.'"')===1, 'one contextual next action');
claim(fv_r288_reconciliation_valid(fv_r288_source_reconciliation()), 'sealed NASA source ledger');
claim(fv_r289_authority_ledger_valid(fv_r289_authority_ledger()), 'sealed four-action chronology');
claim(!str_contains($html, '<script') && !str_contains($html, '<img'), 'no JS or media');
claim(!str_contains(strtolower($html), 'affiliate'), 'no affiliate promotion');
echo "PASS 10/10 R296 PHP source contract\n";
