<?php
const ABSPATH='/test/';
require dirname(__DIR__).'/staging-claim-bridge.php';
if (getenv('FV_R433_FALLBACK')==='1') { echo fv_r433_fallback(); exit; }
$campaign=['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'apollo_documentary_001'];
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R433 local-only fixture</title><style><?php
foreach(['apollo-r429/assets/bridge.css','apollo-r430/assets/educator-case-lab.css','apollo-r431/assets/evidence-notebook.css','apollo-r432/assets/custody-gate.css'] as $file)echo file_get_contents(dirname(__DIR__,2).'/'.$file);
echo file_get_contents(dirname(__DIR__).'/assets/claim-bridge.css');
?></style></head><body><?php echo fv_r433_render(1,$campaign),fv_r433_render(2,[]); ?><script><?php echo file_get_contents(dirname(__DIR__,2).'/apollo-r431/assets/evidence-notebook.js'); ?></script></body></html>
