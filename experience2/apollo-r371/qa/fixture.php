<?php
/* No installed WordPress. Local PHP-rendered browser fixture, explicitly labelled. */
define('ABSPATH', __DIR__ . '/');
require __DIR__.'/../../apollo-r365/chrono-rail.php';
require __DIR__.'/../../apollo-r367/sealed-chronology.php';
require __DIR__.'/../source-gallery.php';
$css=file_get_contents(__DIR__.'/../assets/source-gallery.css');
$render=fv_apollo_r371_render(fv_apollo_r371_catalog(),fv_apollo_r365_rows());
?><!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R371 static fixture — not WordPress</title><style><?php echo $css; ?></style><style>html,body{margin:0;padding:0}body{background:#0d1011}</style></head><body><main><?php echo $render; ?></main></body></html>
