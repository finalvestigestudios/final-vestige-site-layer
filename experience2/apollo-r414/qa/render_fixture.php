<?php
// Same PHP component, synthetic catalogue literals for offline layout tests.
define('ABSPATH', __DIR__);
ob_start();require __DIR__.'/test_php.php';ob_end_clean();
$css = file_get_contents(dirname(__DIR__).'/assets/archive-gallery.css');
print '<!DOCTYPE html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R414 offline staging fixture</title><style>'. $css .'</style><body style="margin:0">';
print fv_r414_markup(1,$rows);
print fv_r414_markup(2,$rows);
print '</body></html>';
