<?php
/** FV Apollo Experience 2.0 R454: isolated staging-only evidence triage. No writes, paid links, external JS or images. */
declare(strict_types=1);

function fv454_sources(): array {
    return [
        ['id'=>'preparation','group'=>'primary','date'=>'1966-10-18','date_type'=>'NASA catalogue caption date',
         'title'=>'Preparation, not a fire record',
         'proof'=>'NASA catalogues the crew\'s altitude-chamber preparation before the January ground test.',
         'limit'=>'A pre-accident photograph cannot establish how the later fire started.',
         'source'=>'NASA Apollo 1 Gallery','url'=>'https://www.nasa.gov/gallery/apollo-1/',
         'rights'=>'Catalogue citation only. No photograph, NASA mark or astronaut likeness reproduced.'],
        ['id'=>'review','group'=>'primary','date'=>'1967-01-27','date_type'=>'Accident date; Board report issued afterward',
         'title'=>'Electrical arc: probable, not proven beyond doubt',
         'proof'=>'The Apollo 204 Review Board identified an electrical arc as the most probable initiator and reported an extremely hazardous oxygen-rich test environment.',
         'limit'=>'No single ignition source was conclusively identified. The accident date is not the report publication date.',
         'source'=>'NASA Apollo 204 Review Board','url'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
         'rights'=>'Official report linked; no NASA images or diagrams reused.'],
        ['id'=>'commemoration','group'=>'later','date'=>'2017-01-27','date_type'=>'NASA announcement / tribute opening',
         'title'=>'The preserved hatch is later historical interpretation',
         'proof'=>'NASA announced a Kennedy Space Center tribute featuring the Apollo 1 command-module hatch.',
         'limit'=>'The public display is not firsthand telemetry of the accident and does not identify the spark.',
         'source'=>'NASA Apollo 1 Tribute Announcement','url'=>'https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/',
         'rights'=>'Announcement linked without reusing exhibition photography.'],
        ['id'=>'testing','group'=>'later','date'=>'2018-02-14','date_type'=>'Publication date of retrospective',
         'title'=>'Later flammability tests do not locate the original spark',
         'proof'=>'NASA described later fire-safety testing conducted in the wake of Apollo 1.',
         'limit'=>'Follow-up testing informs safety changes, not the precise ignition location on January 27, 1967.',
         'source'=>'NASA: 50 Years Ago — Apollo Flammability Tests','url'=>'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
         'rights'=>'Official retrospective linked; no pictures or insignia imported.'],
    ];
}
function fv454_escape(string $value): string { return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv454_render(): string {
    static $instance = 0;
    $instance++;
    $id='fv454-'.(string)$instance;
    $html='<section class="fv454" id="'.$id.'" aria-labelledby="'.$id.'-title">';
    $html.='<p class="fv454__eyebrow">Experience 2.0 / Apollo 1 / Source custody</p>';
    $html.='<h2 id="'.$id.'-title">What the record can actually prove</h2>';
    $html.='<p class="fv454__lead">Read the historical finding beside its limitation. The rail distinguishes the date of an event from the date of a later publication.</p>';
    $html.='<p class="fv454__review">NASA source identity checked against agency pages. Independent editorial acceptance and commercial media clearance remain pending.</p>';
    $html.='<div class="fv454__filters" role="group" aria-label="Filter source periods"><button type="button" data-fv454-filter="all" aria-pressed="true">All four records</button><button type="button" data-fv454-filter="primary" aria-pressed="false">1966–67 evidence</button><button type="button" data-fv454-filter="later" aria-pressed="false">Later interpretation</button></div>';
    $html.='<ol class="fv454__rail">';
    foreach (fv454_sources() as $s) {
        $html.='<li class="fv454__plate" data-fv454-group="'.fv454_escape($s['group']).'">';
        $html.='<span class="fv454__date">'.fv454_escape($s['date']).'</span>';
        $html.='<p class="fv454__date-type">'.fv454_escape($s['date_type']).'</p>';
        $html.='<h3>'.fv454_escape($s['title']).'</h3>';
        $html.='<p class="fv454__label">Supported by source</p><p>'.fv454_escape($s['proof']).'</p>';
        $html.='<details class="fv454__drawer"><summary>Inspect source and limitation</summary>';
        $html.='<p><strong>Does not establish:</strong> '.fv454_escape($s['limit']).'</p>';
        $html.='<p><strong>Rights custody:</strong> '.fv454_escape($s['rights']).'</p>';
        $html.='<p><a href="'.fv454_escape($s['url']).'" rel="noopener noreferrer">'.fv454_escape($s['source']).' — official source</a></p>';
        $html.='</details></li>';
    }
    $html.='</ol>';
    $html.='<aside class="fv454__classroom" aria-labelledby="'.$id.'-classroom"><h3 id="'.$id.'-classroom">Original classroom evidence prompt</h3><p>Which source supports the probable initiator, and which later source cannot prove the original spark? Cite the record and explain the limitation. No signup or download is required.</p></aside>';
    $html.='<div class="fv454__cta"><p>Continue with the complete, free investigation. No paid product is offered here.</p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the full Apollo 1 investigation</a></div>';
    $html.='<p class="fv454__footnote">Original FV educational text. Sources are credited, not endorsed by NASA. No geographic pins or inferred relationships are asserted.</p>';
    $html.='</section>';
    $html.='<style>'.fv454_css().'</style><script>'.fv454_js().'</script>';
    return $html;
}
function fv454_css(): string { return <<<'CSS'
.fv454{--a:#eed3a0;--bg:#121a1b;--surface:#1c2829;--text:#f4f0e8;--muted:#c3cfcd;--line:#778b89;box-sizing:border-box;color:var(--text);background:var(--bg);padding:clamp(18px,5vw,64px);font:16px/1.65 system-ui,sans-serif;max-width:1920px;margin:auto}
.fv454 *{box-sizing:border-box}.fv454 h2{font:400 clamp(2rem,5vw,4.3rem)/1.1 Georgia,serif;max-width:17ch;margin:.4em 0}.fv454 h3{font:400 clamp(1.23rem,2vw,1.8rem)/1.25 Georgia,serif;margin:0 0 .8rem}.fv454 p{max-width:77ch}.fv454 a{color:var(--a);text-underline-offset:4px;overflow-wrap:anywhere}.fv454 :focus-visible{outline:3px solid #ffdf9b;outline-offset:4px}.fv454__eyebrow,.fv454__label,.fv454__date{font:700 .8rem/1.5 ui-monospace,monospace;letter-spacing:.075em;text-transform:uppercase;color:var(--a)}.fv454__lead{font-size:clamp(1.05rem,2vw,1.35rem)}.fv454__review,.fv454__footnote,.fv454__date-type{font-size:.88rem;color:var(--muted)}
.fv454__filters{display:none;flex-wrap:wrap;gap:.65rem;margin:2rem 0}.fv454.fv454--enhanced .fv454__filters{display:flex}.fv454__filters button{font:inherit;cursor:pointer;color:var(--text);background:transparent;border:1px solid var(--line);border-radius:3px;padding:.7rem .9rem;min-height:44px;touch-action:manipulation}.fv454__filters button[aria-pressed=true]{background:var(--a);color:#102022;border-color:var(--a);font-weight:700}
.fv454__rail{list-style:none;padding:0;margin:2rem 0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.fv454__plate{min-width:0;background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--a);padding:clamp(18px,3vw,30px)}.fv454__plate p{margin:.55rem 0 1rem}.fv454__date-type{margin:0 0 1rem!important}.fv454__drawer{border-top:1px solid var(--line);margin-top:1rem;padding-top:.6rem}.fv454__drawer summary{cursor:pointer;padding:.7rem .2rem;min-height:44px;touch-action:manipulation;font-weight:700}.fv454__drawer[open]{padding-bottom:.5rem}
.fv454__classroom{border-left:3px solid var(--a);padding:1rem 1.3rem;margin-top:2rem;background:var(--surface)}.fv454__cta{padding:1.3rem 0;border-top:1px solid var(--line);margin:2rem 0}.fv454__cta a{display:inline-block;border:1px solid var(--a);padding:.85rem 1rem;min-height:44px;font-weight:700;text-decoration:none}.fv454__cta a:hover{background:var(--a);color:var(--bg)}.fv454 [hidden]{display:none!important}
@media(max-width:720px){.fv454__rail{grid-template-columns:1fr}.fv454__plate{padding:18px}}@media(prefers-reduced-motion:reduce){.fv454 *, .fv454 *::before,.fv454 *::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}@media(forced-colors:active){.fv454{background:Canvas;color:CanvasText}.fv454__plate,.fv454__classroom{background:Canvas;border-color:CanvasText}.fv454__filters button[aria-pressed=true]{outline:2px solid Highlight}}@media print{.fv454{background:#fff;color:#000}.fv454__plate,.fv454__classroom{background:#fff;color:#000;border:1px solid #333}.fv454__filters{display:none!important}.fv454__plate[hidden]{display:list-item!important}.fv454 a,.fv454__date,.fv454__label{color:#000}.fv454__drawer:not([open]) > :not(summary){display:block}.fv454__rail{grid-template-columns:1fr}}
CSS; }
function fv454_js(): string { return <<<'JS'
(function(){document.querySelectorAll('.fv454:not(.fv454--enhanced)').forEach(function(root){var controls=root.querySelectorAll('[data-fv454-filter]');var plates=root.querySelectorAll('[data-fv454-group]');if(!controls.length||!plates.length)return;root.classList.add('fv454--enhanced');controls.forEach(function(button){button.addEventListener('click',function(){var wanted=button.getAttribute('data-fv454-filter');controls.forEach(function(b){b.setAttribute('aria-pressed',String(b===button));});plates.forEach(function(card){card.hidden=wanted!=='all'&&card.getAttribute('data-fv454-group')!==wanted;});});});});})();
JS; }
/** No general production registration. Every execution must be specifically enabled on a named staging page. */
if (function_exists('add_action')) {
    add_action('init', static function(): void {
        if (!defined('FV_R454_ENABLE_STAGING') || FV_R454_ENABLE_STAGING !== true ||
            !defined('FV_R454_STAGING_PAGE_ID') || !is_int(FV_R454_STAGING_PAGE_ID) || FV_R454_STAGING_PAGE_ID < 1 ||
            !function_exists('wp_get_environment_type') || wp_get_environment_type() !== 'staging' ||
            !function_exists('add_shortcode')) return;
        add_shortcode('fv_apollo_evidence_lab_r454', static function(): string {
            if (!function_exists('get_queried_object_id') || get_queried_object_id() !== FV_R454_STAGING_PAGE_ID) return '';
            return fv454_render();
        });
    });
}
