<?php
// Isolated lifecycle stub. NOT an installed WordPress acceptance test.
define('ABSPATH', __DIR__);
function plugins_url($path,$file){return '/r334/assets/'.basename($path);}
function add_shortcode($name,$cb){}
require dirname(__DIR__).'/fv-apollo-custody-bridge.php';
$instances=max(1,min(2,(int)($argv[1]??1)));
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FV custody bridge offline staging</title></head><body><main><?php for($i=0;$i<$instances;$i++){echo fv_r334_render();} ?></main></body></html>
