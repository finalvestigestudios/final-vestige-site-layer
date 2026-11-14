<?php
/** R366: LOCAL HTTP-only integration fixture for the exact R365 staging source. No WordPress/CMS, production APIs or network calls. */
declare(strict_types=1);
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
$root = dirname(__DIR__, 2);
header("Content-Security-Policy: default-src 'none'; style-src 'self'; script-src 'none'; img-src 'none'; font-src 'none'; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'");
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');
header('X-Frame-Options: DENY');
if ($path === '/assets/chrono-rail.css') {
    header('Content-Type: text/css; charset=utf-8');
    readfile($root . '/apollo-r365/assets/chrono-rail.css');
    exit;
}
if ($path !== '/' && $path !== '/probe') {
    http_response_code(404); header('Content-Type: text/plain; charset=utf-8'); echo "Not found\n"; exit;
}
header('Content-Type: text/html; charset=utf-8');
if ($path === '/probe') {
    echo '<!doctype html><html lang="en"><meta charset="utf-8"><title>CSP regression</title><p id="probe">Inline execution denied.</p><script>document.getElementById("probe").textContent="CSP FAILED";</script></html>';
    exit;
}
define('ABSPATH', __DIR__);
require_once $root . '/apollo-r365/chrono-rail.php';
?><!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Apollo 1 · Source chronology (local QA only)</title>
<link rel="stylesheet" href="/assets/chrono-rail.css"></head><body>
<main id="main"><?php echo fv_apollo_r365_shortcode(); ?></main>
</body></html>
