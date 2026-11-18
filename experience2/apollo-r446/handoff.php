<?php
/**
 * Apollo R446: no fabricated creator attribution. Inherits the R445 review panel
 * without rewriting its NASA documents. Staging ONLY, no network, sessions, cookies,
 * logging, redirects, analytics installation, checkout, or WordPress content writes.
 */
const FV_R446_PARENT_SHA256 = 'bb5d498bac3e2f767733b9876a77fdea76fb5c2e9f9d5eaa59f3261aebdd6fbb';
const FV_R446_REGISTRY_SHA256 = 'c1a10e8c5989c92d5efde0ead2b85153b2413780e3fb3a181e3693c9b8694e05';
const FV_R446_INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';

function fv_r446_load_registry(): ?array {
    $file = __DIR__ . '/registry.json';
    if (!is_readable($file) || !hash_equals(FV_R446_REGISTRY_SHA256, (string)hash_file('sha256', $file))) return null;
    $data = json_decode((string)file_get_contents($file), true);
    if (!is_array($data) || ($data['schema'] ?? null) !== 'fv-apollo-creator-custody-v1'
        || !isset($data['assets']) || !is_array($data['assets'])
        || !is_bool($data['production_release_approved'] ?? null)
        || !is_bool($data['campaign_handoff_reviewed'] ?? null)) return null;
    return $data;
}
/**
 * Only a reviewed, published creator asset can propagate campaign tokens.
 * This is an allowlist, never a claim that a tagged session or sale occurred.
 */
function fv_r446_authorized_campaign(string $rawQuery, ?array $registry): ?array {
    if ($registry === null || ($registry['schema'] ?? null) !== 'fv-apollo-creator-custody-v1'
        || ($registry['status'] ?? '') !== 'APPROVED_STAGING_ASSETS'
        || ($registry['campaign_handoff_reviewed'] ?? false) !== true
        || !isset($registry['assets']) || !is_array($registry['assets'])) return null;
    if (!function_exists('fv_r445_campaign_from_raw')) return null;
    $campaign = fv_r445_campaign_from_raw($rawQuery);
    if ($campaign === null) return null;
    $matches = 0;
    foreach ($registry['assets'] as $asset) {
        if (!is_array($asset)) return null;
        $keys = [
            'utm_content' => 'asset_id',
            'utm_source' => 'platform',
            'utm_medium' => 'medium',
            'utm_campaign' => 'campaign'
        ];
        $same = true;
        foreach ($keys as $utm => $field) {
            if (!isset($asset[$field]) || !is_string($asset[$field])
                || !hash_equals($campaign[$utm], $asset[$field])) $same = false;
        }
        if (!$same) continue;
        $matches++;
        if (($asset['review_status'] ?? '') !== 'VERIFIED_PUBLISHED'
            || ($asset['rights_review'] ?? '') !== 'PASS'
            || ($asset['placement_review'] ?? '') !== 'PASS'
            || ($asset['landing_review'] ?? '') !== 'PASS'
            || empty($asset['reviewer']) || empty($asset['published_at'])
            || !is_string($asset['post_url'] ?? null)) return null;
        $parts = parse_url($asset['post_url']);
        if (!is_array($parts) || ($parts['scheme'] ?? '') !== 'https'
            || isset($parts['user']) || isset($parts['pass']) || isset($parts['port'])
            || isset($parts['fragment'])) return null;
        $host = strtolower((string)($parts['host'] ?? ''));
        $path = (string)($parts['path'] ?? '');
        if ($campaign['utm_source'] === 'youtube') {
            if (!in_array($host, ['www.youtube.com','youtube.com'], true)
                || !($path === '/watch' || strpos($path, '/shorts/') === 0)) return null;
        } elseif ($campaign['utm_source'] === 'tiktok') {
            if (!in_array($host, ['www.tiktok.com','tiktok.com'], true)
                || !preg_match('#^/@[A-Za-z0-9._-]+/video/[0-9]+$#D', $path)) return null;
        } else return null;
        if (!preg_match('/^20[0-9]{2}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9](Z|[+-][0-2][0-9]:[0-5][0-9])$/D', $asset['published_at'])) return null;
    }
    return $matches === 1 ? $campaign : null;
}
/** Render the unchanged NASA panel. Unknown or unverified creator data is discarded. */
function fv_r446_render(string $query = ''): string {
    $parent = __DIR__ . '/../apollo-r445/bridge.php';
    if (!is_readable($parent) || !hash_equals(FV_R446_PARENT_SHA256, (string)hash_file('sha256', $parent))) {
        return '<p class="fv-r446-fallback">Source preview unavailable. <a href="' . FV_R446_INVESTIGATION . '">Read the free Apollo 1 investigation</a>.</p>';
    }
    require_once $parent;
    $campaign = fv_r446_authorized_campaign($query, fv_r446_load_registry());
    return fv_r445_render($campaign === null ? '' : http_build_query($campaign, '', '&', PHP_QUERY_RFC3986));
}
/** Register only on opt-in WordPress staging; never in production. */
if (defined('ABSPATH') && function_exists('add_shortcode') && function_exists('wp_get_environment_type')
    && wp_get_environment_type() === 'staging'
    && defined('FV_APOLLO_R446_ENABLE_STAGING') && FV_APOLLO_R446_ENABLE_STAGING === true) {
    // Enqueue parent assets before HTML for ordinary singular content. On dynamic
    // reusable blocks, staging QA must confirm the template-specific loading path.
    if (function_exists('add_action')) add_action('wp_enqueue_scripts', function () {
        global $post;
        if (!$post || !function_exists('has_shortcode')
            || !has_shortcode((string)($post->post_content ?? ''), 'fv_apollo_verified_creator_bridge')) return;
        $root = __DIR__ . '/../apollo-r444/';
        $assets = [
            'assets/review-panel.css' => '682d8985fb13779bcb0156dd28322b07cdcc3330ae8e6cb19ebf031c26a52385',
            'assets/review-panel.js' => 'f6f4d52e8f0b435d196cbfd81e94da6a4e02e9b817eb6ea6efe6e8fd26374af5'
        ];
        foreach ($assets as $file => $digest) {
            if (!is_readable($root . $file)
                || !hash_equals($digest, (string)hash_file('sha256', $root . $file))) return;
        }
        if (function_exists('wp_enqueue_style')) wp_enqueue_style('fv-r444-review',
            plugins_url('../apollo-r444/assets/review-panel.css', __FILE__), [], '0.0.1-r444');
        if (function_exists('wp_enqueue_script')) wp_enqueue_script('fv-r444-review',
            plugins_url('../apollo-r444/assets/review-panel.js', __FILE__), [], '0.0.1-r444', true);
    }, 10);
    add_shortcode('fv_apollo_verified_creator_bridge', function () {
        return fv_r446_render((string)($_SERVER['QUERY_STRING'] ?? ''));
    });
}
