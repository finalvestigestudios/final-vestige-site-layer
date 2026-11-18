<?php
/**
 * Apollo R456: source-limited claims review (uninstalled staging-only candidate).
 * No merchant, trackers, cookies, image hotlinks, invented map coordinates, or production registrations.
 */
declare(strict_types=1);
function fv456_cases(): array {
    return [
      ['id'=>'spark','date'=>'1967-01-27','event'=>'Apollo 1 ground test',
       'claim'=>'NASA proved exactly which wire caused the fire.',
       'verdict'=>'Not established',
       'why'=>'The Apollo 204 Review Board found an electrical arc the most probable initiator but explicitly did not identify one ignition source conclusively.',
       'boundary'=>'The test date is not the Review Board report publication date. The most probable initiating mechanism is not a demonstrated specific wire.',
       'source'=>'NASA / Apollo 204 Review Board','url'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
       'role'=>'Primary investigation; report text linked without copying any imagery.',
       'rights'=>'Read the original source. NASA imagery is not reproduced or commercially cleared by this link.'],
      ['id'=>'memorial','date'=>'2017-01-27','event'=>'Kennedy Space Center Apollo 1 tribute',
       'claim'=>'NASA displayed the Apollo 1 hatch in a 2017 memorial tribute.',
       'verdict'=>'Supported, with a boundary',
       'why'=>'NASA’s announcement confirms the 2017 tribute included the spacecraft hatch.',
       'boundary'=>'A museum exhibit establishes an exhibition event, not the cause of the 1967 fire.',
       'source'=>'NASA / Apollo 1 tribute release','url'=>'https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/',
       'role'=>'Agency announcement dated January 27, 2017; not a contemporary accident record.',
       'rights'=>'Exhibit photos are not embedded. Any image or likeness reuse requires separate item review.'],
      ['id'=>'tests','date'=>'2018-02-14','event'=>'NASA flammability retrospective',
       'claim'=>'Later mock-up fire tests prove the exact source of the Apollo 1 ignition.',
       'verdict'=>'Not established',
       'why'=>'NASA describes tests performed after the accident to evaluate redesigned spacecraft and atmospheres.',
       'boundary'=>'The 2018 article publication date is not the test date; later experiments cannot identify the original spark.',
       'source'=>'NASA / 50 Years Ago: Apollo Flammability Tests','url'=>'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
       'role'=>'2018 institutional retrospective about 1967–1968 testing.',
       'rights'=>'Only a NASA text reference is linked; no NASA images or insignia used.']
    ];
}
function fv456_escape(string $s): string {return htmlspecialchars($s, ENT_QUOTES|ENT_SUBSTITUTE, 'UTF-8');}
function fv456_fallback(): string {return '<p class="fv456-fallback">The source exercise is temporarily unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';}
function fv456_valid(array $cases): bool {
    if(count($cases)!==3) return false;
    $ids=[];$dates=[];
    foreach($cases as $c){
      foreach(['id','date','event','claim','verdict','why','boundary','source','url','role','rights'] as $key){if(!isset($c[$key])||!is_string($c[$key])||trim($c[$key])==='')return false;}
      if(!preg_match('/^[a-z]{3,15}$/D',$c['id'])||isset($ids[$c['id']]))return false;
      $date=DateTimeImmutable::createFromFormat('!Y-m-d',$c['date']);
      if(!$date||$date->format('Y-m-d')!==$c['date']||($dates && $c['date']<=end($dates)))return false;
      $p=parse_url($c['url']);
      if(!is_array($p)||($p['scheme']??'')!=='https'||($p['host']??'')!=='www.nasa.gov'||isset($p['user'])||isset($p['pass'])||isset($p['query'])||isset($p['fragment'])||substr($p['path']??'',0,1)!=='/')return false;
      $ids[$c['id']]=true;$dates[]=$c['date'];
    }
    return true;
}
function fv456_assets(): ?array {
    $names=['css'=>['claims.css','3ba6dd76cf90281e1f4683e106522cf6b89ad1a3604784f0e6e610a89f361a47'],'js'=>['claims.js','69477c0475010c6ae59222195e5839e7ed75a42254c3b81d2441624cec74ead5']];$assets=[];
    foreach($names as $type=>$pair){
      [$file,$expected]=$pair;$path=__DIR__.'/assets/'.$file;
      if(!is_readable($path)||!is_file($path)||!hash_equals($expected,hash_file('sha256',$path)))return null;
      $contents=file_get_contents($path);if(!is_string($contents)||!$contents)return null;
      $assets[$type]=$contents;
    }
    return $assets;
}
function fv456_render(): string {
    static $sequence=0;
    $cases=fv456_cases();$assets=fv456_assets();if(!fv456_valid($cases)||$assets===null)return fv456_fallback();
    $id='fv456-'.(++$sequence);
    $html='<section class="fv456" id="'.$id.'" aria-labelledby="'.$id.'-title" data-fv456-root>';
    $html.='<p class="fv456__eyebrow">Final Vestige / Apollo 1 / Research Desk</p>';
    $html.='<h2 id="'.$id.'-title">What does the evidence actually prove?</h2>';
    $html.='<p class="fv456__intro">Three documentary claims. Three official NASA sources. Inspect both the supported conclusion and its limits before trusting a retelling.</p>';
    $html.='<p class="fv456__trust"><strong>Source custody:</strong> This independent editorial exercise links NASA primary and institutional records. NASA does not endorse this page. No NASA photographs or logos are embedded or represented as commercially licensed.</p>';
    $html.='<h3 id="'.$id.'-questions">Choose an evidence question</h3>';
    $html.='<div class="fv456__controls" aria-labelledby="'.$id.'-questions" data-fv456-controls hidden>';
    $html.='<button type="button" data-fv456-select="all" aria-pressed="true">All three claims</button>';
    foreach($cases as $n=>$c){$html.='<button type="button" data-fv456-select="'.fv456_escape($c['id']).'" aria-pressed="false">Claim '.($n+1).'</button>';}
    $html.='</div><p class="fv456__status" data-fv456-status role="status" aria-live="polite">All three claims and their supporting sources are available.</p>';
    $html.='<ol class="fv456__rail" aria-label="Claims ordered by documented event or publication date">';
    foreach($cases as $n=>$c){
      $html.='<li class="fv456__case" data-fv456-case="'.fv456_escape($c['id']).'">';
      $html.='<p class="fv456__index">Case '.($n+1).' / <time datetime="'.fv456_escape($c['date']).'">'.fv456_escape($c['date']).'</time></p>';
      $html.='<p class="fv456__context">'.fv456_escape($c['event']).'</p>';
      $html.='<h4>“'.fv456_escape($c['claim']).'”</h4>';
      $html.='<p class="fv456__verdict"><strong>Judgment:</strong> '.fv456_escape($c['verdict']).'</p>';
      $html.='<p><strong>What NASA supports:</strong> '.fv456_escape($c['why']).'</p>';
      $html.='<p><strong>What it does not settle:</strong> '.fv456_escape($c['boundary']).'</p>';
      $html.='<details><summary>Inspect original citation, source role and media-use limits</summary>';
      $html.='<p><strong>Source role:</strong> '.fv456_escape($c['role']).'</p>';
      $html.='<p><strong>Media custody:</strong> '.fv456_escape($c['rights']).'</p>';
      $html.='<p><a href="'.fv456_escape($c['url']).'" rel="noopener noreferrer">'.fv456_escape($c['source']).' — official source</a></p>';
      $html.='</details></li>';
    }
    $html.='</ol><aside class="fv456__lesson"><h3>For educators: identify the reasoning error</h3><p>Ask learners to label each statement as supported, unsupported, or supported with limitations. Require a citation and one sentence explaining what the source cannot establish. The three worked answers above remain readable without JavaScript.</p></aside>';
    $html.='<p class="fv456__next"><span>Continue from evidence to the original narrative.</span> <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the complete free Apollo 1 investigation</a></p>';
    $html.='<p class="fv456__endnote">Chronology is editorially curated, not geographic. No speculative map pins, manufactured source relationships, product listing or purchase claim.</p></section>';
    return $html.'<style>'.$assets['css'].'</style><script>'.$assets['js'].'</script>';
}
if(function_exists('add_action'))add_action('init',static function(): void {
    if(!defined('FV_R456_ENABLE_STAGING')||FV_R456_ENABLE_STAGING!==true||!defined('FV_R456_STAGING_PAGE_ID')||!is_int(FV_R456_STAGING_PAGE_ID)||FV_R456_STAGING_PAGE_ID<1||!function_exists('wp_get_environment_type')||wp_get_environment_type()!=='staging'||!function_exists('add_shortcode'))return;
    add_shortcode('fv_apollo_claim_review_r456',static function(): string {
        if(!function_exists('get_queried_object_id')||get_queried_object_id()!==FV_R456_STAGING_PAGE_ID)return '';
        return fv456_render();
    });
});
