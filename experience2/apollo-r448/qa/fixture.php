<?php
require dirname(__DIR__).'/crosswalk.php';
if(fv_r448_data()===null){fwrite(STDERR,"Missing or corrupt claim custody manifest\n");exit(1);}
$root=dirname(__DIR__);
$css=file_get_contents($root.'/assets/crosswalk.css');
$js=file_get_contents($root.'/assets/crosswalk.js');
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R448 isolated fixture</title><style>'.$css.'</style></head><body style="margin:0;background:#101611">';
echo fv_r448_render();
if(in_array('--duplicate',$argv,true)) echo fv_r448_render();
echo '<script>'.$js.'</script></body></html>';
