<?php
/** R274 CLI-only fixture. Three exact R273 panels with independent statuses. */
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require __DIR__ . '/../../apollo-r273/review-custody.php';
$known = ['state'=>'review-recorded', 'receipt_sha256'=>str_repeat('a', 64), 'reviewer'=>'Example editor (fixture only)', 'review_date'=>'2026-11-10'];
$cases = [[], ['board'=>$known], ['board'=>$known,'chronology'=>$known]];
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo editorial review custody — three-instance staging test only</title><style><?php echo file_get_contents(__DIR__.'/../../apollo-r273/assets/review-custody.css'); ?></style><style>html{scrollbar-width:none}html::-webkit-scrollbar{display:none}body{margin:0;background:#0b0d10;color:#f1e8d6;font:16px/1.5 system-ui,sans-serif}main>h1{padding:0 1rem;max-width:75rem;margin:1.5rem auto;font-size:clamp(1.25rem,4vw,2rem);overflow-wrap:anywhere}.r274-test-note{max-width:74rem;margin:auto;padding:0 1rem}</style></head><body><main><h1>Review receipt custody / internal staging QA</h1><p class="r274-test-note">Fixture receipts are synthetic, do not authenticate reviews and grant no publishing authorization.</p><?php foreach ($cases as $records) echo fv_ex2_r273_review_panel($records); ?></main></body></html>
