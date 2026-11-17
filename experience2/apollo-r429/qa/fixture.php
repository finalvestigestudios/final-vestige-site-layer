<?php
// Executes the exact staged PHP renderer; no WordPress installation is claimed.
define('ABSPATH', __DIR__);
require dirname(__DIR__) . '/staging-attribution-bridge.php';
$mode = $argv[1] ?? 'valid';
$query = $mode === 'valid' ? ['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'apollo_longform_001'] : [];
$css = file_get_contents(dirname(__DIR__) . '/assets/bridge.css');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R429 offline PHP fixture</title><style>'.$css.'</style></head><body>';
echo fv_r429_render(1,$query), fv_r429_render(2,$query), '</body></html>';
