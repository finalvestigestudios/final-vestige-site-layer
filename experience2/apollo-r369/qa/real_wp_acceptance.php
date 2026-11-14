<?php
/**
 * Read-only actual WP-CLI staging acceptance. DO NOT run on production.
 * Usage: FV_APOLLO_R369_READONLY_STAGING=1 wp eval-file /path/real_wp_acceptance.php
 * Reads only: no wp_insert_post, activate_plugin, option writes or network calls.
 */
if (!defined('WP_CLI') || !WP_CLI || getenv('FV_APOLLO_R369_READONLY_STAGING') !== '1') {
    throw new RuntimeException('HOLD: requires explicit WP-CLI staging acceptance opt-in');
}
$host = strtolower((string)parse_url(home_url('/'), PHP_URL_HOST));
if (in_array($host, array('finalvestige.com','www.finalvestige.com'), true)) {
    throw new RuntimeException('HOLD: refuse production host');
}
if (!function_exists('wp_get_theme') || !function_exists('do_shortcode')) {
    throw new RuntimeException('HOLD: genuine WordPress bootstrap absent');
}
$repo = dirname(__DIR__,2);
foreach (array('apollo-r365/chrono-rail.php','apollo-r367/sealed-chronology.php',
               'apollo-r368/reflow-adapter.php','apollo-r369/evidence-bridge.php') as $relative) {
    $file = $repo.'/'.$relative;
    if (!is_readable($file)) {throw new RuntimeException('Missing repo source: '.$relative);}
    require_once $file;
}
$html = do_shortcode('[fv_apollo_educator_bridge_r369]');
$test = array(
 'theme'=> wp_get_theme()->get('Name'),
 'shortcode'=> shortcode_exists('fv_apollo_educator_bridge_r369'),
 'sources'=>substr_count($html,'data-fv-nasa-source'),
 'source_drawers'=>substr_count($html,'data-fv-source-drawer'),
 'free_ctas'=>substr_count($html,'data-fv-free-cta'),
 'teaching_lenses'=>substr_count($html,'class="fv-apollo-r369__lens"'),
 'enqueued_style'=>wp_style_is('fv-apollo-r369-educator-bridge','enqueued'),
 'payment_href'=>preg_match('~href="https?://(?:www\.)?payhip\.com/~i',$html) === 1,
 'host'=>$host,
 'content_modified'=>false,
);
if ($test['sources'] !== 4 || $test['source_drawers'] !== 4 || $test['free_ctas'] !== 1
 || $test['teaching_lenses'] !== 3 || !$test['shortcode'] || !$test['enqueued_style'] || $test['payment_href']) {
    throw new RuntimeException('FAIL real WordPress source/CTA/asset contract: '.json_encode($test));
}
WP_CLI::log(json_encode($test,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES));
WP_CLI::success('Read-only WordPress acceptance PASS (not HTTP/browser/CSP/axe).');
