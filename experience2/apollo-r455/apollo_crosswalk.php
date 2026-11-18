<?php
/**
 * FV Apollo Experience 2.0 R455 — claim/source crosswalk. Staging-only, inert until manually installed.
 * No telemetry, WP mutations, images, outgoing posts, paid CTAs or speculative coordinates.
 */
declare(strict_types=1);

function fv455_records(): array {
    return [
        [
            'id'=>'preparation','kind'=>'context','date'=>'1966-10-18','date_role'=>'NASA catalogue image caption date',
            'published'=>'NASA gallery page: current publication date not established',
            'title'=>'Photographs show preparation, not ignition',
            'supported'=>'The NASA gallery identifies a crew-preparation photograph dated October 18, 1966, before the ground-test tragedy.',
            'limit'=>'The earlier photograph cannot identify a source of ignition on January 27, 1967.',
            'institution'=>'NASA / Apollo 1 gallery', 'url'=>'https://www.nasa.gov/gallery/apollo-1/',
            'custody'=>'External NASA photo catalogue only. No photograph is embedded or cleared for promotional reuse.'
        ],
        [
            'id'=>'review','kind'=>'investigation','date'=>'1967-01-27','date_role'=>'Accident date, NOT the Board report publication date',
            'published'=>'Review Board report: after the accident; publication date not asserted here',
            'title'=>'A probable arc is not a proven single spark',
            'supported'=>'The Apollo 204 Review Board determined an electrical arc was the most probable initiator and the pure-oxygen cabin conditions were extremely hazardous.',
            'limit'=>'The Board explicitly did not conclusively identify a single ignition source. The accident date must not be misread as the report date.',
            'institution'=>'NASA / Apollo 204 Review Board', 'url'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
            'custody'=>'Primary agency investigation in linked text. This component reproduces no report photographs, plates or diagrams.'
        ],
        [
            'id'=>'tribute','kind'=>'later','date'=>'2017-01-27','date_role'=>'NASA announcement and tribute opening date',
            'published'=>'NASA news release: 2017-01-27',
            'title'=>'The hatch on display is an exhibition object',
            'supported'=>'NASA announced that the 2017 Kennedy Space Center tribute featured the Apollo 1 spacecraft hatch.',
            'limit'=>'A 2017 museum display is not a firsthand record of ignition or a substitute for the 1967 investigation.',
            'institution'=>'NASA / 2017 Apollo 1 tribute news release', 'url'=>'https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/',
            'custody'=>'Official release linked; any exhibition imagery requires separate item-by-item media review.'
        ],
        [
            'id'=>'tests','kind'=>'later','date'=>'2018-02-14','date_role'=>'Retrospective publication date, NOT the dates of experiments',
            'published'=>'NASA retrospective: 2018-02-14',
            'title'=>'Post-accident tests investigated safer designs',
            'supported'=>'NASA described post-fire spacecraft flammability trials, including deliberate ignition testing of mockups in 1967–1968.',
            'limit'=>'Those later tests cannot establish the ignition source in the original January 1967 accident.',
            'institution'=>'NASA / 50 Years Ago: Apollo Flammability Tests', 'url'=>'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
            'custody'=>'Retrospective linked as informational reference; no NASA media copied or presented as licensed advertising material.'
        ],
    ];
}
function fv455_escape(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv455_fallback(): string {
    return '<p class="fv455-fallback">The Apollo evidence comparison is unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the original, free Apollo 1 investigation</a>.</p>';
}
function fv455_validate_records(array $records): bool {
    if (count($records)!==4) return false;
    $ids=[];
    foreach ($records as $record) {
        foreach (['id','kind','date','date_role','published','title','supported','limit','institution','url','custody'] as $key) {
            if (!isset($record[$key]) || !is_string($record[$key]) || trim($record[$key])==='') return false;
        }
        if (isset($ids[$record['id']]) || !in_array($record['kind'], ['context','investigation','later'], true)) return false;
        if (!preg_match('/^\d{4}-\d{2}-\d{2}$/D', $record['date'])) return false;
        $url = parse_url($record['url']);
        if (!is_array($url) || ($url['scheme']??'') !== 'https' || ($url['host']??'') !== 'www.nasa.gov' || isset($url['user']) || isset($url['pass']) || isset($url['query']) || isset($url['fragment']) || strpos($url['path']??'', '/') !== 0) return false;
        $ids[$record['id']]=true;
    }
    return true;
}
function fv455_assets(): ?array {
    $base=__DIR__.'/assets/';
    $files=[
        'css'=>['evidence-crosswalk.css','bb4e09f0ba13984d7a12e5a97f1782da62994914f84557da2eeb3ae76ab6498d'],
        'js'=>['evidence-crosswalk.js','7bbecf1eba8ea224e5ff402bb9a0b196418195a0103bc3a719b86511dcbfda54'],
    ];
    $data=[];
    foreach ($files as $kind=>[$name,$expected]) {
        $p=$base.$name;
        if (!is_file($p) || !is_readable($p) || !hash_equals($expected, hash_file('sha256',$p))) return null;
        $str=file_get_contents($p);
        if (!is_string($str) || $str==='') return null;
        $data[$kind]=$str;
    }
    return $data;
}
function fv455_render(): string {
    static $number=0;
    $records=fv455_records();$assets=fv455_assets();
    if (!fv455_validate_records($records) || $assets===null) return fv455_fallback();
    ++$number;$id='fv455-'.(string)$number;
    $html='<section class="fv455" id="'.$id.'" aria-labelledby="'.$id.'-heading" data-fv455-root>';
    $html.='<p class="fv455__kicker">Final Vestige / Apollo 1 / Evidence Atlas</p>';
    $html.='<h2 id="'.$id.'-heading">The evidence has limits. Show them.</h2>';
    $html.='<p class="fv455__lead">Four dated records, four different evidentiary roles. Browse the claim, the original source, the uncertainty and the media-use boundary together.</p>';
    $html.='<p class="fv455__notice"><strong>Source custody:</strong> NASA links verified as agency sources. This is an independent Final Vestige research exercise, not NASA endorsement. Historical editorial, photo rights and commercial approval remain separate reviews.</p>';
    $html.='<h3 id="'.$id.'-rail">Chronology and claim crosswalk</h3>';
    $html.='<div class="fv455__tools" role="group" aria-label="Filter evidence by role">';
    foreach (['all'=>'All four','context'=>'Context','investigation'=>'Review Board','later'=>'Later accounts'] as $kind=>$label) {
        $html.='<button type="button" data-fv455-filter="'.fv455_escape($kind).'" aria-pressed="'.($kind==='all'?'true':'false').'">'.fv455_escape($label).'</button>';
    }
    $html.='</div><p class="fv455__status" data-fv455-status role="status" aria-live="polite">Four source records available. Filters require JavaScript; all records remain accessible without it.</p>';
    $html.='<ol class="fv455__rail" aria-labelledby="'.$id.'-rail">';
    foreach ($records as $index=>$r) {
        $html.='<li class="fv455__plate" data-fv455-kind="'.fv455_escape($r['kind']).'">';
        $html.='<p class="fv455__index">Record '.(string)($index+1).' of 4 / '.fv455_escape($r['kind']).'</p>';
        $html.='<p class="fv455__date"><time datetime="'.fv455_escape($r['date']).'">'.fv455_escape($r['date']).'</time></p>';
        $html.='<p class="fv455__small">'.fv455_escape($r['date_role']).'</p>';
        $html.='<h4>'.fv455_escape($r['title']).'</h4>';
        $html.='<p data-fv455-supported><span class="fv455__field">The source supports:</span> '.fv455_escape($r['supported']).'</p>';
        $html.='<p data-fv455-limit><span class="fv455__field">It does not establish:</span> '.fv455_escape($r['limit']).'</p>';
        $html.='<details><summary>Inspect citation, publication date and rights custody</summary>';
        $html.='<p><span class="fv455__field">Source date:</span> '.fv455_escape($r['published']).'</p>';
        $html.='<p><span class="fv455__field">Archive/media status:</span> '.fv455_escape($r['custody']).'</p>';
        $html.='<p><a href="'.fv455_escape($r['url']).'" rel="noopener noreferrer">'.fv455_escape($r['institution']).' — source record</a></p>';
        $html.='</details></li>';
    }
    $html.='</ol>';
    $html.='<aside class="fv455__activity" aria-labelledby="'.$id.'-classroom"><h3 id="'.$id.'-classroom">Source-check challenge</h3>';
    $html.='<p>A video states: “NASA identified exactly which wire ignited the Apollo 1 fire.” Does the Review Board support that statement? Compare the probable initiator with the evidence limit.</p>';
    $html.='<details><summary>Reveal the evidence-based answer and educator rubric</summary><p><strong>No.</strong> The Review Board identified an electrical arc as the most probable initiator but explicitly did not conclusively identify a single ignition source. A sound response cites the Review Board and separates probability from certainty. Later museum displays or fire tests do not close that uncertainty.</p></details>';
    $html.='<p class="fv455__small">Original classroom exercise. No student information, signup or purchase is collected.</p></aside>';
    $html.='<div class="fv455__export"><button type="button" data-fv455-export>Download text-only source study note</button><p class="fv455__small">Local text export only. No server submission.</p></div>';
    $html.='<div class="fv455__cta"><p>Continue to the underlying narrative after inspecting the evidence.</p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the complete free Apollo 1 investigation</a></div>';
    $html.='<p class="fv455__small">Curated evidence collection; no geographical map pins or relationship edges are asserted. No NASA photography or logos used.</p></section>';
    $html.='<style>'.$assets['css'].'</style><script>'.$assets['js'].'</script>';
    return $html;
}
/** Require explicit host approval and staging page identity; never automatically register in production. */
if (function_exists('add_action')) {
    add_action('init',static function(): void {
        if (!defined('FV_R455_ENABLE_STAGING') || FV_R455_ENABLE_STAGING !== true ||
            !defined('FV_R455_STAGING_PAGE_ID') || !is_int(FV_R455_STAGING_PAGE_ID) || FV_R455_STAGING_PAGE_ID<1 ||
            !function_exists('wp_get_environment_type') || wp_get_environment_type()!=='staging' ||
            !function_exists('add_shortcode')) return;
        add_shortcode('fv_apollo_crosswalk_r455', static function(): string {
            if (!function_exists('get_queried_object_id') || get_queried_object_id()!==FV_R455_STAGING_PAGE_ID) return '';
            return fv455_render();
        });
    });
}
