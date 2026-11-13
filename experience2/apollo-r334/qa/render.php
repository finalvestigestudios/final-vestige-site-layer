<?php
const ABSPATH = '/staging-fixture/';
function add_action(...$args): void {}
function add_shortcode(...$args): void {}
require __DIR__.'/../apollo-custody-crosswalk.php';
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R334 staging source roles</title><link rel="stylesheet" href="/custody.css"></head><body style="margin:0">';
echo fv_r334_render();
echo '</body></html>';
