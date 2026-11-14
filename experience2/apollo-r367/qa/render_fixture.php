<?php
/** Local-only HTML fixture: no WordPress, requests, CMS, tracking or media. */
declare(strict_types=1);
define('ABSPATH', __DIR__);
require_once dirname(__DIR__, 2) . '/apollo-r365/chrono-rail.php';
require_once dirname(__DIR__) . '/sealed-chronology.php';
$rows = fv_apollo_r365_rows();
if (($argv[1] ?? '') === 'reordered') { [$rows[0], $rows[1]] = [$rows[1], $rows[0]]; }
if (($argv[1] ?? '') === 'altered') { $rows[2]['supported'] = 'This claim was altered'; }
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R367 · Local staging-only fixture</title></head><body><main>';
echo fv_apollo_r367_render($rows);
echo '</main></body></html>';
