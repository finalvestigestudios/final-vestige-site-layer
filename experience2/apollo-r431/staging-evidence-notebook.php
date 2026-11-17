<?php
/**
 * FV Apollo R431 — isolated source-custodied educator notebook, staging only.
 * No stored answers, tracking, signup, merchant links, NASA image or WordPress writes.
 * Uses the *reviewed* R430 component without modifying its records or CTA.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R431_PHP_BLOB = '11a30d871bb0c5840aa3ee8932e12a6068b50cd3';
const FV_R431_CSS_BLOB = 'be6880577faed2453f5633a3718fce8dedf9ac3b';
const FV_R431_FREE_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
function fv_r431_fallback(): string {
    return '<p class="fv-r431-fallback">Evidence notebook unavailable. <a href="'.FV_R431_FREE_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r431_blob(string $bytes): string {
    return sha1('blob '.strlen($bytes)."\0".$bytes);
}
function fv_r431_parent_path(string $part): string {
    return dirname(__DIR__).'/apollo-r430/'.$part;
}
function fv_r431_verified(): bool {
    foreach ([['staging-educator-case-lab.php', FV_R431_PHP_BLOB],
              ['assets/educator-case-lab.css', FV_R431_CSS_BLOB]] as [$part, $sha]) {
        $file = fv_r431_parent_path($part);
        if (is_link($file) || is_link(dirname($file)) || !is_file($file) || !is_readable($file)) return false;
        $contents = file_get_contents($file);
        if (!is_string($contents) || !hash_equals($sha, fv_r431_blob($contents))) return false;
    }
    return true;
}
function fv_r431_allowed(): bool {
    return defined('FV_R431_ENABLED') && FV_R431_ENABLED === true
        && defined('FV_R431_STAGING_PAGE_ID') && is_int(FV_R431_STAGING_PAGE_ID) && FV_R431_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R431_STAGING_PAGE_ID;
}
/** Requires a pristine R430 load. Unknown preloaded implementations are rejected. */
function fv_r431_render(int $instance, array $query): string {
    if ($instance < 1 || $instance > 30 || !fv_r431_verified()) return fv_r431_fallback();
    if (empty($GLOBALS['fv_r431_trusted_loaded'])) {
        if (function_exists('fv_r430_render')) return fv_r431_fallback();
        require_once fv_r431_parent_path('staging-educator-case-lab.php');
        if (!function_exists('fv_r430_render')) return fv_r431_fallback();
        $GLOBALS['fv_r431_trusted_loaded'] = true;
    }
    $inherited = fv_r430_render($instance, $query);
    // Fail open to the free article if R430 itself could not load its R429 sources.
    if (substr_count($inherited, 'class="fv-r430__question"') !== 3
        || substr_count($inherited, 'class="fv-r429__cta"') !== 1) return fv_r431_fallback();
    $id = 'fv-r431-'.$instance;
    $out = '<section class="fv-r431" data-fv-r431 aria-labelledby="'.$id.'-title">';
    $out .= '<header class="fv-r431__intro"><p class="fv-r431__kicker">APOLLO 1 / YOUR EVIDENCE NOTEBOOK</p>';
    $out .= '<h2 id="'.$id.'-title">Keep the reasoning, not just the conclusion.</h2>';
    $out .= '<p>Answer the three source questions below. With JavaScript enabled, you can copy or save a plain-text record containing your responses and the NASA source links. Nothing is sent to Final Vestige or saved automatically.</p></header>';
    $out .= $inherited;
    $out .= '<aside class="fv-r431__tools" aria-labelledby="'.$id.'-tools-title">';
    $out .= '<h3 id="'.$id.'-tools-title">Take your evidence notes with you</h3>';
    $out .= '<p>When the tools are unavailable, the questions, NASA citations and free investigation link remain readable and printable. You can always write on a printed worksheet.</p>';
    // No inert action controls are exposed when JS is disabled or initialization fails.
    $out .= '<div class="fv-r431__actions" data-fv-r431-actions hidden>';
    $out .= '<p class="fv-r431__progress" data-fv-r431-progress aria-live="polite">0 of 3 answers drafted</p>';
    $out .= '<button type="button" data-fv-r431-copy>Copy my cited notes</button>';
    $out .= '<button type="button" data-fv-r431-export>Save .txt notes</button>';
    $out .= '<button type="button" data-fv-r431-print>Print completed worksheet</button>';
    $out .= '<p class="fv-r431__status" role="status" aria-live="polite" data-fv-r431-status></p>';
    $out .= '</div><p class="fv-r431__privacy">Private until you choose to copy, print or download. Your browser controls the destination. Printing and downloads may leave files on your device. This is a free educational tool, not a NASA product or paid checkout.</p>';
    $out .= '</aside></section>';
    return $out;
}
function fv_r431_shortcode(): string {
    if (!fv_r431_allowed() || !fv_r431_verified()) return fv_r431_fallback();
    $next = ($GLOBALS['fv_r431_instances'] ?? 0) + 1;
    if (!is_int($next) || $next > 30) return fv_r431_fallback();
    $GLOBALS['fv_r431_instances'] = $next;
    return fv_r431_render($next, $_GET);
}
function fv_r431_enqueue(): void {
    if (!fv_r431_allowed() || !fv_r431_verified() || !function_exists('plugins_url') || !function_exists('wp_enqueue_style')) return;
    // Source CSS first, then our small isolated controls. No analytics or duplicate tracking.
    wp_enqueue_style('fv-apollo-r431-source', plugins_url('../apollo-r429/assets/bridge.css', __FILE__), [], '15942f8ef27d82695c8d2af8bdc8a807396da33e');
    wp_enqueue_style('fv-apollo-r431-worksheet', plugins_url('../apollo-r430/assets/educator-case-lab.css', __FILE__), ['fv-apollo-r431-source'], FV_R431_CSS_BLOB);
    wp_enqueue_style('fv-apollo-r431-notebook', plugins_url('assets/evidence-notebook.css', __FILE__), ['fv-apollo-r431-worksheet'], 'r431');
    if (function_exists('wp_enqueue_script')) wp_enqueue_script('fv-apollo-r431-notebook', plugins_url('assets/evidence-notebook.js', __FILE__), [], 'r431', true);
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_evidence_notebook_r431', 'fv_r431_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r431_enqueue', 20);
