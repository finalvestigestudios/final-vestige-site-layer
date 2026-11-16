<?php
/**
 * Apollo R399 — UNINSTALLED, default-OFF final HTML tag validation candidate.
 * Alternative to R395/R396/R397/R398 loaders; never enable concurrently.
 * No content, settings, tracking, email, remote HTTP or payment writes.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R399_LEDGER_SHA256 = '60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f';
const FV_R399_BASE_SHA256 = '4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9';
const FV_R399_FIT_SHA256 = '93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756';

function fv_r399_reviewed_file(string $path, string $sha): bool {
    return is_file($path) && !is_link($path) && is_readable($path)
        && hash_equals($sha, (string) hash_file('sha256', $path));
}
/** Independent ten-field, six-record custody, no unexpected fields. */
function fv_r399_reviewed_records($records): bool {
    if (!is_array($records) || array_keys($records) !== range(0, 5)) { return false; }
    $file = dirname(__DIR__).'/apollo-r377/custody.json';
    if (!fv_r399_reviewed_file($file, FV_R399_LEDGER_SHA256)) { return false; }
    $ledger = json_decode((string) file_get_contents($file), true);
    if (!is_array($ledger) || ($ledger['schema'] ?? '') !== 'fv.apollo.research-desk.source-custody.v1'
        || !is_array($ledger['records'] ?? null) || array_keys($ledger['records']) !== range(0, 5)) { return false; }
    $keys = ['id','heading','kind','claim','boundary','evidence_url','evidence_role',
        'context_url','context_role','catalog_note'];
    foreach ($records as $i => $row) {
        $truth = $ledger['records'][$i];
        if (!is_array($row) || count($row) !== 10 || count($truth) !== 10
            || array_diff(array_keys($row), $keys) || array_diff($keys, array_keys($row))) { return false; }
        foreach ($keys as $key) {
            if (!isset($truth[$key]) || !is_string($truth[$key]) || !isset($row[$key])
                || !is_string($row[$key]) || !hash_equals($truth[$key], $row[$key])) { return false; }
        }
        $source = $i === 5
          ? 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
          : 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
        if ($row['evidence_url'] !== $source) { return false; }
    }
    return true;
}
/** Validate a canonical, dot-segment-free plugins directory URL. */
function fv_r399_asset_directory($url, $home) {
    if (!is_string($url) || !is_string($home) || $url === '' || $home === '') { return false; }
    $p = parse_url($url); $h = parse_url($home);
    if (!is_array($p) || !is_array($h)) { return false; }
    foreach ([$p, $h] as $part) {
        if (($part['scheme'] ?? null) !== 'https' || empty($part['host'])
            || isset($part['user']) || isset($part['pass']) || isset($part['port'])
            || isset($part['query']) || isset($part['fragment'])) { return false; }
    }
    if (!hash_equals(strtolower($h['host']), strtolower($p['host']))) { return false; }
    $path = $p['path'] ?? '';
    // Must be an exact plugin sibling location. No ../, percent-encoding, duplicate
    // separators, backslashes, credentials, ports, query strings or fragments.
    if (preg_match('~^/(?:[A-Za-z0-9_-]+/)+experience2/apollo-r399$~D', $path) !== 1) { return false; }
    return substr($url, 0, -strlen('/apollo-r399'));
}
function fv_r399_canonical_css($directory): array {
    return [
      'fv-apollo-r384-gallery' => $directory.'/apollo-r384/assets/gallery.css',
      'fv-apollo-r395-mobile-fit' => $directory.'/apollo-r395/assets/mobile-fit.css',
    ];
}
/** Called before enqueue: aborts instead of adopting preexisting style handles. */
function fv_r399_reviewed_delivery() {
    if (!defined('FV_R399_APOLLO_QA_ENABLE') || FV_R399_APOLLO_QA_ENABLE !== true
        || !function_exists('wp_get_environment_type') || wp_get_environment_type() !== 'staging'
        || !function_exists('is_page') || !is_page('apollo-1-evidence-atlas')
        || !function_exists('fv_r384_records') || !function_exists('wp_style_is')
        || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')
        || !function_exists('home_url') || !function_exists('add_filter')) { return false; }
    if (!fv_r399_reviewed_records(fv_r384_records())) { return false; }
    if (!fv_r399_reviewed_file(dirname(__DIR__).'/apollo-r384/assets/gallery.css', FV_R399_BASE_SHA256)
        || !fv_r399_reviewed_file(dirname(__DIR__).'/apollo-r395/assets/mobile-fit.css', FV_R399_FIT_SHA256)) { return false; }
    foreach (array_keys(fv_r399_canonical_css('')) as $handle) {
        if (wp_style_is($handle, 'registered') || wp_style_is($handle, 'enqueued')) { return false; }
    }
    // WordPress plugins_url($path,__FILE__) does not normalize dot segments in
    // $path; instead derive the base directory and append canonical sibling paths.
    $directory = fv_r399_asset_directory(plugins_url('', __FILE__), home_url('/'));
    return $directory === false ? false : fv_r399_canonical_css($directory);
}
/** Late URL-source gate. WP appends ?ver=<registered version>. */
function fv_r399_guard_style_src($src, $handle) {
    $expected = $GLOBALS['fv_r399_approved_styles'] ?? [];
    if (!in_array($handle, ['fv-apollo-r384-gallery','fv-apollo-r395-mobile-fit'], true)
        || !isset($expected[$handle])) { return $src; }
    $version = $handle === 'fv-apollo-r384-gallery' ? 'r384-reviewed-1' : 'r395-reviewed-1';
    // No double-encoding, reordered parameters, scheme/host swap, CDN rewrite,
    // unauthorized query or relative URL. Empty string prevents a stylesheet URL.
    return is_string($src) && hash_equals($expected[$handle].'?ver='.$version, $src) ? $src : '';
}
/**
 * Final WordPress-core link-tag shape gate. This intentionally accepts ONLY
 * the current documented WP_Styles::do_item() output for our two handles.
 * Any additional markup, data attributes, alternate media, preload tricks,
 * inline script, or rewritten href is refused. Version/core changes may
 * fail closed and require a new independent staging review.
 *
 * This executes at PHP_INT_MAX but cannot prevent same-priority later hooks,
 * output buffers, a CDN, RTL/inline CSS appended outside this filter, or
 * bypass by a different stylesheet handle. Installed-site acceptance is
 * separately mandatory and no release is authorized by passing this gate.
 */
