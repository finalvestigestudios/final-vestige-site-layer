<?php
/**
 * Plugin Name: FV Apollo Research Desk Custody Bridge — R334 (STAGING ONLY)
 * Description: Independent, link-only source-precedence review of Research Desk PR #158. No production activation.
 * Version: 0.0.1-review
 * License: GPL-2.0-or-later
 * Not a modification of PR #158, homepage PR #49, or Apollo runtime R281.
 */
if (!defined('ABSPATH')) { return; }

const FV_R334_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R334_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R334_RETROSPECTIVE = 'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/';

/**
 * Captures the first-link/second-link relationships as found in Research Desk
 * PR #158's ledger.html blob 403d128c57b9bc82dac7c619651689070edef86c.
 * Primary documentary support is shown FIRST in this separate proposed bridge;
 * an image detail page is NEVER represented as a Review Board conclusion.
 * All images are source LINKS only. Commercial-use rights are NOT cleared.
 */
function fv_r334_records(): array {
    return [
        ['01','Ground-test context','CONTEXTUAL RECORD',FV_R334_RETROSPECTIVE,'Later NASA historical summary','https://www.nasa.gov/image-detail/apollo-1-crew-honored/','Later commemorative image record','context'],
        ['02','Oxygen and fire risk','PRIMARY REVIEW BOARD RECORD',FV_R334_BOARD,'1967 Review Board findings','https://www.nasa.gov/image-detail/amf-s67-15717/','Photograph of Spacecraft 012 before the fire','review'],
        ['03','Instrument chronology','INSTRUMENT CHRONOLOGY',FV_R334_BOARD,'1967 Review Board findings','https://www.nasa.gov/image-detail/amf-s66-58038/','1966 crew training photograph','review'],
        ['04','Inward-opening hatch','HARDWARE AND DESIGN FINDING',FV_R334_BOARD,'1967 Review Board findings','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/','2017 tribute exhibition photograph','review'],
        ['05','Ignition-source uncertainty','EVIDENCE BOUNDARY',FV_R334_BOARD,'1967 Review Board findings','https://www.nasa.gov/image-detail/amf-s67-21294/','Post-fire command module photograph','context'],
        ['06','Post-fire redesign','ENGINEERING RESPONSE',FV_R334_BOARD,'1967 Review Board report; additional redesign sources require review','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','2017 tribute exhibition photograph','review'],
    ];
}
function fv_r334_valid(array $records): bool {
    if (count($records)!==6 || array_keys($records)!==range(0,5)) { return false; }
    $expectedImages=[
        'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
        'https://www.nasa.gov/image-detail/amf-s67-15717/',
        'https://www.nasa.gov/image-detail/amf-s66-58038/',
        'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
        'https://www.nasa.gov/image-detail/amf-s67-21294/',
        'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'
    ];
    foreach($records as $i=>$r) {
        if (count($r)!==8 || $r[0]!==sprintf('%02d',$i+1) ||
            $r[3]!==($i===0 ? FV_R334_RETROSPECTIVE : FV_R334_BOARD) ||
            $r[5]!==$expectedImages[$i] ||
            $r[7]!== (in_array($i,[1,2,3,5],true) ? 'review' : 'context')) { return false; }
        foreach($r as $field) { if (!is_string($field) || trim($field)==='') { return false; } }
    }
    return true;
}
function fv_r334_escape(string $text): string {
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv_r334_render(): string {
    $records=fv_r334_records();
    if (!fv_r334_valid($records)) {
        return '<aside data-fv-r334-status="source-custody-failed"><p><strong>Source-custody review is unavailable.</strong> The six-record comparison was withheld because the source check failed.</p><p><a href="'.fv_r334_escape(FV_R334_BOARD).'">Read the original Apollo 204 Review Board findings at NASA</a></p></aside>';
    }
    static $instance=0, $linked=false;
    $instance++;
    $id='fv-r334-'.$instance;
    $s='<section class="fv-r334" aria-labelledby="'.$id.'-title" data-fv-custody-status="staging-editorial-review" data-fv-rights="link-only-not-cleared" data-fv-attribution="none">';
    $s.='<header><p class="fv-r334__eyebrow">Final Vestige / Apollo 1 / Research Desk source audit</p><h2 id="'.$id.'-title">A photograph is not the finding<span class="fv-r334__sr"> · Source audit '.$instance.'</span></h2>';
    $s.='<p>Six Research Desk cards, two different record types. The historical finding must lead to the document that actually states it; an image catalogue entry supplies context, not independent proof or permission to reuse the photograph.</p>';
    $s.='<p class="fv-r334__status">EDITORIAL REVIEW OPEN · Four document/photo precedence questions require a Research Desk owner decision. This is a staging comparison, not a correction to the published website.</p></header>';
    $s.='<ol class="fv-r334__cards" aria-label="Six Research Desk source-custody comparisons">';
    foreach ($records as $r) {
        [$number,$title,$oldLabel,$document,$docType,$media,$mediaType,$status]=$r;
        $s.='<li data-fv-record="'.$number.'" data-fv-review="'.$status.'" data-fv-geo="none"><article aria-labelledby="'.$id.'-record-'.$number.'">';
        $s.='<p class="fv-r334__index">RECORD '.$number.' / 06 · '.fv_r334_escape($oldLabel).'</p><h3 id="'.$id.'-record-'.$number.'">'.fv_r334_escape($title).'</h3>';
        $s.='<p class="fv-r334__source-role"><strong>Finding / investigation source first</strong><span>'.fv_r334_escape($docType).'</span><a data-fv-source-kind="document" href="'.fv_r334_escape($document).'" rel="noopener noreferrer">Inspect the supporting NASA text</a></p>';
        $s.='<details><summary>Inspect the separate photograph record<span class="fv-r334__sr"> · '.fv_r334_escape($title).'</span></summary>';
        $s.='<div class="fv-r334__media"><p><strong>Context only:</strong> '.fv_r334_escape($mediaType).'. Its archive identifier alone does not establish this card’s investigative conclusion.</p>';
        $s.='<p><a data-fv-source-kind="contextual-media" href="'.fv_r334_escape($media).'" rel="noopener noreferrer">Inspect NASA image catalogue entry</a></p>';
        $s.='<p><strong>Media rights:</strong> Link only. Commercial image reuse, NASA endorsement, publicity and trademark permissions have not been established.</p></div></details>';
        if($status==='review') {
            $s.='<p class="fv-r334__flag">Review required: PR #158 presents the photograph link before its documentary support. Source order and the editorial label must be resolved by the Research Desk owner.</p>';
        }
        $s.='</article></li>';
    }
    $s.='</ol>';
    $s.='<footer class="fv-r334__end"><p><strong>Historical boundary:</strong> The 1967 Board identified an electrical arc as the most probable initiator; it did not conclusively establish a single ignition source. A later exhibition photograph cannot verify the 1967 hardware state by itself.</p>';
    $s.='<p><a data-fv-cta="apollo-free-investigation" href="'.fv_r334_escape(FV_R334_FREE).'">Read the free Apollo 1 investigation</a> · Editorial continuation only, not a signup or paid order.</p>';
    $s.='<p>No geographical pins, commercial product, checkout link, analytics beacon or image download is supplied by this review.</p></footer></section>';
    if (!$linked) {
        $linked=true;
        $src=function_exists('plugins_url') ? plugins_url('assets/fv-apollo-custody.css', __FILE__) : '';
        if ($src!=='') { return '<link rel="stylesheet" href="'.fv_r334_escape($src).'">'.$s; }
    }
    return $s;
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_custody_review','fv_r334_render'); }
