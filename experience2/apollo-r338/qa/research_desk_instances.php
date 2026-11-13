<?php
/** R338: repository-executable, real shortcode PHP + bundled six-record template contract.
 * Run: php experience2/apollo-r338/qa/research_desk_instances.php
 * Emit a no-network browser fixture: php .../research_desk_instances.php --emit-fixture
 */
declare(strict_types=1);
define('ABSPATH', __DIR__);
function add_action($hook, $callback, $priority = 10): void {}
function add_shortcode($tag, $callback): void {}
function plugin_dir_path($file): string { return dirname($file) . DIRECTORY_SEPARATOR; }
function esc_url($url): string { return $url; }
function fv_test_assert(bool $condition, string $message): void {
    if (!$condition) { fwrite(STDERR, "FAIL R338: " . $message . PHP_EOL); exit(1); }
}
$root = dirname(__DIR__, 2);
$plugin = $root . '/research-desk/final-vestige-ex2-research-desk.php';
$template = $root . '/research-desk/templates/ledger.html';
$css = $root . '/research-desk/assets/source-ledger.css';
$js = $root . '/research-desk/assets/source-ledger.js';
fv_test_assert(is_file($plugin) && is_file($template), 'actual staging Research Desk source unavailable');
require_once $plugin;
$first = fv_ex2_rd_shortcode();
$second = fv_ex2_rd_shortcode();
$combined = $first . $second;
fv_test_assert($first !== $second, 'two renders must have distinct ID namespaces');
fv_test_assert(substr_count($first, 'data-fvx-record ') === 6, 'six authentic records missing');
fv_test_assert(substr_count($second, 'data-fvx-record ') === 6, 'second instance record count');
fv_test_assert(substr_count($combined, 'data-fvx-source-role="documentary-support"') === 12, 'documentary claims');
fv_test_assert(substr_count($combined, 'data-fvx-source-role="contextual-photo-only"') === 12, 'photographs must remain contextual');
fv_test_assert(substr_count($combined, 'data-fvx-reuse-review="required"') === 12, 'rights review missing');
fv_test_assert(substr_count($combined, 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') === 2, 'one existing free editorial CTA per instance');
fv_test_assert(stripos($combined, '102 deliberate ignition tests') === false, 'unverified numeric claim returned');
fv_test_assert(strpos($combined, 'data-geo-pin=') === false && strpos($combined, 'data-map-edge=') === false, 'speculative geo');
fv_test_assert(strpos($combined, 'payhip.com') === false, 'unauthorized merchant insertion');
preg_match_all('/\\bid="([^"]+)"/', $combined, $idMatches);
$ids = $idMatches[1];
fv_test_assert(count($ids) === count(array_unique($ids)) && count($ids) >= 18, 'duplicate or missing DOM IDs');
foreach (['for', 'aria-controls', 'aria-labelledby'] as $attr) {
    preg_match_all('/\\b' . $attr . '="([^"]+)"/', $combined, $references);
    foreach ($references[1] as $ref) {
        foreach (preg_split('/\\s+/', trim($ref)) as $token) {
            fv_test_assert(in_array($token, $ids, true), 'unresolved ' . $attr . ': ' . $token);
        }
    }
}
fv_test_assert(strpos($first, 'instance-1-search') !== false, 'first search namespace');
fv_test_assert(strpos($second, 'instance-2-search') !== false, 'second search namespace');
if (in_array('--emit-fixture', $argv, true)) {
    fv_test_assert(is_file($css) && is_file($js), 'bundled assets missing');
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>';
    echo file_get_contents($css);
    echo '</style></head><body>' . $combined . '<script>';
    echo file_get_contents($js);
    echo '</script></body></html>';
} else {
    echo 'PASS R338 authentic Research Desk PHP: 2 independent shortcodes; 12 evidence cards, 12 documentary + 12 contextual sources, 18+ unique IDs and resolved accessibility references. Not installed WP or browser QA.' . PHP_EOL;
}
