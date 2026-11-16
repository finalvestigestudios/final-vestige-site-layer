<?php
/**
 * Apollo R396 — standalone, default-OFF staging CSS loader with exact record custody.
 * Replaces (does not modify or activate) the proposed R395 loader in a future,
 * founder/QD-approved staging install. No post, option, email or network writes.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R396_LEDGER_SHA256 = '60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f';
const FV_R396_BASE_SHA256 = '4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9';
const FV_R396_FIT_SHA256 = '93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756';

function fv_r396_file_is_reviewed(string $path, string $sha): bool {
    return is_file($path) && !is_link($path) && is_readable($path)
        && hash_equals($sha, hash_file('sha256', $path));
}

/** Independently pin *all gallery-visible fields*, not merely R384's boolean. */
function fv_r396_records_are_reviewed($observed): bool {
    if (!is_array($observed) || count($observed) !== 6 || array_keys($observed) !== range(0, 5)) {
        return false;
    }
    $ledgerPath = dirname(__DIR__) . '/apollo-r377/custody.json';
    if (!fv_r396_file_is_reviewed($ledgerPath, FV_R396_LEDGER_SHA256)) { return false; }
    $ledger = json_decode((string) file_get_contents($ledgerPath), true);
    if (!is_array($ledger) || ($ledger['schema'] ?? '') !== 'fv.apollo.research-desk.source-custody.v1'
        || !isset($ledger['records']) || !is_array($ledger['records']) || count($ledger['records']) !== 6) {
        return false;
    }
    $visibleFields = array('id', 'heading', 'kind', 'claim', 'boundary',
        'evidence_url', 'evidence_role', 'catalog_note', 'context_url');
    foreach ($observed as $i => $record) {
        if (!is_array($record)) { return false; }
        foreach ($visibleFields as $field) {
            if (!isset($record[$field]) || !is_string($record[$field])
                || !isset($ledger['records'][$i][$field])
                || $record[$field] !== $ledger['records'][$i][$field]) { return false; }
        }
    }
    // Explicitly distinguish 5 questions from the original Board report and
    // 1 from the 2018 later-test retrospective, not six independent documents.
    $board = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
    $later = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
    foreach ($observed as $i => $record) {
        if ($record['evidence_url'] !== ($i === 5 ? $later : $board)) { return false; }
    }
    return true;
}

/** Hard fail-closed until staging gate, canonical records, and assets all agree. */
function fv_r396_prepaint_eligible(): bool {
    if (!defined('FV_R396_APOLLO_QA_ENABLE') || FV_R396_APOLLO_QA_ENABLE !== true
        || !function_exists('wp_get_environment_type') || wp_get_environment_type() !== 'staging'
        || !function_exists('is_page') || !is_page('apollo-1-evidence-atlas')
        || !function_exists('fv_r384_records') || !function_exists('wp_enqueue_style')
        || !function_exists('plugins_url')) { return false; }
    if (!fv_r396_records_are_reviewed(fv_r384_records())) { return false; }
    return fv_r396_file_is_reviewed(dirname(__DIR__) . '/apollo-r384/assets/gallery.css', FV_R396_BASE_SHA256)
        && fv_r396_file_is_reviewed(dirname(__DIR__) . '/apollo-r395/assets/mobile-fit.css', FV_R396_FIT_SHA256);
}

function fv_r396_enqueue_prepaint(): void {
    if (!fv_r396_prepaint_eligible()) { return; }
    // Reuse approved R384/R395 handles and order. Never override an installed
    // third-party stylesheet or use a new tracking/analytics handle.
    wp_enqueue_style('fv-apollo-r384-gallery',
        plugins_url('../apollo-r384/assets/gallery.css', __FILE__), array(), 'r384-reviewed-1', 'all');
    wp_enqueue_style('fv-apollo-r395-mobile-fit',
        plugins_url('../apollo-r395/assets/mobile-fit.css', __FILE__),
        array('fv-apollo-r384-gallery'), 'r395-reviewed-1', 'screen');
}
if (function_exists('add_action')) {
    add_action('wp_enqueue_scripts', 'fv_r396_enqueue_prepaint', 99);
}
