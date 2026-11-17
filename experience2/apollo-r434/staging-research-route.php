<?php
/** R434: isolated, staging-only research-to-free-article route. No CMS writes or analytics. */
if (!defined('ABSPATH')) { exit; }
const FV_R434_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R434_PINS = [
    'apollo-r433/staging-claim-bridge.php' => 'e48e577d0d14964ba77a86f5fc66db6f2c37a830',
    'apollo-r433/assets/claim-bridge.css' => '548c3b479e5003a925babbdebbb43712443675a9',
];
function fv_r434_fallback(): string {
    return '<p class="fv-r434-fallback">The evidence route is temporarily unavailable. <a href="'.FV_R434_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r434_verify(): bool {
    $root = realpath(dirname(__DIR__));
    if ($root === false) return false;
    foreach (FV_R434_PINS as $relative => $expected) {
        $cursor = dirname(__DIR__);
        foreach (explode('/', $relative) as $segment) {
            $cursor .= '/'.$segment;
            if (is_link($cursor)) return false;
        }
        $real = realpath($cursor);
        if ($real === false || !is_file($real) || !is_readable($real)
            || strncmp($real, $root.DIRECTORY_SEPARATOR, strlen($root)+1) !== 0) return false;
        $bytes = file_get_contents($real);
        if (!is_string($bytes)) return false;
        $blob = sha1('blob '.strlen($bytes)."\0".$bytes);
        if (!hash_equals($expected, $blob)) return false;
    }
    return true;
}
function fv_r434_allowed(): bool {
    return defined('FV_R434_ENABLED') && FV_R434_ENABLED === true
        && defined('FV_R434_STAGING_PAGE_ID') && is_int(FV_R434_STAGING_PAGE_ID) && FV_R434_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R434_STAGING_PAGE_ID;
}
function fv_r434_parent(): bool {
    if (!fv_r434_verify()) return false;
    if (!empty($GLOBALS['fv_r434_trusted_parent'])) {
        return function_exists('fv_r433_render') && function_exists('fv_r433_parent_verified')
            && fv_r433_parent_verified() && function_exists('fv_r432_verified') && fv_r432_verified();
    }
    // Refuse unknown in-process implementations; never silently trust a previously loaded parent.
    foreach (['fv_r433_render','fv_r432_render','fv_r431_render','fv_r430_render','fv_r429_render'] as $function) {
        if (function_exists($function)) return false;
    }
    require_once dirname(__DIR__).'/apollo-r433/staging-claim-bridge.php';
    if (!function_exists('fv_r433_load_parent') || !fv_r433_load_parent()
        || !function_exists('fv_r433_claims') || !function_exists('fv_r433_render')) return false;
    $GLOBALS['fv_r434_trusted_parent'] = true;
    return true;
}
/** Reuse source-controlled R433 and relocate exactly one validated CTA above the long evidence notebook. */
function fv_r434_render(int $instance, array $campaign = []): string {
    if ($instance < 1 || $instance > 30 || !fv_r434_parent()) return fv_r434_fallback();
    $inherited = fv_r433_render($instance, $campaign);
    if (substr_count($inherited, 'class="fv-r429__cta"') !== 1
        || substr_count($inherited, 'class="fv-r430__question"') !== 3
        || substr_count($inherited, 'class="fv-r433__claim"') !== 3
        || substr_count($inherited, 'data-fv-r431-actions') !== 1) return fv_r434_fallback();
    $matches = [];
    $pattern = '~<a class="fv-r429__cta" href="([^"]+)">Read the free Apollo 1 investigation</a>~';
    if (preg_match_all($pattern, $inherited, $matches, PREG_SET_ORDER) !== 1) return fv_r434_fallback();
    $rawUrl = html_entity_decode($matches[0][1], ENT_QUOTES | ENT_HTML5, 'UTF-8');
    // A source mutation or unrecognized outbound URL must never become a new public destination.
    if (!function_exists('fv_r429_target') || !hash_equals(fv_r429_target($campaign), $rawUrl)) return fv_r434_fallback();
    $replacement = '<span class="fv-r434__moved">The original free article is linked above.</span>';
    $replaced = 0;
    $inherited = str_replace($matches[0][0], $replacement, $inherited, $replaced);
    if ($replaced !== 1 || str_contains($inherited, 'class="fv-r429__cta"')) return fv_r434_fallback();
    $esc = static function (string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    $id = 'fv-r434-'.$instance;
    $out = '<section class="fv-r434" data-fv-r434 aria-labelledby="'.$id.'-title">';
    $out .= '<header class="fv-r434__hero"><p class="fv-r434__kicker">APOLLO 1 / AN EVIDENCE-FIRST ROUTE</p>';
    $out .= '<h2 id="'.$id.'-title">The evidence, without pretending the gaps are solved.</h2>';
    $out .= '<p>Start with the claim the records can support, check its limitation, then read the full investigation. The longer source desk and private educator worksheet remain available below.</p></header>';
    $out .= '<ol class="fv-r434__summary" aria-label="Chronological source confidence">';
    foreach (fv_r433_claims() as $claim) {
        [$date, $role, $fact, $boundary, $source] = $claim;
        if (!str_starts_with($source,'https://www.nasa.gov/')) return fv_r434_fallback();
        $out .= '<li class="fv-r434__row"><time datetime="'.$esc($date).'">'.$esc($date).'</time>';
        $out .= '<div><strong>'.$esc($role).'</strong><p>'.$esc($fact).'</p>';
        $out .= '<p class="fv-r434__boundary"><span>Limit:</span> '.$esc($boundary).'</p>';
        $out .= '<a href="'.$esc($source).'">Inspect original NASA source</a></div></li>';
    }
    $out .= '</ol><aside class="fv-r434__next" aria-labelledby="'.$id.'-next-title">';
    $out .= '<h3 id="'.$id.'-next-title">Next: follow the full, free evidence trail</h3>';
    $out .= '<p>The article connects the source record with the hatch, cabin atmosphere and unresolved ignition details. No signup or purchase is required.</p>';
    $out .= $matches[0][0].'</aside>';
    $out .= '<details class="fv-r434__deep" id="'.$id.'-desk"><summary>Explore the complete Research Desk, educator questions and private notes</summary>';
    $out .= '<div class="fv-r434__deepcontent">'.$inherited.'</div></details>';
    $out .= '<p class="fv-r434__disclosure">NASA provides the linked source material but does not endorse Final Vestige. Archival images are not republished here; individual media-use and commercial rights remain subject to separate review.</p>';
    $out .= '</section>';
    return $out;
}
function fv_r434_shortcode(): string {
    if (!fv_r434_allowed() || !fv_r434_verify()) return fv_r434_fallback();
    $n = ($GLOBALS['fv_r434_instances'] ?? 0) + 1;
    if (!is_int($n) || $n > 30) return fv_r434_fallback();
    $GLOBALS['fv_r434_instances'] = $n;
    return fv_r434_render($n, $_GET);
}
function fv_r434_enqueue(): void {
    if (!fv_r434_allowed() || !fv_r434_parent() || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) return;
    $base = [
        ['apollo-r429/assets/bridge.css', 'fv-r434-429', []],
        ['apollo-r430/assets/educator-case-lab.css', 'fv-r434-430', ['fv-r434-429']],
        ['apollo-r431/assets/evidence-notebook.css', 'fv-r434-431', ['fv-r434-430']],
        ['apollo-r432/assets/custody-gate.css', 'fv-r434-432', ['fv-r434-431']],
        ['apollo-r433/assets/claim-bridge.css', 'fv-r434-433', ['fv-r434-432']],
    ];
    foreach ($base as [$path,$handle,$deps]) wp_enqueue_style($handle, plugins_url('../'.$path,__FILE__), $deps, 'r434-reviewed');
    wp_enqueue_style('fv-r434-source-route', plugins_url('assets/research-route.css',__FILE__), ['fv-r434-433'], 'r434');
    if (function_exists('wp_enqueue_script')) wp_enqueue_script('fv-r434-private-notes', plugins_url('../apollo-r431/assets/evidence-notebook.js',__FILE__), [], 'r434-reviewed', true);
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_research_route_r434', 'fv_r434_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r434_enqueue', 20);
