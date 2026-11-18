<?php
require dirname(__DIR__) . '/handoff.php';
$html=fv_r446_render((string)($_SERVER['QUERY_STRING'] ?? 'utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_pilot_2026_11&utm_content=AbCdE_12345'));
$root=dirname(__DIR__,2).'/apollo-r444/';
?>
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Apollo R446 isolated QA fixture — not production</title>
<style>body{margin:0;background:#131516;color:#f1f1e8;font:16px/1.6 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:18px}a{color:#f4c978} :focus-visible{outline:3px solid #ffc24d;outline-offset:3px}</style>
<style><?php echo file_get_contents($root.'assets/review-panel.css'); ?></style>
</head><body><main><h1>FV Apollo evidence / offline fixture</h1><?php echo $html; ?></main>
<script><?php echo file_get_contents($root.'assets/review-panel.js'); ?></script></body></html>
