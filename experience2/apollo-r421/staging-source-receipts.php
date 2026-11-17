<?php
/**
 * Plugin Name: FV Apollo R421 Evidence Receipts (STAGING ONLY)
 * Description: Standalone, provenance-pinned source receipts for educator source-custody, no media or commerce.
 * Version: 0.0.1-r421
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
const FV_R421_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R421_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
const FV_R421_DEPENDENCIES = array(
    '../apollo-r420/staging-educator-source-lab.php' => 'e3f1c9897e453512569a0fdd937c01e3b6e7f783',
    'assets/source-receipts.css' => 'b7ec2d43c59fcc5a8c10a747ec0ab08a24ffcf44',
    'assets/source-receipts.js' => 'bb83bb6d1fb203f7f786292aa9701bce149552bb',
);
function fv_r421_blob(string $data): string { return sha1('blob ' . strlen($data) . "\0" . $data); }
function fv_r421_verified(): bool {
    foreach (FV_R421_DEPENDENCIES as $rel => $expected) {
        $p = __DIR__ . '/' . $rel;
        if (!is_file($p) || !is_readable($p)) return false;
        $v = file_get_contents($p);
        if (!is_string($v) || !hash_equals($expected, fv_r421_blob($v))) return false;
    }
    return true;
}
function fv_r421_allowed(): bool {
    return defined('FV_R421_ENABLED') && FV_R421_ENABLED === true
        && defined('FV_R421_STAGING_PAGE_ID') && (int) FV_R421_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id')
        && (int)get_queried_object_id() === (int)FV_R421_STAGING_PAGE_ID;
}
function fv_r421_escape(string $v): string { return htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r421_fallback(): string {
    return '<p class="fv-r421-fallback">Evidence receipts are temporarily unavailable. <a href="' . FV_R421_ARTICLE . '">Read the free Apollo 1 investigation</a>.</p>';
}
/**
 * Reuse exactly the three reviewed R420 educator cases. These link to NASA sources
 * and photographs only; no NASA image is embedded or treated as accident telemetry.
 */
