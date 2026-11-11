<?php
/**
 * Plugin Name: FV Apollo Evidence Experience — R281 (STAGING ONLY)
 * Description: Read-only, NASA-linked Apollo EvidencePlate/SourceDrawer/ChronologyRail pilot. Not for production activation.
 * Version: 0.0.1-staging
 * License: GPL-2.0-or-later
 */
if (!defined('ABSPATH')) { return; }

const FV_R281_NASA_MISSION = 'https://www.nasa.gov/mission/apollo-1/';
const FV_R281_NASA_SAFETY = 'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1';
const FV_R281_NASA_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R281_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R281_STYLE = 'fv-apollo-evidence-r281';
// Review-custody digest is pinned after independent historical copy approval. This
// protects against accidental data drift, not a malicious PHP release editor.
const FV_R282_REVIEWED_EVENTS_SHA256 = '268605391a741300d13e487968336040bfe016dd3d6e2165182a5269ecb19d4d';

/** Immutable, curated chronology. All dates/claims have named official NASA sources. */
function fv_r281_events(): array {
    return [
        ['date'=>'1967-01-27','when'=>'January 27, 1967', 'title'=>'The pad test and fire',
         'statement'=>'During a preflight test for AS-204, a fire swept through the Apollo command module. Virgil Grissom, Edward White and Roger Chaffee died.',
         'boundary'=>'This dated record establishes the accident and crew. It does not identify the precise ignition point.',
         'source_id'=>'nasa_mission', 'source_name'=>'NASA Apollo 1 mission history', 'source_url'=>FV_R281_NASA_MISSION,
         'source_type'=>'Later institutional mission summary', 'source_dependency'=>'A NASA retrospective, not a separate firsthand witness record.'],
        ['date'=>'1967-01-28','when'=>'January 28, 1967', 'title'=>'An investigation begins',
         'statement'=>'NASA established the Apollo 204 Review Board to investigate the accident. The board met and visited the scene on January 28.',
         'boundary'=>'Establishment of an inquiry is not proof that any specific ignition source was confirmed.',
         'source_id'=>'nasa_safety', 'source_name'=>'NASA Safety and Mission Assurance account', 'source_url'=>FV_R281_NASA_SAFETY,
         'source_type'=>'Later institutional safety summary', 'source_dependency'=>'A NASA account of the same investigation, not independent corroboration.'],
        ['date'=>'1967-04','when'=>'April 1967', 'title'=>'The Review Board reports',
         'statement'=>'The review findings identified an electrical arc as the most probable fire initiator, without conclusively identifying the precise ignition source.',
         'boundary'=>'Most probable is not an exact-source finding. The published Board report is primary evidence; later NASA summaries are not an independent eyewitness confirmation.',
         'source_id'=>'nasa_board', 'source_name'=>'NASA Apollo 204 Review Board report', 'source_url'=>FV_R281_NASA_BOARD,
         'source_type'=>'1967 investigative primary report', 'source_dependency'=>'A contemporary institutional investigation, not a conclusive ignition-site identification.'],
    ];
}
function fv_r281_escape(string $text): string {
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
/** Pin official link destinations to an explicit allowlist; fail closed on changed records. */
function fv_r281_valid_records(array $records): bool {
    $allow=['nasa_mission'=>FV_R281_NASA_MISSION,'nasa_safety'=>FV_R281_NASA_SAFETY,'nasa_board'=>FV_R281_NASA_BOARD];
    $seen=[];
    foreach ($records as $record) {
        if (!isset($record['date'],$record['when'],$record['title'],$record['statement'],$record['boundary'],$record['source_id'],$record['source_name'],$record['source_url'],$record['source_type'],$record['source_dependency'])) { return false; }
        if (!isset($allow[$record['source_id']]) || $allow[$record['source_id']] !== $record['source_url']) { return false; }
        if (isset($seen[$record['date']]) || !preg_match('/^1967-(?:01-27|01-28|04)$/D', $record['date'])) { return false; }
        foreach (['when','title','statement','boundary','source_name','source_type','source_dependency'] as $field) {
            if (!is_string($record[$field]) || trim($record[$field]) === '') { return false; }
        }
        $seen[$record['date']]=true;
    }
    if (count($records)!==3 || count($seen)!==3 || array_keys($seen)!==['1967-01-27','1967-01-28','1967-04']) { return false; }
    // This digest covers *all* historical wording and NASA source metadata,
    // not merely date/URL allowlists. Changes require a new reviewed receipt.
    $encoded=json_encode(array_values($records), JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
    return is_string($encoded) && hash_equals(FV_R282_REVIEWED_EVENTS_SHA256, hash('sha256',$encoded));
}
function fv_r281_stylesheet_url(): string {
    return plugins_url('assets/apollo-source-experience.css', __FILE__);
}
/** Enqueue only for explicit shortcode on the singular post, and preserve a body fallback for dynamic blocks. */
function fv_r281_preflight(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')) { return; }
    $post = get_post();
    if ($post && isset($post->post_content) && function_exists('has_shortcode') &&
        has_shortcode((string)$post->post_content, 'fv_apollo_source_experience')) {
        wp_enqueue_style(FV_R281_STYLE, fv_r281_stylesheet_url(), [], 'r281');
    }
}
/** No user content or parameters alter evidence; ids are unique when a shortcode repeats. */
function fv_r281_render($attributes = []): string {
    $records=fv_r281_events();
    if (!fv_r281_valid_records($records)) {
        return '<aside aria-label="Apollo source fallback"><p>Evidence experience unavailable.</p><a href="'.FV_R281_NASA_BOARD.'">Read the NASA Review Board report</a> · <a href="'.FV_R281_FREE.'">Read the free Apollo investigation</a></aside>';
    }
    static $sequence=0, $linked=false;
    $sequence++;
    $id='fv-r281-'.$sequence;
    $s='<section class="fv-r281" aria-labelledby="'.$id.'-heading" data-fv-evidence-status="editorial-review-pending">';
    $s.='<header class="fv-r281__head"><p class="fv-r281__eyebrow">Final Vestige / Evidence Atlas / Apollo 1</p><h2 id="'.$id.'-heading">What the record establishes</h2>';
    $s.='<p>Three documented milestones. Open the source for each claim; note the limits of the evidence. Editorial review remains pending.</p></header>';
    $s.='<nav class="fv-r281__rail" aria-label="Apollo chronology"><ol>';
    foreach ($records as $index=>$r) {
        $point=$id.'-event-'.($index+1);
        $s.='<li><a href="#'.$point.'"><span class="fv-r281__rail-date">'.fv_r281_escape($r['when']).'</span><span>'.fv_r281_escape($r['title']).'</span></a></li>';
    }
    $s.='</ol></nav><ol class="fv-r281__plates" aria-label="Historical evidence plates">';
    foreach ($records as $index=>$r) {
        $point=$id.'-event-'.($index+1);
        $s.='<li class="fv-r281__plate" id="'.$point.'" tabindex="-1"><article aria-labelledby="'.$point.'-heading"><p class="fv-r281__date"><time datetime="'.fv_r281_escape($r['date']).'">'.fv_r281_escape($r['when']).'</time></p>';
        $s.='<h3 id="'.$point.'-heading">'.fv_r281_escape($r['title']).'</h3><p>'.fv_r281_escape($r['statement']).'</p>';
        $s.='<p class="fv-r281__boundary"><strong>Evidence boundary:</strong> '.fv_r281_escape($r['boundary']).'</p>';
        // Native claim-to-catalogue cross-reference; accessible with JS disabled.
        $source_point=$id.'-source-'.($index+1);
        $s.='<p class="fv-r281__source-jump"><a href="#'.$source_point.'">Locate the '.fv_r281_escape($r['source_type']).' in the source catalogue</a></p>';
        $s.='<details class="fv-r281__drawer"><summary>Inspect the source and custody record</summary><div class="fv-r281__drawer-body"><p><strong>Custodian:</strong> NASA · <strong>Record:</strong> '.fv_r281_escape($r['source_id']).' · <strong>Editorial review:</strong> Pending</p><p><strong>Record type:</strong> '.fv_r281_escape($r['source_type']).'. <strong>Source relationship:</strong> '.fv_r281_escape($r['source_dependency']).'</p>';
        $s.='<p><a href="'.fv_r281_escape($r['source_url']).'" rel="noopener noreferrer">Open '.fv_r281_escape($r['source_name']).' (NASA)</a></p>';
        $s.='<p>This is an official-source link, not a claim of NASA endorsement or clearance for promotional use of agency marks, astronaut likenesses, or media.</p></div></details>';
        $s.='</article></li>';
    }
    $s.='</ol><aside class="fv-r281__gallery" aria-label="Source gallery"><h3>Inspect the document sources</h3><p>This is a text-only catalogue of three NASA records, not a photographic gallery or three independent eyewitness accounts. Review remains pending.</p><ul class="fv-r281__source-list">';
    foreach ($records as $index=>$r) {
        // Every catalogue record has a stable target within this component instance.
        $source_point=$id.'-source-'.($index+1);
        $event_point=$id.'-event-'.($index+1);
        $s.='<li id="'.$source_point.'" tabindex="-1"><p class="fv-r281__source-type">'.fv_r281_escape($r['source_type']).'</p>';
        $s.='<a href="'.fv_r281_escape($r['source_url']).'" rel="noopener noreferrer">Inspect '.fv_r281_escape($r['source_name']).' (NASA)</a>';
        $s.='<p>'.fv_r281_escape($r['source_dependency']).'</p>';
        $s.='<p class="fv-r281__source-return"><a href="#'.$event_point.'">Return to evidence: '.fv_r281_escape($r['title']).'</a></p></li>';
    }
    $s.='</ul><p>No archive image, geolocation, ownership or commercial rights are inferred from these source links. NASA does not endorse this website.</p></aside>';
    $s.='<footer class="fv-r281__next"><p>Continue with the investigation, including the original evidence and its uncertainties.</p><p><a href="'.FV_R281_FREE.'">Read the free Apollo 1 investigation</a></p></footer></section>';
    // Body-placed stylesheet is a progressive fallback where an unknown dynamic
    // shortcode executes after wp_head. Never inject JS or remote analytics.
    if (!$linked && (!function_exists('wp_style_is') || !wp_style_is(FV_R281_STYLE, 'done'))) {
        $linked=true;
        return '<link rel="stylesheet" href="'.fv_r281_escape(fv_r281_stylesheet_url()).'">'.$s;
    }
    return $s;
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_r281_preflight',20); }
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_source_experience','fv_r281_render'); }
