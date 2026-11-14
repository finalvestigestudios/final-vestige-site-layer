<?php
/** Local PHP HTML only, staging fixtures. No network or WordPress. */
declare(strict_types=1);
define('ABSPATH', __DIR__);
require_once dirname(__DIR__,2).'/apollo-r365/chrono-rail.php';
require_once dirname(__DIR__,2).'/apollo-r367/sealed-chronology.php';
require_once dirname(__DIR__).'/reflow-adapter.php';
$rows=fv_apollo_r365_rows();
if(($argv[1]??'')==='altered'){$rows[1]['supported']='Unreviewed mutation';}
if(($argv[1]??'')==='reordered'){[$rows[1],$rows[2]]=[$rows[2],$rows[1]];}
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo R368 test fixture</title></head><body><main>';
echo fv_apollo_r367_render($rows);
echo '</main></body></html>';
