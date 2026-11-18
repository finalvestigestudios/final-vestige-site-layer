<?php
require_once dirname(__DIR__).'/gallery.php';
if (fv_r447_manifest() === null) { fwrite(STDERR,"manifest invalid\n"); exit(1); }
$css=(string)file_get_contents(dirname(__DIR__).'/assets/gallery.css');
$js=(string)file_get_contents(dirname(__DIR__).'/assets/gallery.js');
// Offline test fixture: CSS and JS inline so Chromium makes no network requests.
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R447 source gallery test</title><style>' . $css . '</style></head><body style="margin:0;background:#101210">';
echo fv_r447_render();
if (in_array('--duplicate',$argv,true)) echo fv_r447_render();
echo '<script>' . $js . '</script></body></html>';