function fv_r421_receipts(): ?array {
    if (!fv_r421_verified()) return null;
    if (!function_exists('fv_r420_cases')) require_once dirname(__DIR__) . '/apollo-r420/staging-educator-source-lab.php';
    $cases = fv_r420_cases();
    if (!is_array($cases) || count($cases) !== 3) return null;
    $receiptList = array();
    foreach ($cases as $i => $c) {
        if (!is_array($c) || count($c) !== 10 || $c[0] !== sprintf('%02d', $i + 1)) return null;
        foreach ($c as $field) if (!is_string($field) || trim($field) === '' || strlen($field) > 1500) return null;
        foreach (array(7, 8) as $n) {
            $url = parse_url($c[$n]);
            if (!is_array($url) || ($url['scheme'] ?? '') !== 'https' || ($url['host'] ?? '') !== 'www.nasa.gov'
                || isset($url['user']) || isset($url['pass']) || isset($url['fragment']) || isset($url['query'])) return null;
        }
        if (strpos($c[8], 'https://www.nasa.gov/image-detail/') !== 0) return null;
        if (!in_array($c[7], array(
            'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
            'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
        ), true)) return null;
        $receiptList[] = $c;
    }
    return $receiptList;
}
function fv_r421_markup(int $instance, array $data): string {
    if ($instance < 1 || $instance > 1000 || fv_r421_receipts() !== $data) return fv_r421_fallback();
    $prefix = 'fv-r421-' . $instance;
    $s = '<section class="fv-r421" data-fv-r421-receipts aria-labelledby="' . $prefix . '-title"><div class="fv-r421__inner">';
    $s .= '<header><p class="fv-r421__eyebrow">FINAL VESTIGE / APOLLO 1 / RESEARCH DESK</p><h2 id="' . $prefix . '-title">Take the evidence trail with you.</h2>';
    $s .= '<p>Three concise, copy-ready research receipts for independent source checks or classroom discussion. Each identifies the historical finding, its uncertainty, the date of an illustrative photograph, and two separate NASA reference links.</p>';
    $s .= '<p>These are original editorial study notes, not an official NASA record, a photograph license, or a paid educational product.</p></header>';
    $s .= '<nav class="fv-r421__nav" aria-label="Evidence receipt navigation">';
    foreach ($data as $c) $s .= '<a href="#' . $prefix . '-receipt-' . fv_r421_escape($c[0]) . '">Receipt ' . fv_r421_escape($c[0]) . '</a>';
    $s .= '</nav><ol class="fv-r421__list">';
    foreach ($data as $c) {
        list($num,$title,$question,$finding,$limit,$photoDate,$photoLimit,$publication,$photoUrl,$guidance) = $c;
        $target = $prefix . '-receipt-' . $num;
        $text = 'Final Vestige — Apollo 1 / Evidence Receipt ' . $num . "\n";
        $text .= 'Question: ' . $question . "\nHistorical finding: " . $finding;
        $text .= "\nEvidence limitation: " . $limit;
        $text .= "\nRelated photograph date: " . $photoDate;
        $text .= "\nPhotograph is not proof because: " . $photoLimit;
        $text .= "\nNASA historical publication: " . $publication;
        $text .= "\nNASA image catalogue (photo not reproduced): " . $photoUrl;
        $text .= "\nOriginal FV research note, no NASA endorsement or photograph reuse permission.\n";
        $s .= '<li class="fv-r421__card" id="' . fv_r421_escape($target) . '"><p class="fv-r421__tag">RECEIPT ' . fv_r421_escape($num) . ' / 03</p>';
        $s .= '<h3>' . fv_r421_escape($title) . '</h3><p><strong>Research question:</strong> ' . fv_r421_escape($question) . '</p>';
        $s .= '<details><summary>Examine the finding, limitation and photo custody</summary><div class="fv-r421__details">';
        $s .= '<p><strong>Finding:</strong> ' . fv_r421_escape($finding) . '</p><p><strong>Cannot establish:</strong> ' . fv_r421_escape($limit) . '</p>';
        $s .= '<p><strong>Related photo date:</strong> ' . fv_r421_escape($photoDate) . '</p><p><strong>Photo limitation:</strong> ' . fv_r421_escape($photoLimit) . '</p>';
        $s .= '<p><strong>Classroom question:</strong> ' . fv_r421_escape($guidance) . '</p></div></details>';
        $s .= '<div class="fv-r421__sources"><a href="' . fv_r421_escape($publication) . '">NASA historical publication</a>';
        $s .= '<a href="' . fv_r421_escape($photoUrl) . '">NASA photo catalogue (not reproduced)</a></div>';
        $s .= '<div class="fv-r421__copy"><p class="fv-r421__copy-label"><strong>Plain-text receipt:</strong> available to select or print, even without JavaScript.</p>';
        $s .= '<pre tabindex="0" id="' . fv_r421_escape($target) . '-text">' . fv_r421_escape($text) . '</pre>';
        $s .= '<button type="button" hidden data-fv-r421-copy="' . fv_r421_escape($target) . '-text">Copy receipt</button>';
        $s .= '<span class="fv-r421__status" aria-live="polite" aria-atomic="true"></span></div></li>';
    }
    $s .= '</ol><footer class="fv-r421__footer"><p><strong>Editorial and media rights:</strong> citations are not permission to republish NASA photographs or identify NASA as a commercial partner. Consult <a href="' . FV_R421_RIGHTS . '">NASA media use and non-endorsement guidance</a> before any asset reuse.</p>';
    $s .= '<p><a class="fv-r421__next" href="' . FV_R421_ARTICLE . '">Read the full free Apollo 1 investigation</a></p></footer></div></section>';
    return $s;
}
function fv_r421_shortcode(): string {
    if (!fv_r421_allowed()) return fv_r421_fallback();
    $data = fv_r421_receipts();
    if ($data === null) return fv_r421_fallback();
    if (!isset($GLOBALS['fv_r421_instance'])) $GLOBALS['fv_r421_instance'] = 0;
    return fv_r421_markup(++$GLOBALS['fv_r421_instance'], $data);
}
function fv_r421_enqueue(): void {
    if (!fv_r421_allowed() || !fv_r421_verified() || !function_exists('plugins_url')) return;
    if (function_exists('wp_enqueue_style')) wp_enqueue_style('fv-apollo-r421-receipts', plugins_url('assets/source-receipts.css', __FILE__), array(), '0.0.1-r421');
    if (function_exists('wp_enqueue_script')) wp_enqueue_script('fv-apollo-r421-copy', plugins_url('assets/source-receipts.js', __FILE__), array(), '0.0.1-r421', true);
}
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r421_enqueue', 20);
if (function_exists('add_shortcode')) add_shortcode('fv_ex2_apollo_source_receipts_r421', 'fv_r421_shortcode');
