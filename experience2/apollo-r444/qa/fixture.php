<?php
require dirname(__DIR__).'/review_panel.php';
$html='<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R444 staging-only fixture</title><style>'.file_get_contents(dirname(__DIR__).'/assets/review-panel.css').'</style></head><body>';
$html.=fv_r444_render().fv_r444_render();
$html.='<script>'.file_get_contents(dirname(__DIR__).'/assets/review-panel.js').'</script></body></html>';
echo $html;