function fv_r399_guard_style_tag($tag, $handle, $href, $media) {
    $approved = $GLOBALS['fv_r399_approved_styles'] ?? [];
    if (!in_array($handle, ['fv-apollo-r384-gallery','fv-apollo-r395-mobile-fit'], true)
        || !isset($approved[$handle])) { return $tag; }
    $version = $handle === 'fv-apollo-r384-gallery' ? 'r384-reviewed-1' : 'r395-reviewed-1';
    $expected_media = $handle === 'fv-apollo-r384-gallery' ? 'all' : 'screen';
    $expected_href = $approved[$handle].'?ver='.$version;
    if (!is_string($tag) || !is_string($href) || !is_string($media)
        || !hash_equals($expected_media, $media)
        || !hash_equals($expected_href, $href)) { return ''; }
    // The single, exact, no-extra-attributes form WordPress core emits.
    $expected_tag = "<link rel='stylesheet' id='".$handle."-css' href='".$expected_href
        ."' media='".$expected_media."' />\n";
    return hash_equals($expected_tag, $tag) ? $tag : '';
}
function fv_r399_enqueue_prepaint(): void {
    $urls = fv_r399_reviewed_delivery();
    if ($urls === false) { return; }
    $GLOBALS['fv_r399_approved_styles'] = $urls;
    add_filter('style_loader_src', 'fv_r399_guard_style_src', PHP_INT_MAX, 2);
    add_filter('style_loader_tag', 'fv_r399_guard_style_tag', PHP_INT_MAX, 4);
    wp_enqueue_style('fv-apollo-r384-gallery', $urls['fv-apollo-r384-gallery'], [], 'r384-reviewed-1', 'all');
    wp_enqueue_style('fv-apollo-r395-mobile-fit', $urls['fv-apollo-r395-mobile-fit'], ['fv-apollo-r384-gallery'], 'r395-reviewed-1', 'screen');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_r399_enqueue_prepaint', 99); }
