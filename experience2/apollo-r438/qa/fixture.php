<?php
/** Actual PHP component render fixture; not a WP installation. */
define('ABSPATH','/local-ex2/');
require dirname(__DIR__).'/staging-source-atlas.php';
$base=dirname(__DIR__,2);
$files=['apollo-r429/assets/bridge.css','apollo-r430/assets/educator-case-lab.css','apollo-r431/assets/evidence-notebook.css','apollo-r432/assets/custody-gate.css','apollo-r433/assets/claim-bridge.css','apollo-r434/assets/research-route.css','apollo-r435/assets/photo-custody.css','apollo-r436/assets/source-proof.css','apollo-r437/assets/chronology-audit.css','apollo-r438/assets/source-atlas.css'];
?><!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R438 independent evidence atlas QA fixture</title><style>body{margin:0;background:#10110f;color:#f2f0e8;font-family:system-ui}main{width:100%}</style>
<?php foreach($files as $f): ?><style data-file="<?=htmlspecialchars($f,ENT_QUOTES)?>"><?=file_get_contents($base.'/'.$f)?></style><?php endforeach; ?></head><body><main>
<?=fv_r438_render(1,['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'qa_not_published'])?>
<?=fv_r438_render(2,[])?></main>
<script><?=file_get_contents($base.'/apollo-r431/assets/evidence-notebook.js')?></script>
<script><?=file_get_contents($base.'/apollo-r437/assets/chronology-audit.js')?></script>
<script><?=file_get_contents($base.'/apollo-r438/assets/source-atlas.js')?></script></body></html>
