<?php
/**
 * FV Apollo R432: immutable seven-object custody gate, staged read-only pilot.
 * No personal data, analytics, commerce, WordPress writes or NASA media copies.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R432_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R432_PINS = [
    'apollo-r429/staging-attribution-bridge.php' => 'c604bccf9873688ec1d9b64187d1a9a7fdcf89ac',
    'apollo-r429/assets/bridge.css' => '15942f8ef27d82695c8d2af8bdc8a807396da33e',
    'apollo-r430/staging-educator-case-lab.php' => '11a30d871bb0c5840aa3ee8932e12a6068b50cd3',
    'apollo-r430/assets/educator-case-lab.css' => 'be6880577faed2453f5633a3718fce8dedf9ac3b',
    'apollo-r431/staging-evidence-notebook.php' => '32d827d3ae5aa432c350d9db867e4131c8dfb935',
    'apollo-r431/assets/evidence-notebook.css' => '7dae0a5f73a434b40dc9b728657308c07d3b7c0e',
    'apollo-r431/assets/evidence-notebook.js' => '87dfe1b7d5bba87bbe3eb461f919eee16a7815c2',
];
function fv_r432_fallback(): string {
    return '<p class="fv-r432-fallback">The cited teaching notebook is temporarily unavailable. <a href="'.FV_R432_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r432_git_blob(string $text): string {
    return sha1('blob '.strlen($text)."\0".$text);
}
function fv_r432_path(string $part): string {
    return dirname(__DIR__).'/'.$part;
}
function fv_r432_verified(): bool {
    $base = realpath(dirname(__DIR__));
    if ($base === false) return false;
    foreach (FV_R432_PINS as $part => $expected) {
        $file = fv_r432_path($part);
        $parts = explode('/', $part);
        $cursor = dirname(__DIR__);
        foreach ($parts as $segment) {
            $cursor .= '/'.$segment;
            if (is_link($cursor)) return false;
        }
        if (!is_file($file) || !is_readable($file) || realpath($file) === false) return false;
        $real = realpath($file);
        if (strncmp($real, $base.DIRECTORY_SEPARATOR, strlen($base)+1) !== 0) return false;
        $bytes = file_get_contents($file);
        if (!is_string($bytes) || !hash_equals($expected, fv_r432_git_blob($bytes))) return false;
    }
    return true;
}
function fv_r432_allowed(): bool {
    return defined('FV_R432_ENABLED') && FV_R432_ENABLED === true
        && defined('FV_R432_STAGING_PAGE_ID') && is_int(FV_R432_STAGING_PAGE_ID) && FV_R432_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R432_STAGING_PAGE_ID;
}
/** No checkout: a source trail is not evidence of a sellable rights-cleared SKU. */
function fv_r432_render(int $instance, array $campaign = []): string {
    if ($instance < 1 || $instance > 30 || !fv_r432_verified()) return fv_r432_fallback();
    if (empty($GLOBALS['fv_r432_parent_trusted'])) {
        if (function_exists('fv_r431_render') || function_exists('fv_r430_render') || function_exists('fv_r429_render')) {
            return fv_r432_fallback();
        }
        require_once fv_r432_path('apollo-r431/staging-evidence-notebook.php');
        if (!function_exists('fv_r431_render')) return fv_r432_fallback();
        $GLOBALS['fv_r432_parent_trusted'] = true;
    }
    $inherited = fv_r431_render($instance, $campaign);
    if (substr_count($inherited, 'class="fv-r430__question"') !== 3
        || substr_count($inherited, 'class="fv-r429__plate"') !== 3
        || substr_count($inherited, 'class="fv-r429__cta"') !== 1
        || substr_count($inherited, 'data-fv-r431-actions') !== 1) return fv_r432_fallback();
    $id = 'fv-r432-'.$instance;
    $out = '<section class="fv-r432" data-fv-r432 aria-labelledby="'.$id.'-title">';
    $out .= '<header class="fv-r432__banner"><p class="fv-r432__eyebrow">APOLLO 1 / SOURCE-INTEGRITY PILOT</p>';
    $out .= '<h2 id="'.$id.'-title">Trace the evidence. Keep the work.</h2>';
    $out .= '<p>Three original instructor questions, dated NASA source references, and a private, optional notes export. Free investigation access does not depend on purchasing or signing up.</p></header>';
    $out .= $inherited;
    $out .= '<details class="fv-r432__rights"><summary>Source custody, image rights and limits</summary>';
    $out .= '<p>The historical investigation and the later retrospective are cited as separate records. They do not establish the precise ignition spark. Source dates do not turn later museum images into photographs of the accident.</p>';
    $out .= '<p>The worksheet and note-export text are Final Vestige editorial work; linked NASA material is not represented as our property. No NASA images, seals or photographs are reproduced here. Do not assume that identifiable people, third-party media or NASA marks are cleared for sale or promotion.</p>';
    $out .= '<p><a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Read the Apollo 204 Review Board</a> · <a href="https://www.nasa.gov/nasa-brand-center/images-and-media/">Check NASA media-use guidelines</a>. NASA does not endorse Final Vestige Studios.</p>';
    $out .= '</details></section>';
    return $out;
}
function fv_r432_shortcode(): string {
    if (!fv_r432_allowed() || !fv_r432_verified()) return fv_r432_fallback();
    $next = ($GLOBALS['fv_r432_instances'] ?? 0) + 1;
    if (!is_int($next) || $next > 30) return fv_r432_fallback();
    $GLOBALS['fv_r432_instances'] = $next;
    return fv_r432_render($next, $_GET);
}
function fv_r432_enqueue(): void {
    if (!fv_r432_allowed() || !fv_r432_verified() || !function_exists('plugins_url') || !function_exists('wp_enqueue_style')) return;
    // Handles are R432-only, never modify the original R431 plugin or homepage.
    $css = [
        ['apollo-r429/assets/bridge.css', 'fv-r432-archive', [], FV_R432_PINS['apollo-r429/assets/bridge.css']],
        ['apollo-r430/assets/educator-case-lab.css', 'fv-r432-worksheet', ['fv-r432-archive'], FV_R432_PINS['apollo-r430/assets/educator-case-lab.css']],
        ['apollo-r431/assets/evidence-notebook.css', 'fv-r432-notebook', ['fv-r432-worksheet'], FV_R432_PINS['apollo-r431/assets/evidence-notebook.css']],
    ];
    foreach ($css as [$path, $handle, $deps, $version]) {
        wp_enqueue_style($handle, plugins_url('../'.$path, __FILE__), $deps, $version);
    }
    wp_enqueue_style('fv-r432-custody', plugins_url('assets/custody-gate.css', __FILE__), ['fv-r432-notebook'], 'r432');
    if (function_exists('wp_enqueue_script')) {
        wp_enqueue_script('fv-r432-notebook-js', plugins_url('../apollo-r431/assets/evidence-notebook.js', __FILE__), [], FV_R432_PINS['apollo-r431/assets/evidence-notebook.js'], true);
    }
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_custody_gate_r432', 'fv_r432_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r432_enqueue', 20);
