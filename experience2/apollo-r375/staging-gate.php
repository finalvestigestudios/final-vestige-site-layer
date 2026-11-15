<?php
/**
 * FV Apollo Evidence Atlas R375 — controlled, read-only STAGING loader.
 * Include manually from an approved staging-only plugin or WP-CLI harness with
 * the entire experience2/ directory preserved. Not an activation or deployment.
 * No network I/O, DB writes, options, analytics, remote media or payment links.
 */
if (!defined('ABSPATH')) { exit; }

const FV_APOLLO_R375_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';

function fv_apollo_r375_fallback(): string {
    return '<section aria-label="Apollo evidence unavailable"><h2>Documentary evidence temporarily unavailable</h2>'
        . '<p>The independently reviewed evidence experience is not enabled or has not passed source verification.</p>'
        . '<p><a href="'.htmlspecialchars(FV_APOLLO_R375_FREE, ENT_QUOTES, 'UTF-8')
        .'">Read the existing free Apollo 1 investigation</a></p></section>';
}

/** Exact site configuration and explicit founder-approved staging hostname. */
function fv_apollo_r375_environment(): bool {
    if (!defined('FV_APOLLO_R375_STAGING_ENABLED') || FV_APOLLO_R375_STAGING_ENABLED !== true ||
        !defined('FV_APOLLO_R375_APPROVED_HOST') ||
        !function_exists('wp_get_environment_type') || !function_exists('home_url')) { return false; }
    if (wp_get_environment_type() !== 'staging') { return false; }
    $host = FV_APOLLO_R375_APPROVED_HOST;
    if (!is_string($host) || !preg_match('/^[a-z0-9][a-z0-9.-]{1,250}[a-z0-9]$/D', $host) ||
        in_array($host, array('finalvestige.com', 'www.finalvestige.com', 'localhost', '127.0.0.1'), true)) {
        return false;
    }
    $parts = parse_url(home_url('/'));
    return is_array($parts) && ($parts['scheme'] ?? '') === 'https' &&
        ($parts['host'] ?? '') === $host && !isset($parts['user']) && !isset($parts['pass']) &&
        (!isset($parts['port']) || (int)$parts['port'] === 443);
}

/** SHA-256 is a review seal, not a commercial-media license or NASA endorsement. */
function fv_apollo_r375_manifest(): array {
    return array(
        'apollo-r365/chrono-rail.php' => '3628aacdb8abb70861a8304d80dcfe937918a7053812bba60c8ab3ab5f49cfd9',
        'apollo-r367/sealed-chronology.php' => '0c6e6d04711a3ec66263a2757ee291e515f4a553f80be41148e484487b5e5f6b',
        'apollo-r371/source-gallery.php' => 'fabe48bc49c208cb7762c96dace0fbbecfd1d56ac2873666b77b3874f413310b',
        'apollo-r372/evidence-path.php' => 'ede74dcee85ba936af7710b3704ffc29aa376b541686002a7ac4552816d917f5',
        'apollo-r372/staging-assets.php' => 'c560dc9a094163fe9d45fa5d560bbf470154685ad9bd3a759737908c2b557fce',
        'apollo-r372/assets/evidence-path.css' => 'a7b05064f31439840d68a973db000bc6d6836c05d60b5a6f239f83fb1b9fb5c7',
    );
}

/** Resolve without following symlinks; reject missing, altered or escaped paths. */
function fv_apollo_r375_files_valid(string $root): bool {
    $root = realpath($root);
    if ($root === false || !is_dir($root)) { return false; }
    foreach (fv_apollo_r375_manifest() as $relative => $expected) {
        $file = realpath($root . '/' . $relative);
        if ($file === false || !str_starts_with($file, $root . DIRECTORY_SEPARATOR) ||
            !is_file($file) || !is_readable($file) || is_link($root . '/' . $relative) ||
            !hash_equals($expected, hash_file('sha256', $file))) { return false; }
    }
    return true;
}

/** Do not override an already active version or other owners' shortcode handlers. */
function fv_apollo_r375_conflict(): bool {
    foreach (array('fv_apollo_r365_rows','fv_apollo_r367_is_sealed',
        'fv_apollo_r371_catalog','fv_apollo_r372_render') as $symbol) {
        if (function_exists($symbol)) { return true; }
    }
    return false;
}

function fv_apollo_r375_activate(): bool {
    if (!fv_apollo_r375_environment() || fv_apollo_r375_conflict() ||
        !function_exists('remove_action') || !function_exists('wp_enqueue_style') ||
        !function_exists('plugins_url')) { return false; }
    $root = dirname(__DIR__);
    if (!fv_apollo_r375_files_valid($root)) { return false; }
    foreach (array('apollo-r365/chrono-rail.php', 'apollo-r367/sealed-chronology.php',
        'apollo-r371/source-gallery.php', 'apollo-r372/evidence-path.php',
        'apollo-r372/staging-assets.php') as $relative) { require_once $root . '/' . $relative; }
    // Legacy R365 registers a sitewide CSS enqueue. This gate only permits the
    // R372 component and its bounded, pre-head shortcode-aware R372 CSS loader.
    remove_action('wp_enqueue_scripts', 'fv_apollo_r365_enqueue', 20);
    return function_exists('fv_apollo_r372_shortcode') && function_exists('fv_apollo_r372_needs_assets');
}

// Even when disabled, shortcode outputs a useful safe HTML link, never raw syntax.
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_source_path_r372', 'fv_apollo_r375_fallback');
}
if (function_exists('add_action')) {
    add_action('plugins_loaded', 'fv_apollo_r375_activate', 50);
}
