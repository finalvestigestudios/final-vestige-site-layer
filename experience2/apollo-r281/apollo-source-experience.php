<?php
/**
 * Plugin Name: FV Apollo Evidence Experience — R281 (STAGING ONLY)
 * Description: Read-only, NASA-linked Apollo EvidencePlate/SourceDrawer/ChronologyRail pilot. Not for production activation.
 * Version: 0.0.1-staging
 * License: GPL-2.0-or-later
 */
if (!defined('ABSPATH')) { return; }

const FV_R281_NASA_MISSION = 'https://www.nasa.gov/mission/apollo-1/';
const FV_R287_NASA_PROCEEDINGS = 'https://www.nasa.gov/history/Apollo204/proceed.html';
const FV_R281_NASA_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R281_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R281_STYLE = 'fv-apollo-evidence-r281';
// R294: stylesheet version is tied to reviewed CSS bytes (sha256 prefix). Keep
// WordPress's enqueued link and the no-preflight body fallback cache-consistent.
const FV_R294_STYLE_VERSION = 'r296-41ab84cba066';
// Staging-only digest of corrected chronology, pending independent historical editorial
// approval. It detects accidental data drift; it does not certify publication.
const FV_R287_STAGING_EVENTS_SHA256 = '2a473986ed2e9c8ca98d19fb5ce0d32fea62d060d9dadcd2fa4613167eba36ef';


// R288: discrepancy custody. NASA's original Review Board narrative says that
// authority was initiated orally on Jan 27, while a later NASA safety summary
// dates establishment Jan 28. This is a source-attribution distinction, NOT
// permission to declare that either record is independently corroborated.
const FV_R288_BOARD_NARRATIVE = 'https://www.nasa.gov/history/Apollo204/narr.html';
const FV_R288_NASA_SAFETY = 'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1';
// R295: NASA's archived Board memorandum is a related primary source. Its webpage
// title names January 27, but the transcribed memorandum body has no visible date.
const FV_R295_NASA_MEMORANDUM = 'https://www.nasa.gov/history/Apollo204/15.html';
const FV_R288_RECONCILIATION_SHA256 = 'a7ccd1ead52d5b036540e083dcaa2dd6774f43a6f88c90a6c7492914c69121a7';

