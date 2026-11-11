<?php
require __DIR__ . '/../review-custody.php';
$state = isset($argv[1]) ? $argv[1] : 'pending';
$records = [];
if ($state === 'review-recorded') {
  foreach (['board','chronology'] as $k) $records[$k] = ['state'=>'review-recorded','receipt_sha256'=>str_repeat('a',64),'reviewer'=>'Example editor','review_date'=>'2026-11-10'];
}
if ($state === 'invalid') $records = ['board'=>['state'=>'review-recorded','reviewer'=>'','review_date'=>'2026-13-99','receipt_sha256'=>'fake']];
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>FV Apollo R273 Staging Preview — Not Live</title><style><?php echo file_get_contents(__DIR__.'/../assets/review-custody.css'); ?></style><style>body{margin:0;background:#0b0d10;color:#f1e8d6;font:16px/1.5 system-ui,sans-serif}main>h1{padding:0 1rem;max-width:75rem;margin:1.5rem auto;font-size:1.5rem}</style></head><body><main><h1>Staging only: Apollo editorial review transparency</h1><?php echo fv_ex2_r273_review_panel($records); ?></main></body></html>
