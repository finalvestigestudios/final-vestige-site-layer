<?php
/* PHP-rendered local fixture, not installed WordPress or network/browser HTTP. */
define('ABSPATH', __DIR__.'/');
require __DIR__.'/../../apollo-r365/chrono-rail.php';
require __DIR__.'/../../apollo-r367/sealed-chronology.php';
require __DIR__.'/../../apollo-r371/source-gallery.php';
require __DIR__.'/../evidence-path.php';
$css = file_get_contents(__DIR__.'/../assets/evidence-path.css');
$html = fv_apollo_r372_render(fv_apollo_r365_rows(),fv_apollo_r371_catalog());
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R372 staging fixture; NOT WordPress</title><style><?php echo $css; ?></style><style>html,body{margin:0;padding:0}body{background:#0d1011}</style></head><body><main><?php echo $html; ?></main></body></html>
