<?php
/**
 * Apollo R350: documentary-record integrity guard for isolated research staging.
 * These are REVIEWED EDITORIAL ROW snapshots, NOT NASA file-content hashes,
 * proof of copyright clearance, or proof that upstream pages never change.
 * Intentional editorial changes require manual review and manifest regeneration.
 */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r350_expected_digests(): array {
    return array(
        'chronology' => '11bbee62ff36da8e1e43a84eaad34e2944350f0c2694439efbc66bc4c1454c67',
        'claims' => '3dac1beb7c6f39c478c87e5d100a3d8243d93eddddbbe3fe1a2f4c9fb5850701',
        'photos' => 'e213e7355599709e4c95b54e4afbabeba510c1985fc3d3f2f43ce74b9f7045b0',
    );
}

/** Pure testable comparison: every field, row order and count belongs to the reviewed snapshot. */
function fv_apollo_r350_rows_match(array $rows, string $kind): bool {
    $expected = fv_apollo_r350_expected_digests();
    if (!isset($expected[$kind])) { return false; }
    $json = json_encode($rows, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    return is_string($json) && hash_equals($expected[$kind], hash('sha256', $json));
}

/** Fail visibly closed if a required module, function or reviewed field has changed. */
function fv_apollo_r350_integrity_ok(): bool {
    static $checked = false, $passed = false;
    if ($checked) { return $passed; }
    $checked = true;
    $modules = array(
        'chronology' => array(dirname(__DIR__) . '/apollo-r339/chronology-rail.php', 'fv_apollo_r339_chronology'),
        'claims' => array(dirname(__DIR__) . '/apollo-r345/evidence-plate.php', 'fv_apollo_r345_claims'),
        'photos' => array(dirname(__DIR__) . '/apollo-r340/apollo-accession-gallery.php', 'fv_apollo_r340_accessions'),
    );
    foreach ($modules as $item) {
        if (!is_readable($item[0])) { return false; }
        require_once $item[0];
        if (!function_exists($item[1])) { return false; }
    }
    foreach ($modules as $name => $item) {
        $rows = call_user_func($item[1]);
        if (!is_array($rows) || !fv_apollo_r350_rows_match($rows, $name)) { return false; }
    }
    $passed = true;
    return true;
}
