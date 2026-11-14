<?php
/** Local-only HTTP/CSP fixture. NOT a WordPress installer or production configuration. */
declare(strict_types=1);
define('ABSPATH', true);
header("Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Cache-Control: no-store');
header('Content-Type: text/html; charset=utf-8');
require_once dirname(__DIR__, 2) . '/apollo-r348/source-custody.php';
$styles = [
    'apollo-r339/assets/chronology-rail.css',
    'apollo-r345/evidence-plate.css',
    'apollo-r340/assets/accession-gallery.css',
    'apollo-r347/assets/source-index.css',
    'apollo-r348/assets/source-custody.css',
];
?><!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research-only Apollo 1 HTTP/CSP acceptance fixture</title>
<?php foreach ($styles as $css): ?><link rel="stylesheet" href="/experience2/<?php echo htmlspecialchars($css, ENT_QUOTES, 'UTF-8'); ?>">
<?php endforeach; ?>
<script defer src="/experience2/apollo-r347/assets/source-index.js"></script>
<!-- Negative CSP control: must never run; no inline-script allowance. -->
<script>window.__fvInlineCspProbe=true</script></head><body style="margin:0">
<?php echo fv_apollo_r348_experience_shortcode(); ?>
</body></html>
