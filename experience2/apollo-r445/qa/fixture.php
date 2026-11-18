<?php
require dirname(__DIR__) . '/bridge.php';
$query = (string)($argv[1] ?? '');
$css = file_get_contents(dirname(__DIR__, 2) . '/apollo-r444/assets/review-panel.css');
$js = file_get_contents(dirname(__DIR__, 2) . '/apollo-r444/assets/review-panel.js');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">';
echo '<title>R445 campaign-safe Apollo evidence source trail</title><style>' . $css . '</style></head><body>';
echo fv_r445_render($query);
echo fv_r445_render('utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_pilot_2026_11&utm_content=VIDEOEXAMPLE123');
echo '<script>' . $js . '</script></body></html>';
