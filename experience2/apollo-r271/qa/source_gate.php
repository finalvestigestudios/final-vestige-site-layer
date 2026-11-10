<?php
/* Exact PR #158 shortcode + R270 filter; simulated WordPress API, not installation. */
define('ABSPATH','/cli-only/');
function add_action(...$a) {}
function add_shortcode(...$a) {}
function add_filter(...$a) {}
function esc_url($s) {return $s;}
function plugin_dir_path($f) {return dirname($f).'/';}
require __DIR__.'/../fixtures/research-desk/final-vestige-ex2-research-desk.php';
require __DIR__.'/../fixtures/rd-instance-scope.php';
$original=file_get_contents(__DIR__.'/../fixtures/research-desk/templates/ledger.html');
if(fv_ex2_rd_shortcode()!==$original){fwrite(STDERR,"original shortcode mismatch\n");exit(2);}
$parts=[];
for($i=0;$i<3;$i++)$parts[]=fv_ex2_r270_scope_desk($original,'fv_ex2_research_desk',[],[]);
if($parts[0]!==$original || strpos($parts[1],'--fvx-2')===false || strpos($parts[2],'--fvx-3')===false){exit(3);}
$bad=str_replace('data-fvx-record','data-corrupted-record',$original);
if(fv_ex2_r270_scope_desk($bad,'fv_ex2_research_desk',[],[])!==$bad){exit(4);}
$joined=implode('',$parts);
preg_match_all('/\bid="([^"]+)"/',$joined,$ids);
if(count($ids[1])!==27||count(array_unique($ids[1]))!==27){exit(5);}
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main>'.$joined.'</main></body></html>';
