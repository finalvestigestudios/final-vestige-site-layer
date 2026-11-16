<?php
/**
 * Plugin Name: FV Apollo R407 Verified Chronology Research Desk (STAGING ONLY)
 * Description: OFF by default, source-locked, no WordPress writes or remote calls.
 * Version: 0.0.1-r407
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

const FV_R407_FREE_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R407_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';

/** These original file identities come from independently read GitHub PRs #158/#2728. */
function fv_r407_expected_blobs(): array {
    return array(
        'templates/ledger.html' => '403d128c57b9bc82dac7c619651689070edef86c',
        'assets/source-ledger.css' => 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
        'assets/research-desk-resilient.css' => '2c99fdeecd4d4245908c0f52f6a679c6f5d7718a',
        'assets/research-desk-r407.js' => '222e084d4d5cba5b979037df2018d82946fa9a75',
        'assets/chronology.css' => 'd60a1c52dca1a6b82f15cb6009a1a876a2ad33b2',
    );
}
function fv_r407_git_blob(string $path): ?string {
    if (!is_file($path) || !is_readable($path)) return null;
    $bytes = file_get_contents($path);
    if (!is_string($bytes)) return null;
    return sha1('blob ' . strlen($bytes) . "\0" . $bytes);
}
function fv_r407_assets_valid(string $root): bool {
    foreach (fv_r407_expected_blobs() as $name => $expected) {
        if (!hash_equals($expected, fv_r407_git_blob($root . '/' . $name) ?? '')) return false;
    }
    return true;
}
/**
 * Strict semantic gate alongside immutable template hash. No outbound merchant
 * links, injected assets, unsupported claims or counterfeit source domains.
 * Input is the exact release-reviewed static file, never user content.
 */
