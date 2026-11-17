<?php
/** Exact R432 PHP + seven SHA-pinned parent objects; offline browser fixture only. */
define('ABSPATH', __DIR__);
require dirname(__DIR__).'/staging-custody-gate.php';
$campaign=['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'apollo_documentary_001'];
$root=dirname(__DIR__,2);
$styles=['apollo-r429/assets/bridge.css','apollo-r430/assets/educator-case-lab.css','apollo-r431/assets/evidence-notebook.css','apollo-r432/assets/custody-gate.css'];
$css='';foreach($styles as $f){$css.=file_get_contents($root.'/'.$f)."\n";}
$js=file_get_contents($root.'/apollo-r431/assets/evidence-notebook.js');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R432 source-chain fixture</title><style>',$css,'</style></head><body>';
echo fv_r432_render(1,$campaign), fv_r432_render(2,[]);
echo '<script>',$js,'</script></body></html>';
