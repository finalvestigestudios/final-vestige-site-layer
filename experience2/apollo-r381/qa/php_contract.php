<?php
error_reporting(E_ALL); ini_set('display_errors','1');
define('ABSPATH',__DIR__.'/');
require __DIR__.'/../../apollo-r377/source-role-desk.php';
require __DIR__.'/../atlas.php';
$checks=0;
function verify($ok,$name){global $checks; $checks++;if(!$ok){fwrite(STDERR,"FAIL: $name\n");exit(1);}}
$records=fv_r377_records(); verify(is_array($records)&&count($records)===6,'R377 SHA256 sealed records');
verify(fv_r381_approved($records),'approved six records');
$html=fv_r381_render($records); verify(str_contains($html,'data-fv-atlas'),'render atlas');
verify(substr_count($html,'data-fv-atlas-plate ')===6,'six evidence plates');
verify(substr_count($html,'data-fv-atlas-phase ')===3,'three chronology phases');
verify(substr_count($html,'data-fv-nasa-source')===6,'six external source records');
verify(substr_count($html,'data-fv-free-cta')===1,'single free editorial CTA');
verify(!str_contains($html,'<img')&&!str_contains($html,'<iframe'),'no foreign media');
verify(!str_contains($html,'checkout')&&!str_contains($html,'payhip'),'no unverified merchant');
verify(!str_contains($html,'latitude')&&!str_contains($html,'longitude'),'no invented geospatial data');
verify(str_contains($html,'December 1967–February 1968'),'later test time boundary');
verify(str_contains($html,'not conclusively identify'),'ignition uncertainty');
foreach (array_keys($records) as $i){$tamper=$records;$tamper[$i]['claim'].=' INVASION';verify(!fv_r381_approved($tamper),'reject modified record '.($i+1));verify(str_contains(fv_r381_render($tamper),'Evidence Atlas unavailable'),'withhold tamper '.($i+1));}
$reverse=array_reverse($records);verify(!fv_r381_approved($reverse),'reject reordered records');
$duplicate=$records;$duplicate[4]=$duplicate[0];verify(!fv_r381_approved($duplicate),'reject duplicate source record');
$extension=$records;$extension[]=array('id'=>'fake');verify(!fv_r381_approved($extension),'reject extra invented record');
verify(!fv_r381_approved(null),'reject missing source');
verify(fv_r381_assets_verified(),'exact CSS and JS sha checks');
$css=file_get_contents(__DIR__.'/../assets/atlas.css'); $js=file_get_contents(__DIR__.'/../assets/atlas.js');
verify(str_contains($css,'@media print')&&str_contains($css,'[hidden]'),'print restore hidden records');
verify(str_contains($js,'controls.hidden = false'),'no-JS controls hidden by default');
verify(!str_contains($js,'fetch(')&&!str_contains($js,'localStorage')&&!str_contains($js,'sendBeacon'),'no network/analytics');
$html2=fv_r381_render($records);verify($html!==$html2,'unique IDs per instance');
verify(str_contains($html2,'fv-a381-2-title'),'second instance unique title');
echo json_encode(array('status'=>'PASS','assertions'=>$checks,'tested'=>'PHP contract, source custody, no-JS, asset hashes, unique IDs'),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