function fv_r407_contract_valid(string $html): bool {
    if (!preg_match('/<section\b[^>]*data-fvx-ledger\b/i', $html)) return false;
    if (preg_match('/<(script|iframe|img|form|map|video|audio|object)\b/i', $html)) return false;
    if (preg_match_all('/<article\b[^>]*data-fvx-record\b/i', $html) !== 6) return false;
    if (substr_count($html, 'EVIDENCE LIMITATION') !== 6) return false;
    if (substr_count($html, 'data-fvx-search=') !== 6 || !preg_match('/<input\b[^>]*data-fvx-search\b/i', $html)) return false; // six card indexes plus the search input
    if (substr_count($html, FV_R407_FREE_ARTICLE) !== 1) return false;
    if (strpos($html, 'The spark was never conclusively identified.') === false) return false;
    if (strpos($html, 'not interpolated sensor measurements') === false) return false;
    if (!preg_match_all('/<a\b[^>]*href="([^"]+)"/i', $html, $matches)) return false;
    if (count($matches[1]) !== 14) return false; // six archive + six research + one primary board + one free CTA
    foreach ($matches[1] as $href) {
        if ($href !== FV_R407_FREE_ARTICLE && strpos($href, 'https://www.nasa.gov/') !== 0) return false;
    }
    return true;
}
function fv_r407_authorized(): bool {
    return defined('FV_R407_ENABLED') && FV_R407_ENABLED === true
        && defined('FV_R407_STAGING_PAGE_ID') && (int) FV_R407_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int) get_queried_object_id() === (int) FV_R407_STAGING_PAGE_ID;
}
function fv_r407_conflict(): bool {
    foreach (array('fv-ex2-research-desk', 'fv-ex2-r405-access', 'fv-ex2-r406-access') as $handle) {
        if (function_exists('wp_script_is') && (wp_script_is($handle, 'enqueued') || wp_script_is($handle, 'done'))) return true;
        if (function_exists('wp_style_is') && (wp_style_is($handle, 'enqueued') || wp_style_is($handle, 'done'))) return true;
    }
    return false;
}
function fv_r407_namespace_markup(string $html, int $instance): string {
    if ($instance < 1) throw new InvalidArgumentException('Instance must be positive');
    return str_replace('fv-ex2-ledger-apollo1-', 'fv-ex2-ledger-apollo1-r407-i' . $instance . '-', $html);
}
function fv_r407_fallback(): string {
    return '<p>Research Desk temporarily unavailable. <a href="' . FV_R407_FREE_ARTICLE . '">Read the original Apollo 1 investigation</a>.</p>';
}
/** A real chronology, not invented precision or a geographical plot. */
function fv_r407_chronology(int $instance): string {
    $p = 'fv-ex2-ledger-apollo1-r407-i' . $instance . '-';
    return '<nav class="fv-r407__rail" aria-labelledby="fv-r407-rail-' . $instance . '">'
        . '<h2 id="fv-r407-rail-' . $instance . '">What the record can actually date</h2>'
        . '<p>Four documented markers, not a simulated fire or a second-by-second reconstruction. Each opens the related evidence record.</p>'
        . '<ol>'
        . '<li><span class="fv-r407__time">23:30:55 GMT · Jan 27, 1967</span><a href="#' . $p . 'record-05">Brief electrical-power interruption</a><span class="fv-r407__kind">Recorded marker; not proof of a particular ignition wire</span></li>'
        . '<li><span class="fv-r407__time">About 23:31:04.7 GMT</span><a href="#' . $p . 'record-03">First report of fire</a><span class="fv-r407__kind">Approximate communication timeline</span></li>'
        . '<li><span class="fv-r407__time">About 23:31:19 GMT</span><a href="#' . $p . 'record-03">Cabin pressure-vessel rupture</a><span class="fv-r407__kind">Approximate instrument marker, not interpolated telemetry</span></li>'
        . '<li><span class="fv-r407__time">Dec 1967 – Feb 1968</span><a href="#' . $p . 'record-06">Subsequent fire-safety testing</a><span class="fv-r407__kind">Later deliberate tests; not evidence identifying the original ignition</span></li>'
        . '</ol><p class="fv-r407__limits">Source: <a href="' . FV_R407_BOARD . '">NASA Apollo 204 Review Board</a> and the six reviewed records below. No geographic points are plotted: locations and relationships require separate source review.</p></nav>';
}
function fv_r407_enqueue(): void {
    $GLOBALS['fv_r407_ready'] = false;
    if (!fv_r407_authorized() || fv_r407_conflict() || !fv_r407_assets_valid(__DIR__)) return;
    if (!function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script') || !function_exists('plugins_url')) return;
    $html = file_get_contents(__DIR__ . '/templates/ledger.html');
    if (!is_string($html) || !fv_r407_contract_valid($html)) return;
    wp_enqueue_style('fv-r407-ledger', plugins_url('assets/source-ledger.css', __FILE__), array(), '0.0.1-r407');
    wp_enqueue_style('fv-r407-access', plugins_url('assets/research-desk-resilient.css', __FILE__), array('fv-r407-ledger'), '0.0.1-r407');
    wp_enqueue_style('fv-r407-chronology', plugins_url('assets/chronology.css', __FILE__), array('fv-r407-access'), '0.0.1-r407');
    wp_enqueue_script('fv-r407-script', plugins_url('assets/research-desk-r407.js', __FILE__), array(), '0.0.1-r407', true);
    $GLOBALS['fv_r407_ready'] = true;
}
function fv_r407_shortcode($atts = array()): string {
    static $instance = 0;
    if (!fv_r407_authorized() || fv_r407_conflict() || empty($GLOBALS['fv_r407_ready']) || !fv_r407_assets_valid(__DIR__)) return fv_r407_fallback();
    $html = file_get_contents(__DIR__ . '/templates/ledger.html');
    if (!is_string($html) || !fv_r407_contract_valid($html)) return fv_r407_fallback();
    $instance++;
    return '<div class="fv-r407" data-fv-r407>' . fv_r407_chronology($instance) . fv_r407_namespace_markup($html, $instance) . '</div>';
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r407_enqueue', 99);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_research_desk_r407', 'fv_r407_shortcode');
