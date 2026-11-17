<?php
/** Render the ACTUAL R440 shortcode PHP in a minimal local fixture, never claim this is WP staging. */
define('ABSPATH', '/local-test/');
require dirname(__DIR__).'/staging-educator-intent.php';
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R440 educator preview test</title>
<style>body{margin:0;background:#121416;color:#f2eee5;font-family:system-ui}main{width:100%}</style>
<style><?=file_get_contents(dirname(__DIR__).'/assets/educator-intent.css')?></style></head><body><main>
<?=fv_r440_render(1)?>
<?=fv_r440_render(2)?>
</main><script><?=file_get_contents(dirname(__DIR__).'/assets/educator-intent.js')?></script></body></html>
