<?php
/* Staging-only adapter integrity gate: no WordPress/site writes. */
define('ABSPATH', __DIR__);
function plugin_dir_path($file) { return dirname($file).DIRECTORY_SEPARATOR; }
function add_action(...$args) {}
function add_shortcode(...$args) {}
$root=$argv[1] ?? '';
if (!is_file($root.'/fv-ex2-apollo-r224.php')) { fwrite(STDERR,"Missing staged plugin\n"); exit(2); }
require $root.'/fv-ex2-apollo-r224.php';
if (!fv_ex2_r224_assets_ok()) { fwrite(STDERR,"Unmodified staging pin rejected\n"); exit(3); }
$css=$root.'/assets/atlas-scoped.css';
$prior=file_get_contents($css);
try {
 file_put_contents($css, $prior."\n/* unauthorized mutation */");
 if (fv_ex2_r224_assets_ok()) { throw new RuntimeException('Corruption improperly accepted'); }
 if (strpos(fv_ex2_r224_fallback(),'Read the original investigation')===false) { throw new RuntimeException('Fallback missing'); }
} finally { file_put_contents($css,$prior); }
if (!fv_ex2_r224_assets_ok()) { fwrite(STDERR,"Restored pin failed\n"); exit(4); }
echo "PHP_ADAPTER_PIN_PASS\n";
