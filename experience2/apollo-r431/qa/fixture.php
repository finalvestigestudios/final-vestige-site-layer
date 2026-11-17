<?php
/** Exact real R431 PHP + inherited SHA-pinned R430 and R429, no WordPress install. */
define('ABSPATH', __DIR__);
require dirname(__DIR__).'/staging-evidence-notebook.php';
$query = ['utm_source'=>'youtube', 'utm_medium'=>'organic_social', 'utm_campaign'=>'history_pilot_2026_11', 'utm_content'=>'reviewed_apollo_asset'];
$root = dirname(__DIR__, 2);
$css = file_get_contents($root.'/apollo-r429/assets/bridge.css') . "\n"
    . file_get_contents($root.'/apollo-r430/assets/educator-case-lab.css') . "\n"
    . file_get_contents(dirname(__DIR__).'/assets/evidence-notebook.css');
$js = file_get_contents(dirname(__DIR__).'/assets/evidence-notebook.js');
// CSS / JS are literal copied bytes, not substitute or reimplemented fixtures.
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo R431 real PHP offline acceptance</title><style>', $css, '</style></head><body>';
echo fv_r431_render(1, $query), fv_r431_render(2, []);
echo '<script>', $js, '</script></body></html>';
