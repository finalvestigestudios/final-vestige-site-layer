<?php
// Actual R430 PHP + verified exact-parent R429 sources. Offline fixture, not WP integration.
define('ABSPATH', __DIR__);
require dirname(__DIR__) . '/staging-educator-case-lab.php';
$query = ['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'apollo_longform_001'];
$css = file_get_contents(dirname(__DIR__, 2) . '/apollo-r429/assets/bridge.css') . "\n" . file_get_contents(dirname(__DIR__) . '/assets/educator-case-lab.css');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R430 actual-PHP fixture</title><style>', $css, '</style></head><body>';
echo fv_r430_render(1, $query), fv_r430_render(2, []), '</body></html>';
