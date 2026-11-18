<?php
/**
 * Apollo R445: first-party, non-tracking, campaign continuity for the free investigation.
 * Standalone isolated staging candidate; requires hash-pinned R444 parent.
 * No outbound tracking, JS, redirects, collection or checkout.
 */
const FV_R445_R444_FILE_SHA256 = '19366737af847a0bc69ef91d238016d1436fa6c95ccc46848ebf4ead8ce8ae01';
const FV_R445_DESTINATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R445_PARENT_RELATIVE = '/../apollo-r444/review_panel.php';

/** Parse only canonical four UTM fields; suspicious/partial/duplicate tokens discard the entire quartet. */
function fv_r445_campaign_from_raw(string $raw): ?array {
    if ($raw === '' || strlen($raw) > 768) return null;
    $expected = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
    $values = [];
    foreach (explode('&', $raw) as $pair) {
        $parts = explode('=', $pair, 2);
        $key = rawurldecode($parts[0]);
        if (!in_array($key, $expected, true)) continue;
        if (array_key_exists($key, $values) || count($parts) !== 2) return null;
        $values[$key] = rawurldecode($parts[1]);
    }
    if (count($values) !== 4) return null;
    if (!in_array($values['utm_source'], ['youtube','tiktok'], true)) return null;
    if ($values['utm_medium'] !== 'organic_social') return null;
    if (!preg_match('/^apollo_pilot_20[0-9]{2}_(0[1-9]|1[0-2])$/D', $values['utm_campaign'])) return null;
    if (!preg_match('/^[A-Za-z0-9][A-Za-z0-9_-]{5,79}$/D', $values['utm_content'])) return null;
    return array_replace(array_fill_keys($expected, ''), $values);
}
function fv_r445_destination(?array $campaign): string {
    if ($campaign === null) return FV_R445_DESTINATION;
    return FV_R445_DESTINATION . '?' . http_build_query($campaign, '', '&', PHP_QUERY_RFC3986);
}
function fv_r445_fallback(): string {
    return '<p class="fv-r445-fallback">Evidence preview unavailable. <a href="' . FV_R445_DESTINATION . '">Read the free Apollo 1 investigation</a>.</p>';
}
/**
 * Render the exact R444 evidence panel, modifying ONLY its already-existing next-step destination.
 * Never display creator/visitor identifiers, promise that attribution is measured, or insert a second CTA.
 */
function fv_r445_render(string $rawQuery = ''): string {
    $parent = __DIR__ . FV_R445_PARENT_RELATIVE;
    if (!is_readable($parent) || !hash_equals(FV_R445_R444_FILE_SHA256, (string)hash_file('sha256', $parent))) return fv_r445_fallback();
    require_once $parent;
    if (!function_exists('fv_r444_render') || !function_exists('fv_r444_sources')) return fv_r445_fallback();
    if (fv_r444_sources() === null) return fv_r445_fallback();
    foreach (['assets/review-panel.css' => FV_R444_CSS_SHA256, 'assets/review-panel.js' => FV_R444_JS_SHA256] as $name => $digest) {
        $asset = dirname($parent) . '/' . $name;
        if (!is_readable($asset) || !hash_equals($digest, (string)hash_file('sha256', $asset))) return fv_r445_fallback();
    }
    $html = fv_r444_render();
    $old = 'href="' . FV_R445_DESTINATION . '"';
    if (substr_count($html, $old) !== 1 || substr_count($html, 'class="fv-r444__next"') !== 1) return fv_r445_fallback();
    $new = 'href="' . htmlspecialchars(fv_r445_destination(fv_r445_campaign_from_raw($rawQuery)), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '"';
    return str_replace($old, $new, $html);
}
/**
 * WordPress integration is explicitly staging-only and NOT activated by this source-only PR.
 * Production never registers this shortcode, regardless of its content.
 */
if (defined('ABSPATH') && function_exists('add_shortcode') && function_exists('wp_get_environment_type')
    && wp_get_environment_type() === 'staging'
    && defined('FV_APOLLO_R445_ENABLE_STAGING') && FV_APOLLO_R445_ENABLE_STAGING === true) {
    // Pre-head enqueue for ordinary singular post content. Reusable/dynamic block templates need separate staging QA.
    if (function_exists('add_action')) add_action('wp_enqueue_scripts', function () {
        global $post;
        if (!$post || !function_exists('has_shortcode') || !has_shortcode((string)($post->post_content ?? ''), 'fv_apollo_campaign_bridge')) return;
        $root = dirname(__DIR__) . '/apollo-r444/';
        $assets = ['assets/review-panel.css' => 'fv-r444-review', 'assets/review-panel.js' => 'fv-r444-review'];
        $parent = $root . 'review_panel.php';
        if (!is_readable($parent) || !hash_equals(FV_R445_R444_FILE_SHA256, (string)hash_file('sha256', $parent))) return;
        foreach ($assets as $path => $handle) {
            $digest = substr($path, -4) === '.css' ? '682d8985fb13779bcb0156dd28322b07cdcc3330ae8e6cb19ebf031c26a52385' : 'f6f4d52e8f0b435d196cbfd81e94da6a4e02e9b817eb6ea6efe6e8fd26374af5';
            if (!is_readable($root . $path) || !hash_equals($digest, (string)hash_file('sha256', $root . $path))) return;
        }
        if (function_exists('wp_enqueue_style')) wp_enqueue_style('fv-r444-review', plugins_url('../apollo-r444/assets/review-panel.css', __FILE__), [], '0.0.1-r444');
        if (function_exists('wp_enqueue_script')) wp_enqueue_script('fv-r444-review', plugins_url('../apollo-r444/assets/review-panel.js', __FILE__), [], '0.0.1-r444', true);
    }, 10);
    add_shortcode('fv_apollo_campaign_bridge', function () {
        return fv_r445_render((string)($_SERVER['QUERY_STRING'] ?? ''));
    });
}
