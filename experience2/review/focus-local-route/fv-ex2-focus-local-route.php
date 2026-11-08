<?php
/**
 * Plugin Name: FV EX2 Isolated Focus Journey Guard (Review Only)
 * Description: Routes the five seven-chapter preview Focus links to a disposable local QA page. Never registers on production.
 * Version: 0.1.0
 * License: Internal, isolated WordPress Playground review only.
 *
 * This file does not register signups, add tracking, send email, collect visitor
 * data, set cookies, process a checkout or claim Jetpack success.
 */
if (!defined('ABSPATH') || !function_exists('home_url') || !function_exists('wp_parse_url')) { return; }
if (defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'production') { return; }
$fv_ex2_route_host = strtolower(rtrim((string) wp_parse_url(home_url('/'), PHP_URL_HOST), '.'));
$fv_ex2_route_local = in_array($fv_ex2_route_host, array('localhost','127.0.0.1','::1','[::1]'), true)
    || (strlen($fv_ex2_route_host) > 10 && substr($fv_ex2_route_host, -10) === '.localhost')
    || $fv_ex2_route_host === 'wpsandbox.wordpress.net';
unset($fv_ex2_route_host);
if (!$fv_ex2_route_local) { unset($fv_ex2_route_local); return; }
unset($fv_ex2_route_local);
if (!function_exists('get_option') ||
    get_option('fv_ex2_playground_review_only', '') !== 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1') { return; }
if (!function_exists('add_filter')) { return; }

add_filter('do_shortcode_tag', static function ($html, $tag) {
    if ($tag !== 'fv_ex2_playground' || !function_exists('is_page') || !is_page('fv-ex2-review')) {
        return $html;
    }
    if (!is_string($html) || strlen($html) < 30000 || strpos($html, 'data-fv-home-flagship') === false) {
        throw new RuntimeException('FV EX2 isolated Focus route: incomplete flagship markup');
    }
    // The exact five existing links are replaced ONLY inside the isolated preview
    // shortcode's output; no WP editor source, global options or public pages change.
    $original = 'href="https://finalvestige.com/focus/"';
    if (substr_count($html, $original) !== 5) {
        throw new RuntimeException('FV EX2 isolated Focus route: expected five Focus links; refuse drift');
    }
    if (!function_exists('esc_url')) {
        throw new RuntimeException('FV EX2 isolated Focus route: missing WordPress escaping function');
    }
    $url = esc_url(home_url('/fv-ex2-focus-review/'));
    if (!$url) { throw new RuntimeException('FV EX2 isolated Focus route: empty local URL'); }
    $replacement = 'href="' . $url . '" data-fv-ex2-isolated-focus="1"';
    $out = str_replace($original, $replacement, $html);
    if (substr_count($out, 'data-fv-ex2-isolated-focus="1"') !== 5 || strpos($out, $original) !== false) {
        throw new RuntimeException('FV EX2 isolated Focus route: incomplete rewrite');
    }
    return $out;
}, 90, 4);
