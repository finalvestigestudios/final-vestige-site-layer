<?php
/**
 * FV Experience 2.0 R429 — Apollo source-to-article attribution bridge.
 * Staging only, inert unless explicitly enabled on one staging page.
 * No cookies, external analytics, forms, merchant links, or NASA media copies.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R429_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R429_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R429_HISTORY = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R429_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/';
function fv_r429_esc(string $x): string { return htmlspecialchars($x, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r429_allowed(): bool {
    return defined('FV_R429_ENABLED') && FV_R429_ENABLED === true
        && defined('FV_R429_STAGING_PAGE_ID') && is_int(FV_R429_STAGING_PAGE_ID) && FV_R429_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R429_STAGING_PAGE_ID;
}
/** Only pass Grok's agreed, public campaign metadata; never forward arbitrary query inputs. */
function fv_r429_campaign(array $query): array {
    foreach (['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'] as $name) {
        if (!isset($query[$name]) || !is_string($query[$name]) || strlen($query[$name]) > 80) return [];
    }
    $source = $query['utm_source'];
    $medium = $query['utm_medium'];
    $campaign = $query['utm_campaign'];
    $asset = $query['utm_content'];
    if (!in_array($source, ['youtube','tiktok','instagram','facebook','pinterest','x','bluesky'], true)
        || $medium !== 'organic_social'
        || !preg_match('/^(?:history|mysteries|mind|preparedness)_pilot_20[0-9]{2}_(?:0[1-9]|1[0-2])$/D', $campaign)
        || !preg_match('/^[a-z0-9][a-z0-9_-]{3,63}$/D', $asset)) return [];
    return ['utm_source'=>$source, 'utm_medium'=>$medium, 'utm_campaign'=>$campaign, 'utm_content'=>$asset];
}
function fv_r429_target(array $query): string {
    $campaign = fv_r429_campaign($query);
    return FV_R429_ARTICLE . ($campaign ? '?' . http_build_query($campaign, '', '&', PHP_QUERY_RFC3986) : '');
}
function fv_r429_sources(): array {
    return [
        ['1967-01-27', 'The ground-test fire', 'Historical event',
            'Apollo 1 crew members died in the January 27 ground-test fire.',
            'An event date cannot be inferred from a photograph made during a different year.',
            FV_R429_BOARD, 'Apollo 204 Review Board (primary investigation)'],
        ['1967-04-05', 'Investigation findings', 'Primary documentary source',
            'The Board found the most probable initiator to be an electrical arc, but no single ignition source was conclusively identified.',
            'Probable cause is not proof of an individual wire or precise initial spark.',
            FV_R429_BOARD, 'Apollo 204 Review Board: findings and determinations'],
        ['2018-02-14', 'Later flammability retrospective', 'Later institutional history',
            'A later NASA account reports three series of 102 deliberate ignitions of Command Module Boilerplate 1224 in 1967–1968.',
            'Tests after the accident explain redesign research; they do not identify the spark that initiated the original fire.',
            FV_R429_HISTORY, 'NASA Johnson Space Center: 50 Years Ago — Apollo Flammability Tests'],
    ];
}
function fv_r429_fallback(): string {
    return '<p class="fv-r429-fallback">Evidence experience unavailable. <a href="' . FV_R429_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r429_render(int $instance, array $query): string {
    if ($instance < 1 || $instance > 100) return fv_r429_fallback();
    $id = 'fv-r429-' . $instance;
    $href = fv_r429_esc(fv_r429_target($query));
    $out = '<section class="fv-r429" data-fv-r429 aria-labelledby="' . $id . '-title">';
    $out .= '<p class="fv-r429__kicker">APOLLO 1 / EVIDENCE &amp; SOURCE CUSTODY</p><h2 id="' . $id . '-title">A source trail, not a reconstruction.</h2>';
    $out .= '<p>Read three dated records. Each identifies what the evidence supports—and what it cannot establish. Dates are the dates of the event or publication, not an invented photographic timeline.</p>';
    $out .= '<ol class="fv-r429__rail">';
    foreach (fv_r429_sources() as $record) {
        [$date,$heading,$role,$claim,$limit,$source,$label] = $record;
        $out .= '<li class="fv-r429__plate"><time datetime="'.fv_r429_esc($date).'">'.fv_r429_esc($date).'</time>';
        $out .= '<h3>'.fv_r429_esc($heading).'</h3><p class="fv-r429__role">'.fv_r429_esc($role).'</p>';
        $out .= '<p>'.fv_r429_esc($claim).'</p><details><summary>Evidence limitation</summary><p>'.fv_r429_esc($limit).'</p></details>';
        $out .= '<p class="fv-r429__printlimit"><strong>Evidence limitation:</strong> '.fv_r429_esc($limit).'</p>';
        $out .= '<p><a href="'.fv_r429_esc($source).'">'.fv_r429_esc($label).'</a></p></li>';
    }
    $out .= '</ol><aside class="fv-r429__next" aria-labelledby="'.$id.'-next"><h3 id="'.$id.'-next">Continue the investigation</h3>';
    $out .= '<p>The full free article connects the hatch, cabin atmosphere and uncertain ignition evidence. No source claims a conclusively identified initiating spark.</p>';
    $out .= '<a class="fv-r429__cta" href="'.$href.'">Read the free Apollo 1 investigation</a>';
    $out .= '<p class="fv-r429__disclosure">NASA sources are linked, not republished; NASA does not endorse Final Vestige. Check <a href="'.FV_R429_RIGHTS.'">NASA media and branding guidance</a> before reusing media. No purchase or subscription is required.</p>';
    $out .= '</aside></section>';
    return $out;
}
function fv_r429_shortcode(): string {
    if (!fv_r429_allowed()) return fv_r429_fallback();
    $next = ($GLOBALS['fv_r429_instances'] ?? 0) + 1;
    if (!is_int($next) || $next > 100) return fv_r429_fallback();
    $GLOBALS['fv_r429_instances'] = $next;
    return fv_r429_render($next, $_GET);
}
function fv_r429_enqueue(): void {
    if (fv_r429_allowed() && function_exists('wp_enqueue_style') && function_exists('plugins_url')) {
        wp_enqueue_style('fv-apollo-r429', plugins_url('assets/bridge.css', __FILE__), [], 'r429');
    }
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_campaign_bridge_r429', 'fv_r429_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r429_enqueue', 20);
