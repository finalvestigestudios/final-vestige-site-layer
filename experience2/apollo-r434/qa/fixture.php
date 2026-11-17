<?php
/** Render actual SHA-pinned R429-R434 PHP locally. Not a WordPress staging claim. */
const ABSPATH = '/test/';
require dirname(__DIR__).'/staging-research-route.php';
$query = ['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'fixture_not_a_published_asset'];
if (getenv('FV_R434_ONLY_FALLBACK') === '1') { echo fv_r434_fallback(); exit; }
$root = dirname(__DIR__,2);
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R434 exact-source local fixture</title><style><?php
foreach (['apollo-r429/assets/bridge.css','apollo-r430/assets/educator-case-lab.css','apollo-r431/assets/evidence-notebook.css','apollo-r432/assets/custody-gate.css','apollo-r433/assets/claim-bridge.css','apollo-r434/assets/research-route.css'] as $relative) echo file_get_contents($root.'/'.$relative)."\n";
?></style></head><body><main><?php echo fv_r434_render(1, $query),fv_r434_render(2, []); ?></main><script><?php echo file_get_contents($root.'/apollo-r431/assets/evidence-notebook.js'); ?></script></body></html>
