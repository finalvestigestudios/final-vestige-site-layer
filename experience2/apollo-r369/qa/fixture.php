<?php
declare(strict_types=1);
define('ABSPATH', __DIR__);
require_once dirname(__DIR__,2).'/apollo-r365/chrono-rail.php';
require_once dirname(__DIR__,2).'/apollo-r367/sealed-chronology.php';
require_once dirname(__DIR__).'/evidence-bridge.php';
$rows=fv_apollo_r365_rows();
$mode=$argv[1]??'';
if($mode==='altered'){$rows[0]['supported']='A different and unreviewed claim';}
if($mode==='reordered'){[$rows[0],$rows[1]]=[$rows[1],$rows[0]];}
if($mode==='missing'){array_pop($rows);}
if($mode==='duplicate'){$rows[2]=$rows[1];}
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo 1 evidence bridge · staging</title></head><body><main>';
echo fv_apollo_r369_render($rows);
echo '</main></body></html>';
