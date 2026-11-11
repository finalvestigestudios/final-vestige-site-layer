<?php
/** R290 native authority provenance navigation + historical regression; no WordPress installation or network writes. */
define('ABSPATH', '/offline/');
function add_action($event, $callback, $priority=10) {}
function add_shortcode($name,$callback) {}
function plugins_url($path,$file) { return '/offline/'.$path; }
function wp_style_is($name,$status) { return true; }
require __DIR__.'/../../apollo-r281/apollo-source-experience.php';
$checked=0;
function verify($name,$ok) {
    global $checked;
    if (!$ok) { throw new RuntimeException('FAIL '.$name); }
    ++$checked; echo "$name PASS\n";
}
$events=fv_r281_events();
$ledger=fv_r289_authority_ledger();
$sources=fv_r288_source_reconciliation();
verify('r289_authority_custody_sha_pin',fv_r289_authority_ledger_valid($ledger));
verify('r289_four_date_actions',array_column($ledger,'date')===['1967-01-27','1967-01-28','1967-01-31','1967-02-03']);
verify('r289_memorandum_date_distinguished',str_contains($ledger[2]['finding'],'memorandum dated January 28'));
foreach (['date','label','finding','boundary','source','url'] as $field) {
 $bad=$ledger;$bad[2][$field].=' TAMPER';verify('r289_reject_mutation_'.$field,!fv_r289_authority_ledger_valid($bad));
}
verify('source_reconciliation_sha_pin',fv_r288_reconciliation_valid($sources));
verify('authority_dates_visible',str_contains($sources[0]['statement'],'January 27, 1967') && str_contains($sources[1]['statement'],'January 28, 1967'));
verify('source_allowlist', $sources[0]['url']===FV_R288_BOARD_NARRATIVE && $sources[1]['url']===FV_R288_NASA_SAFETY);
foreach (['statement','boundary','authority'] as $key) { $bad=$sources;$bad[0][$key].=' UNREVIEWED';verify('reject_mutated_'.$key,!fv_r288_reconciliation_valid($bad)); }
$bad=$sources; $bad[1]['url']='https://attacker.invalid';verify('reject_external_date_provenance',!fv_r288_reconciliation_valid($bad));
$bad=$sources;unset($bad[1]);verify('reject_missing_date_provenance',!fv_r288_reconciliation_valid($bad));
verify('reviewed_staging_digest_valid',fv_r281_valid_records($events));
verify('first_date_fire', $events[0]['date']==='1967-01-27');
verify('board_meeting_jan_28', $events[1]['date']==='1967-01-28' && str_contains($events[1]['statement'],'convened at Kennedy Space Center on January 28, 1967'));
verify('authorizing_date_distinguished',str_contains($events[1]['boundary'],'later NASA safety summary'));
verify('board_proceedings_primary', $events[1]['source_url']==='https://www.nasa.gov/history/Apollo204/proceed.html' && str_contains($events[1]['source_type'],'primary'));
verify('secondary_summary_no_longer_mislabels_formation', !str_contains($events[1]['statement'], 'established the Apollo 204 Review Board') && !str_contains($events[1]['source_url'],'sma.nasa.gov'));
verify('final_report_ignition_uncertainty',str_contains($events[2]['statement'],'most probable') && str_contains($events[2]['statement'],'without conclusively'));
$bad=$events;$bad[1]['statement']='NASA established the Apollo 204 Review Board on January 28.';
verify('mutation_rejected',!fv_r281_valid_records($bad));
$bad=$events;$bad[1]['source_url']='https://example.invalid/';
verify('source_domain_injection_rejected',!fv_r281_valid_records($bad));
$out=fv_r281_render(['editorial'=>'approved','merchant'=>'https://example.invalid/']);
verify('render_pending_and_no_commerce',str_contains($out,'data-fv-evidence-status="editorial-review-pending"') && !str_contains($out,'https://example.invalid'));
verify('render_uses_primary_board_proceedings', substr_count($out,'href="'.FV_R287_NASA_PROCEEDINGS.'"')===4 && $events[1]['source_url']===FV_R287_NASA_PROCEEDINGS);
verify('date_disagreement_retains_pending_review',str_contains($out,'data-fv-date-review="editorial-review-pending"') && substr_count($out,'Read source at NASA')===2);
verify('r289_four_custody_records_render',substr_count($out,'fv-r281__authority-date')===4);
verify('r289_distinct_date_provenance_links',substr_count($out,'Inspect Original Review Board narrative at NASA')===2&&substr_count($out,'Inspect 1967 Review Board proceedings at NASA')===2);
verify('single_free_investigation_action',substr_count($out,'href="'.FV_R281_FREE.'"')===1 && substr_count($out,'Read the free Apollo 1 investigation')===1);
verify('source_navigation_native',substr_count($out,'class="fv-r281__source-jump"')===3 && substr_count($out,'class="fv-r281__source-return"')===3);
verify('authority_fragment_unique',substr_count($out,'id="fv-r281-1-authority-')===4);
verify('board_claim_to_authority_native_link',substr_count($out,'class="fv-r281__authority-jump"')===1 && str_contains($out,'href="#fv-r281-1-authority-1"'));
verify('authority_entries_return_to_claim',substr_count($out,'href="#fv-r281-1-event-2"')===6 && substr_count($out,'class="fv-r281__authority-return"')===4);
verify('authority_target_not_tab_stop',substr_count($out,'tabindex="-1"')===10 && !str_contains($out,'tabindex="0"'));
verify('no_images_or_map_pins',!str_contains($out,'<img') && !str_contains($out,'data-lat') && !str_contains($out,'<script'));
echo "R290 authority navigation and chronology source contract $checked/$checked PASS (offline PHP, editorial status pending)\n";
