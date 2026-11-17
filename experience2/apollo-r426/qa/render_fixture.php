<?php
// Offline QA only. Not WordPress or an installed staging page.
define('ABSPATH', __DIR__);
require dirname(__DIR__) . '/staging-source-comparison.php';
$css = file_get_contents(dirname(__DIR__) . '/assets/source-comparison.css');
$n = max(1, min(2, (int) ($argv[1] ?? 1)));
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R426 local isolated fixture</title><style>' . $css . '</style></head><body style="margin:0">';
for ($i=1;$i<=$n;$i++) echo fv_r426_render($i);
echo '</body></html>';
