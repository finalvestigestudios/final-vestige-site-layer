<?php
/**
 * Apollo R397 — prospective, OFF-by-default WordPress staging delivery guard.
 * Independent alternative to R395/R396; never activate more than one loader.
 * This file performs no settings/post/network/commerce writes and is NOT installed.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R397_LEDGER_SHA256 = '60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f';
const FV_R397_BASE_SHA256   = '4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9';
const FV_R397_FIT_SHA256    = '93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756';

function fv_r397_reviewed_file(string $path, string $expected): bool {
    return is_file($path) && !is_link($path) && is_readable($path)
        && hash_equals($expected, (string)hash_file('sha256', $path));
}

/** Full row custody, including context_role and absence of additional attributes. */
function fv_r397_exact_records($observed): bool {
    if (!is_array($observed) || array_keys($observed) !== range(0, 5)) { return false; }
    $path = dirname(__DIR__) . '/apollo-r377/custody.json';
    if (!fv_r397_reviewed_file($path, FV_R397_LEDGER_SHA256)) { return false; }
    $ledger = json_decode((string)file_get_contents($path), true);
    if (!is_array($ledger) || ($ledger['schema'] ?? '') !== 'fv.apollo.research-desk.source-custody.v1'
        || !is_array($ledger['records'] ?? null) || array_keys($ledger['records']) !== range(0, 5)) { return false; }
    $expectedKeys = array('id','heading','kind','claim','boundary','evidence_url',
        'evidence_role','context_url','context_role','catalog_note');
    foreach ($observed as $i => $record) {
        $truth = $ledger['records'][$i];
        if (!is_array($record) || count($record) !== count($expectedKeys)
            || !empty(array_diff(array_keys($record), $expectedKeys))
            || !empty(array_diff($expectedKeys, array_keys($record)))) { return false; }
        foreach ($expectedKeys as $key) {
            if (!array_key_exists($key, $truth) || !is_string($truth[$key])
                || !array_key_exists($key, $record) || !is_string($record[$key])
                || !hash_equals($truth[$key], $record[$key])) { return false; }
        }
        $expectedNASA = $i === 5
            ? 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
            : 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
        if ($record['evidence_url'] !== $expectedNASA) { return false; }
    }
    return true;
}

/** Strict staging same-origin HTTPS asset URLs; rejects filtered/offsite delivery. */
function fv_r397_reviewed_asset_url($url, $site, string $suffix): bool {
    if (!is_string($url) || !is_string($site) || $url === '' || $site === '') { return false; }
    $asset = parse_url($url);
    $origin = parse_url($site);
    if (!is_array($asset) || !is_array($origin)) { return false; }
    foreach (array($asset, $origin) as $pieces) {
        if (($pieces['scheme'] ?? '') !== 'https' || empty($pieces['host'])
            || isset($pieces['user']) || isset($pieces['pass']) || isset($pieces['port'])
            || isset($pieces['query']) || isset($pieces['fragment'])) { return false; }
    }
    if (strcasecmp($asset['host'], $origin['host']) !== 0) { return false; }
    $path = $asset['path'] ?? '';
    // plugins_url('../sibling', __FILE__) includes exactly one reviewed /../ segment.
    // Do not follow encoded dot segments, backslashes, double slashes or other traversal.
    if (strpos($path, '%') !== false || strpos($path, '\\') !== false || strpos($path, '//') !== false
        || substr($path, -strlen('/apollo-r397/../'.$suffix)) !== '/apollo-r397/../'.$suffix) { return false; }
    $prefix = substr($path, 0, -strlen('/apollo-r397/../'.$suffix));
    if ($prefix === '' || strpos($prefix, '/..') !== false || strpos($prefix, '/./') !== false) { return false; }
    return true;
}

/**
 * Return delivery URLs only if the whole admission contract is satisfied.
 * Blocks pre-registered/enqueued handle collisions rather than silently using
 * a third-party stylesheet registered under the expected handle.
 */
function fv_r397_reviewed_delivery() {
    if (!defined('FV_R397_APOLLO_QA_ENABLE') || FV_R397_APOLLO_QA_ENABLE !== true
        || !function_exists('wp_get_environment_type') || wp_get_environment_type() !== 'staging'
        || !function_exists('is_page') || !is_page('apollo-1-evidence-atlas')
        || !function_exists('fv_r384_records') || !function_exists('wp_enqueue_style')
        || !function_exists('wp_style_is') || !function_exists('plugins_url')
        || !function_exists('home_url')) { return false; }
    if (!fv_r397_exact_records(fv_r384_records())) { return false; }
    if (!fv_r397_reviewed_file(dirname(__DIR__).'/apollo-r384/assets/gallery.css', FV_R397_BASE_SHA256)
        || !fv_r397_reviewed_file(dirname(__DIR__).'/apollo-r395/assets/mobile-fit.css', FV_R397_FIT_SHA256)) { return false; }
    foreach (array('fv-apollo-r384-gallery','fv-apollo-r395-mobile-fit') as $handle) {
        if (wp_style_is($handle, 'registered') || wp_style_is($handle, 'enqueued')) { return false; }
    }
    $source = __FILE__;
    $base = plugins_url('../apollo-r384/assets/gallery.css', $source);
    $fit = plugins_url('../apollo-r395/assets/mobile-fit.css', $source);
    $site = home_url('/');
    if (!fv_r397_reviewed_asset_url($base, $site, 'apollo-r384/assets/gallery.css')
        || !fv_r397_reviewed_asset_url($fit, $site, 'apollo-r395/assets/mobile-fit.css')) { return false; }
    return array('base'=>$base, 'fit'=>$fit);
}

function fv_r397_enqueue_prepaint(): void {
    $urls = fv_r397_reviewed_delivery();
    if ($urls === false) { return; }
    wp_enqueue_style('fv-apollo-r384-gallery', $urls['base'], array(), 'r384-reviewed-1', 'all');
    wp_enqueue_style('fv-apollo-r395-mobile-fit', $urls['fit'],
        array('fv-apollo-r384-gallery'), 'r395-reviewed-1', 'screen');
}
if (function_exists('add_action')) {
    add_action('wp_enqueue_scripts', 'fv_r397_enqueue_prepaint', 99);
}
