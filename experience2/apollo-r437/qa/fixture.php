<?php
/** Local executable HTTP fixture. No WP bootstrap, no network calls, no staged installation. */
define('ABSPATH', '/local-qa/');
require dirname(__DIR__).'/staging-chronology-audit.php';
$root=dirname(__DIR__,2);
$css=[
 'apollo-r429/assets/bridge.css','apollo-r430/assets/educator-case-lab.css',
 'apollo-r431/assets/evidence-notebook.css','apollo-r432/assets/custody-gate.css',
 'apollo-r433/assets/claim-bridge.css','apollo-r434/assets/research-route.css',
 'apollo-r435/assets/photo-custody.css','apollo-r436/assets/source-proof.css',
 'apollo-r437/assets/chronology-audit.css'
];
?><!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo Evidence Chronology / real localhost HTTP QA</title>
<style>html{color-scheme:dark}body{margin:0;font-family:system-ui;background:#111}main{max-width:100%;margin:auto}.fixture-sep{margin:2rem 0}</style>
<?php foreach($css as $path): ?><style data-source="<?=htmlspecialchars($path,ENT_QUOTES)?>"><?=file_get_contents($root.'/'.$path)?></style><?php endforeach; ?>
</head><body><main>
<?=fv_r437_render(1,['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'fixture_not_a_published_asset'])?>
<div class="fixture-sep" aria-hidden="true"></div>
<?=fv_r437_render(2,[])?>
</main><script><?=file_get_contents($root.'/apollo-r431/assets/evidence-notebook.js')?></script><script><?=file_get_contents($root.'/apollo-r437/assets/chronology-audit.js')?></script></body></html>
