<?php
/**
 * Apollo R349 — shared reviewed source-page identities (READ-ONLY research staging).
 * A URL on nasa.gov is not sufficient: each page/record needs independent editorial
 * and media-rights review. Exact-match only; no URL canonicalization or redirects.
 */
if (!defined('ABSPATH')) { exit; }
function fv_apollo_r349_approved_sources(): array {
    return array(
        'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html' => '1967 Review Board — findings',
        'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html' => '1967 Review Board — investigation',
        'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html' => '1967 Review Board — chronology',
        'https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/' => 'Later NASA institutional history',
        'https://www.nasa.gov/image-detail/amf-s67-15717/' => 'NASA photo accession S67-15717',
        'https://www.nasa.gov/image-detail/amf-s66-58038/' => 'NASA photo accession S66-58038',
        'https://www.nasa.gov/image-detail/amf-s67-21294/' => 'NASA photo accession S67-21294',
        'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/' => 'NASA photo accession KSC-20170124-PH_KLS01_0090',
    );
}
function fv_apollo_r349_is_source_approved($url): bool {
    return is_string($url) && array_key_exists($url, fv_apollo_r349_approved_sources());
}
/**
 * Returns a safe accessible link or visible quarantine notice. Text and provenance
 * remain intact. Unreviewed links are NEVER silently used in screen or print HTML.
 * This renders no image, starts no network request, and adds no analytics.
 */
function fv_apollo_r349_source_link($url, $label, array $data = array()): string {
    $esc = static function($value): string {
        return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    };
    $integrity_file = dirname(__DIR__) . '/apollo-r350/integrity.php';
    if (is_readable($integrity_file)) { require_once $integrity_file; }
    $reviewed_record_pairing = function_exists('fv_apollo_r350_integrity_ok') && fv_apollo_r350_integrity_ok();
    if (!fv_apollo_r349_is_source_approved($url) || !$reviewed_record_pairing) {
        return '<span class="fv-apollo-source-quarantined" data-fv-source-review-required="true">'
             . $esc($label) . ' — source link withheld pending editorial verification</span>';
    }
    $attrs = '';
    foreach ($data as $key=>$value) {
        // Accept only reviewable data attributes, not onclick, style, href, etc.
        if (is_string($key) && preg_match('/\Adata-[a-z][a-z0-9-]*\z/D', $key)) {
            $attrs .= ' ' . $key . '="' . $esc($value) . '"';
        }
    }
    return '<a href="' . $esc($url) . '" rel="noopener noreferrer"' . $attrs . '>' . $esc($label) . '</a>';
}
