<?php
/** Local only. Actual PHP component rendered into navigable file; never WordPress staging. */
define('ABSPATH', '/fixture/');
require dirname(__DIR__).'/staging-source-proof.php';
$root = dirname(__DIR__, 2);
$css = [
  'apollo-r429/assets/bridge.css',
  'apollo-r430/assets/educator-case-lab.css',
  'apollo-r431/assets/evidence-notebook.css',
  'apollo-r432/assets/custody-gate.css',
  'apollo-r433/assets/claim-bridge.css',
  'apollo-r434/assets/research-route.css',
  'apollo-r435/assets/photo-custody.css',
  'apollo-r436/assets/source-proof.css'
];
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R436 source-photo custody / local fixture</title>
<style>html{color-scheme:dark;font-family:system-ui}body{margin:0}main{max-width:100%;margin:auto} .fixture-sep{margin:5rem 0}</style>
<?php foreach ($css as $f): ?><style data-css-file="<?=htmlspecialchars($f, ENT_QUOTES)?>"><?=file_get_contents($root.'/'.$f)?></style><?php endforeach; ?>
</head><body><main>
<?=fv_r436_render(1, ['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'fixture_not_a_published_asset'])?>
<div class="fixture-sep" aria-hidden="true"></div>
<?=fv_r436_render(2, [])?>
</main><script><?=file_get_contents($root.'/apollo-r431/assets/evidence-notebook.js')?></script></body></html>