function fv_r288_source_reconciliation(): array {
    return [
        ['authority'=>'Original Apollo 204 Review Board narrative',
         'statement'=>'The Board narrative records establishment on January 27, 1967, initiated through oral instructions, and separately dates the first Kennedy meeting January 28.',
         'boundary'=>'A retrospective published with the original investigation; it describes the Board\'s own formation, not an independent account.',
         'url'=>FV_R288_BOARD_NARRATIVE],
        ['authority'=>'Later NASA Safety and Mission Assurance summary',
         'statement'=>'NASA\'s later safety summary dates the Deputy Administrator\'s establishment of the Board to January 28, 1967.',
         'boundary'=>'A later institutional summary, not independent evidence that supersedes the 1967 Board narrative.',
         'url'=>FV_R288_NASA_SAFETY],
        ['authority'=>'NASA archive: memorandum for the Apollo 204 Review Board',
         'statement'=>'NASA\'s archival page is titled Memorandum - January 27, 1967, and transcribes instructions to establish and appoint the Review Board.',
         'boundary'=>'The transcribed memorandum body does not display a separate signed date. The archival title is not independent confirmation of when oral instructions were issued or when the Board first convened.',
         'url'=>FV_R295_NASA_MEMORANDUM],
    ];
}
function fv_r288_reconciliation_valid(array $items): bool {
    if (count($items) !== 3 || array_keys($items) !== [0,1,2]) { return false; }
    if (($items[0]['url'] ?? null) !== FV_R288_BOARD_NARRATIVE || ($items[1]['url'] ?? null) !== FV_R288_NASA_SAFETY || ($items[2]['url'] ?? null) !== FV_R295_NASA_MEMORANDUM) { return false; }
    foreach ($items as $item) {
        if (array_keys($item) !== ['authority','statement','boundary','url']) { return false; }
        foreach (['authority','statement','boundary'] as $key) {
            if (!is_string($item[$key]) || trim($item[$key]) === '') { return false; }
        }
    }
    $encoded=json_encode($items, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
    return is_string($encoded) && hash_equals(FV_R288_RECONCILIATION_SHA256, hash('sha256', $encoded));
}


// R289: more exact document custody, not new independent witness evidence.
// The Board's own proceedings mention a January 28 memorandum being received
// January 31. Its narrative also cites February 3 written confirmation.
// Dates refer to distinct DOCUMENTARY ACTIONS, not a silently chosen "formation".
const FV_R289_AUTHORITY_LEDGER_SHA256 = '29ecbb11dd75eea3aa7a584c53036b0496e05cf351a35a197b3e4f759d094558';
function fv_r289_authority_ledger(): array {
    return [
        ['date'=>'1967-01-27','label'=>'January 27 · oral authority',
         'finding'=>'The Board narrative dates its establishment to January 27, initiated by the Deputy Administrator through oral instructions.',
         'boundary'=>'This is the Board\'s account of its authority, not an independently witnessed appointment.',
         'source'=>'Original Review Board narrative', 'url'=>FV_R288_BOARD_NARRATIVE],
        ['date'=>'1967-01-28','label'=>'January 28 · board convenes',
         'finding'=>'The Board assembled and met at Kennedy Space Center, then inspected Launch Complex 34.',
         'boundary'=>'A first meeting and site visit do not by themselves settle the date a board was authorized.',
         'source'=>'1967 Review Board proceedings', 'url'=>FV_R287_NASA_PROCEEDINGS],
        ['date'=>'1967-01-31','label'=>'January 31 · dated memorandum received',
         'finding'=>'The proceedings record that the chairman received and distributed a memorandum dated January 28 that established the Review Board.',
         'boundary'=>'The memorandum\'s date and the date it was received are different; this is the Board\'s own proceedings.',
         'source'=>'1967 Review Board proceedings', 'url'=>FV_R287_NASA_PROCEEDINGS],
        ['date'=>'1967-02-03','label'=>'February 3 · written confirmation',
         'finding'=>'The Board narrative describes written confirmation of its authority on February 3.',
         'boundary'=>'Later written confirmation is not evidence that the Board did not operate before February 3.',
         'source'=>'Original Review Board narrative', 'url'=>FV_R288_BOARD_NARRATIVE],
    ];
}
function fv_r289_authority_ledger_valid(array $items): bool {
    if (count($items)!==4 || array_keys($items)!==[0,1,2,3]) { return false; }
    $dates=['1967-01-27','1967-01-28','1967-01-31','1967-02-03'];
    $links=[FV_R288_BOARD_NARRATIVE,FV_R287_NASA_PROCEEDINGS,FV_R287_NASA_PROCEEDINGS,FV_R288_BOARD_NARRATIVE];
    foreach ($items as $i=>$item) {
        if (array_keys($item)!==['date','label','finding','boundary','source','url'] ||
            $item['date']!==$dates[$i] || $item['url']!==$links[$i]) { return false; }
        foreach (['label','finding','boundary','source'] as $key) {
            if (!is_string($item[$key]) || trim($item[$key])==='') { return false; }
        }
    }
    $encoded=json_encode($items,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
    return is_string($encoded) && hash_equals(FV_R289_AUTHORITY_LEDGER_SHA256,hash('sha256',$encoded));
}

/** Immutable, curated chronology. All dates/claims have named official NASA sources. */
function fv_r281_events(): array {
    return [
        ['date'=>'1967-01-27','when'=>'January 27, 1967', 'title'=>'The pad test and fire',
         'statement'=>'During a preflight test for AS-204, a fire swept through the Apollo command module. Virgil Grissom, Edward White and Roger Chaffee died.',
         'boundary'=>'This dated record establishes the accident and crew. It does not identify the precise ignition point.',
         'source_id'=>'nasa_mission', 'source_name'=>'NASA Apollo 1 mission history', 'source_url'=>FV_R281_NASA_MISSION,
         'source_type'=>'Later institutional mission summary', 'source_dependency'=>'A NASA retrospective, not a separate firsthand witness record.'],
        ['date'=>'1967-01-28','when'=>'January 28, 1967', 'title'=>'The Board convenes at Kennedy',
         'statement'=>'The Apollo 204 Review Board convened at Kennedy Space Center on January 28, 1967, then visited Launch Complex 34 after its initial general session.',
         'boundary'=>'This is the date of the Board meeting and site visit, not its establishment. The Board\'s own narrative dates oral authority to January 27, while a later NASA safety summary uses January 28 for establishment. Neither establishes an ignition source.',
         'source_id'=>'nasa_proceedings', 'source_name'=>'NASA Apollo 204 Review Board proceedings', 'source_url'=>FV_R287_NASA_PROCEEDINGS,
         'source_type'=>'1967 investigative primary proceedings', 'source_dependency'=>'The Board proceedings are part of its own investigation, not an independent eyewitness account.'],
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
    $allow=['nasa_mission'=>FV_R281_NASA_MISSION,'nasa_proceedings'=>FV_R287_NASA_PROCEEDINGS,'nasa_board'=>FV_R281_NASA_BOARD];
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
    return is_string($encoded) && hash_equals(FV_R287_STAGING_EVENTS_SHA256, hash('sha256',$encoded));
}
function fv_r281_stylesheet_url(): string {
    return plugins_url('assets/apollo-source-experience.css', __FILE__);
}
/** Matching cache key when shortcode renders after wp_head (no queued style). */
function fv_r294_fallback_stylesheet_url(): string {
    $base = fv_r281_stylesheet_url();
    $separator = strpos($base, '?') === false ? '?' : '&';
    return $base . $separator . 'ver=' . rawurlencode(FV_R294_STYLE_VERSION);
}
/**
 * Read-only, bounded discovery of shortcode placement in a singular post, including
 * published synced patterns (core/block). Never render or execute block content
 * during wp_head preflight. Rejected / unavailable blocks fall back to the
 * already-existing body link. This is NOT a general-purpose block resolver.
 */
function fv_r285_content_has_shortcode(string $content, array &$visited = [], int $depth = 0, ?array &$budget = null): bool {
    // Shared across ALL synced-block branches: per-node limits alone permit
    // expensive fan-out (or many near-250KB wp_block payloads) in wp_head.
    if ($budget === null) { $budget = ['nodes'=>0, 'reads'=>0, 'bytes'=>0, 'exhausted'=>false]; }
    if ($budget['exhausted'] || $depth > 8) { return false; }
    $size = strlen($content);
    if ($size > 250000 || $budget['bytes'] + $size > 500000) {
        $budget['exhausted'] = true;
        return false;
    }
    $budget['bytes'] += $size;
    if (function_exists('has_shortcode') && has_shortcode($content, 'fv_apollo_source_experience')) {
        return true;
    }
    if (!function_exists('parse_blocks') || strpos($content, '<!-- wp:') === false) { return false; }
    $blocks = parse_blocks($content);
    if (!is_array($blocks)) { return false; }
    return fv_r285_blocks_have_shortcode($blocks, $visited, $depth, $budget);
}
function fv_r285_blocks_have_shortcode(array $blocks, array &$visited, int $depth, ?array &$budget = null): bool {
    if ($budget === null) { $budget = ['nodes'=>0, 'reads'=>0, 'bytes'=>0, 'exhausted'=>false]; }
    if ($budget['exhausted'] || $depth > 8) { return false; }
    $count = 0;
    foreach ($blocks as $block) {
        if (++$count > 128 || ++$budget['nodes'] > 256 || !is_array($block)) {
            $budget['exhausted'] = true;
            return false;
        }
        if (($block['blockName'] ?? null) === 'core/block' && function_exists('get_post')) {
            $ref = $block['attrs']['ref'] ?? null;
            if (is_int($ref) || (is_string($ref) && ctype_digit($ref) && strlen($ref) < 18)) {
                $id=(int)$ref;
                if ($id > 0 && !isset($visited[$id]) && count($visited) < 128) {
                    // Limit database queries across all branches, not per level.
                    if (++$budget['reads'] > 32) { $budget['exhausted'] = true; return false; }
                    $visited[$id]=true; // prevent cycles and repeated database fetches
                    $post=get_post($id);
                    if (is_object($post) && ($post->post_type ?? null) === 'wp_block' &&
                        ($post->post_status ?? null) === 'publish' && is_string($post->post_content ?? null) &&
                        fv_r285_content_has_shortcode($post->post_content, $visited, $depth + 1, $budget)) {
                        return true;
                    }
                    if ($budget['exhausted']) { return false; }
                }
            }
        }
        if (!empty($block['innerBlocks']) && is_array($block['innerBlocks']) &&
            fv_r285_blocks_have_shortcode($block['innerBlocks'], $visited, $depth + 1, $budget)) { return true; }
        if ($budget['exhausted']) { return false; }
        // Relevant for noncanonical/editor-exported innerHTML fixtures.
        if (is_string($block['innerHTML'] ?? null) && function_exists('has_shortcode') &&
            has_shortcode($block['innerHTML'], 'fv_apollo_source_experience')) { return true; }
    }
    return false;
}
/** Enqueue a confirmed public shortcode before wp_head, without unrelated pages. */
function fv_r281_preflight(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')) { return; }
    $post = get_post();
    if ($post && is_string($post->post_content ?? null)) {
        $visited=[];
        if (fv_r285_content_has_shortcode($post->post_content, $visited)) {
            wp_enqueue_style(FV_R281_STYLE, fv_r281_stylesheet_url(), [], FV_R294_STYLE_VERSION);
        }
    }
}
/** No user content or parameters alter evidence; ids are unique when a shortcode repeats. */
function fv_r281_render($attributes = []): string {
    $records=fv_r281_events();
    $date_reconciliation=fv_r288_source_reconciliation();
    $authority_ledger=fv_r289_authority_ledger();
    if (!fv_r281_valid_records($records) || !fv_r288_reconciliation_valid($date_reconciliation) || !fv_r289_authority_ledger_valid($authority_ledger)) {
        return '<aside aria-label="Apollo source fallback"><p>Evidence experience unavailable.</p><a href="'.FV_R281_NASA_BOARD.'">Read the NASA Review Board report</a> · <a href="'.FV_R281_FREE.'">Read the free Apollo investigation</a></aside>';
    }
    static $sequence=0, $linked=false;
    $sequence++;
    $id='fv-r281-'.$sequence;
    // R297: WordPress can render the shortcode more than once. Each
    // chronology and source landmark needs a distinguishable name in AT.
    $landmark_instance=' — atlas instance '.$sequence;
    $s='<section class="fv-r281" aria-labelledby="'.$id.'-heading" data-fv-evidence-status="editorial-review-pending">';
    $s.='<header class="fv-r281__head"><p class="fv-r281__eyebrow">Final Vestige / Evidence Atlas / Apollo 1</p><h2 id="'.$id.'-heading">What the record establishes</h2>';
    $s.='<p>Three documented milestones. Open the source for each claim; note the limits of the evidence. Editorial review remains pending.</p>';
    // R292: an early direct source-catalogue route for visitors arriving from research-led films.
    // Targets the existing focusable first catalogue record; no extra tab stops, JS,
    // outbound commercial link, new source URL, or second investigation CTA.
    $s.='<p class="fv-r292__source-route"><a href="#'.$id.'-source-1">Skip to the NASA source catalogue (first record)</a></p></header>';
    $s.='<nav class="fv-r281__rail" aria-label="Apollo 1 chronology'.$landmark_instance.'"><ol>';
    foreach ($records as $index=>$r) {
        $point=$id.'-event-'.($index+1);
        $s.='<li><a href="#'.$point.'"><span class="fv-r281__rail-date">'.fv_r281_escape($r['when']).'</span><span>'.fv_r281_escape($r['title']).'</span></a></li>';
    }
    $s.='</ol></nav><ol class="fv-r281__plates" aria-label="Apollo 1 evidence plates'.$landmark_instance.'">';
    foreach ($records as $index=>$r) {
        $point=$id.'-event-'.($index+1);
        $s.='<li class="fv-r281__plate" id="'.$point.'" tabindex="-1"><article aria-labelledby="'.$point.'-heading"><p class="fv-r281__date"><time datetime="'.fv_r281_escape($r['date']).'">'.fv_r281_escape($r['when']).'</time></p>';
        $s.='<h3 id="'.$point.'-heading">'.fv_r281_escape($r['title']).'</h3><p>'.fv_r281_escape($r['statement']).'</p>';
        $s.='<p class="fv-r281__boundary"><strong>Evidence boundary:</strong> '.fv_r281_escape($r['boundary']).'</p>';
        // Native claim-to-catalogue cross-reference; accessible with JS disabled.
        $source_point=$id.'-source-'.($index+1);
        $s.='<p class="fv-r281__source-jump"><a href="#'.$source_point.'">Locate the '.fv_r281_escape($r['source_type']).' in the source catalogue</a></p>';
        // R290: the Jan 28 Board claim has its own four-act custody chain.
        // Direct native fragment movement is available without JS or a map.
        if ($index === 1) {
            $s.='<p class="fv-r281__authority-jump"><a href="#'.$id.'-authority-1">Examine the four dated Board authority records</a></p>';
        }
        $s.='<details class="fv-r281__drawer"><summary>Inspect the source and custody record</summary><div class="fv-r281__drawer-body"><p><strong>Custodian:</strong> NASA · <strong>Record:</strong> '.fv_r281_escape($r['source_id']).' · <strong>Editorial review:</strong> Pending</p><p><strong>Record type:</strong> '.fv_r281_escape($r['source_type']).'. <strong>Source relationship:</strong> '.fv_r281_escape($r['source_dependency']).'</p>';
        $s.='<p><a href="'.fv_r281_escape($r['source_url']).'" rel="noopener noreferrer">Open '.fv_r281_escape($r['source_name']).' (NASA)</a></p>';
        $s.='<p>This is an official-source link, not a claim of NASA endorsement or clearance for promotional use of agency marks, astronaut likenesses, or media.</p></div></details>';
        $s.='</article></li>';
    }
    // Do not silently flatten discrepant NASA dates into one unsupported claim.
    // Plain text is available without JS and in print; all source anchors are
    // direct official NASA destinations, with clear source-dependency labels.
    $s.='</ol><aside class="fv-r281__reconciliation" aria-label="NASA source-date reconciliation'.$landmark_instance.'" data-fv-date-review="editorial-review-pending"><h3>Why NASA sources give different establishment dates</h3>';
    $s.='<p><strong>Unresolved source distinction:</strong> The Apollo 204 Review Board narrative dates its original oral authorization to January 27, 1967. A later NASA safety summary describes the Board as established on January 28. Both place its first Kennedy meeting on January 28. We preserve that distinction instead of calling two institutional descriptions independent corroboration.</p>';
    $s.='<h4>Document custody: four different dated actions</h4><p>These dates describe the Board\'s authority, meeting, memorandum and later confirmation. Its own 1967 narrative and proceedings are parts of the same investigation, not independent eyewitness corroboration.</p>';
    $s.='<details class="fv-r291__authority-disclosure"><summary>Inspect all four dated Board authority records</summary><p class="fv-r291__disclosure-intro">Each entry identifies what the Board documented and what that record does not establish. Source links lead to NASA, not a commercial offer.</p><ol class="fv-r281__authority-ledger" aria-label="Board authority document chronology'.$landmark_instance.'">';
    foreach ($authority_ledger as $index=>$entry) {
        $authority_point=$id.'-authority-'.($index+1);
        $s.='<li id="'.$authority_point.'" tabindex="-1"><p class="fv-r281__authority-date"><time datetime="'.fv_r281_escape($entry['date']).'">'.fv_r281_escape($entry['label']).'</time></p>';
        $s.='<p>'.fv_r281_escape($entry['finding']).'</p><p class="fv-r281__authority-boundary"><strong>Limit:</strong> '.fv_r281_escape($entry['boundary']).'</p>';
        $s.='<p><a href="'.fv_r281_escape($entry['url']).'" rel="noopener noreferrer">Inspect '.fv_r281_escape($entry['source']).' at NASA</a></p>';
        $s.='<p class="fv-r281__authority-return"><a href="#'.$id.'-event-2">Return to January 28 evidence</a></p></li>';
    }
    // R296: on mobile, keep the disagreement and editorial boundary visible,
    // but make the three longer related NASA-source accounts opt-in. Native
    // details is keyboard/touch/no-JS capable; print exposes the full custody
    // record; source URLs are unchanged and never rewritten as commercial links.
    $s.='</ol></details><details class="fv-r296__date-disclosure"><summary>Compare all three NASA source descriptions</summary><p class="fv-r296__date-guide">Three related NASA institutional records, not three independent witnesses. Each source states a date or documents an action, with its limits shown below.</p><ul class="fv-r281__reconciliation-list">';
    foreach ($date_reconciliation as $source) {
        $s.='<li><strong>'.fv_r281_escape($source['authority']).'</strong><p>'.fv_r281_escape($source['statement']).'</p>';
        $s.='<p class="fv-r281__reconciliation-boundary">Source boundary: '.fv_r281_escape($source['boundary']).'</p>';
        $s.='<p><a href="'.fv_r281_escape($source['url']).'" rel="noopener noreferrer">Read source at NASA</a></p></li>';
    }
    $s.='</ul></details><p>Original investigation and later NASA summaries are different records. Editorial reconciliation remains pending.</p></aside>';
    $s.='<aside class="fv-r281__gallery" aria-label="Apollo source catalogue'.$landmark_instance.'"><h3>Inspect the document sources</h3><p>This is a text-only catalogue of three NASA records, not a photographic gallery or three independent eyewitness accounts. Review remains pending.</p><ul class="fv-r281__source-list">';
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
    // R293: never emit a second stylesheet link when WordPress has already queued
    // the Apollo stylesheet but has not yet printed it. Keep the body fallback
    // only for genuinely unqueued dynamic shortcodes (including no-JS).
    if (!$linked && (!function_exists('wp_style_is') ||
        (!wp_style_is(FV_R281_STYLE, 'done') && !wp_style_is(FV_R281_STYLE, 'enqueued')))) {
        $linked=true;
        return '<link rel="stylesheet" href="'.fv_r281_escape(fv_r294_fallback_stylesheet_url()).'">'.$s;
    }
    return $s;
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_r281_preflight',20); }
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_source_experience','fv_r281_render'); }
