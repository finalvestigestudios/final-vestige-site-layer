<?php
/**
 * Plugin Name: FV Apollo Research Desk Source-Role Crosswalk — R334 (Staging Only)
 * Description: Read-only six-record comparison, distinguishing NASA photographs from documentary findings.
 * Version: 0.0.1-staging
 * License: GPL-2.0-or-later
 */
if (!defined('ABSPATH')) { return; }

const FV_R334_REPORT = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R334_OVERVIEW = 'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/';
const FV_R334_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';

function fv_r334_records(): array {
    // Original six Research Desk identities/links from PR #158, ledger.html Git blob
    // 403d128c57b9bc82dac7c619651689070edef86c. Photo catalogue records
    // are context, not proof of Review Board conclusions or reusable media.
    return [
        ['01', 'Three men. One ground test.', 'S67-19766', 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/', FV_R334_OVERVIEW, 'NASA historical overview'],
        ['02', 'An atmosphere built for a different risk.', 'S67-15717', 'https://www.nasa.gov/image-detail/amf-s67-15717/', FV_R334_REPORT, 'Apollo 204 Review Board report'],
        ['03', 'Fourteen seconds changed the system.', 'S66-58038', 'https://www.nasa.gov/image-detail/amf-s66-58038/', FV_R334_REPORT, 'Apollo 204 Review Board report'],
        ['04', 'The hatch opened inward.', 'KSC-20170124-PH_KLS01_0164', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/', FV_R334_REPORT, 'Apollo 204 Review Board report'],
        ['05', 'The spark was never conclusively identified.', 'S67-21294', 'https://www.nasa.gov/image-detail/amf-s67-21294/', FV_R334_REPORT, 'Apollo 204 Review Board report'],
        ['06', 'Inward became outward.', 'KSC-20170124-PH_KLS01_0090', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/', FV_R334_REPORT, 'Apollo 204 Review Board report'],
    ];
}
function fv_r334_e(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r334_valid(array $records): bool {
    if (count($records) !== 6) { return false; }
    $seen = [];
    foreach ($records as $r) {
        if (count($r) !== 6 || !preg_match('/^0[1-6]$/', $r[0]) || isset($seen[$r[0]])) { return false; }
        $seen[$r[0]] = true;
        if (!(strpos($r[3], 'https://www.nasa.gov/image-detail/') === 0)) { return false; }
        if (!in_array($r[4], [FV_R334_REPORT, FV_R334_OVERVIEW], true)) { return false; }
        if ($r[0] === '01' ? $r[4] !== FV_R334_OVERVIEW : $r[4] !== FV_R334_REPORT) { return false; }
    }
    return true;
}
function fv_r334_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('has_shortcode') || !function_exists('get_post')) { return; }
    $post = get_post();
    if ($post && has_shortcode((string) $post->post_content, 'fv_apollo_custody_r334') && function_exists('wp_enqueue_style')) {
        wp_enqueue_style('fv-apollo-custody-r334', plugins_url('assets/custody.css', __FILE__), [], '0.0.1-r334');
    }
}
function fv_r334_render(): string {
    static $instance = 0;
    $instance++;
    $records = fv_r334_records();
    if (!fv_r334_valid($records)) {
        return '<aside data-fv-custody-status="withheld"><p>Source roles could not be verified. This staging comparison is withheld.</p><a href="'.fv_r334_e(FV_R334_REPORT).'">Read NASA’s Review Board report</a></aside>';
    }
    $id = 'fv-r334-'.$instance;
    $h = '<section class="fv-r334" data-fv-custody-status="source-roles-staging-review" data-fv-geo-policy="no-coordinates-or-map" aria-labelledby="'.$id.'-heading">';
    $h .= '<header><p class="fv-r334__eyebrow">FINAL VESTIGE / APOLLO 1 / RESEARCH DESK</p><h2 id="'.$id.'-heading">What a photograph can — and cannot — establish</h2>';
    $h .= '<p>Six Research Desk records pair NASA image-detail pages with separate NASA historical documents. The image links identify visual records, not evidence that a photograph proves each finding. This crosswalk is awaiting editorial and media-rights approval.</p></header>';
    $h .= '<ol class="fv-r334__records" aria-label="NASA source-role crosswalk">';
    foreach ($records as $r) {
        [$n, $title, $accession, $image, $document, $doclabel] = $r;
        $entry = $id.'-record-'.$n;
        $h .= '<li class="fv-r334__record" id="'.$entry.'" data-fv-record="'.$n.'" data-fv-source-photo="context-only" data-fv-source-document="institutional-source" data-fv-image-rights="not-cleared-for-reuse">';
        $h .= '<p class="fv-r334__number">RESEARCH DESK '.$n.' / 06</p><h3>'.fv_r334_e($title).'</h3><p>NASA photographic accession: <code>'.fv_r334_e($accession).'</code> — not a Review Board report identifier.</p>';
        $h .= '<details><summary>Compare the two source roles — record '.$n.'</summary><div class="fv-r334__details">';
        $h .= '<p><strong>Photographic context only:</strong> <a data-fv-source-role="contextual-photo" href="'.fv_r334_e($image).'" rel="noopener noreferrer">NASA image-detail record '.fv_r334_e($accession).'</a>. This metadata is not independent proof of the finding or commercial reuse permission.</p>';
        $h .= '<p><strong>Institutional documentary source:</strong> <a data-fv-source-role="documentary-source" href="'.fv_r334_e($document).'" rel="noopener noreferrer">'.fv_r334_e($doclabel).'</a>. Review the original source and its limitations; the same NASA institution is not an independent witness.</p>';
        $h .= '</div></details></li>';
    }
    $h .= '</ol><footer><p><strong>Editorial boundary:</strong> No definitive Apollo 1 ignition point, NASA endorsement, image-reuse clearance, geolocation, paid offer or sale is asserted here.</p>';
    $h .= '<p><a data-fv-cta="apollo-read-free-investigation" href="'.fv_r334_e(FV_R334_FREE).'">Read the free Apollo 1 investigation</a> (editorial continuation, not checkout)</p></footer></section>';
    return $h;
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_r334_enqueue', 20); }
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_custody_r334', 'fv_r334_render'); }
